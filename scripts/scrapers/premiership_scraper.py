"""
Gallagher Premiership (England) standings scraper.
Competition-specific rules hardcoded:
  - 4 points for a win, 2 for a draw, 0 for a loss
  - Bonus point for scoring 4+ tries (try_bonus)
  - Bonus point for losing by 7 or fewer points (losing_bonus)
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

# Premiership bonus point rules
TRY_BONUS_THRESHOLD = 4   # 4 tries scored → +1 BP
LOSING_BONUS_MARGIN = 7   # Lose by ≤7 points → +1 BP


def _get_team_info(name: str) -> tuple[str, str, str]:
    info = get_canonical_info(name)
    if info:
        return info["jp"], info["flag"], info["slug"]
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return name, "🏴󠁧󠁢󠁥󠁮󠁧󠁿", slug


class PremiershipScraper(BaseCompetitionScraper):
    competition_id = "premiership"

    # Column indices in the official site table (0-based)
    _IDX_RANK   = 0
    _IDX_TEAM   = 1
    _IDX_PLAYED = 2
    _IDX_WON    = 3
    _IDX_DRAWN  = 4
    _IDX_LOST   = 5
    _IDX_DIFF   = 6
    _IDX_POINTS = 11  # Total points (last meaningful column)

    def _fetch_raw(self) -> list[dict]:
        from bs4 import BeautifulSoup

        url = "https://www.premiershiprugby.com/competitions/gallagher-prem/standings"
        print(f"[Premiership] Scraping {url} ...")

        try:
            resp = requests.get(url, headers=_HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as exc:
            print(f"[Premiership] fetch error: {exc}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        entries = []

        for row in soup.select("tbody tr"):
            cells = row.select("td")
            if len(cells) < 7:
                continue

            rank = cells[self._IDX_RANK].get_text(strip=True)

            team_cell = cells[self._IDX_TEAM]
            name_el = team_cell.select_one("span.font-condensed")
            raw_name = (
                name_el.get_text(strip=True) if name_el
                else team_cell.get_text(strip=True)
            )

            played = cells[self._IDX_PLAYED].get_text(strip=True)
            won    = cells[self._IDX_WON].get_text(strip=True)
            drawn  = cells[self._IDX_DRAWN].get_text(strip=True)
            lost   = cells[self._IDX_LOST].get_text(strip=True)
            diff   = cells[self._IDX_DIFF].get_text(strip=True)
            points = cells[self._IDX_POINTS].get_text(strip=True) if len(cells) > self._IDX_POINTS else ""

            # Bonus point columns (7 = try BP, 8 = losing BP) — may not exist
            try_bonus    = cells[7].get_text(strip=True) if len(cells) > 7 else None
            losing_bonus = cells[8].get_text(strip=True) if len(cells) > 8 else None

            jp, flag, slug = _get_team_info(raw_name)

            entries.append({
                "rank": rank,
                "team_name": raw_name,
                "display_name": jp,
                "flag": flag,
                "slug": slug,
                "played": played,
                "won": won,
                "drawn": drawn,
                "lost": lost,
                "diff": diff,
                "points": points,
                "try_bonus": try_bonus,
                "losing_bonus": losing_bonus,
            })

        print(f"[Premiership] Parsed {len(entries)} teams.")
        return entries
