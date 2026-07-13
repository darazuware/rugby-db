"""P1-4: レガシー移行の純関数（日付正規化・教育配列・キャリア解析・名寄せ・レコード生成）。"""
from pipeline import migrate_legacy as m
from pipeline.schemas import Player


def test_norm_bd():
    assert m._norm_bd("1994.06.08") == "1994-06-08"
    assert m._norm_bd("2003年07月25日") == "2003-07-25"
    assert m._norm_bd("1994-5-22") == "1994-05-22"
    assert m._norm_bd("//2007") is None  # 年月日が揃わない → 捏造しない
    assert m._norm_bd("") is None
    assert m._norm_bd("1994.13.40") is None  # 月日が範囲外


def test_education_filters_nullish():
    edu = m._education({"high_school": "國學院久我山高校", "university": "nan"})
    assert len(edu) == 1
    assert edu[0] == {"school_id": None, "name_raw": "國學院久我山高校", "type": "hs",
                      "grad_year": None, "source_url": None, "scraped_at": None}
    assert m._education({"high_school": "", "university": "なし"}) == []


def test_career_parse():
    out = m._career(["Stade Toulousain (2009 - 2023)", "Blagnac (2023 - 2023)", "現役 ()"])
    assert out[0] == {"team": "Stade Toulousain", "from": 2009, "to": 2023}
    assert out[1]["to"] == 2023
    assert out[2]["team"] == "現役 ()" and out[2]["from"] is None


def test_season_helpers():
    assert m._season_of("九州電力キューデンヴォルテクス（2025-26）") == "2025-26"
    assert m._strip_season("九州電力キューデンヴォルテクス（2025-26）") == "九州電力キューデンヴォルテクス"
    assert m._season_stats({"matches_played": 5, "tries": 0, "points": 0}, None) is None  # season不明→捏造しない
    assert m._season_stats({"matches_played": 5, "tries": 1, "points": 5}, "2025-26")["matches"] == 5


def test_match_keys():
    keys = m._match_keys("Futoshi Mori", "森 太志", "1988-04-25")
    assert "en|futoshi mori|1988-04-25" in keys
    assert "ja|森太志|1988-04-25" in keys


def test_build_player_passes_schema():
    raw = {
        "id": "lo_483678", "name_en": "Shinichi Tanaka", "name_ja": "田中 真一",
        "position": "FL", "team": "九州電力キューデンヴォルテクス（2025-26）",
        "height": "186", "weight": "98", "birthdate": "1994.06.08",
        "high_school": "國學院久我山高校", "university": "明治大学",
        "league_one_caps": 9, "career_history": [],
        "all_rugby_stats": {"matches_played": 5, "tries": 0, "points": 0},
    }
    tally = m.NullTally()
    rec, warns = m._build_player(raw, league="league-one-d2", team_id="lo_team_107",
                                 pid="lo_483678", source="league-one.jp",
                                 source_url="https://league-one.jp/player/483678", tally=tally)
    assert rec is not None
    assert rec["slug"] == "shinichi-tanaka-483678"
    assert rec["height_cm"] == 186 and rec["birthdate"] == "1994-06-08"
    assert len(rec["education"]) == 2
    assert rec["season_stats"]["season"] == "2025-26"
    # 再検証（by_alias dump が Player を通る）
    Player.parse(rec)


def test_build_player_bad_birthdate_nulled():
    raw = {"id": "lo_1", "name_en": "Test Player", "team": "x（2025-26）",
           "birthdate": "不明", "career_history": []}
    tally = m.NullTally()
    rec, _ = m._build_player(raw, league="league-one-d1", team_id="lo_team_1",
                             pid="lo_1", source="league-one.jp",
                             source_url="https://league-one.jp/player/1", tally=tally)
    assert rec is not None and rec["birthdate"] is None
    assert tally.dropped["birthdate"] == 1
