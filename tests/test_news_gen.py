"""P3-1: pipeline.news_gen のテスト（fixture差分 → 期待md生成、network/実ファイル不使用）。

完了条件（09_TASKS.md P3-1 / 05）:
  - signings / transfers(team_id変化) が「{選手名}が{チーム名}に加入」記事になる
  - departures が「{選手名}が{チーム名}を退団」記事になる
  - first_caps が「{選手名}が{国}代表初キャップ」記事になる
  - caps_updates は1件ずつ記事化されず、週次まとめ1本にマージされる
  - newly_finished_rounds がスコア表のみの節結果記事になる
  - 選手名/チーム名/代表国名など穴埋めに必要な値が欠けている場合は記事を作らない
"""
from datetime import date

from pipeline import news_gen as ng


def _diff(league="top14", **overrides):
    base = {
        "league": league,
        "signings": [],
        "transfers": [],
        "departures": [],
        "first_caps": [],
        "caps_updates": [],
        "pending_departures": [],
        "newly_finished_rounds": [],
    }
    base.update(overrides)
    return base


TEAMS = {
    "t1": {"id": "t1", "name_ja": "スタッド・トゥールーザン", "name_en": "Stade Toulousain"},
    "t2": {"id": "t2", "name_ja": "ASM クレルモン", "name_en": "ASM Clermont"},
    "t3": {"id": "t3", "name_ja": None, "name_en": None},
}

PLAYERS = {
    "ar_1": {"id": "ar_1", "slug": "taro-yamada", "name_ja": "山田太郎", "name_en": "Taro Yamada"},
}


# ---------------------------------------------------------------------------
# 加入（signings / transfers）
# ---------------------------------------------------------------------------

def test_join_article_from_signing():
    diff = _diff(signings=[
        {"id": "ar_1", "name_en": "Taro Yamada", "name_ja": "山田太郎", "team_id": "t1"},
    ])
    articles = ng.build_join_articles(diff, players_by_id=PLAYERS, teams_by_id=TEAMS,
                                      pub_date="2026-07-18", source_diff="2026-07-18_top14.json")
    assert len(articles) == 1
    a = articles[0]
    assert a.title == "山田太郎がスタッド・トゥールーザンに加入"
    assert a.body == "[山田太郎](/players/taro-yamada/)がスタッド・トゥールーザン（Top14）に加入した。"
    assert a.slug == "top14-join-ar_1-2026-07-18"
    assert a.tags == ["Top14", "加入"]
    assert a.category == "auto"


def test_join_article_from_transfer_uses_to_team():
    diff = _diff(transfers=[
        {"id": "ar_1", "name_en": "Taro Yamada", "name_ja": "山田太郎",
         "from_team_id": "t2", "to_team_id": "t1"},
    ])
    articles = ng.build_join_articles(diff, players_by_id=PLAYERS, teams_by_id=TEAMS,
                                      pub_date="2026-07-18", source_diff="x.json")
    assert len(articles) == 1
    assert articles[0].title == "山田太郎がスタッド・トゥールーザンに加入"


def test_join_article_skipped_when_team_name_unknown():
    diff = _diff(signings=[
        {"id": "ar_1", "name_en": "Taro Yamada", "name_ja": "山田太郎", "team_id": "t3"},
    ])
    articles = ng.build_join_articles(diff, players_by_id=PLAYERS, teams_by_id=TEAMS,
                                      pub_date="2026-07-18", source_diff="x.json")
    assert articles == []


def test_join_article_skipped_when_name_unknown():
    diff = _diff(signings=[{"id": "ar_9", "name_en": None, "name_ja": None, "team_id": "t1"}])
    articles = ng.build_join_articles(diff, players_by_id=PLAYERS, teams_by_id=TEAMS,
                                      pub_date="2026-07-18", source_diff="x.json")
    assert articles == []


def test_join_article_plain_name_when_no_slug():
    diff = _diff(signings=[
        {"id": "ar_99", "name_en": "New Guy", "name_ja": None, "team_id": "t1"},
    ])
    articles = ng.build_join_articles(diff, players_by_id=PLAYERS, teams_by_id=TEAMS,
                                      pub_date="2026-07-18", source_diff="x.json")
    assert articles[0].body == "New Guyがスタッド・トゥールーザン（Top14）に加入した。"


