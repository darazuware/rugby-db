"""league-one.jp スクレイパー（02: リーグワン D1/D2/D3）。

チーム一覧（順位表ページ）→ 各チームページの所属選手 → 個別選手ページ の順に辿る。
HTML構造が想定と違う項目は null にして warning を積む（例外で全体を止めない、02）。
取得した生 dict は transform.normalize で 01 スキーマへ変換する。

公開関数:
    collect(division) -> {"players","teams","matches","standings","warnings"}
      division は "d1"/"d2"/"d3"。run.py の SCRAPERS から呼ぶ。
"""
from __future__ import annotations

import os
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from pipeline import llm_fallback
from pipeline.transform import normalize

BASE = "https://league-one.jp"
STANDINGS_URL = f"{BASE}/standings/"

# 学校名の種別判定（正規表現）。jrfu.py と同じ日本語サフィックスに加え、
# 外国人選手向けの英語表記（high school/grammar school/university）も判定する。
_HS_SUFFIX_RE = re.compile(r"(高等学校|高等科|高校)$")
_UNIV_SUFFIX_RE = re.compile(r"(大学校|大学)$")
_EN_HS_RE = re.compile(r"(high\s*school|grammar\s*school)$", re.IGNORECASE)
_EN_UNIV_RE = re.compile(r"(university|univ\.?)$", re.IGNORECASE)
# 末尾の「（日本語訳・国名等）」括弧はサフィックス判定の邪魔になるので判定時のみ除去。
_TRAILING_PAREN_RE = re.compile(r"[（(][^）)]*[）)]\s*$")


def _classify_school_regex(name: str) -> Optional[str]:
    s = _TRAILING_PAREN_RE.sub("", name.strip()).strip()
    if _HS_SUFFIX_RE.search(s) or _EN_HS_RE.search(s):
        return "hs"
    if _UNIV_SUFFIX_RE.search(s) or _EN_UNIV_RE.search(s):
        return "univ"
    return None
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
_SLEEP = 1.5
_TIMEOUT = 15
_RETRIES = 2

# スモークテスト用の上限（本番は未設定）。LEAGUE_ONE_MAX_TEAMS / _MAX_PLAYERS。
_MAX_TEAMS = int(os.environ.get("LEAGUE_ONE_MAX_TEAMS", "0")) or None
_MAX_PLAYERS = int(os.environ.get("LEAGUE_ONE_MAX_PLAYERS", "0")) or None

_standings_soup: Optional[BeautifulSoup] = None


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


def _season(soup: BeautifulSoup) -> str:
    m = re.search(r"20\d{2}-\d{2}", soup.get_text(" ", strip=True))
    return m.group(0) if m else ""


def _load_standings() -> Optional[BeautifulSoup]:
    global _standings_soup
    if _standings_soup is None:
        html = _get(STANDINGS_URL)
        time.sleep(_SLEEP)
        if html is None:
            return None
        _standings_soup = BeautifulSoup(html, "html.parser")
    return _standings_soup


def _division_table(soup: BeautifulSoup, n: int):
    """division-{n} セクションの詳細順位表（列数最大のtable）を返す。"""
    sec = soup.select_one(f"#division-{n}")
    if sec is None:
        return None
    best, best_cols = None, 0
    for t in sec.find_all("table"):
        cols = max((len(r.find_all(["td", "th"])) for r in t.select("tbody tr")), default=0)
        if cols > best_cols:
            best, best_cols = t, cols
    return best


def _team_id(href: str) -> Optional[str]:
    m = re.search(r"/team/(\d+)", href)
    return m.group(1) if m else None


def parse_standings(soup: BeautifulSoup, n: int):
    """詳細順位表 → (standing_rows_raw, [(team_id, team_name)])。

    列: 順位, (ロゴ), チーム名, 試合数, 勝点, 勝, 分, 負, ...
    """
    table = _division_table(soup, n)
    rows: list[dict] = []
    teams: list[tuple[str, str]] = []
    if table is None:
        return rows, teams
    for tr in table.select("tbody tr"):
        cells = tr.find_all(["td", "th"])
        if len(cells) < 8:
            continue
        tid = next((_team_id(a["href"]) for a in tr.find_all("a", href=True) if _team_id(a["href"])), None)
        if tid is None:
            continue
        texts = [c.get_text(strip=True) for c in cells]
        # 名前列 = i>0 で最初の「非空・非数値」セル（ロゴ列は空、順位列は数値）。
        try:
            name_idx = next(i for i, t in enumerate(texts) if i > 0 and t and not t.isdigit())
        except StopIteration:
            continue
        name = texts[name_idx]
        nums = texts[name_idx + 1:]
        rows.append({
            "team_id": tid,
            "rank": texts[0],
            "played": nums[0] if len(nums) > 0 else None,
            "points": nums[1] if len(nums) > 1 else None,
            "won": nums[2] if len(nums) > 2 else None,
            "drawn": nums[3] if len(nums) > 3 else None,
            "lost": nums[4] if len(nums) > 4 else None,
        })
        teams.append((tid, name))
    return rows, teams


def parse_team_page(html: str, tid: str):
    """チームページ → (team_name, [player_id...])。"""
    soup = BeautifulSoup(html, "html.parser")
    name = None
    if soup.title:
        name = re.sub(r"（20\d{2}-\d{2}）.*$", "", soup.title.get_text(strip=True)).strip()
    pids = []
    seen = set()
    for a in soup.find_all("a", href=True):
        m = re.search(r"/player/(\d+)", a["href"])
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            pids.append(m.group(1))
    return name, pids


