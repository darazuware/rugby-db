"""P1-3: league-one スクレイパーのパース + transform をオフラインHTMLで検証。"""
import pathlib

import pytest
from bs4 import BeautifulSoup

from pipeline.scrape import league_one
from pipeline.transform import normalize

FX = pathlib.Path(__file__).parent / "fixtures"


def _read(name):
    return (FX / name).read_text(encoding="utf-8")


def test_parse_player_page():
    raw = league_one.parse_player_page(_read("lo_player.html"), "451687")
    assert raw["name_en"] == "Ollie Stonham"
    assert "ストーンハム" in raw["name_ja"]
    assert raw["position"] == "FL"
    assert raw["height_cm"] == "193"
    assert raw["weight_kg"] == "106"
    assert raw["birthdate"] == "2001-02-16"
    assert raw["league_caps"] == "0"


def test_parse_team_page():
    name, pids = league_one.parse_team_page(_read("lo_team.html"), "71")
    assert name and "（" not in name  # シーズン括弧が除去されている
    assert len(pids) > 20
    assert all(p.isdigit() for p in pids)


def test_parse_standings():
    soup = BeautifulSoup(_read("lo_standings.html"), "html.parser")
    rows, teams = league_one.parse_standings(soup, 1)
    assert len(rows) == 12 and len(teams) == 12
    row0 = rows[0]
    assert row0["rank"] == "1"
    assert int(row0["played"]) == int(row0["won"]) + int(row0["drawn"]) + int(row0["lost"])


def test_transform_player_valid():
    raw = league_one.parse_player_page(_read("lo_player.html"), "451687")
    player, warns = normalize.player(raw, league="league-one-d1", team_id="lo_team_71")
    assert player is not None
    assert player["id"] == "lo_451687"
    assert player["league"] == "league-one-d1"
    assert player["team_id"] == "lo_team_71"
    assert player["height_cm"] == 193


def test_transform_standing_drops_bad_sum():
    rows = [
        {"team_id": "1", "rank": "1", "played": "10", "won": "5", "drawn": "0", "lost": "5", "points": "25"},
        {"team_id": "2", "rank": "2", "played": "10", "won": "9", "drawn": "0", "lost": "0", "points": "40"},
    ]
    st, warns = normalize.standing(rows, league="league-one-d1", season="2024-25")
    assert st is not None
    assert len(st["rows"]) == 1  # 2件目は played≠W+D+L で除外
    assert any("W+D+L" in w for w in warns)


def test_collect_light_skips_team_and_player_fetch(monkeypatch):
    """軽量モード（--only matches,standings）: 順位表ページ以外への GET を一切行わず
    standings のみ返す（players/teams は空）。team/player 個別ページ取得（本来
    数百リクエスト）を叩いたら即失敗させて検知する。"""
    monkeypatch.setattr(league_one, "_standings_soup", None)

    def fake_get(url):
        if url != league_one.STANDINGS_URL:
            pytest.fail(f"light モードで想定外のGET: {url}")
        return _read("lo_standings.html")

    monkeypatch.setattr(league_one, "_get", fake_get)
    monkeypatch.setattr(league_one.time, "sleep", lambda *_: None)

    result = league_one.collect("d1", light=True)
    assert result["players"] == []
    assert result["teams"] == []
    assert result["matches"] == []
    assert len(result["standings"]) == 1
    assert len(result["standings"][0]["rows"]) == 12
