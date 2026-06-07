"""
Japan Rugby League One standings scraper.
Rules: Standard 4-2-1-0 point system. No bonus points.
Divisions: D1, D2, D3.
"""
from __future__ import annotations

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
    )
}


def _get_team_info(name: str) -> tuple[str, str, str]:
    info = get_canonical_info(name)
    if info:
        return info["jp"], info["flag"], info["slug"]
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return name, "🇯🇵", slug


class LeagueOneScraper(BaseCompetitionScraper):
    competition_id = "league-one"

    def _fetch_raw(self) -> list[dict]:
        from bs4 import BeautifulSoup

        url = "https://league-one.jp/standings/"
        print(f"[LeagueOne] Scraping {url} ...")

        try:
            resp = requests.get(url, headers=_HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as exc:
            print(f"[LeagueOne] fetch error: {exc}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        tables = (
            soup.select("table.standings-table")
            or soup.select("table[class*='standing']")
            or soup.find_all("table")
        )
        print(f"[LeagueOne] found {len(tables)} table(s)")

        entries = []
        for div_idx, table in enumerate(tables):
            division = f"D{div_idx + 1}"
            for row in table.select("tbody tr"):
                cols = row.select("td, th")
                if len(cols) < 8:
                    continue

                # Locate team name via anchor
                link = None
                name_col = 0
                for ci in range(min(4, len(cols))):
                    a_tag = cols[ci].select_one("a")
                    if a_tag and a_tag.text.strip():
                        link = a_tag
                        name_col = ci
                        break
                if not link:
                    continue

                name = link.text.strip()

                def safe_col(idx: int) -> str:
                    return cols[idx].get_text(strip=True) if idx < len(cols) else "0"

                nc = name_col
                jp, flag, slug = _get_team_info(name)

                entries.append({
                    "rank": safe_col(0),
                    "team_name": name,
                    "display_name": jp,
                    "flag": flag,
                    "slug": slug,
                    "played": safe_col(nc + 1),
                    "points": safe_col(nc + 2),
                    "won": safe_col(nc + 3),
                    "drawn": safe_col(nc + 4),
                    "lost": safe_col(nc + 5),
                    "diff": safe_col(len(cols) - 1),
                    "division": division,
                })

        print(f"[LeagueOne] Parsed {len(entries)} teams.")
        return entries
