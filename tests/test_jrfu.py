"""P1-7: JRFU（rugby-japan.jp）日程スクレイパー + all.rugby 代表(national) enrich を
オフラインの生JSON/HTMLフラグメントで検証（ネットワークアクセスなし）。"""
import pathlib

from pipeline.scrape import all_rugby, jrfu
from pipeline.transform import normalize

FX = pathlib.Path(__file__).parent / "fixtures"


def _read(name):
    return (FX / name).read_text(encoding="utf-8")


# game.php game_list[0] 相当（実レスポンスから必要フィールドのみ抜粋、2026-07-18確認）
FINISHED_GAME = {
    "game_status": 2,
    "home_team_points": 27,
    "away_team_points": 10,
    "start_time_plan": 1783154400,
    "stadium": {"name": "秩父宮ラグビー場"},
}
SCHEDULED_GAME = {
    "game_status": 0,
    "home_team_points": None,
    "away_team_points": None,
    "start_time_plan": 1784364000,
    "stadium": {"name": "国立競技場"},
}


def test_match_jrfu_finished():
    match, warns = normalize.match_jrfu(
        FINISHED_GAME, home_slug="japan", away_slug="italy", game_id=29966)
    assert match is not None
    assert match["id"] == "jrfu_29966"
    assert match["league"] == "national"
    assert match["status"] == "finished"
    assert match["home_score"] == 27 and match["away_score"] == 10
    assert match["venue_raw"] == "秩父宮ラグビー場"
    assert match["venue"] is None  # 正規化しない（02）
    assert match["source_url"] == "https://www.rugby-japan.jp/match/29966"
    assert warns == []


def test_match_jrfu_scheduled_has_no_score():
    match, warns = normalize.match_jrfu(
        SCHEDULED_GAME, home_slug="japan", away_slug="france", game_id=29967)
    assert match is not None
    assert match["status"] == "scheduled"
    assert match["home_score"] is None and match["away_score"] is None


def test_match_jrfu_unknown_status_falls_back_to_scheduled_with_warning():
    g = dict(SCHEDULED_GAME, game_status=9)
    match, warns = normalize.match_jrfu(g, home_slug="japan", away_slug="france", game_id=1)
    assert match is not None
    assert match["status"] == "scheduled"
    assert any("game_status" in w for w in warns)


def test_process_entry_opponent_is_away_when_home_is_japan():
    entry = {"id": 29966, "home": "日本代表", "away": "イタリア代表"}
    match, opponent, warns = jrfu.process_entry(entry, FINISHED_GAME)
    assert match is not None
    assert opponent == "italy"
    assert match["home_team_id"] == "japan" and match["away_team_id"] == "italy"


def test_process_entry_excludes_non_country_opponent():
    entry = {"id": 29964, "home": "JAPAN XV", "away": "マオリ・オールブラックス"}
    match, opponent, warns = jrfu.process_entry(entry, FINISHED_GAME)
    assert match is not None  # 試合レコード自体は保持する
    assert opponent is None  # だが「対戦国」としては扱わない


def test_process_entry_unknown_team_name_skips_with_warning():
    entry = {"id": 99999, "home": "日本代表", "away": "謎の代表"}
    match, opponent, warns = jrfu.process_entry(entry, FINISHED_GAME)
    assert match is None and opponent is None
    assert any("未登録チーム表記" in w for w in warns)


def test_parse_player_caps_matches_team_summary_row():
    caps = all_rugby.parse_player_caps(_read("ar_player_caps.html"), "Canada")
    assert caps == 21


def test_parse_player_caps_unknown_country_is_none():
    assert all_rugby.parse_player_caps(_read("ar_player_caps.html"), "France") is None


def test_player_allrugby_carries_caps_through():
    raw = {"slug": "cali-martinez", "name_en": "Cali MARTINEZ", "position": "Prop",
           "height_raw": "1.71 m", "weight_raw": "112 kg",
           "caps": {"team": "Canada", "count": 21, "source_url": "https://all.rugby/player/cali-martinez"}}
    player, warns = normalize.player_allrugby(raw, league="national", team_id="canada")
    assert player is not None
    assert player["caps"] == {"team": "Canada", "count": 21,
                               "source_url": "https://all.rugby/player/cali-martinez"}
    assert player["league"] == "national" and player["team_id"] == "canada"


def test_national_registered_in_run_scrapers():
    from pipeline import run

    assert "national" in run.SCRAPERS
    assert "national" in run.ALL_LEAGUES