def parse_player_page(html: str, pid: str) -> dict:
    """個別選手ページ → 生 dict（transform に渡す前段）。"""
    soup = BeautifulSoup(html, "html.parser")

    def _text(sel: str) -> Optional[str]:
        el = soup.select_one(sel)
        return el.get_text(" ", strip=True) if el else None

    name_en = _text(".player-kv-engname")
    raw_ttl = _text(".player-ttl") or ""
    pos = None
    mpos = re.search(r"\(([^)]+)\)\s*$", raw_ttl)
    if mpos:
        pos = mpos.group(1).strip()
    name_ja = re.sub(r"\s*\([^)]*\)\s*$", "", raw_ttl).strip() or None

    detail = _text(".player-kv-detail") or ""
    height = weight = birthdate = league_caps = None
    m = re.search(r"身長\s*/\s*体重\s*：\s*(\d+)\s*cm\s*/\s*(\d+)\s*kg", detail)
    if m:
        height, weight = m.group(1), m.group(2)
    m = re.search(r"生年月日\s*：\s*(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})", detail)
    if m:
        birthdate = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.search(r"リーグワンキャップ数\s*：\s*(\d+)", detail)
    if m:
        league_caps = m.group(1)

    education_segments_raw: list[str] = []
    m = re.search(r"出身校・チーム歴\s*：\s*(.+?)(?:\s*登録区分|\s*リーグワンキャップ数|$)", detail)
    if m:
        for seg in m.group(1).split("\xa0"):
            seg = seg.strip()
            if seg:
                education_segments_raw.append(seg)

    image_url = None
    img = soup.select_one(".player-kv-img img")
    if img and img.get("src", "").startswith("http"):
        image_url = img["src"]

    return {
        "player_id": pid,
        "name_en": name_en or None,
        "name_ja": name_ja,
        "position": pos,
        "height_cm": height,
        "weight_kg": weight,
        "birthdate": birthdate,
        "league_caps": league_caps,
        "image_url": image_url,
        "education_segments_raw": education_segments_raw,
    }


def collect(division: str) -> dict:
    """division = 'd1'/'d2'/'d3'。players/teams/standings（transform済み）を返す。"""
    n = {"d1": 1, "d2": 2, "d3": 3}[division]
    league = f"league-one-{division}"
    warnings: list[str] = []

    soup = _load_standings()
    if soup is None:
        warnings.append(f"{league}: 順位表ページ取得失敗")
        return {"players": [], "teams": [], "matches": [], "standings": [], "warnings": warnings}

    season = _season(soup)
    standing_rows_raw, team_list = parse_standings(soup, n)
    if _MAX_TEAMS:
        team_list = team_list[:_MAX_TEAMS]

    teams_out: list[dict] = []
    players_out: list[dict] = []
    roster_by_team: dict[str, list[str]] = {}
    team_meta: list[tuple[str, str, list[str]]] = []  # (tid, team_name, pids)
    raws_by_pid: dict[str, dict] = {}

    for tid, std_name in team_list:
        html = _get(f"{BASE}/team/{tid}")
        time.sleep(_SLEEP)
        if html is None:
            warnings.append(f"{league}: team/{tid} 取得失敗、スキップ")
            continue
        team_name, pids = parse_team_page(html, tid)
        team_name = team_name or std_name
        if _MAX_PLAYERS:
            pids = pids[:_MAX_PLAYERS]

        kept_pids: list[str] = []
        for pid in pids:
            phtml = _get(f"{BASE}/player/{pid}")
            time.sleep(_SLEEP)
            if phtml is None:
                warnings.append(f"{league}: player/{pid} 取得失敗、スキップ")
                continue
            raws_by_pid[pid] = parse_player_page(phtml, pid)
            kept_pids.append(pid)
        team_meta.append((tid, team_name, kept_pids))

    # 出身校の正規表現分類→未判定分のみまとめてSonnetフォールバック（jrfu.py と同方針）。
    unresolved: set[str] = set()
    for raw in raws_by_pid.values():
        for seg in raw.get("education_segments_raw", []):
            if _classify_school_regex(seg) is None:
                unresolved.add(seg)
    llm_result: dict[str, str] = {}
    if unresolved:
        llm_result = llm_fallback.classify_school_names(sorted(unresolved))
        still_unresolved = sorted(set(unresolved) - set(llm_result))
        if still_unresolved:
            warnings.append(
                f"{league}: 出身校{len(still_unresolved)}件を正規表現・Sonnet"
                f"いずれでもtype判定できず（例: {still_unresolved[:3]}）"
            )

    def _type_of(name: str) -> Optional[str]:
        return _classify_school_regex(name) or llm_result.get(name)

    for raw in raws_by_pid.values():
        education: list[dict] = []
        for seg in raw.get("education_segments_raw", []):
            t = _type_of(seg)
            if t is not None:
                education.append({"name_raw": seg, "type": t})
        raw["_education"] = education

    for tid, team_name, kept_pids in team_meta:
        roster_ids: list[str] = []
        for pid in kept_pids:
            raw = raws_by_pid[pid]
            player, pw = normalize.player(raw, league=league, team_id=f"lo_team_{tid}")
            warnings.extend(pw)
            if player is None:
                continue
            players_out.append(player)
            roster_ids.append(player["id"])
        roster_by_team[tid] = roster_ids

        team, tw = normalize.team(
            {"team_id": tid, "name_ja": team_name, "roster_ids": roster_ids},
            league=league,
        )
        warnings.extend(tw)
        if team is not None:
            teams_out.append(team)

    standings_out: list[dict] = []
    # 実際に取得できたチームのみ順位表に残す（roster対称性と team_ref を壊さない）
    valid_tids = {t["id"] for t in teams_out}
    rows = [r for r in standing_rows_raw if f"lo_team_{r['team_id']}" in valid_tids]
    standing, sw = normalize.standing(rows, league=league, season=season)
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
