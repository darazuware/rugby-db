"""P1-8: pipeline.diffs.detect のテスト（fixture のみ、network 不使用）。

完了条件（09_TASKS.md P1-8 / 02 / 05）:
  - 移籍（team_id変化）・新規加入・初キャップ・キャップ増分が検知される
  - 退団は1回目 pending に保留され、2回連続で消失が確認されたときのみ確定する
  - pending 中に再出現したら誤検知としてキャンセルされる
  - matches の finished 化が節単位でまとめられる
"""
from pipeline.diffs import detect


def _player(pid, team_id="t1", caps_count=None, **kw):
    base = dict(id=pid, name_en=f"Player {pid}", name_ja=None, team_id=team_id,
                caps=({"team": "Japan", "count": caps_count, "source_url": None}
                      if caps_count is not None else None))
    base.update(kw)
    return base


def _match(mid, status="scheduled", season="2026", round=1, league="top14"):
    return dict(id=mid, league=league, season=season, round=round, status=status)


def test_signing_new_id():
    prev = [_player("a")]
    new = [_player("a"), _player("b")]
    section, pending = detect.diff_players(new, prev)
    assert [s["id"] for s in section["signings"]] == ["b"]
    assert section["transfers"] == []
    assert pending == {}


def test_transfer_on_team_change():
    prev = [_player("a", team_id="t1")]
    new = [_player("a", team_id="t2")]
    section, _ = detect.diff_players(new, prev)
    assert section["transfers"] == [
        {"id": "a", "name_en": "Player a", "name_ja": None,
         "from_team_id": "t1", "to_team_id": "t2"}
    ]


def test_no_transfer_when_new_team_is_null():
    prev = [_player("a", team_id="t1")]
    new = [_player("a", team_id=None)]
    section, _ = detect.diff_players(new, prev)
    assert section["transfers"] == []


def test_first_cap_detected():
    prev = [_player("a", caps_count=0)]
    new = [_player("a", caps_count=1)]
    section, _ = detect.diff_players(new, prev)
    assert [c["id"] for c in section["first_caps"]] == ["a"]
    assert section["caps_updates"] == []


def test_first_cap_from_null_caps():
    prev = [_player("a")]  # caps=None
    new = [_player("a", caps_count=1)]
    section, _ = detect.diff_players(new, prev)
    assert [c["id"] for c in section["first_caps"]] == ["a"]


def test_caps_increase_not_first_is_caps_update():
    prev = [_player("a", caps_count=5)]
    new = [_player("a", caps_count=7)]
    section, _ = detect.diff_players(new, prev)
    assert section["first_caps"] == []
    assert section["caps_updates"] == [
        {"id": "a", "name_en": "Player a", "name_ja": None,
         "team": "Japan", "from_count": 5, "to_count": 7}
    ]


def test_caps_decrease_is_ignored():
    # checks.check_caps_monotonic が既に前回値へ書き戻す前提なので、万一減少が来ても無視する
    prev = [_player("a", caps_count=10)]
    new = [_player("a", caps_count=3)]
    section, _ = detect.diff_players(new, prev)
    assert section["first_caps"] == []
    assert section["caps_updates"] == []


def test_departure_needs_two_consecutive_misses():
    prev = [_player("a")]
    new: list[dict] = []

    # 1回目: 消失 → pending に保留、まだ確定しない
    section1, pending1 = detect.diff_players(new, prev, pending={})
    assert section1["departures"] == []
    assert list(pending1.keys()) == ["a"]
    assert section1["pending_departures"][0]["id"] == "a"

    # 2回目: 引き続き消失 → 確定し、pending から消える
    section2, pending2 = detect.diff_players(new, prev, pending=pending1)
    assert [d["id"] for d in section2["departures"]] == ["a"]
    assert pending2 == {}


def test_departure_cancelled_on_reappearance():
    prev = [_player("a")]
    _, pending1 = detect.diff_players([], prev, pending={})
    assert "a" in pending1

    # 再出現 → pending から除去され、退団確定しない
    section2, pending2 = detect.diff_players([_player("a")], prev, pending=pending1)
    assert section2["departures"] == []
    assert pending2 == {}


def test_diff_matches_groups_newly_finished_by_round():
    prev = [_match("m1", status="scheduled"), _match("m2", status="finished")]
    new = [_match("m1", status="finished", round=3), _match("m2", status="finished")]
    rounds = detect.diff_matches(new, prev)
    # m2 は既に finished だったので対象外。m1 のみ新規finished。
    assert rounds == [{"season": "2026", "round": 3, "match_ids": ["m1"]}]


def test_build_league_diff_filters_matches_by_league():
    prev_players = [_player("a")]
    new_players = [_player("a")]
    new_matches = [_match("m1", status="finished", league="top14"),
                   _match("m2", status="finished", league="super-rugby")]
    diff, _ = detect.build_league_diff(
        "top14", new_players, prev_players, {},
        new_matches=new_matches, prev_matches=[],
    )
    assert diff["league"] == "top14"
    assert [r["match_ids"] for r in diff["newly_finished_rounds"]] == [["m1"]]


def test_run_all_covers_multiple_leagues_and_persists_pending():
    players_by_league = {"top14": [], "league-one-d1": [_player("b")]}
    prev_players_by_league = {"top14": [_player("a")], "league-one-d1": [_player("b")]}
    diffs_by_league, updated_pending = detect.run_all(
        players_by_league, prev_players_by_league, pending_departures={},
    )
    # top14: a が1回目の消失 → pending に入るが departures はまだ0
    assert diffs_by_league["top14"]["departures"] == []
    assert "a" in updated_pending["top14"]
    assert updated_pending["league-one-d1"] == {}
