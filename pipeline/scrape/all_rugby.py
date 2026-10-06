"""all.rugby スクレイパー（02: Top14 / Super Rugby / 代表 / 順位表）。

このモジュールは P1-5 で Top14 を実装する。トーナメント表 →
各クラブの squad ページ → 選手の順に辿る。squad ページの一覧テーブルに
氏名・ポジション・身長・体重が載っており、選手個別ページを1件ずつ叩かずに
基本レコードを構築できる（14リクエストで完走、レート負荷が小さい）。

国籍・career_path・テストキャップは選手個別ページの bio/parcours にあるが、
500件超の個別取得は遅く不安定なため既定では取得しない。環境変数
`ALL_RUGBY_ENRICH=1` を立てると個別ページを辿って nationality/career を補完する。

公開関数:
    collect(tournament, *, with_caps=False) -> {"players","teams","matches","standings","warnings"}
      tournament は "top14" / "super-rugby-pacific" / "mlr" / "urc" / "premiership"。
      run.py の SCRAPERS から呼ぶ。with_caps=True の場合、選手個別ページを全員enrichし
      （ALL_RUGBY_ENRICH フラグに関わらず常に）、代表テストキャップも取得する
      （URC/Premiership のようにnational.json（日本代表＋直近対戦国のみ）でカバーされない
      国の代表キャップを補うため。2026-07-26: 旧 collect_star の部分収集(P4-6)は
      フルスコッド化に伴い廃止し、この with_caps フラグに統合）。
    collect_national() -> 同形式（P1-7）。日本代表＋pipeline.scrape.jrfu が返す
      直近対戦国のみのスコッドを対象とし、テストキャップ enrich は常時行う
      （対象人数が少ないため ALL_RUGBY_ENRICH フラグに依存しない）。
"""
from __future__ import annotations

import os
import re
import time
import unicodedata
from datetime import datetime, timezone, timedelta
from typing import Optional

import requests
from bs4 import BeautifulSoup

from pipeline import io
from pipeline.transform import normalize

JST = timezone(timedelta(hours=9))
BASE = "https://all.rugby"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
_SLEEP = 1.5
_TIMEOUT = 15
_RETRIES = 2

# トーナメント設定。key は all.rugby の URL キー（実ページで確認済み）。
# Super Rugby: 2026-07-18 に実ページで確認。/tournament/super-rugby/table は
# 過去シーズン（2020）に固定された古いページで現行データではない。
# /tournament/super-rugby-pacific/table が現行 2026 シーズン表（title に "2026" を確認、
# club 11件: blues/brumbies/chiefs/crusaders/fijian-drua/highlanders/hurricanes/
# moana-pasifika/reds/waratahs/western-force）なのでこちらを採用する。
TOURNAMENTS = {
    "top14": {"key": "top-14", "league": "top14"},
    "super-rugby-pacific": {"key": "super-rugby-pacific", "league": "super-rugby"},
    "mlr": {"key": "mlr", "league": "mlr"},
    # key は all.rugby の URL キー（2026-07-19 に実ページで確認:
    #   /tournament/urc/table → title "URC Table 2025 / 2026 (BKT United Rugby Championship)"、club 16件
    #     (benetton/bulls/cardiff/connacht/dragons/edinburgh/glasgow/leinster/lions/munster/
    #      ospreys/scarlets/sharks/stormers/ulster/zebre)
    #   /tournament/premiership/table → title "Premiership Table 2025 / 2026 (Gallagher Premiership)"、club 10件
    #     (bath/bristol/exeter/gloucester/harlequins/leicester/newcastle/northampton/sale/saracens)
    #   ※ united-rugby-championship / premiership-rugby / gallagher-premiership は 404）。
    "urc": {"key": "urc", "league": "urc"},
    "premiership": {"key": "premiership", "league": "premiership"},
}

