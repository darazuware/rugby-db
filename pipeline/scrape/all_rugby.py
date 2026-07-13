"""all.rugby スクレイパー（02: Top14 / Super Rugby / 代表 / 順位表）。

このモジュールは P1-5 で Top14 を実装する。トーナメント表 →
各クラブの squad ページ → 選手の順に辿る。squad ページの一覧テーブルに
氏名・ポジション・身長・体重が載っており、選手個別ページを1件ずつ叩かずに
基本レコードを構築できる（14リクエストで完走、レート負荷が小さい）。

国籍・career_path・テストキャップは選手個別ページの bio/parcours にあるが、
500件超の個別取得は遅く不安定なため既定では取得しない。環境変数
`ALL_RUGBY_ENRICH=1` を立てると個別ページを辿って nationality/career を補完する。

公開関数:
    collect(tournament) -> {"players","teams","matches","standings","warnings"}
      tournament は "top14"（P1-6 で super-rugby を追加）。run.py の SCRAPERS から呼ぶ。
"""
from __future__ import annotations

import os
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from pipeline.transform import normalize

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
# Super Rugby は P1-6 で追加（key は実ページで要確認、02）。
TOURNAMENTS = {
    "top14": {"key": "top-14", "league": "top14"},
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


def parse_player_bio(html: str) -> dict:
    """選手個別ページ → {'nationality': [...], 'career': [...]}（enrich 用の純パース）。"""
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
    return {"nationality": nats, "career": career}


def _enrich(raw: dict) -> None:
    """選手個別ページから nationality/career を補完（ALL_RUGBY_ENRICH 時のみ）。"""
    html = _get(f"{BASE}/player/{raw['slug']}")
    time.sleep(_SLEEP)
    if html is None:
        return
    bio = parse_player_bio(html)
    if bio["nationality"]:
        raw["nationality"] = bio["nationality"]
    if bio["career"]:
        raw["career"] = bio["career"]


def collect(tournament: str) -> dict:
    """tournament = 'top14' 等。players/teams/standings（transform 済み）を返す。"""
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

    teams_out: list[dict] = []
    players_out: list[dict] = []
    seen_players: set[str] = set()  # 同一 slug の重複所属を防ぐ（最初のクラブに割当）

    for slug in club_slugs:
        shtml = _get(f"{BASE}/club/{slug}/squad")
        time.sleep(_SLEEP)
        if shtml is None:
            warnings.append(f"{league}: club/{slug}/squad 取得失敗、スキップ")
            continue
        squad = parse_squad(shtml)
        if _MAX_PLAYERS:
            squad = squad[:_MAX_PLAYERS]

        roster_ids: list[str] = []
        for raw in squad:
            if raw["slug"] in seen_players:
                continue
            seen_players.add(raw["slug"])
            if _ENRICH:
                _enrich(raw)
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
