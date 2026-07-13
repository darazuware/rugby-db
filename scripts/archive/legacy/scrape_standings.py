"""
Standings orchestrator.
Instantiates each competition-specific scraper, runs validation via Pydantic,
and writes the merged result to data/standings.json.

Fail-safe: if a scraper returns fewer entries than the minimum expected,
the previous data is kept (fallback).
"""
import json
import os
import sys

# Ensure scripts/ is on the path so team_utils and scrapers/ are importable
sys.path.insert(0, os.path.dirname(__file__))

from scrapers.league_one_scraper   import LeagueOneScraper
from scrapers.top14_scraper        import Top14Scraper
from scrapers.urc_scraper          import URCScraper
from scrapers.super_rugby_scraper  import SuperRugbyScraper
from scrapers.premiership_scraper  import PremiershipScraper

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'standings.json')

# Minimum team count to accept a fresh scrape (below → use cached data)
MIN_TEAMS = {
    "league-one":  12,
    "top14":       14,
    "urc":         16,
    "super-rugby": 11,
    "premiership": 10,
}


def _load_existing() -> dict:
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _get_old(current: dict, league: str, key: str) -> list:
    league_data = current.get(league, {})
    if isinstance(league_data, dict):
        return league_data.get(key, [])
    if isinstance(league_data, list) and key == "standings":
        return league_data
    return []


def _run_scraper(scraper_cls, current: dict, league_id: str) -> dict:
    """Run a scraper and return a validated output dict.
    Falls back to cached data if scrape returns too few entries.
    """
    try:
        scraper = scraper_cls()
        output  = scraper.to_output(results=_get_old(current, league_id, "results"))
        count   = len(output.get("standings", []))
        minimum = MIN_TEAMS.get(league_id, 1)

        if count < minimum:
            print(f"[{league_id}] Only {count} entries (min {minimum}). Keeping cached data.")
            standings = _get_old(current, league_id, "standings")
            results   = _get_old(current, league_id, "results")
            output["standings"] = standings
            output["results"]   = results

        return output
    except Exception as exc:
        import traceback
        print(f"[{league_id}] Scraper failed: {exc}")
        traceback.print_exc()
        # Full fallback: preserve cached data, still attach metadata
        cached_standings = _get_old(current, league_id, "standings")
        cached_results   = _get_old(current, league_id, "results")
        return {
            "sport_type":  "rugby_union",
            "competition": league_id,
            "season":      "",
            "updated_at":  "",
            "standings":   cached_standings,
            "results":     cached_results,
            "error":       str(exc),
        }


def main() -> None:
    current = _load_existing()

    scrapers = [
        (LeagueOneScraper,  "league-one"),
        (Top14Scraper,      "top14"),
        (URCScraper,        "urc"),
        (SuperRugbyScraper, "super-rugby"),
        (PremiershipScraper,"premiership"),
    ]

    all_data: dict = {}
    for scraper_cls, league_id in scrapers:
        print(f"\n{'='*40}\n  {league_id}\n{'='*40}")
        all_data[league_id] = _run_scraper(scraper_cls, current, league_id)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\nStandings saved → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
