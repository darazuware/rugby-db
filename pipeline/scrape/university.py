"""P5-5: 大学ラグビー部員名簿スクレイパー（10_YOUTH_AGEGRADE.md 大学スコープ / 02_SCRAPERS.md）。

対象6区分: 関東大学対抗戦A/B・関東大学リーグ戦1部/2部・関西大学A/Bリーグ。

所属校の一覧は各連盟公式サイトの実ページで確認した（2026-07-18）:
  - 関東対抗戦A/B・リーグ戦1部/2部: 関東ラグビーフットボール協会 www.rugby.or.jp の
    直近シーズン星取表（/univ/sheet/{id}/）。各校の公式サイトURLは関東大学ラグビー
    フットボール連盟 www.kurfa.org/team/ のチーム一覧（1部/2部は同じ16校の入れ替え
    のみで対抗戦とは独立集計のため、対抗戦A/Bの8校×2はチーム一覧に無く個別検索で
    確認した）。
  - 関西A/B: 関西ラグビーフットボール協会 rugby-kansai.or.jp/gameuniversity の
    2026年度シーズン日程（A/Bとも8校）。各校公式サイトURLは個別に実在確認した。
連盟サイト自体は日程・星取表のみで部員名簿を持たないため、名簿は各校公式サイトから
取得する（02の想定通り「各連盟公式 + 大学部公式サイト」）。

各校公式サイトはHTML構造が統一されていない（自作/WordPress/Wix/r-cms.jp等バラバラ）。
_extract_records() は「かな氏名の行」を手がかりに前後数行を探索し、漢字氏名・学年・
ポジション・出身高校・身長体重（公式サイトが記載している場合のみ）を拾う汎用スキャナで
抽出する。かな氏名+漢字氏名の組が拾えても学年・ポジションのどちらも伴わない場合は
信頼度不足として捨てる（00原則3: 迷ったら null/スキップ）。

十分な件数（_MIN_CONFIDENT件）が正規表現で拾えたチームはそのまま採用し、拾えなかった
チームのみ pipeline.llm_fallback.extract_roster_members() にページ本文プレーンテキスト
を渡す（02:「抽出失敗時のみSonnetに粗抽出ブロックだけ渡す」の踏襲）。

実データで確認済みの既知の失敗パターン（2026-07-18）。偽データは作らず warning に残す:
  - Wix/React等クライアントサイド描画のサイト（立教大学、筑波大学の一部）は
    requests での静的取得では本文が空になる。
  - 中央大学 curfcsc.jp・拓殖大学 takushoku-rugby.com・白鷗大学 hakuoh-rugby.com・
    追手門学院大学 otemongakuinrfc.com は名前解決不可（サイト消滅/移転の可能性）。
  - 日本大学等、部員一覧がJSでの絞り込みUI経由でのみ描画されるサイトは静的取得では
    フィルタ用の見出し語しか取れない。
  - 国士舘大学は公式サイトが個人ブログ(ameblo.jp)のみで安定した名簿ページが無いため
    DIVISIONS に含めない（対象外）。

学年(grade)は取得できるが生年月日は取得しない・掲載しない（10: 学生は成人でも生年月日
禁止、学年のみ）。身長体重は各校サイトが名簿ページ自体に明記している場合のみ拾う
（10:「身長体重...大学以上は公式発表分のみ」）。SNS・写真は一切収集しない。
"""
from __future__ import annotations

import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from pipeline import llm_fallback
from pipeline.transform import normalize

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
_SLEEP = 1.5
_TIMEOUT = 15
_RETRIES = 2
_MIN_CONFIDENT = 5  # これ未満なら regex 結果を信頼せず LLM フォールバックに回す

