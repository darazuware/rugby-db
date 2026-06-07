"""
Base class for all competition-specific standings scrapers.
Provides: Pydantic validation, negative keyword filtering, sport_type enforcement.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List, Literal, Optional

from pydantic import BaseModel, field_validator, model_validator, ValidationError


# ---------------------------------------------------------------------------
# Negative keyword filter
# ---------------------------------------------------------------------------

EXCLUDED_SPORT_KEYWORDS: frozenset[str] = frozenset([
    # Basketball
    "bリーグ", "b.league", "b league", "nba", "バスケ", "basketball",
    # Baseball
    "プロ野球", "npb", "mlb", "球団", "baseball", "野球",
    # Football / Soccer
    "サッカー", "jリーグ", "j.league", "j league", "fifa", "football",
    # Rugby League (not Union)
    "ラグビーリーグ", "rugby league", "nrl",
    # Para-sports
    "車いすラグビー", "wheelchair rugby", "wheelchair",
    # Other sports
    "ハンドボール", "handball", "volleyball", "バレー",
    "アメフト", "american football", "nfl",
])


def _is_contaminated(name: str) -> bool:
    lower = name.lower()
    return any(kw in lower for kw in EXCLUDED_SPORT_KEYWORDS)


# ---------------------------------------------------------------------------
# Pydantic models (backward-compatible field names)
# ---------------------------------------------------------------------------

class StandingEntry(BaseModel):
    rank: int
    team_name: str           # English name (source)
    display_name: Optional[str] = None  # Japanese / display name
    flag: Optional[str] = None
    slug: str
    played: int
    won: int
    drawn: int
    lost: int
    diff: str = "0"          # Keep as str: can be "+200" or "-50"
    points: int
    try_bonus: Optional[int] = None      # Top 14, Premiership
    losing_bonus: Optional[int] = None  # Top 14, Premiership
    division: Optional[str] = None       # League One divisions

    @field_validator("rank", "played", "won", "drawn", "lost", "points", mode="before")
    @classmethod
    def coerce_non_negative_int(cls, v):
        try:
            return max(0, int(str(v).strip()))
        except (TypeError, ValueError):
            return 0

    @field_validator("try_bonus", "losing_bonus", mode="before")
    @classmethod
    def coerce_optional_int(cls, v):
        if v is None or v == "":
            return None
        try:
            return max(0, int(str(v).strip()))
        except (TypeError, ValueError):
            return None

    @field_validator("diff", mode="before")
    @classmethod
    def coerce_diff_str(cls, v):
        if v is None:
            return "0"
        return str(v).strip() or "0"

    @field_validator("rank", mode="after")
    @classmethod
    def rank_at_least_one(cls, v: int) -> int:
        return max(1, v)

    @model_validator(mode="after")
    def fix_played_count(self) -> "StandingEntry":
        total = self.won + self.drawn + self.lost
        if self.played != total:
            object.__setattr__(self, "played", total)
        return self


class CompetitionStandings(BaseModel):
    sport_type: Literal["rugby_union"] = "rugby_union"
    competition: str
    season: str
    updated_at: str
    standings: List[StandingEntry]
    results: List[dict] = []


# ---------------------------------------------------------------------------
# Base scraper
# ---------------------------------------------------------------------------

class BaseCompetitionScraper(ABC):
    """
    Subclass this for each competition.
    Implement `_fetch_raw()` returning a list of raw dicts.
    Call `to_output(results=[...])` to get a validated, serialisable dict.
    """

    competition_id: str = ""

    @property
    def season(self) -> str:
        return str(datetime.now(timezone.utc).year)

    @abstractmethod
    def _fetch_raw(self) -> list[dict]:
        """Fetch and parse standings from source. Return raw un-validated dicts."""
        ...

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _filter_contaminated(self, entries: list[dict]) -> list[dict]:
        clean = []
        for e in entries:
            name = str(e.get("team_name", ""))
            if _is_contaminated(name):
                print(f"[FILTER] Discarded contaminated entity: {name!r}")
            else:
                clean.append(e)
        return clean

    def _validate_entries(self, entries: list[dict]) -> list[StandingEntry]:
        valid: list[StandingEntry] = []
        for raw in entries:
            try:
                valid.append(StandingEntry.model_validate(raw))
            except ValidationError as exc:
                team = raw.get("team_name", "<unknown>")
                print(f"[WARN] Entry discarded team={team!r}: {exc}")
        return valid

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scrape(self) -> list[StandingEntry]:
        raw = self._fetch_raw()
        clean = self._filter_contaminated(raw)
        return self._validate_entries(clean)

    def to_output(self, results: list | None = None) -> dict:
        entries = self.scrape()
        payload = CompetitionStandings(
            competition=self.competition_id,
            season=self.season,
            updated_at=datetime.now(timezone.utc).isoformat(),
            standings=entries,
            results=results or [],
        )
        return payload.model_dump()
