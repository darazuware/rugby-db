"""
United Rugby Championship standings scraper (GraphQL API).
Competition-specific rules:
  - 4-2-1-0 point system with try and losing bonus points
  - Uses persisted GraphQL query against unitedrugby.com
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
    "Referer": "https://www.unitedrugby.com/",
}

# GraphQL persisted query — seasonId 202501 = 2025/26 season
_GRAPHQL_URL = "https://www.unitedrugby.com/graphql"
_SEASON_ID   = 202501
_QUERY_HASH  = "702a2903fbc5f7e05fb7004f6979f6c0e3a747ad1e62f8e0c0008beca15f34f3"


def _get_team_info(name: str) -> tuple[str, str, str]:
    info = get_canonical_info(name)
    if info:
        return info["jp"], info["flag"], info["slug"]
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return name, "🏟️", slug


class URCScraper(BaseCompetitionScraper):
    competition_id = "urc"

    def _fetch_raw(self) -> list[dict]:
        print(f"[URC] Querying GraphQL API (seasonId={_SEASON_ID}) ...")

        params = {
            "operationName": "GetStandingData",
            "variables": json.dumps({"seasonId": _SEASON_ID}),
            "extensions": json.dumps({
                "persistedQuery": {"version": 1, "sha256Hash": _QUERY_HASH}
            }),
        }

        try:
            resp = requests.get(_GRAPHQL_URL, params=params, headers=_HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            print(f"[URC] fetch error: {exc}")
            return []

        items = data.get("data", {}).get("standings", [])
        entries = []

        for i, item in enumerate(items):
            stats   = item.get("performance_stats", {})
            raw     = item.get("team_name", "")
            jp, flag, slug = _get_team_info(raw)

            entries.append({
                "rank":          str(item.get("position", i + 1)),
                "team_name":     raw,
                "display_name":  jp,
                "flag":          flag,
                "slug":          slug,
                "played":        str(stats.get("played", "0")),
                "won":           str(stats.get("won", "0")),
                "drawn":         str(stats.get("drawn", "0")),
                "lost":          str(stats.get("lost", "0")),
                "diff":          str(stats.get("pointsDiff", "0")),
                "points":        str(stats.get("points", "0")),
                "try_bonus":     str(stats.get("tryBonus", "")) or None,
                "losing_bonus":  str(stats.get("losingBonus", "")) or None,
            })

        print(f"[URC] Parsed {len(entries)} teams.")
        return entries
