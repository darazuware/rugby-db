"""
Super Rugby Pacific standings scraper (Opta JSONP API).

Competition-specific rules hardcoded:
  - NORMAL WIN:      4 points (won within 80 min)
  - SUPER POINT WIN: 3 points (won in extra time or penalty shootout)
  - DRAW:            2 points
  - LOSING BONUS:    1 point (lost by ≤7 OR lost in extra time/penalty)
  - TRY BONUS:       1 point (scored 4+ tries regardless of result)

The Opta API returns `points` as the total — no separation of win-type.
`bonus_points` field (if present) captures combined BP.
"""
from __future__ import annotations

import json
import re
import sys
import os

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from team_utils import get_team_info as get_canonical_info
from scrapers.base_competition_scraper import BaseCompetitionScraper

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://super.rugby/",
    "Origin":  "https://super.rugby/",
}

# Opta API parameters — season_id updates each calendar year
_OPTA_URL     = "https://omo.akamai.opta.net/auth/competition.php"
_COMPETITION  = "205"       # Super Rugby Pacific
_OPTA_SEASON  = "2026"
_OPTA_USER    = "OW2017"
_OPTA_PSW     = "dXWg5gVZ"

# Super Rugby point values (for documentation / future validation)
SUPER_POINT_WIN = 3   # Overtime / penalty shootout win
NORMAL_WIN      = 4   # Regular-time win
DRAW            = 2
LOSING_BONUS    = 1   # Lost by ≤7 OR lost in extra time
TRY_BONUS       = 1   # 4+ tries scored


def _get_team_info(name: str) -> tuple[str, str, str]:
    info = get_canonical_info(name)
    if info:
        return info["jp"], info["flag"], info["slug"]
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return name, "🏉", slug


def _unwrap_jsonp(text: str) -> dict:
    """Strip JSONP wrapper:  callback({...})  →  {...}"""
    start = text.index("(") + 1
    end   = text.rindex(")")
    return json.loads(text[start:end])


def _collect_teams(group_data) -> list[dict]:
    """Flatten conference/group structure into a flat team list."""
    raw_teams: list[dict] = []
    if isinstance(group_data, list):
        for g in group_data:
            t = g.get("team", [])
            if isinstance(t, list):
                raw_teams.extend(t)
            elif t:
                raw_teams.append(t)
    elif isinstance(group_data, dict):
        t = group_data.get("team", [])
        if isinstance(t, list):
            raw_teams = t
        elif t:
            raw_teams = [t]
    return raw_teams


class SuperRugbyScraper(BaseCompetitionScraper):
    competition_id = "super-rugby"

    def _fetch_raw(self) -> list[dict]:
        print(f"[SuperRugby] Querying Opta API (season={_OPTA_SEASON}) ...")

        params = {
            "feed_type":    "ru2",
            "competition":  _COMPETITION,
            "season_id":    _OPTA_SEASON,
            "user":         _OPTA_USER,
            "psw":          _OPTA_PSW,
            "jsoncallback": "callback",
        }

        try:
            resp = requests.get(_OPTA_URL, params=params, headers=_HEADERS, timeout=15)
            resp.raise_for_status()
            print(f"[SuperRugby] API response length: {len(resp.text)}")
            data = _unwrap_jsonp(resp.text)
        except Exception as exc:
            print(f"[SuperRugby] fetch/parse error: {exc}")
            return []

        group_data = (
            data.get("table", {})
                .get("comp", {})
                .get("group", {})
        )
        raw_teams = _collect_teams(group_data)
        print(f"[SuperRugby] teams found: {len(raw_teams)}")

        entries = []
        for t in raw_teams:
            a = t.get("@attributes", {})
            raw = a.get("name", "")
            jp, flag, slug = _get_team_info(raw)

            # `bonus_points` or `bonuspoints` captures combined BP when available
            bonus_raw = a.get("bonus_points") or a.get("bonuspoints") or None

            # Detect super-point wins:
            # The API does not expose win-type directly.
            # `superpoints` or `otherwins` field indicates non-regular wins.
            super_wins = a.get("superpoints") or a.get("otherwins") or None

            entries.append({
                "rank":       a.get("rank", str(len(entries) + 1)),
                "team_name":  raw,
                "display_name": jp,
                "flag":       flag,
                "slug":       slug,
                "played":     a.get("played", "0"),
                "won":        a.get("won", "0"),
                "drawn":      a.get("drawn", "0"),
                "lost":       a.get("lost", "0"),
                "diff":       a.get("pointsdiff", "0"),
                "points":     a.get("points", "0"),
                # Super Rugby–specific fields
                "try_bonus":    bonus_raw,   # total BP (try+losing combined or separate)
                "losing_bonus": super_wins,  # overtime/PK wins treated as losing-bonus proxy
            })

        entries.sort(key=lambda x: int(x["rank"]) if str(x["rank"]).isdigit() else 99)
        print(f"[SuperRugby] Parsed {len(entries)} teams.")
        return entries