# ---------------------------------------------------------------------------
# 退団
# ---------------------------------------------------------------------------

def test_departure_article():
    diff = _diff(departures=[
        {"id": "ar_1", "name_en": "Taro Yamada", "name_ja": "山田太郎", "team_id": "t2"},
    ])
    # 退団済みなので現masterに存在しない想定（players_by_id に無い）
    articles = ng.build_departure_articles(diff, players_by_id={}, teams_by_id=TEAMS,
                                           pub_date="2026-07-18", source_diff="x.json")
    assert len(articles) == 1
    a = articles[0]
    assert a.title == "山田太郎がASM クレルモンを退団"
    assert a.body == "山田太郎がASM クレルモン（Top14）を退団した。"
    assert a.tags == ["Top14", "退団"]


def test_departure_article_skipped_when_team_unknown():
    diff = _diff(departures=[
        {"id": "ar_1", "name_en": "Taro Yamada", "name_ja": "山田太郎", "team_id": None},
    ])
    articles = ng.build_departure_articles(diff, players_by_id={}, teams_by_id=TEAMS,
                                           pub_date="2026-07-18", source_diff="x.json")
    assert articles == []


# ---------------------------------------------------------------------------
# 初キャップ
# ---------------------------------------------------------------------------

def test_first_cap_article():
    diff = _diff(league="national", first_caps=[
        {"id": "ar_1", "name_en": "Taro Yamada", "name_ja": "山田太郎", "team": "日本", "count": 1},
    ])
    articles = ng.build_first_cap_articles(diff, players_by_id=PLAYERS,
                                           pub_date="2026-07-18", source_diff="x.json")
    assert len(articles) == 1
    a = articles[0]
    assert a.title == "山田太郎が日本代表初キャップ"
    assert a.body == "[山田太郎](/players/taro-yamada/)が日本代表で初キャップを記録した。"
    assert a.slug == "national-first-cap-ar_1-2026-07-18"


# ---------------------------------------------------------------------------
# キャップ更新（週次まとめ）
# ---------------------------------------------------------------------------

def test_merge_caps_updates_keeps_first_from_and_max_to():
    existing = [{"id": "ar_1", "name_ja": "山田太郎", "team": "日本", "from_count": 10, "to_count": 12}]
    new = [{"id": "ar_1", "name_ja": "山田太郎", "team": "日本", "from_count": 12, "to_count": 15}]
    merged = ng.merge_caps_updates(existing, new)
    assert len(merged) == 1
    assert merged[0]["from_count"] == 10
    assert merged[0]["to_count"] == 15
    assert merged[0]["team"] == "日本"


def test_merge_caps_updates_adds_new_id():
    existing = [{"id": "ar_1", "name_ja": "A", "team": "日本", "from_count": 1, "to_count": 2}]
    new = [{"id": "ar_2", "name_ja": "B", "team": "日本", "from_count": 3, "to_count": 4}]
    merged = ng.merge_caps_updates(existing, new)
    assert [m["id"] for m in merged] == ["ar_1", "ar_2"]


def test_build_caps_weekly_article():
    entries = [
        {"id": "ar_1", "name_ja": "山田太郎", "name_en": "Taro Yamada", "team": "日本",
         "from_count": 10, "to_count": 12},
    ]
    a = ng.build_caps_weekly_article("national", "2026-W29", entries, players_by_id=PLAYERS,
                                     pub_date="2026-07-18", source_diff="x.json")
    assert a is not None
    assert a.title == "代表週間代表キャップ更新まとめ（2026-W29）"
    assert a.body == "- [山田太郎](/players/taro-yamada/): 日本代表10→12キャップ"
    assert a.slug == "national-caps-weekly-2026-W29"


def test_build_caps_weekly_article_none_when_empty():
    assert ng.build_caps_weekly_article("national", "2026-W29", [], players_by_id={},
                                        pub_date="2026-07-18", source_diff="x.json") is None