# division key -> (label, 連盟公式ソース(所属校一覧の根拠), [(校名, 部員名簿URL), ...])
# 校名・URLは実ページで到達性を確認済み（2026-07-18、fetch_status確認）。
DIVISIONS: dict[str, dict] = {
    "kanto_taikosen_a": {
        "label": "関東大学対抗戦Aグループ",
        "source_url": "https://www.rugby.or.jp/univ/sheet/2651/",
        "teams": [
            ("早稲田大学", "https://www.wasedarugby.com/list/member/"),
            ("帝京大学", "https://www.teikyo-sports.jp/rugby/member/"),
            ("明治大学", "https://www.meijirugby.jp/players/"),
            ("慶應義塾大学", "https://keiorugby.com/team/team_cat/player/"),
            ("青山学院大学", "https://www.aogaku-rugby.com/member_list/"),
            ("筑波大学", "https://tsa.tsukuba.ac.jp/rugby/member/"),
            ("立教大学", "https://www.rikkyo-rugby.com/member"),
            ("日本体育大学", "https://nssurfc.jp/member/"),
        ],
    },
    "kanto_taikosen_b": {
        "label": "関東大学対抗戦Bグループ",
        "source_url": "https://www.rugby.or.jp/univ/sheet/2667/",
        "teams": [
            ("成蹊大学", "https://www.seikeiruggerclub.com/member_list/"),
            ("明治学院大学", "http://www.mgurfc.com/member_list/"),
            ("武蔵大学", "https://musashi-rugby.net/member/"),
            ("東京大学", "https://www.turfc.com/member_list/"),
            ("上智大学", "https://sophia-rugby.com/player"),
            ("成城大学", "https://www.seijorugby.com/"),
            ("一橋大学", "https://hurfc.jp/member/"),
            ("学習院大学", "https://www.gakushuin-rugby.com/member/"),
        ],
    },
    "kanto_league_1": {
        "label": "関東大学リーグ戦1部",
        "source_url": "https://www.rugby.or.jp/univ/sheet/2652/",
        "teams": [
            ("大東文化大学", "https://www.daito-rfc.com/"),
            ("東洋大学", "https://toyorugby.com/category/member/"),
            ("東海大学", "http://seagales.com/member/"),
            ("流通経済大学", "http://rku-rugby.jp/"),
            ("法政大学", "https://hosei-rugby.org/"),
            ("立正大学", "http://www.ris.ac.jp/sports/rugby/index.html"),
            ("日本大学", "http://www.nurfc.net/member/"),
            ("関東学院大学", "http://www.kgu-rugby.net/"),
        ],
    },
    "kanto_league_2": {
        "label": "関東大学リーグ戦2部",
        "source_url": "https://www.rugby.or.jp/univ/sheet/2668/",
        "teams": [
            ("中央大学", "http://www.curfcsc.jp/"),
            ("専修大学", "http://www.senshurugby.com/"),
            ("山梨学院大学", "http://www.ygu.ac.jp/sports/rugby/"),
            ("拓殖大学", "http://www.takushoku-rugby.com/"),
            ("白鷗大学", "http://hakuoh-rugby.com/"),
            ("國學院大學", "http://kokugakuinrugby.com/archives/members/4th"),
            ("朝鮮大学校", "http://krurfc.d2.r-cms.jp/member_list/"),
            # 国士舘大学: 公式サイトが個人ブログ(ameblo.jp)のみのため対象外（本文冒頭参照）
        ],
    },
    "kansai_a": {
        "label": "関西大学Aリーグ",
        "source_url": "https://rugby-kansai.or.jp/gameuniversity",
        "teams": [
            ("立命館大学", "https://www.ritsumeirugby.com/member/"),
            ("京都産業大学", "https://www.cc.kyoto-su.ac.jp/circle/rugby/pg22.html"),
            ("摂南大学", "https://setsunan-rugby.com/"),
            ("天理大学", "https://rugby.tenri-u.net/player4/"),
            ("関西大学", "https://kandairugby.com/member.php"),
            ("同志社大学", "https://www.doshisha-rugby.com/member"),
            ("近畿大学", "https://kindai-rugby.jp/members"),
            ("関西学院大学", "https://www.kgrfc.net/member_list/"),
        ],
    },
    "kansai_b": {
        "label": "関西大学Bリーグ",
        "source_url": "https://rugby-kansai.or.jp/gameuniversity",
        "teams": [
            ("大阪体育大学", "https://www.ouhs.jp/ouhs-athletics/rugby/"),
            ("京都大学", "https://www.kiurfc.com/player"),
            ("甲南大学", "https://konan-rugby.com/member.html"),
            ("大阪経済大学", "http://ouerugby.o-oku.jp/"),
            ("龍谷大学", "https://ryukoku-univ-rugby.com/memberprofile/"),
            ("大阪国際大学", "https://oiu-rugby.com/members"),
            ("追手門学院大学", "https://www.otemongakuinrfc.com/"),
            ("大阪産業大学", "https://osu-rugby.jp/"),
        ],
    },
}

