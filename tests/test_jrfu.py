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


# ---------------------------------------------------------------------------
# P5-3: セブンズ/U代表スコッド
# ---------------------------------------------------------------------------

def _detail_raw(**over):
    raw = jrfu._parse_detail(
        _read("jrfu_member_detail.html"),
        "https://www.rugby-japan.jp/sevens/member/detail/481724")
    raw["detail_id"] = "481724"
    raw["squad"] = "sevens_m"
    raw.update(over)
    return raw


def test_parse_detail_extracts_profile_fields():
    raw = _detail_raw()
    assert raw["name_ja"] == "試験太郎"
    assert raw["name_en"] == "Taro SHIKEN"
    assert raw["position"] == "FW"
    assert raw["team_raw"] == "テストクラブ東京"
    assert raw["height_cm"] == "183" and raw["weight_kg"] == "84"
    assert raw["birthdate"] == "1999/01/22"
    assert raw["instagram"] == "https://www.instagram.com/test_taro/"
    # 出身校: 括弧（都道府県）除去済み。中学は残るが _classify_and_build で落とす
    assert raw["education_segments_raw"] == ["試験市立試験中学校", "試験学園高校", "試験大学"]


def test_classify_school_regex():
    assert jrfu._classify_school_regex("桐蔭学園高等学校") == "hs"
    assert jrfu._classify_school_regex("試験学園高校") == "hs"
    assert jrfu._classify_school_regex("学習院高等科") == "hs"
    assert jrfu._classify_school_regex("帝京大学") == "univ"
    assert jrfu._classify_school_regex("朝鮮大学校") == "univ"
    assert jrfu._classify_school_regex("静岡ブルーレヴズ") is None


def test_classify_and_build_offline(monkeypatch):
    # Sonnetフォールバック無効（APIキー無し想定）でも regex 判定分だけで組み立てる
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    players, warns = jrfu._classify_and_build([_detail_raw()], league="sevens-national")
    assert len(players) == 1
    p = players[0]
    assert p["id"] == "jrfu_sevens_m_481724"
    assert p["league"] == "sevens-national" and p["squad"] == "sevens_m"
    assert p["team_id"] is None  # NO_TEAM_LEAGUES
    assert p["birthdate"] == "1999-01-22"
    assert p["is_minor"] is False  # 1999年生まれ
    assert p["nationality"] == ["JP"]
    # 中学は education に入れない（10: hs/univ のみ）
    assert [(e["name_raw"], e["type"]) for e in p["education"]] == [
        ("試験学園高校", "hs"), ("試験大学", "univ")]
    assert all(e["source_url"] == p["source_url"] for e in p["education"])
    # 所属クラブ（学校でない）は career へ
    assert [c["team"] for c in p["career"]] == ["テストクラブ東京"]


def test_jrfu_is_minor_by_birthdate_and_league_default():
    assert normalize._jrfu_is_minor("2010/01/01", "age-grade") is True
    assert normalize._jrfu_is_minor("1999/01/22", "age-grade") is False
    # 生年月日欠落: age-grade は保守的に True、sevens は False（00原則5）
    assert normalize._jrfu_is_minor(None, "age-grade") is True
    assert normalize._jrfu_is_minor(None, "sevens-national") is False


def test_dup_person_allows_same_person_in_different_squads():
    from pipeline.validate import checks

    base = {"name_en": "Taro SHIKEN", "birthdate": "2008-04-01"}
    players = [
        {**base, "id": "jrfu_u18_1", "squad": "u18"},
        {**base, "id": "jrfu_u20_2", "squad": "u20"},
    ]
    r = checks.check_dup_person({"age-grade": players})
    assert r.errors == []
    # 同一squad内の重複は従来通りエラー
    dup = [{**base, "id": "a", "squad": "u18"}, {**base, "id": "b", "squad": "u18"}]
    assert checks.check_dup_person({"age-grade": dup}).errors


def test_sevens_and_age_grade_registered_in_run_scrapers():
    from pipeline import run

    for key in ("sevens-national", "age-grade"):
        assert key in run.SCRAPERS
        assert key in run.ALL_LEAGUES