def test_iso_week_str():
    assert ng.iso_week_str(date(2026, 7, 18)) == "2026-W29"


# ---------------------------------------------------------------------------
# 節の結果
# ---------------------------------------------------------------------------

MATCHES = {
    "m1": {"id": "m1", "home_team_id": "t1", "away_team_id": "t2",
           "home_score": 24, "away_score": 17},
    "m2": {"id": "m2", "home_team_id": "t2", "away_team_id": "t3",
           "home_score": 10, "away_score": 20},  # t3 のチーム名が無いので除外される
}


def test_round_result_article():
    diff = _diff(newly_finished_rounds=[{"season": "2025-26", "round": 5, "match_ids": ["m1", "m2"]}])
    articles = ng.build_round_result_articles(diff, matches_by_id=MATCHES, teams_by_id=TEAMS,
                                               pub_date="2026-07-18", source_diff="x.json")
    assert len(articles) == 1
    a = articles[0]
    assert a.title == "Top14第5節 結果まとめ"
    assert "| スタッド・トゥールーザン | 24 - 17 | ASM クレルモン |" in a.body
    assert "t3" not in a.body  # チーム名不明の試合は除外
    assert a.slug == "top14-round-5-2025-26"


def test_round_result_article_skipped_when_round_missing():
    diff = _diff(newly_finished_rounds=[{"season": "2025-26", "round": None, "match_ids": ["m1"]}])
    articles = ng.build_round_result_articles(diff, matches_by_id=MATCHES, teams_by_id=TEAMS,
                                               pub_date="2026-07-18", source_diff="x.json")
    assert articles == []


# ---------------------------------------------------------------------------
# Article.to_markdown / write_articles
# ---------------------------------------------------------------------------

def test_article_to_markdown_matches_expected():
    a = ng.Article(slug="top14-join-ar_1-2026-07-18", title="山田太郎がスタッド・トゥールーザンに加入",
                   body="[山田太郎](/players/taro-yamada/)がスタッド・トゥールーザン（Top14）に加入した。",
                   tags=["Top14", "加入"], pub_date="2026-07-18",
                   source_diff="2026-07-18_top14.json")
    expected = (
        "---\n"
        'title: "山田太郎がスタッド・トゥールーザンに加入"\n'
        "pubDate: 2026-07-18\n"
        'category: "auto"\n'
        'tags: ["Top14", "加入"]\n'
        'source_diff: "2026-07-18_top14.json"\n'
        "draft: false\n"
        "---\n"
        "\n"
        "[山田太郎](/players/taro-yamada/)がスタッド・トゥールーザン（Top14）に加入した。\n"
    )
    assert a.to_markdown() == expected


def test_write_articles(tmp_path):
    a = ng.Article(slug="foo", title="タイトル", body="本文。", tags=["Top14"],
                   pub_date="2026-07-18", source_diff="x.json")
    paths = ng.write_articles([a], out_dir=tmp_path)
    assert len(paths) == 1
    assert paths[0].name == "foo.md"
    assert paths[0].read_text(encoding="utf-8") == a.to_markdown()


# ---------------------------------------------------------------------------
# build_articles_for_diff（統合: 1つの diff から複数種の記事がまとめて作られる）
# ---------------------------------------------------------------------------

def test_build_articles_for_diff_integration():
    diff = _diff(
        signings=[{"id": "ar_1", "name_en": "Taro Yamada", "name_ja": "山田太郎", "team_id": "t1"}],
        departures=[{"id": "ar_2", "name_en": "Old Player", "name_ja": None, "team_id": "t2"}],
        newly_finished_rounds=[{"season": "2025-26", "round": 5, "match_ids": ["m1"]}],
    )
    articles = ng.build_articles_for_diff(
        diff, players_by_id=PLAYERS, teams_by_id=TEAMS, matches_by_id=MATCHES,
        pub_date="2026-07-18", source_diff="2026-07-18_top14.json",
    )
    slugs = {a.slug for a in articles}
    assert slugs == {
        "top14-join-ar_1-2026-07-18",
        "top14-departure-ar_2-2026-07-18",
        "top14-round-5-2025-26",
    }