# --- 抽出用パターン ---------------------------------------------------------
_POS_TOKENS = r"PR|HO|LO|FL|N[O0]\.?8|SH|SO|CTB|WTB|FB"
_POS_RE = re.compile(rf"^({_POS_TOKENS})([\s/／]+({_POS_TOKENS}))*$", re.I)
# 末尾に $ を付けない: 「2年生 / 桐蔭学園高校」のように学年と出身校が1行に
# まとまっているサイト（慶應義塾大学等、実データ確認）があり、行全体一致だと
# 学年を一切拾えなくなるため先頭一致のみ要求する。
_GRADE_RE = re.compile(r"^([1-4１２３４])\s*(回生|年生|年)(?:[\s　]|$)")
_KANA_RE = re.compile(r"^[ぁ-んァ-ヶー　\s]{3,20}$")
_KANJI_NAME_RE = re.compile(r"^[一-龥々ヶ]{1,4}[　 ][一-龥々ぁ-んァ-ヶー]{1,8}$")
_SCHOOL_RE = re.compile(r"(高等学校|高校|高等部|高等科)$")
_HEIGHT_RE = re.compile(r"(\d{3})\s*cm")
_WEIGHT_RE = re.compile(r"(\d{2,3})\s*kg")
# 名前らしく見えても実際は見出し・ラベルであるノイズ（実データ確認で誤検出したもの）
_NAME_STOPWORDS = {"部員 紹介", "部員 一覧", "選手 一覧", "メンバー 紹介", "学年 別", "採用 担当"}
# スタッフ肩書・ポジション名（カタカナ表記）は全てカタカナの行で氏名の読みと
# 区別がつきにくく、表組みのヘッダ行を氏名として誤検出することがある
# （実データ確認: 天理大学の選手一覧テーブルでポジション名カタカナ「プロップ」等が
# かな氏名候補に誤ってヒットし、表ヘッダ「学年」「体重」を漢字氏名として拾ってしまう
# 誤検出を確認した）。かな氏名候補から明示的に除外する。
_KANA_STOPWORDS = {
    "スタッフ", "コーチ", "ヘッドコーチ", "アシスタントコーチ", "チームディレクター",
    "ドクター", "トレーナー", "マネージャー", "アナリスト", "キャプテン",
    "アスレチックトレーナー", "パフォーマンスインテグレーター", "エスアンドシーコーチ",
    "プロップ", "フッカー", "ロック", "フランカー", "ナンバーエイト", "スクラムハーフ",
    "スタンドオフ", "センター", "ウイング", "フルバック", "フォワード", "バックス",
}

_GRADE_INT = {"1": 1, "2": 2, "3": 3, "4": 4, "１": 1, "２": 2, "３": 3, "４": 4}
_WINDOW = 5  # 漢字氏名探索の最大幅（かな氏名行からの距離）
_FIELD_WINDOW = 3  # 学年/ポジション/出身校/身長体重/スタッフ判定の探索幅（隣接レコードとの混線防止のためkanjiより狭める）


