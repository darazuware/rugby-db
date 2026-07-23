"""JRFU 代表戦日程スクレイパー（02: 「JRFU（jrfu.jp）」日本代表の試合日程・会場）。

02 は "jrfu.jp" と表記するが、その名前は解決不可能（実在しないドメイン）。
日本代表応援サイトの実ドメインは www.rugby-japan.jp（2026-07-18 に実ページで確認、
schemas.ALLOWED_DOMAINS に追加済み）。

試合一覧の索引は www.rugby-japan.jp/braveblossoms/ が読み込む静的JSON
（S3ホスト。rugby-japan.jp ドメイン外のため source_url には使わず、match_id の
列挙にのみ使う）から取得する。各試合の詳細（開催日時・会場・スコア・ステータス）
は同ドメイン自身のAPI /v1.0/game.php?game_id={id} から取得する（これは
公式サイト自身が提供するエンドポイントで rugby-japan.jp ドメイン内）。

公開関数:
    collect_matches(year=None) -> {"matches": [...], "opponent_slugs": [...], "warnings": [...]}
      opponent_slugs は all.rugby のクラブslug相当（02: national.json のスコッド
      取得対象国の絞り込みに scrape.all_rugby.collect_national() が使う）。
    collect_sevens() / collect_age_grade() -> {"players": [...], "teams": [], "matches": [],
      "standings": [], "warnings": [...]}（P5-3: 10_YOUTH_AGEGRADE.md セブンズ/U代表スコッド）。
      構造化された一覧+詳細ページ（/{squad}/member/ , /{squad}/member/detail/{id}）を使う。
      02が想定していた「記事HTML内の名簿を粗抽出」より安定した公式データソースが
      実ページ確認（2026-07-18）で見つかったため、選手個人の事実
      （氏名・所属・身長体重・生年月日・SNS）は詳細ページの構造化フィールドから直接取得する。
      Sonnetフォールバックは、詳細ページのBIOGRAPHY自由記述にある出身校テキスト
      （正規表現の高校/大学サフィックス判定で分類できなかったもののみ）の
      hs/univ 種別判定にのみ使う（pipeline.llm_fallback）。
"""
from __future__ import annotations

import os
import re
import time
import unicodedata
from typing import Optional

import requests
from bs4 import BeautifulSoup

from pipeline import llm_fallback, school_types
from pipeline.schemas import normalize_name_en
from pipeline.transform import normalize

BASE = "https://www.rugby-japan.jp"
# 試合一覧の索引用JSON（S3配信、rugby-japan.jp ドメイン外なので source_url には使わない）。
_SCHEDULE_INDEX_URL = (
    "https://rugby-japan.s3.ap-northeast-1.amazonaws.com/"
    "static-assets/wbb/js/data/match-schedule.json"
)
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
_SLEEP = 1.5
_TIMEOUT = 15
_RETRIES = 2

# JRFU上のチーム表記 → all.rugby クラブslug相当（実ページで確認、2026-07-18時点の
# 15人制男子代表スケジュールに登場する範囲のみ登録。原則3: 未登録表記は突合しない）。
TEAM_SLUGS = {
    "日本代表": "japan",
    "JAPAN XV": "japan-xv",
    "フランス代表": "france",
    "イタリア代表": "italy",
    "アイルランド代表": "ireland",
    "オーストラリア代表": "australia",
    "カナダ代表": "canada",
    "スコットランド代表": "scotland",
    "マオリ・オールブラックス": "maori-all-blacks",
}
# JAPAN XV・マオリ・オールブラックスは主権国代表ではないため、
# national.json のスコッド取得対象（対戦"国"）からは除外する（02）。
NON_COUNTRY_SLUGS = {"japan-xv", "maori-all-blacks"}
_JAPAN_SIDE_NAMES = {"日本代表", "JAPAN XV"}


def _get_json(url: str) -> Optional[object]:
    """GET→JSON（timeout=15、指数バックオフ最大2回、失敗はNone）。"""
    delay = 1.0
    for attempt in range(_RETRIES + 1):
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if attempt >= _RETRIES:
                return None
            time.sleep(delay)
            delay *= 2
    return None