# クラブ slug → 日本語表記（data/legacy/top14_teams.json 由来の事実、migrate_legacy と一致）。
# 昇降格で live 表に出た未知 slug は英語名でフォールバックする。
NAME_JA = {
    "toulouse": "トゥールーズ", "bordeaux": "ボルドー・ベグル", "paris": "スタッド・フランセ",
    "toulon": "トゥーロン", "la-rochelle": "ラ・ロシェル", "racing-92": "ラシン92",
    "lyon": "リヨン", "castres": "カストル", "pau": "ポー", "perpignan": "ペルピニャン",
    "bayonne": "バイヨンヌ", "clermont": "クレルモン", "montpellier": "モンペリエ",
    "vannes": "ヴァンヌ", "mont-de-marsan": "モンドマルサン", "provence": "プロヴァンス",
    "grenoble": "グルノーブル", "biarritz": "ビアリッツ", "brive": "ブリーヴ",
    "agen": "アジャン", "beziers": "ベジエ", "oyonnax": "オヨナ",
    "colomiers": "コロミエ", "aurillac": "オーリヤック", "nevers": "ヌヴェール",
    "dax": "ダクス", "carcassonne": "カルカソンヌ", "montauban": "モントーバン",
    "valence-romans": "ヴァランス・ロマン", "soyaux-angouleme": "スワイヨ・アングレーム",
}
# Super Rugby Pacific のクラブは、確認済みの和文表記の出典（data/legacy 含む）が
# 無いため意図的に未登録（原則3: 不明は null）。team_allrugby が英語名/slugへ
# フォールバックする。
#
# URC / Premiership のクラブ和文表記（P4-6）: 既存サイト表示データ data/teams.json
# （league="urc"/"premiership" の team_name）由来の事実。all.rugby slug との対応は
# 同ファイルの team_en_name / slug で機械的に突合した（AIによる新規翻訳はしない）。
NAME_JA |= {
    # URC（data/teams.json league="urc"）
    "benetton": "ベネットン・ラグビー・トレヴィーゾ", "bulls": "ヴォーダコム・ブルズ",
    "cardiff": "カーディフ・ラグビー", "connacht": "コナート・ラグビー",
    "dragons": "ドラゴンズ・ラグビー", "edinburgh": "エディンバラ・ラグビー",
    "glasgow": "グラスゴー・ウォリアーズ", "leinster": "レンスター・ラグビー",
    "lions": "10ベット・ライオンズ", "munster": "マンスター・ラグビー",
    "ospreys": "オスプリーズ", "scarlets": "スカーレッツ",
    "sharks": "ハリウッドベッツ・シャークス", "stormers": "DHLストーマーズ",
    "ulster": "アルスター・ラグビー", "zebre": "ゼブレ・パルマ",
    # Premiership（data/teams.json league="premiership"）
    "bath": "バース・ラグビー", "bristol": "ブリストル・ベアーズ",
    "exeter": "エクセター・チーフス", "gloucester": "グロスター・ラグビー",
    "harlequins": "ハーレクインズ", "leicester": "レスター・タイガーズ",
    "newcastle": "ニューカッスル・ファルコンズ", "northampton": "ノーサンプトン・セインツ",
    "sale": "セール・シャークス", "saracens": "サラセンズ",
}

# スモークテスト用の上限（本番未設定）。ALL_RUGBY_MAX_TEAMS / _MAX_PLAYERS。
_MAX_TEAMS = int(os.environ.get("ALL_RUGBY_MAX_TEAMS", "0")) or None
_MAX_PLAYERS = int(os.environ.get("ALL_RUGBY_MAX_PLAYERS", "0")) or None
_ENRICH = os.environ.get("ALL_RUGBY_ENRICH", "") not in ("", "0", "false")


def _get(url: str) -> Optional[str]:
    """GET（timeout=15、指数バックオフ最大2回、失敗は None）。"""
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


def _club_slug(href: str) -> Optional[str]:
    m = re.search(r"/club/([\w\-]+)", href)
    return m.group(1) if m else None


def _player_slug(href: str) -> Optional[str]:
    m = re.search(r"/player/([\w\-]+)/?$", href)
    return m.group(1) if m else None


