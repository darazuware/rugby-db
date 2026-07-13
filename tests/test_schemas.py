"""P1-1: サンプルPlayer 1件が検証を通る / 壊れた1件が落ちる。"""
import pytest
from pydantic import ValidationError

from pipeline.schemas import Player, Team, Match, Standing


GOOD_PLAYER = {
    "id": "lo_483678",
    "source": "league-one.jp",
    "source_url": "https://league-one.jp/player/483678",
    "scraped_at": "2026-07-07T09:00:00+09:00",
    "name_en": "Shinichi Tanaka",
    "name_ja": "田中 真一",
    "name_kana": None,
    "slug": "shinichi-tanaka-lo483678",
    "position": "FL",
    "team_id": "kyuden-voltex",
    "league": "league-one-d1",
    "height_cm": "186",  # 文字列→int 変換される
    "weight_kg": 98,
    "birthdate": "1994-06-08",
    "nationality": ["JP"],
    "caps": {"team": "Japan", "count": 12, "source_url": "https://all.rugby/x"},
    "league_caps": 9,
    "career": [{"team": "NEC", "from": 2017, "to": 2020, "source_url": "https://all.rugby/y"}],
    "education": [{"school_id": None, "name_raw": "明治大学", "type": "univ"}],
}


def test_good_player_passes():
    p, warnings = Player.parse(GOOD_PLAYER)
    assert p.id == "lo_483678"
    assert p.height_cm == 186  # 文字列が数値化
    assert warnings == []


def test_career_from_alias_roundtrips():
    p, _ = Player.parse(GOOD_PLAYER)
    dumped = p.model_dump(by_alias=True)
    assert dumped["career"][0]["from"] == 2017


def test_broken_player_missing_required_fails():
    broken = dict(GOOD_PLAYER)
    del broken["source_url"]
    with pytest.raises(ValidationError):
        Player.parse(broken)


def test_no_name_fails():
    broken = dict(GOOD_PLAYER, name_en=None, name_ja=None)
    with pytest.raises(ValidationError):
        Player.parse(broken)


def test_team_league_requires_team_id():
    broken = dict(GOOD_PLAYER, team_id=None)
    with pytest.raises(ValidationError):
        Player.parse(broken)


def test_national_allows_null_team_id():
    nat = dict(GOOD_PLAYER, id="ar_1", league="national", team_id=None,
               source="all.rugby", source_url="https://all.rugby/player/1")
    p, _ = Player.parse(nat)
    assert p.team_id is None


def test_disallowed_domain_fails():
    broken = dict(GOOD_PLAYER, source_url="https://evil.example.com/x")
    with pytest.raises(ValidationError):
        Player.parse(broken)


def test_out_of_range_height_nulled_with_warning():
    p, warnings = Player.parse(dict(GOOD_PLAYER, height_cm=300))
    assert p.height_cm is None
    assert any("height_cm" in w for w in warnings)


def test_unparseable_birthdate_nulled():
    p, warnings = Player.parse(dict(GOOD_PLAYER, birthdate="不明"))
    assert p.birthdate is None
    assert any("birthdate" in w for w in warnings)


def test_birthdate_slash_normalized():
    p, _ = Player.parse(dict(GOOD_PLAYER, birthdate="1994/06/08"))
    assert p.birthdate == "1994-06-08"


def test_unknown_league_fails():
    with pytest.raises(ValidationError):
        Player.parse(dict(GOOD_PLAYER, league="bundesliga"))


def test_extra_field_forbidden():
    with pytest.raises(ValidationError):
        Player.parse(dict(GOOD_PLAYER, made_up_field="x"))


def test_team_and_match_and_standing_parse():
    Team.model_validate({
        "id": "toulouse", "league": "top14",
        "name_en": "Toulouse", "source_url": "https://all.rugby/club/toulouse",
        "scraped_at": "2026-07-07T09:00:00+09:00",
    })
    Match.model_validate({
        "id": "top14_2025-26_r12_a-b", "league": "top14", "season": "2025-26",
        "home_team_id": "a", "away_team_id": "b", "status": "scheduled",
        "source_url": "https://all.rugby/x", "scraped_at": "2026-07-07T09:00:00+09:00",
    })
    Standing.model_validate({
        "league": "top14", "season": "2025-26", "scraped_at": "x",
        "source_url": "https://all.rugby/table",
        "rows": [{"rank": 1, "team_id": "a", "played": 3, "won": 2,
                  "drawn": 0, "lost": 1, "points": 10}],
    })
