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
    assert not checks.check_dup_id({"league-one-d1": [_player("a"), _player("a")]}).ok
    assert checks.check_dup_id({"league-one-d1": [_player("a"), _player("b")]}).ok
    # リーグ横断の同一id（代表とクラブ両方掛け持ち等）はエラーにしない
    assert checks.check_dup_id({
        "league-one-d1": [_player("a", league="league-one-d1")],
        "national": [_player("a", league="national", team_id=None)],
    }).ok


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


def test_dedupe_league_ids_merges_same_person():
    """同一リーグ内の同一 id 二重掲載（移籍直後に旧新クラブ両方の squad 等）は畳む。"""
    a = _player("ar_x", league="top14", team_id="paris", name_en="Foo Bar", birthdate=None)
    b = _player("ar_x", league="top14", team_id="toulon", name_en="Foo Bar", birthdate="1995-01-01")
    out, dropped, warns = checks.dedupe_league_ids([a, b, _player("ar_y", league="top14")], "top14")
    assert [p["id"] for p in out] == ["ar_x", "ar_y"]
    assert out[0]["team_id"] == "paris" and out[0]["birthdate"] == "1995-01-01"
    assert dropped == [b] and len(warns) == 1
    assert checks.check_dup_id({"top14": out}).ok


def test_dedupe_league_ids_keeps_collision_for_dup_id_error():
    """name_en/birthdate が食い違う同一 id（ID衝突疑い）は畳まず check_dup_id で止める。"""
    a = _player("ar_x", league="top14", name_en="Foo Bar", birthdate="1990-01-01")
    b = _player("ar_x", league="top14", name_en="Baz Qux", birthdate="1990-01-01")
    out, dropped, _ = checks.dedupe_league_ids([a, b], "top14")
    assert len(out) == 2 and not dropped
    assert not checks.check_dup_id({"top14": out}).ok


def test_cross_league_id_same_person_is_ok():
    """代表×クラブ・クラブ間掛け持ちの同一 id はエラーにも警告にもしない。"""
    pbl = {
        "national": [_player("ar_x", league="national", team_id="japan", birthdate="1999-04-15")],
        "super-rugby": [_player("ar_x", league="super-rugby", birthdate=None)],
        "urc": [_player("ar_x", league="urc")],
    }
    assert checks.check_dup_id(pbl).ok
    r = checks.check_cross_league_id(pbl)
    assert r.ok and not r.warnings
    pbl["urc"] = [_player("ar_x", league="urc", name_en="Other Person")]
    r = checks.check_cross_league_id(pbl)
    assert r.ok and len(r.warnings) == 1


def test_drop_roster_ids_after_dedupe():
    from pipeline import run
    a = _player("ar_x", league="top14", team_id="paris")
    b = _player("ar_x", league="top14", team_id="toulon")
    out, dropped, _ = checks.dedupe_league_ids([a, b], "top14")
    teams = [_team("paris", roster_ids=["ar_x"]), _team("toulon", roster_ids=["ar_x"])]
    run._drop_roster_ids(teams, out, dropped)
    assert teams[0]["roster_ids"] == ["ar_x"] and teams[1]["roster_ids"] == []
    assert checks.check_roster_sym(out, teams).ok