def parse_tournament_table(html: str):
    """トーナメント表ページ → ([club_slug...], standing_rows_raw)。

    順位表は最初の table。列見出しの 'PTS' 以降を各データ行の氏名列より後の
    セルへ対応づける（シーズン序盤は空欄→行は落ちる）。
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    slugs: list[str] = []
    rows_raw: list[dict] = []
    if table is None:
        return slugs, rows_raw

    trs = table.find_all("tr")
    if not trs:
        return slugs, rows_raw
    header = [c.get_text(strip=True) for c in trs[0].find_all(["td", "th"])]
    try:
        pts_i = header.index("PTS")
    except ValueError:
        pts_i = None
    header_stats = header[pts_i:] if pts_i is not None else []

    seen = set()
    for tr in trs[1:]:
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue
        texts = [c.get_text(strip=True) for c in cells]
        name_idx = None
        slug = None
        for i, c in enumerate(cells):
            a = c.find("a", href=True)
            if a and _club_slug(a["href"]):
                name_idx = i
                slug = _club_slug(a["href"])
                break
        if slug is None or slug in seen:
            continue
        seen.add(slug)
        slugs.append(slug)
        if not header_stats:
            continue
        stats = dict(zip(header_stats, texts[name_idx + 1:]))
        rows_raw.append({
            "team_id": slug,
            "rank": texts[0],
            "points": stats.get("PTS"),
            "played": stats.get("PL"),
            "won": stats.get("W"),
            "drawn": stats.get("D"),
            "lost": stats.get("L"),
        })
    return slugs, rows_raw


def parse_squad(html: str) -> list[dict]:
    """squad ページ → 選手生 dict リスト。

    氏名・ポジション・身長・体重の列を持つ一覧テーブル（見出しに 'Height' を含む）
    のみ対象。'Contracts ended' テーブル（見出しに 'Reason'）は除外。
    """
    soup = BeautifulSoup(html, "html.parser")
    out: list[dict] = []
    seen: set[str] = set()
    for table in soup.find_all("table"):
        trs = table.find_all("tr")
        if not trs:
            continue
        header = [c.get_text(strip=True) for c in trs[0].find_all(["td", "th"])]
        col = {label: i for i, label in enumerate(header)}
        if "Height" not in col:
            continue  # 移籍/契約終了テーブルなど、選手一覧でないものは除外
        for tr in trs[1:]:
            cells = tr.find_all(["td", "th"])
            a = tr.find("a", href=True)
            slug = _player_slug(a["href"]) if a else None
            if slug is None or slug in seen:
                continue
            seen.add(slug)
            texts = [c.get_text(" ", strip=True) for c in cells]

            def _cell(label: str) -> Optional[str]:
                i = col.get(label)
                return texts[i] if i is not None and i < len(texts) else None

            name = _cell("Name")
            if not name:
                continue
            out.append({
                "slug": slug,
                "name_en": name,
                "position": _cell("Position"),
                "height_raw": _cell("Height"),
                "weight_raw": _cell("Weight"),
            })
    return out


def parse_player_bio(html: str, *, now_year: Optional[int] = None) -> dict:
    """選手個別ページ → {'nationality': [...], 'career': [...]}（enrich 用の純パース）。

    now_year: テスト用に「取得時点の年」を固定する。省略時は実行時の年（JST）。
    """
    soup = BeautifulSoup(html, "html.parser")
    nats: list[str] = []
    bio = soup.find("div", class_="bio")
    if bio:
        for div in bio.find_all("div"):
            span = div.find("span", class_="gras")
            if not span:
                continue
            label = span.get_text(strip=True)
            img = div.find("img")
            if img and img.get("alt") and ("Nationality #" in label or "Sporting nationality" in label):
                country = img["alt"].replace("Drapeau ", "").strip()
                if country and country not in nats:
                    nats.append(country)
    career: list[dict] = []
    parcours = soup.find("div", class_="parcours")
    if parcours:
        for li in parcours.find_all("li"):
            t = li.get_text(" ", strip=True)
            m = re.match(r"(.+?)\s*\((\d{4})\s*[-–]\s*(\d{4})\)", t)
            if m:
                career.append({"team": m.group(1).strip(),
                               "from": m.group(2), "to": m.group(3)})
            elif t:
                career.append({"team": t})
    current_year = now_year if now_year is not None else datetime.now(JST).year
    if career and career[-1].get("to") == str(current_year):
        # all.rugby は在籍中チームにも "present" マーカーを出さず、単に取得時点の
        # 年をtoに表示する（サイト側の仕様）。career は時系列順のため、末尾要素の
        # to が取得年と一致する場合は在籍中とみなしnull化する（=現在も所属中）。
        career[-1] = {**career[-1], "to": None}
    return {"nationality": nats, "career": career}


def _enrich(raw: dict, *, with_caps: bool = False) -> None:
    """選手個別ページから nationality/career を補完（ALL_RUGBY_ENRICH または with_caps 時）。

    with_caps=True の場合は代表テストキャップも取得する（national.json（日本代表＋
    直近対戦国のみ）でカバーされないリーグ向け。旧 _enrich_star を統合）。
    """
    html = _get(f"{BASE}/player/{raw['slug']}")
    time.sleep(_SLEEP)
    if html is None:
        return
    bio = parse_player_bio(html)
    if bio["nationality"]:
        raw["nationality"] = bio["nationality"]
    if bio["career"]:
        raw["career"] = bio["career"]
    if with_caps:
        country = parse_sporting_nationality(html)
        if country:
            caps_count = parse_player_caps(html, country)
            if caps_count is not None and caps_count > 0:
                raw["caps"] = {
                    "team": country,
                    "count": caps_count,
                    "source_url": f"{BASE}/player/{raw['slug']}",
                }


def parse_player_caps(html: str, country_display: str) -> Optional[int]:
    """選手個別ページの通算成績表（class="JOverall"）末尾の「TEAM」集計セクションから、
    対象代表チームの通算試合数（テストキャップ相当）を抽出する（P1-7 enrich 用）。

    このセクションは所属クラブ・代表チームごとの全期間合計試合数の一覧で、
    国名の行に一致すればその Matches 列を採用する。見つからない場合は None
    （原則3: 不明は null）。
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="JOverall")
    if table is None:
        return None
    trs = table.find_all("tr")
    start = None
    for i, tr in enumerate(trs):
        cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
        if len(cells) >= 2 and cells[1] == "TEAM":
            start = i + 1
            break
    if start is None:
        return None
    target = country_display.strip().lower()
    for tr in trs[start:]:
        cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
        if len(cells) < 3:
            break  # 空行でセクション終端
        if cells[1].strip().lower() == target:
            try:
                return int(cells[2])
            except ValueError:
                return None
    return None


