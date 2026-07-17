"""01_DATA_ARCHITECTURE.md のスキーマ定義（pydantic v2）。

使い方:
    player, warnings = Player.parse(raw_dict)
raw値の正規化（文字列数値の変換・範囲外→null・日付パース）は parse() が行い、
落とした値は warnings に文字列で返す。ValidationError は呼び出し側で捕捉する。
"""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from typing import Any, Literal, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# リーグキー（01）。チーム所属必須のリーグと、team_id=null を許可するリーグ（03）
TEAM_LEAGUES = {
    "league-one-d1", "league-one-d2", "league-one-d3",
    "top14", "super-rugby", "urc", "premiership", "nrl",
}
NO_TEAM_LEAGUES = {"national", "sevens-national", "age-grade", "university", "highschool"}
LEAGUE_KEYS = TEAM_LEAGUES | NO_TEAM_LEAGUES

# source_url 許可ドメイン（03）。Phase4/5 での追加はここに1行足す
# rugby-japan.jp: P1-7で追加。02は「JRFU（jrfu.jp）」と表記するが jrfu.jp は
# 名前解決不可（実在しない）。日本代表公式サイトの実ドメインは www.rugby-japan.jp
# （2026-07-18 に実ページで確認）のため、正データ取得元としてこちらを許可する。
ALLOWED_DOMAINS = {"league-one.jp", "all.rugby", "jrfu.jp", "rugby-japan.jp"}

HEIGHT_RANGE = (150, 230)
WEIGHT_RANGE = (60, 170)
BIRTHYEAR_RANGE = (1970, 2010)


def _check_domain(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in ALLOWED_DOMAINS)


def _validate_source_url(url: str) -> str:
    if not _check_domain(url):
        raise ValueError(f"source_url のドメインが許可リスト外: {url}")
    return url


def _to_int(v: Any) -> Optional[int]:
    """'186' や 186.0 を int に。変換不能は ValueError。"""
    if v is None:
        return None
    if isinstance(v, bool):
        raise ValueError(f"数値でない: {v!r}")
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, str):
        s = v.strip()
        if re.fullmatch(r"-?\d+", s):
            return int(s)
    raise ValueError(f"数値に変換できない: {v!r}")


def _parse_date(v: Any) -> Optional[str]:
    """YYYY-MM-DD に正規化。パース不能は None（03: 推測しない）。"""
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"):
            try:
                return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
    return None