def process_entry(entry: dict, g: dict) -> tuple[Optional[dict], Optional[str], list[str]]:
    """索引1件(entry) + game.php詳細(g) → (Match dict|None, 対戦国slug|None, warnings)。

    ネットワークを伴わない純粋関数（テスト容易性のため collect_matches から分離）。
    対戦国slug は home が日本側（日本代表/JAPAN XV）なら away 側、そうでなければ
    home 側を採用する。NON_COUNTRY_SLUGS（JAPAN XV・マオリ・オールブラックス）は
    「対戦国」としては返さない（02の絞り込み対象外）。
    """
    game_id = entry.get("id")
    home_raw = (entry.get("home") or "").strip()
    away_raw = (entry.get("away") or "").strip()
    home_slug = TEAM_SLUGS.get(home_raw)
    away_slug = TEAM_SLUGS.get(away_raw)
    if home_slug is None or away_slug is None:
        return None, None, [
            f"jrfu: game_id={game_id} の未登録チーム表記 home={home_raw!r} "
            f"away={away_raw!r} のためスキップ"]

    opp_slug = away_slug if home_raw in _JAPAN_SIDE_NAMES else home_slug
    opponent = opp_slug if opp_slug not in NON_COUNTRY_SLUGS else None

    match, warnings = normalize.match_jrfu(g, home_slug=home_slug, away_slug=away_slug, game_id=game_id)
    return match, opponent, warnings


def collect_matches(year: Optional[int] = None) -> dict:
    """試合索引→詳細を辿って Match レコードと対戦国スラッグ一覧を組み立てる。

    year は現状未使用（索引JSONが常に直近シーズン分のみを返すため）。
    将来的にシーズンを跨いだ絞り込みが必要になった場合に備えて引数だけ残す。
    """
    warnings: list[str] = []
    index = _get_json(_SCHEDULE_INDEX_URL)
    if not isinstance(index, list):
        warnings.append("jrfu: 試合スケジュール索引の取得失敗")
        return {"matches": [], "opponent_slugs": [], "warnings": warnings}

    matches_out: list[dict] = []
    opponent_slugs: list[str] = []
    seen_opponents: set[str] = set()

    for entry in index:
        game_id = entry.get("id")
        if not game_id:
            continue
        detail = _get_json(f"{BASE}/v1.0/game.php?game_id={game_id}")
        time.sleep(_SLEEP)
        game_list = detail.get("game_list") if isinstance(detail, dict) else None
        if not game_list:
            warnings.append(f"jrfu: game_id={game_id} 詳細取得失敗、スキップ")
            continue

        match, opponent, ew = process_entry(entry, game_list[0])
        warnings.extend(ew)
        if match is not None:
            matches_out.append(match)
        if opponent is not None and opponent not in seen_opponents:
            seen_opponents.add(opponent)
            opponent_slugs.append(opponent)

    return {"matches": matches_out, "opponent_slugs": opponent_slugs, "warnings": warnings}


# ---------------------------------------------------------------------------
# P5-3: セブンズ/U代表スコッド（10_YOUTH_AGEGRADE.md）
#
# ソース: www.rugby-japan.jp の一覧+詳細ページ（実ページ確認 2026-07-18）。
#   一覧: /{squad}/member/               -> <li><a href=".../detail/{id}">...
#   詳細: /{squad}/member/detail/{id}    -> 氏名(和文/英文)・所属・身長体重・
#                                            生年月日・SNS・(セブンズのみ)BIOGRAPHY
# 02は「記事HTML内の名簿を粗抽出→Sonnetで抽出」という設計だったが、実際には
# このmember一覧+詳細ページの方が構造が安定しており選手個人の事実を直接取得できる
# ため、そちらを正データ源とする。Sonnetフォールバックは 10 が想定した用途
# （粗抽出テキストからのJSON構造化）そのものではなく、詳細ページの自由記述
# BIOGRAPHY にある出身校名の hs/univ 種別判定という、同じ「構造が不定な部分だけ
# LLMに絞って渡す」設計思想を保った適用箇所として使う。
# ---------------------------------------------------------------------------