def parse_sporting_nationality(html: str) -> Optional[str]:
    """選手個別ページの bio から Sporting nationality（代表資格国）の国名を返す。

    bio の 'Sporting nationality' 行の国旗 img alt（'Drapeau {国名}'）を使う。
    無ければ None（原則3: 不明は null）。
    """
    soup = BeautifulSoup(html, "html.parser")
    bio = soup.find("div", class_="bio")
    if not bio:
        return None
    for div in bio.find_all("div"):
        span = div.find("span", class_="gras")
        if not span or span.get_text(strip=True) != "Sporting nationality":
            continue
        img = div.find("img")
        if img and img.get("alt"):
            country = img["alt"].replace("Drapeau ", "").strip()
            if country:
                return country
    return None



def _enrich_national(raw: dict, country_display: str) -> None:
    """national squad 用 enrich: nationality/career/代表通算試合数を1回のfetchで補完。

    club squad の collect() と異なり ALL_RUGBY_ENRICH フラグに関わらず常に行う
    （対象人数が国単位で高々数十人と少なく、02が明示するテストキャップ取得に必要）。
    """
    html = _get(f"{BASE}/player/{raw['slug']}")
    time.sleep(_SLEEP)
    if html is None:
        return
    bio = parse_player_bio(html)
    if bio["nationality"]:
        raw["nationality"] = bio["nationality"]
    if bio["career"]:
        raw["career"] = bio["career"]
    caps_count = parse_player_caps(html, country_display)
    if caps_count is not None:
        raw["caps"] = {
            "team": country_display,
            "count": caps_count,
            "source_url": f"{BASE}/player/{raw['slug']}",
        }


def parse_club_name(html: str) -> Optional[str]:
    """squad ページの <title>「Blues rugby team players for 2025/2026 - All.Rugby」→ 'Blues'。"""
    m = re.search(r"<title>\s*(.*?)\s+rugby team players", html or "", re.I | re.S)
    return m.group(1).strip() if m else None


_CLUB_GENERIC = {"rugby", "rfc", "rufc", "fc", "club", "the", "union", "football", "team",
                 "de", "du", "la", "le", "pro"}


def _club_tokens(name: str) -> set[str]:
    s = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode().lower()
    return {t for t in re.findall(r"[a-z0-9]+", s) if t not in _CLUB_GENERIC}


def club_name_matches(a: Optional[str], b: Optional[str]) -> bool:
    """'Bath' と 'Bath Rugby'、'Northampton (Saints)' と 'Northampton Saints' 等を同一視。
    汎用語を除いたトークン集合の一方が他方を含むとき一致とする。"""
    A, B = _club_tokens(a or ""), _club_tokens(b or "")
    return bool(A) and bool(B) and (A <= B or B <= A)