def _get_html(url: str) -> Optional[str]:
    """GET→HTML文字列（timeout=15、指数バックオフ最大2回、失敗はNone）。"""
    delay = 1.0
    for attempt in range(_RETRIES + 1):
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or resp.encoding
            return resp.text
        except Exception:
            if attempt >= _RETRIES:
                return None
            time.sleep(delay)
            delay *= 2
    return None


def _flatten(html: str) -> list[str]:
    """HTML -> 空行を除いたテキスト行のリスト（script/style除去）。"""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text("\n")
    return [l.strip() for l in text.split("\n") if l.strip()]


def _extract_records(lines: list[str]) -> list[dict]:
    """かな氏名行を手がかりに周辺から漢字氏名/学年/ポジション/出身校/身長体重を拾う。

    学年・ポジションのどちらも伴わない候補は信頼度不足として捨てる（誤検出対策）。
    """
    records: list[dict] = []
    for i, l in enumerate(lines):
        if not _KANA_RE.match(l):
            continue
        if len(l.replace("　", "").replace(" ", "")) < 3:
            continue
        if l.replace("　", "").replace(" ", "") in _KANA_STOPWORDS:
            continue
        lo, hi = max(0, i - _WINDOW), min(len(lines), i + _WINDOW + 1)
        # (行番号, 文字列) を中心 i からの距離が近い順に見る -> 隣接レコードの
        # 値を拾ってしまう混線を避け、このかな氏名に最も近い値を優先する。
        window = sorted(range(lo, hi), key=lambda j: abs(j - i))
        kanji = grade = pos = school = height = weight = None
        kanji_dist = None
        is_staff = False
        for j in window:
            w = lines[j]
            if j == i:
                continue
            dist = abs(j - i)
            # 漢字氏名(kanji)だけは _WINDOW いっぱいまで探す（サイトごとに氏名との
            # 相対位置が離れがちなため）。それ以外の項目は近傍(_FIELD_WINDOW)に
            # 無ければ「このレコードには無い」とみなし、隣接レコードの値を
            # 誤って借用しない（実データ確認: 学年+出身校が1行にまとまるサイトで
            # 出身校未記載の選手が隣の選手の出身校を誤って拾うケースがあった）。
            if kanji is None and _KANJI_NAME_RE.match(w) and w not in _NAME_STOPWORDS:
                kanji = w
                kanji_dist = dist
            if dist > _FIELD_WINDOW:
                continue
            if w in ("スタッフ", "STAFF", "監督・コーチ", "COACH"):
                is_staff = True
            if grade is None:
                gm = _GRADE_RE.match(w)
                if gm:
                    grade = gm.group(1)
            if pos is None and _POS_RE.match(w.upper()):
                pos = w.upper()
            if school is None and _SCHOOL_RE.search(w):
                # 「2年生 / 桐蔭学園高校」のように学年+出身校が1行にまとまっている
                # 場合は "/" 以降の校名部分だけを取り出す。
                school = re.split(r"[/／]", w)[-1].strip().replace("\xa0", "")
            if height is None:
                hm = _HEIGHT_RE.search(w)
                if hm:
                    height = hm.group(1)
            if weight is None:
                wm = _WEIGHT_RE.search(w)
                if wm:
                    weight = wm.group(1)
        if is_staff:
            continue  # 監督・コーチ・スタッフは選手名簿ではないため除外
        if kanji and (grade or pos):
            records.append({
                "kana": re.sub(r"\s+", "", l),
                "kanji": kanji,
                "grade": _GRADE_INT.get(grade) if grade else None,
                "position": pos,
                "school_raw": school,
                "height_cm": height,
                "weight_kg": weight,
                "_kanji_dist": kanji_dist,
            })
    # 同一漢字氏名の重複除去。ローマ字表記の外国人選手が隣接すると、その選手の
    # かな氏名が「漢字表記が無い(ローマ字なので_KANJI_NAME_REに一致しない)」ため
    # window内の別の日本人選手の漢字氏名を誤って一番近いものとして拾ってしまう
    # ケースを実データで確認した（例: 慶應義塾大学 "Thomas Nicholas Pappas" の
    # かな「とーます にこらす ぱぱす」が隣の日本人選手「長山 晃久」の漢字と
    # 誤って組まれる）。同じ漢字氏名について複数候補がある場合は、かな氏名からの
    # 行距離が最も近い(=本来のペアである可能性が最も高い)ものだけを残す。
    best: dict[str, dict] = {}
    for r in records:
        cur = best.get(r["kanji"])
        if cur is None or r["_kanji_dist"] < cur["_kanji_dist"]:
            best[r["kanji"]] = r
    out = []
    for r in best.values():
        r.pop("_kanji_dist", None)
        out.append(r)
    return out