# squad key -> URL パス（末尾 /member を除く）。u19 は 2026-07-18 時点で
# 一覧ページが404（現行スコッド未発表）。存在しない場合は _collect_squad が
# warning を積むだけでスキップする（無理に偽データを作らない）。
_SQUAD_PATH = {
    "sevens_m": "/sevens",
    "sevens_w": "/sevens-womens",
    "u17": "/u17",
    "u18": "/u18",
    "u19": "/u19",
    "u20": "/u20",
    "u23": "/u23",
    "national": "/japan",
}

# 15人制日本代表スコッド一覧（/japan/member/）に掲載されていない選手（例: 大学
# 在籍で候補どまり）でも、rugby-japan.jp の汎用選手データベース /player/{id} に
# 個別ページを持つことがある（2026-07-23実ページ確認: /player/482538 = 矢崎由高
# 〈早稲田大学〉、squad詳細ページと同一のHTML構造）。人手でURLを確認できたものの
# みここに登録する（normalize_name_en(氏名) -> 数値ID）。
_EXTRA_PLAYER_IDS = {
    "yoshitaka yazaki": "482538",
}
SEVENS_SQUADS = ("sevens_m", "sevens_w")
AGE_GRADE_SQUADS = ("u17", "u18", "u19", "u20", "u23")

# 学校名の種別判定（正規表現）。用字ゆれ（高等科等）は実データ確認済みの範囲で追加。
_HS_SUFFIX_RE = re.compile(r"(高等学校|高等科|高校)$")
_UNIV_SUFFIX_RE = re.compile(r"(大学校|大学)$")
_MS_SUFFIX_RE = re.compile(r"(中学校|中等部|中学)$")


def _get_html(url: str) -> Optional[str]:
    """GET→HTML文字列（timeout=15、指数バックオフ最大2回、失敗はNone）。"""
    delay = 1.0
    for attempt in range(_RETRIES + 1):
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.text
        except Exception:
            if attempt >= _RETRIES:
                return None
            time.sleep(delay)
            delay *= 2
    return None


def _num(text: Optional[str]) -> Optional[str]:
    """'171cm' / '102kg' -> '171'。数字が無ければNone。"""
    if not text:
        return None
    m = re.search(r"\d+", text)
    return m.group(0) if m else None


def _classify_school_regex(name: str) -> Optional[str]:
    """学校名文字列 -> "hs"|"univ"|None（サフィックス→ローカル辞書、不能ならNone）。"""
    s = name.strip()
    if _HS_SUFFIX_RE.search(s):
        return "hs"
    if _UNIV_SUFFIX_RE.search(s):
        return "univ"
    return school_types.classify(s)