def current_club(career: list[dict], *, now_year: Optional[int] = None) -> Optional[str]:
    """career 末尾が在籍中（to=null または to>=取得年）ならそのチーム名、でなければ None。"""
    if not career:
        return None
    last = career[-1]
    year = now_year if now_year is not None else datetime.now(JST).year
    to = last.get("to")
    if to is None or (str(to).isdigit() and int(to) >= year):
        return last.get("team")
    return None


def active_clubs(career: list[dict], *, now_year: Optional[int] = None) -> list[str]:
    """在籍中（to=null または to>=取得年）の全チーム名。SR選手のNPC州代表・ローン先等で
    在籍中が複数あるケースに対応（末尾だけ見ると親クラブを取りこぼす）。"""
    year = now_year if now_year is not None else datetime.now(JST).year
    out = []
    for c in career or []:
        to = c.get("to")
        if c.get("team") and (to is None or (str(to).isdigit() and int(to) >= year)):
            out.append(c["team"])
    return out


def pick_club(pages: list[str], club_names: dict[str, list[str]], career: list[dict]) -> Optional[str]:
    """掲載ページ群から選手の所属クラブを1つ選ぶ。在籍中チームと名前が一致するページが
    1つならそれ。無ければ career 末尾（最新）のチームと一致するページが1つならそれ。"""
    def hits(team_names: list[str]) -> list[str]:
        return [p for p in pages
                if any(club_name_matches(n, t) for n in club_names.get(p, [p]) for t in team_names)]
    h = hits(active_clubs(career))
    if len(h) == 1:
        return h[0]
    if len(h) > 1:
        # 移籍期（旧クラブ to=今年・新クラブ from=今年）で両方在籍中扱いになる場合は
        # from が最も新しい在籍中チームに一意に一致するページを採る
        act = [c for c in career if c.get("team") in active_clubs(career)]
        latest = max((str(c.get("from") or "") for c in act), default="")
        newest = [c["team"] for c in act if str(c.get("from") or "") == latest]
        h2 = hits(newest)
        return h2[0] if len(h2) == 1 else None
    if not h and career:
        # 在籍中に一致なし（ローン先・下部クラブのみ在籍中等）→ 過去を含む在籍歴で最新の一致
        year = datetime.now(JST).year
        for c in reversed(career):
            to = str(c.get("to") or "")
            if to.isdigit() and int(to) < year - 1:
                continue  # 2年以上前に離れたクラブは根拠にしない
            h = hits([c.get("team")])
            if len(h) == 1:
                return h[0]
            if h:
                return None
    return None


def resolve_duplicate_members(squads: dict[str, list[dict]], club_names: dict[str, Optional[str]],
                              career_of) -> tuple[dict[str, str], list[str]]:
    """複数クラブの squad ページに載る選手（all.rugby 側で他クラブの選手が混入する
    事象、2026-10-05 確認: Super Rugby 全11クラブのページに共通の約20名が載り、
    blues ページには Brumbies の選手も載っていた）の所属を、選手個別ページの
    現所属（career 末尾）とクラブ名の一致で決める。

    返り値: ({slug: 採用クラブslug}, warnings)。一意に決まらない選手は返り値に
    含めない（呼び出し側でどのクラブにも割り当てない＝原則3の保守的判断）。
    career_of(slug) -> list[dict] は選手個別ページの career を返す関数。
    """
    clubs_of: dict[str, list[str]] = {}
    for club, rows in squads.items():
        for r in rows:
            clubs_of.setdefault(r["slug"], [])
            if club not in clubs_of[r["slug"]]:
                clubs_of[r["slug"]].append(club)
    resolved: dict[str, str] = {}
    warnings: list[str] = []
    for slug, clubs in clubs_of.items():
        if len(clubs) < 2:
            continue
        career = career_of(slug) or []
        names = {c: [club_names[c]] for c in clubs if club_names.get(c)}
        hit = pick_club(clubs, names, career)
        if hit:
            resolved[slug] = hit
        else:
            warnings.append(f"all.rugby: {slug} が複数クラブ {clubs} の squad に掲載、"
                            f"在籍中 {active_clubs(career)} と一致せず除外")
    return resolved, warnings


def _career_from_page(slug: str) -> list[dict]:
    html = _get(f"{BASE}/player/{slug}")
    time.sleep(_SLEEP)
    return parse_player_bio(html)["career"] if html else []