def normalize_name_en(name: str) -> str:
    """人物同一性突合用の name_en 正規化（01/03 cross_person）。"""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[\s\-'.]+", " ", s.lower()).strip()
    return s


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Caps(_StrictModel):
    team: str
    count: int = Field(ge=0)
    source_url: Optional[str] = None

    @field_validator("source_url")
    @classmethod
    def _url(cls, v: Optional[str]) -> Optional[str]:
        return _validate_source_url(v) if v else None


class CareerEntry(_StrictModel):
    team: str
    from_: Optional[int] = Field(default=None, alias="from")
    to: Optional[int] = None
    source_url: Optional[str] = None
    model_config = ConfigDict(extra="forbid", populate_by_name=True, serialize_by_alias=True)

    @field_validator("source_url")
    @classmethod
    def _url(cls, v: Optional[str]) -> Optional[str]:
        return _validate_source_url(v) if v else None


class SeasonStats(_StrictModel):
    season: str
    matches: Optional[int] = Field(default=None, ge=0)
    tries: Optional[int] = Field(default=None, ge=0)
    points: Optional[int] = Field(default=None, ge=0)


class Education(_StrictModel):
    school_id: Optional[str] = None
    name_raw: Optional[str] = None
    type: Literal["hs", "univ"]
    grad_year: Optional[int] = None
    source_url: Optional[str] = None
    scraped_at: Optional[str] = None

    @field_validator("source_url")
    @classmethod
    def _url(cls, v: Optional[str]) -> Optional[str]:
        return _validate_source_url(v) if v else None


class Player(_StrictModel):
    id: str = Field(min_length=1)
    source: str
    source_url: str
    scraped_at: str
    name_en: Optional[str] = None
    name_ja: Optional[str] = None
    name_kana: Optional[str] = None
    slug: str = Field(min_length=1)
    position: Optional[str] = None
    team_id: Optional[str] = None
    league: str
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    birthdate: Optional[str] = None
    nationality: list[str] = Field(default_factory=list)
    caps: Optional[Caps] = None
    league_caps: Optional[int] = Field(default=None, ge=0)
    career: list[CareerEntry] = Field(default_factory=list)
    season_stats: Optional[SeasonStats] = None
    education: list[Education] = Field(default_factory=list)
    instagram: Optional[str] = None
    image_url: Optional[str] = None  # 参考保持のみ、表示禁止（02/06）
    squad: Optional[str] = None  # P5: sevens_m/sevens_w/u17..u23
    is_featured: bool = False
    is_minor: bool = False
    merged_from: list[str] = Field(default_factory=list)

    @field_validator("source_url")
    @classmethod
    def _url(cls, v: str) -> str:
        return _validate_source_url(v)

    @field_validator("league")
    @classmethod
    def _league(cls, v: str) -> str:
        if v not in LEAGUE_KEYS:
            raise ValueError(f"未定義のリーグキー: {v}")
        return v

    @field_validator("birthdate")
    @classmethod
    def _birthdate_fmt(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            raise ValueError(f"birthdate は YYYY-MM-DD: {v}")
        return v

    @model_validator(mode="after")
    def _rules(self) -> "Player":
        if not (self.name_en or self.name_ja):
            raise ValueError("name_en か name_ja のどちらかは必須")
        if self.league in TEAM_LEAGUES and not self.team_id:
            raise ValueError(f"リーグ所属選手は team_id 必須（league={self.league}）")
        return self

    @classmethod
    def parse(cls, raw: dict[str, Any]) -> tuple["Player", list[str]]:
        """raw dict を正規化してから検証。落とした値の warning を返す。"""
        data = dict(raw)
        warnings: list[str] = []
        pid = data.get("id", "?")

        for key, (lo, hi) in (("height_cm", HEIGHT_RANGE), ("weight_kg", WEIGHT_RANGE)):
            if key in data and data[key] is not None:
                try:
                    n = _to_int(data[key])
                except ValueError:
                    n = None
                if n is None or not (lo <= n <= hi):
                    warnings.append(f"{pid}: {key}={data[key]!r} を範囲外/変換不能のため null 化")
                    n = None
                data[key] = n

        if data.get("birthdate") is not None:
            d = _parse_date(data["birthdate"])
            if d is not None:
                year = int(d[:4])
                if not (BIRTHYEAR_RANGE[0] <= year <= BIRTHYEAR_RANGE[1]):
                    warnings.append(f"{pid}: birthdate={d} が範囲外のため null 化")
                    d = None
            elif data["birthdate"] is not None:
                warnings.append(f"{pid}: birthdate={data['birthdate']!r} をパース不能のため null 化")
            data["birthdate"] = d

        if data.get("league_caps") is not None:
            try:
                data["league_caps"] = _to_int(data["league_caps"])
            except ValueError:
                warnings.append(f"{pid}: league_caps={data['league_caps']!r} を変換不能のため null 化")
                data["league_caps"] = None

        return cls.model_validate(data), warnings


class Stadium(_StrictModel):
    name: str
    source_url: Optional[str] = None


class Team(_StrictModel):
    id: str = Field(min_length=1)
    league: str
    name_ja: Optional[str] = None
    name_en: Optional[str] = None
    source_url: str
    scraped_at: str
    home_area: Optional[str] = None
    home_stadiums: list[Stadium] = Field(default_factory=list)
    founded: Optional[int] = None
    colors: dict[str, str] = Field(default_factory=dict)
    official_url: Optional[str] = None
    roster_mode: Literal["full", "partial"] = "full"
    roster_ids: list[str] = Field(default_factory=list)

    @field_validator("source_url")
    @classmethod
    def _url(cls, v: str) -> str:
        return _validate_source_url(v)

    @field_validator("league")
    @classmethod
    def _league(cls, v: str) -> str:
        if v not in TEAM_LEAGUES:
            raise ValueError(f"Team のリーグキーが不正: {v}")
        return v

    @model_validator(mode="after")
    def _name(self) -> "Team":
        if not (self.name_ja or self.name_en):
            raise ValueError("name_ja か name_en のどちらかは必須")
        return self


class Match(_StrictModel):
    id: str = Field(min_length=1)
    league: str
    season: str
    round: Optional[int] = None
    kickoff_utc: Optional[str] = None
    home_team_id: str
    away_team_id: str
    home_score: Optional[int] = Field(default=None, ge=0)
    away_score: Optional[int] = Field(default=None, ge=0)
    status: Literal["scheduled", "finished", "postponed"]
    venue: Optional[str] = None
    venue_raw: Optional[str] = None  # JRFU 原文（02）
    source_url: str
    scraped_at: str

    @field_validator("source_url")
    @classmethod
    def _url(cls, v: str) -> str:
        return _validate_source_url(v)


class StandingRow(_StrictModel):
    rank: int = Field(ge=1)
    team_id: str
    played: int = Field(ge=0)
    won: int = Field(ge=0)
    drawn: int = Field(ge=0)
    lost: int = Field(ge=0)
    points: int
    bonus: Optional[int] = None


class Standing(_StrictModel):
    league: str
    season: str
    scraped_at: str
    source_url: str
    rows: list[StandingRow]

    @field_validator("source_url")
    @classmethod
    def _url(cls, v: str) -> str:
        return _validate_source_url(v)