def _parse_detail(html: str, detail_url: str) -> dict:
    """詳細ページHTML -> raw dict（氏名/所属/身長体重/生年月日/SNS/出身校自由記述）。"""
    soup = BeautifulSoup(html, "html.parser")
    info = soup.select_one("div.info")
    name_ja = name_en = None
    if info is not None:
        jp = info.select_one("strong.jp")
        en = info.select_one("span.en")
        name_ja = jp.get_text(strip=True) if jp else None
        name_en = en.get_text(strip=True) if en else None
    if not name_ja:
        # セブンズ一覧ページのカード表記に近いフォールバック（詳細ページ構造が
        # 想定と異なる場合のみ使用）。
        strong = soup.select_one("strong.name") or soup.select_one("strong.jp")
        name_ja = strong.get_text(strip=True) if strong else None

    position_el = soup.select_one("span.position")
    position = position_el.get_text(strip=True) if position_el else None

    team_el = soup.select_one("div.team")
    team_raw = team_el.get_text(strip=True) if team_el else None

    height_cm = weight_kg = birthdate = None
    for li in soup.select("ul.list li"):
        th = li.select_one("span.th")
        td = li.select_one("strong.td")
        if th is None or td is None:
            continue
        label = th.get_text(strip=True)
        val = td.get_text(strip=True)
        if label == "Height":
            height_cm = _num(val)
        elif label == "Weight":
            weight_kg = _num(val)
        elif label == "Date of Birth":
            birthdate = val or None

    instagram = None
    for a in soup.select("div.sns a"):
        href = (a.get("href") or "").strip()
        if href.startswith("https://www.instagram.com/") or href.startswith("http://www.instagram.com/"):
            instagram = href
            break

    education_segments_raw: list[str] = []
    bio_p = soup.select_one("div.biography p")
    if bio_p is not None:
        text = bio_p.get_text("\n", strip=True)
        m = re.search(r"【出身校】\s*\n(.+?)(?:\n【|\Z)", text, re.S)
        if m:
            block = m.group(1).strip()
            for seg in re.split(r"[〜~]", block):
                seg = seg.strip()
                # 末尾の全角/半角括弧（都道府県・国名等）を除去。
                seg = re.sub(r"[（(][^）)]*[）)]\s*$", "", seg).strip()
                if seg:
                    education_segments_raw.append(seg)

    return {
        "detail_url": detail_url,
        "name_ja": name_ja,
        "name_en": name_en,
        "position": position,
        "team_raw": team_raw,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "birthdate": birthdate,
        "instagram": instagram,
        "education_segments_raw": education_segments_raw,
    }


def _collect_squad(squad_key: str) -> dict:
    """1スコッド分の一覧→詳細を辿り、raw dict のリストを返す（教育歴は未分類）。"""
    warnings: list[str] = []
    path = _SQUAD_PATH[squad_key]
    list_html = _get_html(f"{BASE}{path}/member/")
    time.sleep(_SLEEP)
    if list_html is None:
        warnings.append(f"jrfu {squad_key}: 一覧ページ取得失敗（404含む）、スキップ")
        return {"raws": [], "warnings": warnings}

    ids = sorted(set(re.findall(rf"{re.escape(path)}/member/detail/(\d+)", list_html)), key=int)
    if not ids:
        warnings.append(f"jrfu {squad_key}: 一覧ページからdetail IDが0件のためスキップ")
        return {"raws": [], "warnings": warnings}

    raws: list[dict] = []
    for did in ids:
        durl = f"{BASE}{path}/member/detail/{did}"
        dhtml = _get_html(durl)
        time.sleep(_SLEEP)
        if dhtml is None:
            warnings.append(f"jrfu {squad_key}: detail/{did} 取得失敗、スキップ")
            continue
        raw = _parse_detail(dhtml, durl)
        raw["detail_id"] = did
        raw["squad"] = squad_key
        raws.append(raw)
    return {"raws": raws, "warnings": warnings}


