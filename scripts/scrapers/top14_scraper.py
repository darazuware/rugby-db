"""
Top 14 standings scraper.
Competition-specific rules hardcoded:
  - Bonus point for scoring 4+ tries in a match (try_bonus)
  - Bonus point for losing by 7 points or fewer (losing_bonus)
"""
from __future__ import annotations

import re
import subprocess
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from team_utils import get_team_info as get_canonical_info
from scrapers.base_competition_scraper import BaseCompetitionScraper

_GOOGLEBOT_UA = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

# Top 14 bonus point rules (LNR regulations)
TRY_BONUS_THRESHOLD = 4   # 4 tries scored in a match → +1 BP
LOSING_BONUS_MARGIN = 7   # Lose by ≤7 points → +1 BP


def _get_team_info(name: str) -> tuple[str, str, str]:
    info = get_canonical_info(name)
    if info:
        return info["jp"], info["flag"], info["slug"]
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return name, "🇫🇷", slug


class Top14Scraper(BaseCompetitionScraper):
    competition_id = "top14"

    # Columns in the LNR scrollable stats block
    # idx: 0=Pts, 1=J(played), 2=V(won), 3=N(drawn), 4=D(lost),
    #       5=BP(try_bonus?), 6=BP défaite(losing_bonus?), 7=..., 8=Diff
    _IDX_POINTS = 0
    _IDX_PLAYED = 1
    _IDX_WON    = 2
    _IDX_DRAWN  = 3
    _IDX_LOST   = 4
    _IDX_DIFF   = 8

    def _fetch_raw(self) -> list[dict]:
        from bs4 import BeautifulSoup

        url = "https://top14.lnr.fr/classement"
        print(f"[Top14] Scraping {url} ...")

        result = subprocess.run(
            ["curl", "-s", "-L", "-A", _GOOGLEBOT_UA, url],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if result.returncode != 0:
            print(f"[Top14] curl error: {result.stderr}")
            return []

        soup = BeautifulSoup(result.stdout, "html.parser")

        fixed_rows = soup.select(".ranking__fixed-block .table-line--ranking-fixed")
        scroll_rows = soup.select(".ranking__scrollable-cells .table-line--ranking-scrollable")

        if not fixed_rows:
            fixed_rows = soup.find_all("div", class_=re.compile(r"table-line--ranking-fixed"))
            scroll_rows = soup.find_all("div", class_=re.compile(r"table-line--ranking-scrollable"))

        print(f"[Top14] fixed={len(fixed_rows)}, scroll={len(scroll_rows)}")

        entries = []
        for i in range(min(len(fixed_rows), len(scroll_rows))):
            fixed = fixed_rows[i]
            scroll = scroll_rows[i]

            rank_el = fixed.find(class_=re.compile(r"rank"))
            rank = re.sub(r"\D", "", re.sub(r"<[^>]+>", "", str(rank_el))) if rank_el else ""
            if not rank:
                rank = str(i + 1)

            img_el = fixed.find("img", alt=True)
            raw_name = img_el["alt"].strip() if img_el else ""
            if not raw_name:
                link = scroll.find("a", class_=re.compile(r"base-link"))
                raw_name = re.sub(r"<[^>]+>", "", str(link)).strip() if link else f"Team {rank}"

            wrappers = scroll.find_all("div", class_=re.compile(r"table-line__cell-wrapper--small"))
            stats = []
            for w in wrappers:
                val = re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", str(w))).strip()
                stats.append(val)

            if len(stats) >= 9:
                points  = stats[self._IDX_POINTS]
                played  = stats[self._IDX_PLAYED]
                won     = stats[self._IDX_WON]
                drawn   = stats[self._IDX_DRAWN]
                lost    = stats[self._IDX_LOST]
                diff    = stats[self._IDX_DIFF]
                # Try to extract bonus points if available (columns 5 & 6)
                try_bonus    = stats[5] if len(stats) > 5 else None
                losing_bonus = stats[6] if len(stats) > 6 else None
            else:
                points = played = won = drawn = lost = diff = ""
                try_bonus = losing_bonus = None

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

        print(f"[Top14] Parsed {len(entries)} teams.")
        return entries