def _grade_from_llm_text(g: Optional[str]) -> Optional[int]:
    if not g:
        return None
    m = re.search(r"([1-4１２３４])", g)
    return _GRADE_INT.get(m.group(1)) if m else None


def _collect_team(team_name: str, url: str) -> dict:
    """1校分の名簿ページ取得 -> raw records（{kanji,kana,grade,position,school_raw,...}）。"""
    warnings: list[str] = []
    html = _get_html(url)
    time.sleep(_SLEEP)
    if html is None:
        warnings.append(f"university {team_name}: 名簿ページ取得失敗（接続不可/DNS不可/404）、スキップ")
        return {"records": [], "warnings": warnings, "used_llm": False}

    lines = _flatten(html)
    records = _extract_records(lines)
    used_llm = False
    if len(records) < _MIN_CONFIDENT:
        text = "\n".join(lines)
        llm_hits = llm_fallback.extract_roster_members(text, team_name)
        if llm_hits:
            used_llm = True
            records = [{
                "kana": h["kana"] or "",
                "kanji": h["name"],
                "grade": _grade_from_llm_text(h.get("grade")),
                "position": h.get("position"),
                "school_raw": None,
                "height_cm": None,
                "weight_kg": None,
            } for h in llm_hits]
        if not records:
            warnings.append(
                f"university {team_name}: 名簿抽出0件（regex/Sonnetいずれも不可。"
                f"JS描画サイト・フィルタUI経由の可能性）、スキップ")
    return {"records": records, "warnings": warnings, "used_llm": used_llm}


def _dedupe_players(players: list[dict], warnings: list[str]) -> list[dict]:
    """id重複を最終防御としてここでも弾く（サイト側の一時的な二重描画等、_extract_records
    のチーム内かな氏名/漢字氏名重複除去をすり抜けるケースへの安全策。00原則5）。"""
    seen: set[str] = set()
    out = []
    for p in players:
        if p["id"] in seen:
            warnings.append(f"university: id重複 {p['id']} を検出、2件目以降を除外")
            continue
        seen.add(p["id"])
        out.append(p)
    return out


def collect(division_key: str) -> dict:
    """1区分（対抗戦A等）分の全校名簿を収集する。"""
    warnings: list[str] = []
    players: list[dict] = []
    div = DIVISIONS[division_key]
    for team_name, url in div["teams"]:
        res = _collect_team(team_name, url)
        warnings.extend(res["warnings"])
        for rec in res["records"]:
            player, pw = normalize.player_university(
                rec, team_name=team_name, division=division_key, source_url=url)
            warnings.extend(pw)
            if player is not None:
                players.append(player)
    players = _dedupe_players(players, warnings)
    return {"players": players, "teams": [], "matches": [], "standings": [], "warnings": warnings}


def collect_all() -> dict:
    """6区分（大学スコープ全体）をまとめて収集する（run.py の league="university" 用）。"""
    warnings: list[str] = []
    players: list[dict] = []
    for division_key in DIVISIONS:
        res = collect(division_key)
        players.extend(res["players"])
        warnings.extend(res["warnings"])
    players = _dedupe_players(players, warnings)
    return {"players": players, "teams": [], "matches": [], "standings": [], "warnings": warnings}