def _classify_and_build(all_raws: list[dict], *, league: str) -> tuple[list[dict], list[str]]:
    """team_raw・出身校自由記述を分類し、Player dict のリストに変換する。

    分類は 1) 正規表現サフィックス、2) それでも不明な項目のみを束ねて
    pipeline.llm_fallback.classify_school_names() に1回だけ渡す、の2段構え
    （02: 「抽出失敗時のみSonnetに粗抽出ブロックだけ渡す」の思想を踏襲）。
    どちらでも判定できなかった学校名は education に入れず warning のみ残す
    （00原則3: 不明はnull。学校名という事実自体はスクレイプ結果のまま変えない）。
    """
    warnings: list[str] = []
    unresolved: set[str] = set()

    for raw in all_raws:
        tr = raw.get("team_raw")
        if tr and _classify_school_regex(tr) is None:
            unresolved.add(tr)
        kept_segments = []
        for seg in raw.get("education_segments_raw", []):
            if _MS_SUFFIX_RE.search(seg):
                continue  # 中学は Education スキーマの対象外（hs/univのみ）
            kept_segments.append(seg)
            if _classify_school_regex(seg) is None:
                unresolved.add(seg)
        raw["_education_segments"] = kept_segments

    llm_result: dict[str, str] = {}
    if unresolved:
        llm_input = sorted(unresolved)
        llm_result = llm_fallback.classify_school_names(llm_input)
        still_unresolved = sorted(set(llm_input) - set(llm_result))
        if still_unresolved:
            warnings.append(
                f"jrfu {league}: 学校名{len(still_unresolved)}件を正規表現・辞書・Sonnet"
                f"いずれでもtype判定できず（例: {still_unresolved[:3]}）"
            )
        if not llm_result and not os.environ.get("ANTHROPIC_API_KEY"):
            warnings.append(
                f"jrfu {league}: ANTHROPIC_API_KEY未設定のためSonnetフォールバックを"
                f"スキップ（未判定{len(unresolved)}件は学校扱いにしない: "
                f"所属欄はcareerへ、出身校欄はeducationから除外）"
            )

    def _type_of(name: str) -> Optional[str]:
        return _classify_school_regex(name) or llm_result.get(name)

    players_out: list[dict] = []
    for raw in all_raws:
        education: list[dict] = []
        career: list[dict] = []

        team_raw = raw.get("team_raw")
        if team_raw:
            t = _type_of(team_raw)
            if t is not None:
                education.append({"name_raw": team_raw, "type": t})
            else:
                career.append({"team": team_raw})

        for seg in raw.get("_education_segments", []):
            t = _type_of(seg)
            if t is not None:
                education.append({"name_raw": seg, "type": t})
            # 判定不能segmentは落とす（既にwarning済み）

        raw["_education"] = education
        raw["_career"] = career
        player, pw = normalize.player_jrfu_squad(raw, league=league)
        warnings.extend(pw)
        if player is not None:
            players_out.append(player)

    return players_out, warnings


def collect_sevens() -> dict:
    """男女セブンズ日本代表スコッド（squad: sevens_m/sevens_w）を収集する（P5-3）。"""
    warnings: list[str] = []
    all_raws: list[dict] = []
    for squad_key in SEVENS_SQUADS:
        res = _collect_squad(squad_key)
        warnings.extend(res["warnings"])
        all_raws.extend(res["raws"])

    players, cw = _classify_and_build(all_raws, league="sevens-national")
    warnings.extend(cw)
    return {"players": players, "teams": [], "matches": [], "standings": [], "warnings": warnings}


def collect_age_grade() -> dict:
    """U17/U18/U19/U20/U23日本代表スコッドを収集する（P5-3）。

    u19 は 2026-07-18 時点でスコッド未発表（一覧ページ404）。他squadの取得は
    継続し、警告のみ積む。
    """
    warnings: list[str] = []
    all_raws: list[dict] = []
    for squad_key in AGE_GRADE_SQUADS:
        res = _collect_squad(squad_key)
        warnings.extend(res["warnings"])
        all_raws.extend(res["raws"])

    players, cw = _classify_and_build(all_raws, league="age-grade")
    warnings.extend(cw)
    return {"players": players, "teams": [], "matches": [], "standings": [], "warnings": warnings}