def fetch_squads(club_slugs: list[str], warnings: list[str], league: str):
    """club_slugs の squad を取得し、重複掲載を解決して {club: [raw...]} を返す。"""
    squads: dict[str, list[dict]] = {}
    names: dict[str, Optional[str]] = {}
    for slug in club_slugs:
        shtml = _get(f"{BASE}/club/{slug}/squad")
        time.sleep(_SLEEP)
        if shtml is None:
            warnings.append(f"{league}: club/{slug}/squad 取得失敗、スキップ")
            continue
        squads[slug] = parse_squad(shtml)
        names[slug] = parse_club_name(shtml)
    resolved, rw = resolve_duplicate_members(squads, names, _career_from_page)
    warnings.extend(rw)
    counts: dict[str, int] = {}
    for rows in squads.values():
        for r in rows:
            counts[r["slug"]] = counts.get(r["slug"], 0) + 1
    out = {}
    corrections = io.read_manual(ROSTER_CORRECTIONS, default={}).get("players", {})
    for club, rows in squads.items():
        out[club] = [r for r in rows
                     if (counts[r["slug"]] == 1 or resolved.get(r["slug"]) == club)
                     and allowed_by_corrections(r["slug"], club, corrections)]
    return out


# pipeline/roster_repair.py が全リーグ横断の検査（選手個別ページの在籍歴で突合）で確定した
# 是正結果。日次収集が混入したページをそのまま取り込んで是正を巻き戻さないよう、ここで適用する。
ROSTER_CORRECTIONS = "roster_corrections.json"


def allowed_by_corrections(slug: str, club: str, corrections: dict) -> bool:
    """corrections[slug] = {"club": 所属クラブ or None, ...}。None は対象リーグ外（どのページでも採らない）。"""
    c = corrections.get(slug)
    if c is None:
        return True
    return c.get("club") == club


def collect(tournament: str, *, with_caps: bool = False, light: bool = False) -> dict:
    """tournament = 'top14' 等。players/teams/standings（transform 済み）を返す。

    with_caps=True の場合、ALL_RUGBY_ENRICH フラグに関わらず個別ページenrichを行い
    代表テストキャップも取得する（URC/Premiership 用。旧 collect_star を統合）。

    light=True（軽量モード、matches/standings のみ書き込む --only 用）の場合、
    このリーグは matches を持たず standings のみ提供するため、トーナメント表
    ページ（1リクエスト）の情報だけで standings を組み、club毎のsquad/選手個別
    ページ取得（本来数十〜数百リクエスト、with_caps時はさらに増える）を省略する。
    """
    cfg = TOURNAMENTS[tournament]
    league = cfg["league"]
    warnings: list[str] = []

    html = _get(f"{BASE}/tournament/{cfg['key']}/table")
    time.sleep(_SLEEP)
    if html is None:
        warnings.append(f"{league}: トーナメント表取得失敗")
        return {"players": [], "teams": [], "matches": [], "standings": [], "warnings": warnings}

    club_slugs, standing_rows_raw = parse_tournament_table(html)
    sm = re.search(r"(20\d{2})\s*/\s*(20\d{2})", html)
    season = f"{sm.group(1)}-{sm.group(2)[2:]}" if sm else "unknown"
    if _MAX_TEAMS:
        club_slugs = club_slugs[:_MAX_TEAMS]

    if light:
        valid = set(club_slugs)
        rows = [r for r in standing_rows_raw if r["team_id"] in valid]
        standing, sw = normalize.standing_allrugby(
            rows, league=league, season=season,
            source_url=f"{BASE}/tournament/{cfg['key']}/table",
        )
        warnings.extend(sw)
        standings_out = [standing] if standing is not None else []
        return {"players": [], "teams": [], "matches": [], "standings": standings_out, "warnings": warnings}

    teams_out: list[dict] = []
    players_out: list[dict] = []
    seen_players: set[str] = set()  # 念のための二重割当防止（重複掲載は fetch_squads で解決済み）

    # 複数クラブに載る選手は「最初のクラブに割当」だと他クラブ選手の混入を招く
    # （blues に Brumbies 選手が入った事例）ため、現所属で解決してから組み立てる。
    squads = fetch_squads(club_slugs, warnings, league)
    for slug in club_slugs:
        if slug not in squads:
            continue
        squad = squads[slug]
        if _MAX_PLAYERS:
            squad = squad[:_MAX_PLAYERS]

        roster_ids: list[str] = []
        for raw in squad:
            if raw["slug"] in seen_players:
                continue
            seen_players.add(raw["slug"])
            if _ENRICH or with_caps:
                _enrich(raw, with_caps=with_caps)
            player, pw = normalize.player_allrugby(raw, league=league, team_id=slug)
            warnings.extend(pw)
            if player is None:
                continue
            players_out.append(player)
            roster_ids.append(player["id"])

        team, tw = normalize.team_allrugby(
            {"slug": slug, "name_ja": NAME_JA.get(slug), "roster_ids": roster_ids},
            league=league,
        )
        warnings.extend(tw)
        if team is not None:
            teams_out.append(team)

    standings_out: list[dict] = []
    valid = {t["id"] for t in teams_out}
    rows = [r for r in standing_rows_raw if r["team_id"] in valid]
    standing, sw = normalize.standing_allrugby(
        rows, league=league, season=season,
        source_url=f"{BASE}/tournament/{cfg['key']}/table",
    )
    warnings.extend(sw)
    if standing is not None:
        standings_out.append(standing)

    return {
        "players": players_out,
        "teams": teams_out,
        "matches": [],
        "standings": standings_out,
        "warnings": warnings,
    }


