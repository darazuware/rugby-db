"""P3-2: pipeline.run の --only matches,standings 軽量モードのテスト。

完了条件（05: 試合日の軽量ジョブ）:
  - --only matches,standings 指定時は players/teams の master 書き込みをスキップする
  - pending_departures は更新されない（同日2回実行で誤って「2回連続消失」確定しないため）
  - signings/departures/first_caps/caps_updates の diff は空のまま出力される
  - newly_finished_rounds の diff と matches/standings の master 書き込みは通常通り行われる
  - --only 未指定時は従来通り players/teams/matches/standings すべて書き込まれる

fixture のみで network は使わない（SCRAPERS をモックに差し替える）。
"""
from pipeline import io, run


def _player(pid, team_id="t1"):
    return dict(id=pid, source="test", source_url="https://example.test/x", scraped_at="x",
                name_en=f"Player {pid}", name_ja=None, slug=pid, league="top14",
                team_id=team_id, birthdate=None, name_kana=None, nationality=[], caps=None)


def _team(tid, roster_ids):
    return dict(id=tid, league="top14", name_en=tid,
                source_url="https://example.test/x", scraped_at="x",
                roster_mode="full", roster_ids=roster_ids)


def _match(mid, status="finished", round_=1):
    return dict(id=mid, league="top14", season="2025-26", round=round_,
                home_team_id="t1", away_team_id="t1", status=status,
                home_score=10 if status == "finished" else None,
                away_score=5 if status == "finished" else None,
                source_url="https://example.test/x", scraped_at="x")


def _standing():
    return {"league": "top14", "season": "2025-26", "rows": [
        {"rank": 1, "team_id": "t1", "played": 1, "won": 1, "drawn": 0, "lost": 0, "points": 5},
    ]}


def _setup(monkeypatch, tmp_path, *, prev_players):
    master_dir = tmp_path / "master"
    monkeypatch.setattr(io, "MASTER_DIR", master_dir)
    monkeypatch.setattr(io, "META_DIR", master_dir / "_meta")
    monkeypatch.setattr(io, "MANUAL_DIR", tmp_path / "manual")
    if prev_players is not None:
        io.write_records(io.players_path("top14"), prev_players)

    def fake_scraper():
        return {
            "players": [_player("a"), _player("b")],
            "teams": [_team("t1", ["a", "b"])],
            "matches": [_match("m1")],
            "standings": [_standing()],
            "warnings": [],
        }

    monkeypatch.setattr(run, "SCRAPERS", {"top14": fake_scraper})


def test_only_skips_player_writes_and_pending(monkeypatch, tmp_path):
    # 前回は選手 a のみ -> 今回 a,b。b は新規signingになるはずだが --only では検知しない。
    _setup(monkeypatch, tmp_path, prev_players=[_player("a")])

    rc = run.run_leagues(["top14"], dry_run=False, only={"matches", "standings"})
    assert rc == 0

    # players/teams は書き込まれない
    assert io.read_records(io.players_path("top14")) == [_player("a")]
    assert io.read_records(io.teams_path("top14")) == []
    # matches/standings は書き込まれる
    assert io.read_records(io.matches_path("top14", "2025-26")) == [_match("m1")]
    assert io.read_json(io.standings_path("top14", "2025-26")) == _standing()
    # pending_departures は触られない
    assert io.read_pending_departures() == {}
    # diff は player 系が空、rounds のみ入る
    import json
    diff_files = list((io.META_DIR / "diff").glob("*_top14.json"))
    assert len(diff_files) == 1
    diff = json.loads(diff_files[0].read_text())
    assert diff["signings"] == []
    assert diff["departures"] == []
    assert len(diff["newly_finished_rounds"]) == 1


def test_national_run_writes_callup_master_and_injects_diff(monkeypatch, tmp_path):
    """gap B: national 実行で招集イベントが callups master に永続化され、national diff に
    call_ups が注入されて news_gen が記事化できる（--only 時はスキップ、冪等）。"""
    import pathlib
    from pipeline.scrape import jrfu

    master_dir = tmp_path / "master"
    monkeypatch.setattr(io, "MASTER_DIR", master_dir)
    monkeypatch.setattr(io, "META_DIR", master_dir / "_meta")
    monkeypatch.setattr(io, "MANUAL_DIR", tmp_path / "manual")

    fx = pathlib.Path(__file__).parent / "fixtures" / "jrfu_news_callup.html"
    event = jrfu.parse_call_up_article(fx.read_text(encoding="utf-8"),
                                       "https://www.rugby-japan.jp/news/54087")
    callup_players, _ = jrfu.callup_members_to_players(event)
    for p in callup_players:
        p["team_id"] = "japan"

    def fake_national():
        return {"players": callup_players, "teams": [], "matches": [],
                "standings": [], "warnings": [], "call_ups": [event]}

    monkeypatch.setattr(run, "SCRAPERS", {"national": fake_national})

    rc = run.run_leagues(["national"], dry_run=False, only=None)
    assert rc == 0

    # callups master が書かれ、34名のイベントが1件記録される
    master = io.read_records(io.callups_path("national"))
    assert len(master) == 1
    assert master[0]["id"] == "callup_national_54087"
    assert len(master[0]["members"]) == 34

    # national diff に call_ups が注入され、新規イベントとして1件入る
    import json
    diff = json.loads(next((io.META_DIR / "diff").glob("*_national.json")).read_text())
    assert len(diff["call_ups"]) == 1
    assert diff["call_ups"][0]["news_id"] == "54087"

    # 2回目の実行は同一イベント＝新規なし（冪等）
    rc2 = run.run_leagues(["national"], dry_run=False, only=None)
    assert rc2 == 0
    diff2 = json.loads(next((io.META_DIR / "diff").glob("*_national.json")).read_text())
    assert diff2["call_ups"] == []
    assert len(io.read_records(io.callups_path("national"))) == 1  # 重複追加なし


def test_full_run_writes_players_and_pending(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path, prev_players=[_player("a")])

    rc = run.run_leagues(["top14"], dry_run=False, only=None)
    assert rc == 0

    players = io.read_records(io.players_path("top14"))
    assert [p["id"] for p in players] == ["a", "b"]
    assert io.read_records(io.teams_path("top14")) != []

    import json
    diff_files = list((io.META_DIR / "diff").glob("*_top14.json"))
    diff = json.loads(diff_files[0].read_text())
    assert [s["id"] for s in diff["signings"]] == ["b"]