def collect_national_birthdates() -> dict:
    """15人制日本代表（/japan/member/、squad="national"）を1回のfetchで収集する。

    2用途を同じ /japan/member/ 一覧+詳細から取得する（二重fetchを避けるため統合）:

    1. 生年月日マップ（"map"）: all.rugby の日本代表選手個別ページには生年月日が
       載っておらず null になる（2026-07-22 確認）ため、氏名突合でJRFU公式の値を
       正として補うためのマップ。all_rugby.collect_national() が使う。

    2. スコッド選手レコード（"players"）: /japan/member/ には all.rugby の
       /club/japan/squad（＝国際キャップ保持者）に載らない国内の代表候補
       （例: 明大・伊藤龍之介ら大学/リーグワン所属の未キャップ選手）が含まれる。
       これらは従来 birthdate だけ抜いて選手本体を捨てていたが、名鑑サイトとしては
       代表候補こそ拾いたい情報のため、squad="national" のPlayerレコードとして
       返す。all_rugby.collect_national() 側で、all.rugby由来のJapan選手と氏名突合
       できなかった（＝キャップ無しでall.rugbyに載らない）者のみ national.json に
       追加する。当代表チームのキャップ・career等の正データ源は引き続き all.rugby。

    戻り値: {"map": {normalize_name_en(氏名): {"birthdate": "YYYY/MM/DD",
    "source_url": str}}, "players": [Player dict, ...], "warnings": [...]}
    """
    res = _collect_squad("national")
    warnings = list(res["warnings"])

    # /japan/member/ の raws をそのままPlayerレコード化（squad="national"）。
    # team_id はここでは None のまま（player_jrfu_squad の既定）。国別グルーピング用の
    # team_id="japan" は all_rugby.collect_national() 追加時に付与する。
    squad_players, pw = _classify_and_build(res["raws"], league="national")
    warnings.extend(pw)
    name_map: dict[str, dict] = {}
    for raw in res["raws"]:
        name_en = raw.get("name_en")
        birthdate = raw.get("birthdate")
        if not name_en or not birthdate:
            continue
        entry = {"birthdate": birthdate, "source_url": raw["detail_url"]}
        # normalize_name_en はアポストロフィを空白に変換するため、all.rugby側の
        # 表記（アポストロフィなし）と食い違うことがある（例: HA'ANGANA）。
        # アポストロフィを削除した版も突合キーとして併せて登録する。
        for key in {normalize_name_en(name_en), normalize_name_en(name_en.replace("'", ""))}:
            name_map[key] = entry

    for key, player_id in _EXTRA_PLAYER_IDS.items():
        if key in name_map:
            continue
        detail_url = f"{BASE}/player/{player_id}"
        html = _get_html(detail_url)
        time.sleep(_SLEEP)
        if html is None:
            warnings.append(f"jrfu national extra: /player/{player_id} 取得失敗、スキップ")
            continue
        raw = _parse_detail(html, detail_url)
        if not raw.get("birthdate"):
            continue
        name_map[key] = {"birthdate": raw["birthdate"], "source_url": detail_url}

    return {"map": name_map, "players": squad_players, "warnings": warnings}


# ---------------------------------------------------------------------------
# gap B: 招集・合宿メンバー発表ニュース。
#   /news/category/national/ の「参加メンバーのお知らせ」記事本文には、FW/BKごとの
#   HTMLテーブル（氏名和英・所属チーム和英・出身校和英・身長・体重・生年月日・キャップ）が
#   埋まっており、選手個別ページ（detail）を辿らずとも34名分の事実を直接取得できる
#   （2026-07-23 /news/54087 実ページで確認）。標準の登録メンバー表(/japan/member/)に
#   載らない追加招集・合宿参加選手（＝名鑑サイトが最も拾いたい代表候補）を、招集イベント
#   として拾うためのソース。純関数（list_national_callup_news / parse_call_up_article）と
#   ネットワーク収集（collect_call_ups）に分け、前者をフィクスチャで単体テストする。
# ---------------------------------------------------------------------------
_NEWS_BASE = f"{BASE}/news"
_NEWS_CATEGORY_NATIONAL = f"{_NEWS_BASE}/category/national/"
_NEWS_ID_RE = re.compile(r"/news/(\d+)")
_DATE_YMD_JP = re.compile(r"(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日")
_DATE_YMD_DOT = re.compile(r"(\d{4})\.(\d{1,2})\.(\d{1,2})")
_POS_HEAD_RE = re.compile(r"[■●]?\s*(FW|BK)")
# 男子15人制代表のロースター発表のみを対象にする事前フィルタ。女子/セブンズ/U世代/
# レポート/実施予告は本タスク（league="national"）の対象外。本文テーブル有無での最終
# 判定（parse側でNone返し）と併せた二段構えで、タイトルだけの誤判定を本文で救済する。
_CALLUP_TITLE_INCLUDE = re.compile(r"(参加メンバー|招集メンバー)")
_CALLUP_TITLE_EXCLUDE = re.compile(
    r"(セブンズ|7人制|７人制|女子|U-?2\d|U-?1\d|ジュニア|SDS|デベロップメント|"
    r"レポート|リポート|実施のお知らせ|TID|大学選抜)")
