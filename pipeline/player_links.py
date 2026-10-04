"""選手へのリンク先の決定（src/lib/master.ts の isIndexablePlayer / playerFallbackPath / playerHref と同じ規則）。

docs/adsense/01_DESIGN.md §2: 個別ページ（/players/{slug}/）を持つのは data/manual/player_pages.json
（scripts/build_player_pages.py 生成）に載る選手のみ。それ以外はチーム名簿アンカーへリンクする。
news_gen.py / scripts/link_news.py が共用する。data/master は読み取りのみ。
"""
from __future__ import annotations

import glob
import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent


def _load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


@lru_cache(maxsize=1)
def indexable_slugs() -> frozenset[str]:
    pages = _load(ROOT / "data/manual/player_pages.json", {})
    return frozenset(r["slug"] for r in pages.get("players", []))


@lru_cache(maxsize=1)
def merges() -> dict[str, str]:
    return _load(ROOT / "data/manual/player_merges.json", {})


def canon(pid: str) -> str:
    seen: set[str] = set()
    m = merges()
    while pid in m and pid not in seen:
        seen.add(pid)
        pid = m[pid]
    return pid


@lru_cache(maxsize=1)
def master_players() -> dict[str, dict]:
    """id -> player。national とクラブの id 重複はクラブ側を優先（master.ts dedupePlayersById 相当）。"""
    by_id: dict[str, dict] = {}
    for f in sorted(glob.glob(str(ROOT / "data/master/players/*.json"))):
        for p in _load(Path(f), []):
            ex = by_id.get(p["id"])
            if ex is None or (ex.get("league") == "national" and p.get("league") != "national"):
                by_id[p["id"]] = p
    return by_id


@lru_cache(maxsize=1)
def slug_to_player() -> dict[str, dict]:
    """slug（統合前の旧 slug を含む）-> 現存する選手。同一 slug は個別ページ対象を優先。"""
    players = master_players()
    out: dict[str, dict] = {}
    for pid, p in players.items():
        out.setdefault(p["slug"], players.get(canon(pid), p))
    for pid, p in players.items():
        if canon(pid) == pid and (p["slug"] not in out or p["slug"] in indexable_slugs()):
            out[p["slug"]] = p
    return out


def _legacy_league(league: str) -> Optional[str]:
    if league.startswith("league-one"):
        return "league-one"
    return league if league in ("top14", "super-rugby", "urc", "premiership") else None


@lru_cache(maxsize=1)
def _clubs() -> dict[str, str]:
    """チーム名（日本語を含むもの）-> /teams/{league}/{slug}/（link_news.py の club 辞書と同じ規則）。"""
    clubs: dict[str, str] = {}
    for t in _load(ROOT / "data/teams.json", []):
        slug, lg = t.get("slug"), t.get("league")
        if not slug or not lg or slug == "2025-26":
            continue
        url = f"/teams/{lg}/{slug}/"
        for k in (t.get("team_name"), t.get("team_en_name")):
            k = (k or "").strip()
            if len(k) >= 4 and any(ord(c) > 127 for c in k):
                clubs.setdefault(k, url)
    for lg_map in _load(ROOT / "data/team_names_jp.json", {}).values():
        if not isinstance(lg_map, dict):
            continue
        for data in lg_map.values():
            jp = (data or {}).get("jp")
            url = clubs.get(jp) if jp else None
            if not url:
                continue
            for al in data.get("aliases") or []:
                al = al.strip()
                if len(al) >= 4 and any(ord(c) > 127 for c in al):
                    clubs.setdefault(al, url)
    return clubs


@lru_cache(maxsize=1)
def _page_slugs() -> frozenset[tuple[str, str]]:
    return frozenset((t["league"], t["slug"]) for t in _load(ROOT / "data/teams.json", []) if t.get("slug"))


@lru_cache(maxsize=1)
def _master_teams() -> dict[str, dict]:
    teams: dict[str, dict] = {}
    for f in sorted(glob.glob(str(ROOT / "data/master/teams/*.json"))):
        for t in _load(Path(f), []):
            teams[t["id"]] = t
    return teams


@lru_cache(maxsize=1)
def _national_slugs() -> frozenset[str]:
    return frozenset(t["slug"] for t in _load(ROOT / "data/national_teams_config.json", []) if t.get("slug"))


def team_page_path(team: dict) -> Optional[str]:
    lg = _legacy_league(team["league"])
    if not lg:
        return None
    for nm in (team.get("name_ja"), team.get("name_en")):
        url = _clubs().get((nm or "").strip())
        if url and url.startswith(f"/teams/{lg}/"):
            return url
    if (lg, team["id"]) in _page_slugs():
        return f"/teams/{lg}/{team['id']}/"
    return None


def fallback_path(p: dict) -> str:
    """個別ページを持たない選手の行き先（master.ts playerFallbackPath と同じ規則）。無ければ '/players/'。"""
    tid = p.get("team_id")
    team = _master_teams().get(tid) if tid else None
    tp = team_page_path(team) if team else None
    if tp:
        return f"{tp}#p-{p['slug']}"
    if tid in _national_slugs():
        return f"/national-teams/{tid}/#p-{p['slug']}"
    lg = _legacy_league(p.get("league", ""))
    return f"/leagues/{lg}/" if lg else "/players/"


def is_indexable(p: dict) -> bool:
    return p.get("league") != "highschool" and p.get("slug") in indexable_slugs()


def player_href(p: dict) -> Optional[str]:
    """記事内リンク先。個別ページがあればそこ、チーム名簿に行があればアンカー、行き先が /players/ だけなら None（平文）。"""
    if not p or not p.get("slug"):
        return None
    if is_indexable(p):
        return f"/players/{p['slug']}/"
    if p.get("league") == "highschool":
        return None
    target = fallback_path(p)
    return None if target == "/players/" else target