RWC2027_SLUGS = [
    # 自動出場（RWC2023 各プール上位3）
    "new-zealand", "france", "italy", "south-africa", "ireland", "scotland",
    "wales", "australia", "fiji", "england", "argentina", "japan",
    # 予選勝ち上がり
    "georgia", "spain", "portugal", "romania", "hong-kong", "zimbabwe",
    "uruguay", "chile", "usa", "canada", "tonga", "samoa",
]


def collect_national() -> dict:
    """代表（national.json、02: 日本代表＋直近1年で日本と対戦する国のみ）を収集する。

    対戦国は pipeline.scrape.jrfu.collect_matches() が JRFU公式日程から導出する
    opponent_slugs を使う（全世界の代表を取らない）。squad一覧は club team と同じ
    /club/{slug}/squad を使うが、team_id には Team レコードを作らず（"national" は
    schemas.TEAM_LEAGUES に含まれないためチーム所属必須ではない）国のslugをそのまま
    設定し、players 側での国別グルーピングと Match の home/away_team_id 参照に使う。
    """
    from pipeline.scrape import jrfu  # 循環import回避のためlocal import
    from pipeline.schemas import japan_name_keys as _name_keys

    warnings: list[str] = []
    sched = jrfu.collect_matches()
    matches = sched.get("matches", [])
    warnings.extend(sched.get("warnings", []))

    # 日本代表の生年月日は all.rugby の代表選手個別ページに載っておらず常にnullに
    # なっていた（2026-07-22 確認）ため、JRFU公式（jrfu.collect_national_birthdates）
    # の氏名突合マップで補う。他国はall.rugbyの値（無ければnull）のまま。
    jrfu_birthdates: dict[str, dict] = {}
    bd_res = jrfu.collect_national_birthdates()
    jrfu_birthdates = bd_res.get("map", {})
    # /japan/member/ 掲載の代表候補（all.rugbyの /club/japan/squad ＝キャップ保持者に
    # 載らない国内選手を含む）。all.rugby由来のJapan選手と氏名突合できなかった者のみ
    # 後段で national.json に追加する（squad="national"）。
    jrfu_squad_players: list[dict] = bd_res.get("players", [])
    warnings.extend(bd_res.get("warnings", []))

    # gap B: 招集・合宿メンバー発表ニュース。最新イベントのメンバーを facts として
    # national.json に取り込む（/japan/member/ に載らない追加招集・合宿参加の代表候補を
    # 救う）。イベント自体（差分検知→記事化）は run.py 側の pipeline.callups が扱うため、
    # ここでは events をそのまま結果に返す（二重スクレイプ回避）。
    def _nid(ev: dict) -> int:
        nid = ev.get("news_id")
        return int(nid) if (nid or "").isdigit() else 0

    callup_res = jrfu.collect_call_ups()
    call_up_events: list[dict] = callup_res.get("events", [])
    warnings.extend(callup_res.get("warnings", []))
    callup_players: list[dict] = []
    if call_up_events:
        latest_event = max(call_up_events, key=_nid)
        callup_players, cw = jrfu.callup_members_to_players(latest_event)
        warnings.extend(cw)

    # JRFU公式の現行スコッドページ（/japan/member/）は選考中の一部選手しか載せて
    # いないため、そこに無い日本代表選手は league_one.py が既に取得済みの
    # 国内リーグ名鑑（生年月日を個別ページから正規取得済み）で氏名突合して補う
    # （2026-07-22 確認: league-one-d1.json 等に多くが既に存在）。国内リーグに
    # 未所属の選手（海外在籍等）はここでも見つからず null のまま。
    domestic_birthdates: dict[str, str] = {}
    for league in ("league-one-d1", "league-one-d2", "league-one-d3", "university", "highschool"):
        for p in io.read_records(io.players_path(league)):
            bd = p.get("birthdate")
            name_en = p.get("name_en")
            if not bd or not name_en:
                continue
            for key in _name_keys(name_en):
                domestic_birthdates.setdefault(key, bd)

    slugs: list[str] = ["japan"]
    for s in sched.get("opponent_slugs", []):
        if s not in slugs:
            slugs.append(s)
    # RWC2027 出場24カ国は常時収集する（サイトが RWC2027 全チームを扱うため）。
    # all.rugby の国 slug。取得失敗した slug は下のループで warn+skip される。
    for s in RWC2027_SLUGS:
        if s not in slugs:
            slugs.append(s)
    if _MAX_TEAMS:
        slugs = slugs[:_MAX_TEAMS]

    players_out: list[dict] = []
    seen_players: set[str] = set()
    japan_name_keys: set[str] = set()  # all.rugby由来のJapan選手の氏名突合キー

    for slug in slugs:
        shtml = _get(f"{BASE}/club/{slug}/squad")
        time.sleep(_SLEEP)
        if shtml is None:
            warnings.append(f"national: club/{slug}/squad 取得失敗、スキップ")
            continue
        squad = parse_squad(shtml)
        if _MAX_PLAYERS:
            squad = squad[:_MAX_PLAYERS]
        country_display = slug.replace("-", " ").title()

        for raw in squad:
            if raw["slug"] in seen_players:
                continue
            seen_players.add(raw["slug"])
            _enrich_national(raw, country_display)
            if slug == "japan" and raw.get("name_en"):
                keys = _name_keys(raw["name_en"])
                hit = next((jrfu_birthdates[k] for k in keys if k in jrfu_birthdates), None)
                domestic_hit = next((domestic_birthdates[k] for k in keys if k in domestic_birthdates), None)
                if hit:
                    raw["birthdate"] = hit["birthdate"]
                elif domestic_hit:
                    raw["birthdate"] = domestic_hit
                else:
                    warnings.append(
                        f"national japan: {raw['name_en']!r} をJRFU公式スコッドと"
                        f"氏名突合できず、生年月日は取得できなかった")
            player, pw = normalize.player_allrugby(raw, league="national", team_id=slug)
            warnings.extend(pw)
            if player is None:
                continue
            if slug == "japan" and player.get("name_en"):
                japan_name_keys.update(_name_keys(player["name_en"]))
            players_out.append(player)

    # JRFU公式スコッド（/japan/member/）のうち、all.rugbyのJapan選手と氏名突合できなかった
    # 代表候補（＝国際キャップ無しでall.rugbyに載らない国内選手）を national.json に追加。
    for sp in jrfu_squad_players:
        name_en = sp.get("name_en")
        if not name_en:
            continue
        if any(k in japan_name_keys for k in _name_keys(name_en)):
            continue  # all.rugby側に既にいる（キャップ保持者）→そちらを優先
        japan_name_keys.update(_name_keys(name_en))  # JRFUスコッド内の重複も防ぐ
        sp["team_id"] = "japan"
        players_out.append(sp)

    # 招集・合宿メンバー（gap B）も同様に、既出でない代表候補のみ追加する。
    # /japan/member/ にも all.rugby にも載らない純粋な追加招集選手を national.json に載せる。
    for cp in callup_players:
        name_en = cp.get("name_en")
        if not name_en:
            continue
        if any(k in japan_name_keys for k in _name_keys(name_en)):
            continue
        japan_name_keys.update(_name_keys(name_en))
        cp["team_id"] = "japan"
        players_out.append(cp)

    return {
        "players": players_out,
        "call_ups": call_up_events,
        "teams": [],
        "matches": matches,
        "standings": [],
        "warnings": warnings,
    }