_CALLUP_KIND = (("合宿", "camp"), ("遠征", "tour"), ("登録", "squad"), ("スコッド", "squad"))
_CALLUP_MAX_ARTICLES = 8  # 一覧上位のみ本文確認（過剰fetch防止）


def _nfc(text: Optional[str]) -> Optional[str]:
    """JRFUニュースHTMLは濁点分解（NFD、例「バ」=「ハ」+U+3099）で配信されることがある
    （2026-07-23 /news/54087 で確認）。正規表現・氏名突合が壊れるためNFCに正規化する。"""
    return unicodedata.normalize("NFC", text) if text else text


def _callup_kind(title: str) -> str:
    for kw, kind in _CALLUP_KIND:
        if kw in title:
            return kind
    return "squad"


def _callup_title_head(link_text: str) -> str:
    """一覧リンクは「タイトル 2026.7.23 （曜）本文抜粋…」の連結なので、日付トークンの
    手前までをタイトルとみなす（本文抜粋の語で誤フィルタしないため）。"""
    link_text = _nfc(link_text) or ""
    m = _DATE_YMD_DOT.search(link_text)
    return link_text[: m.start()].strip() if m else link_text.strip()


def list_national_callup_news(html: str) -> list[dict]:
    """カテゴリ一覧HTML → [{news_id, url, title}]（タイトル事前フィルタ通過分のみ）。"""
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    out: list[dict] = []
    for a in soup.find_all("a", href=_NEWS_ID_RE):
        m = _NEWS_ID_RE.search(a.get("href", ""))
        if not m:
            continue
        nid = m.group(1)
        if nid in seen:
            continue
        title = _callup_title_head(a.get_text(" ", strip=True))
        if not _CALLUP_TITLE_INCLUDE.search(title) or _CALLUP_TITLE_EXCLUDE.search(title):
            continue
        seen.add(nid)
        out.append({"news_id": nid, "url": f"{_NEWS_BASE}/{nid}", "title": title})
    return out


def _cell_ja_en(cell) -> tuple[Optional[str], Optional[str]]:
    """テーブルセル（<p>和文</p><p>英文</p>）→ (和文, 英文)。"""
    ps = [_nfc(p.get_text(" ", strip=True).replace("\xa0", " ").strip()) for p in cell.find_all("p")]
    ps = [p for p in ps if p]
    if not ps:
        t = _nfc(cell.get_text(" ", strip=True).replace("\xa0", " ").strip())
        return (t or None, None)
    return (ps[0] or None, (ps[1] if len(ps) > 1 else None) or None)


