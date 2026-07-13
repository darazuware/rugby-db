"""P1-2: 各チェックに pass/fail の fixture。"""
from pipeline.validate import checks


def _player(pid, league="league-one-d1", team_id="t1", **kw):
    base = dict(id=pid, source="league-one.jp",
                source_url="https://league-one.jp/x", scraped_at="x",
                name_en="Foo Bar", slug=pid, league=league, team_id=team_id,
                birthdate=None, name_kana=None, nationality=[], caps=None)
    base.update(kw)
    return base


def _team(tid, league="league-one-d1", **kw):
    base = dict(id=tid, league=league, name_en=tid,
                source_url="https://league-one.jp/x", scraped_at="x",
                roster_mode="full", roster_ids=[])
    base.update(kw)
    return base


def test_dup_id():
    assert not checks.check_dup_id([_player("a"), _player("a")]).ok
    assert checks.check_dup_id([_player("a"), _player("b")]).ok


def test_dup_person():
    a = _player("a", name_en="John Smith", birthdate="1990-01-01")
    b = _player("b", name_en="John Smith", birthdate="1990-01-01")
    assert not checks.check_dup_person({"league-one-d1": [a, b]}).ok
    # birthdate 欠損はスキップ
    c = _player("c", name_en="John Smith", birthdate=None)
    d = _player("d", name_en="John Smith", birthdate=None)
    assert checks.check_dup_person({"league-one-d1": [c, d]}).ok


def test_cross_person_warns_and_candidates():
    lo = _player("lo_1", name_en="Kotaro Matsushima", birthdate="1993-02-26")
    ar = _player("ar_1", league="national", team_id=None,
                 source="all.rugby", source_url="https://all.rugby/x",
                 name_en="Kotaro  Matsushima", birthdate="1993-02-26")
    r = checks.check_cross_person({"league-one-d1": [lo], "national": [ar]})
    assert r.ok  # warning のみ
    assert r.warnings and r.merge_candidates
    # merges で解決済みなら除外
    r2 = checks.check_cross_person({"league-one-d1": [lo], "national": [ar]},
                                   player_merges={"ar_1": "lo_1"})
    assert not r2.warnings


def test_team_ref():
    p = _player("a", team_id="ghost")
    assert not checks.check_team_ref([p], [_team("t1")]).ok
    assert checks.check_team_ref([_player("a", team_id="t1")], [_team("t1")]).ok
    # national は対象外
    nat = _player("n", league="national", team_id=None)
    assert checks.check_team_ref([nat], []).ok


def test_roster_sym():
    p = _player("a", team_id="t1")
    good = checks.check_roster_sym([p], [_team("t1", roster_ids=["a"])])
    assert good.ok
    bad = checks.check_roster_sym([p], [_team("t1", roster_ids=["a", "b"])])
    assert not bad.ok
    # partial は免除
    part = checks.check_roster_sym([p], [_team("t1", roster_mode="partial", roster_ids=["a", "b"])])
    assert part.ok


def test_shrink():
    prev = [_player(str(i)) for i in range(10)]
    new = [_player(str(i)) for i in range(6)]  # 40%減
    assert not checks.check_shrink(new, prev, "league-one-d1").ok
    assert checks.check_shrink([_player(str(i)) for i in range(8)], prev, "x").ok


def test_caps_monotonic_maintains_prev():
    prev = [_player("a", caps={"team": "Japan", "count": 40})]
    new = [_player("a", caps={"team": "Japan", "count": 12})]
    r = checks.check_caps_monotonic(new, prev)
    assert r.warnings
    assert new[0]["caps"]["count"] == 40  # 前回値に戻る
    # corrections で免除
    new2 = [_player("a", caps={"team": "Japan", "count": 12})]
    r2 = checks.check_caps_monotonic(new2, prev, caps_corrections={"a": {"count": 12}})
    assert not r2.warnings
    assert new2[0]["caps"]["count"] == 12


def _match(mid="m1", status="finished", home_score=10, away_score=5):
    return dict(id=mid, league="top14", season="2025-26", home_team_id="a",
                away_team_id="b", status=status, home_score=home_score,
                away_score=away_score, source_url="https://all.rugby/x", scraped_at="x")


def test_match_sanity():
    assert checks.check_match_sanity([_match()]).ok
    assert not checks.check_match_sanity([_match(status="scheduled")]).ok  # 未実施にスコア
    assert not checks.check_match_sanity([_match(home_score=200)]).ok


def test_standings_sum():
    good = {"league": "top14", "season": "s", "rows": [
        {"rank": 1, "team_id": "a", "played": 3, "won": 2, "drawn": 0, "lost": 1, "points": 10}]}
    bad = {"league": "top14", "season": "s", "rows": [
        {"rank": 1, "team_id": "a", "played": 5, "won": 2, "drawn": 0, "lost": 1, "points": 10}]}
    assert checks.check_standings_sum([good]).ok
    assert not checks.check_standings_sum([bad]).ok


def test_kana_coverage():
    fr = _player("a", nationality=["FR"], name_kana=None)
    r = checks.check_kana_coverage([fr])
    assert r.ok and r.warnings  # warning のみ


def test_run_all_integration():
    p = _player("a", team_id="t1")
    t = _team("t1", roster_ids=["a"])
    r = checks.run_all({"league-one-d1": [p]}, [t], [_match()], [])
    assert r.ok