def parse_call_up_article(html: str, url: str) -> Optional[dict]:
    """招集・合宿メンバー記事HTML → イベントdict。メンバーテーブルが無ければNone
    （＝ロースター記事でない。実施予告・レポート等をここで確実に弾く）。"""
    soup = BeautifulSoup(html, "html.parser")
    title = None
    tt = soup.find("title")
    if tt:
        title = _nfc(tt.get_text(strip=True).split("｜")[0].strip()) or None

    member_tables = []
    for t in soup.find_all("table"):
        head = t.find("tr")
        if head and "名前" in head.get_text(" ", strip=True) and "キャップ" in head.get_text(" ", strip=True):
            member_tables.append(t)
    if not member_tables:
        return None

    members: list[dict] = []
    for t in member_tables:
        pg = None
        prev = t
        for _ in range(6):
            prev = prev.find_previous(["p", "h2", "h3", "h4", "strong", "b"])
            if prev is None:
                break
            m = _POS_HEAD_RE.search(prev.get_text(" ", strip=True))
            if m:
                pg = m.group(1)
                break
        for r in t.find_all("tr")[1:]:
            cells = r.find_all(["td", "th"])
            if len(cells) < 7:
                continue
            name_ja, name_en = _cell_ja_en(cells[0])
            if not (name_ja or name_en):
                continue
            club_ja, _ = _cell_ja_en(cells[1])
            school_ja, _ = _cell_ja_en(cells[2])
            caps_raw = cells[6].get_text(strip=True)
            members.append({
                "name_ja": name_ja,
                "name_en": name_en,
                "position_group": pg,
                "club_raw": club_ja,
                "school_raw": school_ja,
                "height_cm": _num(cells[3].get_text(strip=True)),
                "weight_kg": _num(cells[4].get_text(strip=True)),
                "birthdate": cells[5].get_text(strip=True) or None,
                "caps": int(caps_raw) if caps_raw.isdigit() else None,
            })
    if not members:
        return None

    body_text = _nfc(soup.get_text("\n", strip=True)) or ""
    start_date = venue = None
    for line in body_text.split("\n"):
        if start_date is None and ("日程" in line or "期間" in line):
            m = _DATE_YMD_JP.search(line)
            if m:
                start_date = f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        if venue is None and "会場" in line:
            mq = re.search(r"「([^」]+)」", line)
            if mq:
                venue = mq.group(1).strip()
    nid_m = _NEWS_ID_RE.search(url)
    return {
        "news_id": nid_m.group(1) if nid_m else None,
        "source_url": url,
        "title": title,
        "kind": _callup_kind(title or ""),
        "venue": venue,
        "start_date": start_date,
        "members": members,
        "warnings": [],
    }


def callup_members_to_players(event: dict, *, league: str = "national") -> tuple[list[dict], list[str]]:
    """招集イベントのメンバー行 → Player dict リスト（facts統合用）。

    所属チーム(club_raw)→career、出身校(school_raw)→education(hs/univは正規表現分類)。
    出身校が単一の学校名（bio自由記述でない）なのでLLMフォールバックは不要。
    """
    players: list[dict] = []
    warnings: list[str] = []
    src = event.get("source_url")
    for m in event.get("members", []):
        education: list[dict] = []
        career: list[dict] = []
        school = m.get("school_raw")
        if school:
            t = _classify_school_regex(school)
            if t is not None:
                education.append({"name_raw": school, "type": t})
            else:
                warnings.append(f"jrfu callup: 出身校 {school!r} をtype判定できずeducationから除外")
        club = m.get("club_raw")
        if club:
            career.append({"team": club})
        raw = dict(m)
        raw["_education"] = education
        raw["_career"] = career
        player, pw = normalize.player_jrfu_callup(raw, league=league, source_url=src)
        warnings.extend(pw)
        if player is not None:
            players.append(player)
    return players, warnings


def collect_call_ups() -> dict:
    """/news/category/national/ から男子代表の招集・合宿メンバー発表を収集する（gap B）。

    戻り値: {"events": [parse_call_up_article の出力, ...], "warnings": [...]}。
    events は news_id 昇順（＝発表が新しいものほど大きい）にソートして返す。
    """
    warnings: list[str] = []
    idx = _get_html(_NEWS_CATEGORY_NATIONAL)
    if idx is None:
        return {"events": [], "warnings": ["jrfu callup: カテゴリ一覧取得失敗、スキップ"]}
    cands = list_national_callup_news(idx)[:_CALLUP_MAX_ARTICLES]
    events: list[dict] = []
    for c in cands:
        html = _get_html(c["url"])
        time.sleep(_SLEEP)
        if html is None:
            warnings.append(f"jrfu callup: {c['url']} 取得失敗、スキップ")
            continue
        ev = parse_call_up_article(html, c["url"])
        if ev is None:
            continue
        warnings.extend(ev.pop("warnings", []))
        events.append(ev)
    events.sort(key=lambda e: int(e["news_id"]) if (e.get("news_id") or "").isdigit() else 0)
    return {"events": events, "warnings": warnings}
