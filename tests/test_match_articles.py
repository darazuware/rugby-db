"""日本代表戦プレビュー/レビュー自動生成（pipeline/match_articles.py）をオフラインで検証。"""
from datetime import date, datetime, timezone

from pipeline import match_articles as ma

KO = int(datetime(2026, 10, 24, 5, 50, tzinfo=timezone.utc).timestamp())  # 14:50 JST


def _team(name, eng):
    return {"name": name, "name_eng": eng}


def _entry(n, last, first, eng, *, cap=False, team="X", college="Y", reserved=None, cap_num="3"):
    return {"shirt_number": str(n), "captain": cap, "unentried": 0,
            "player": {"last_name": last, "first_name": first, "english_name": eng + " ",
                       "in_team": team, "descent_college": college, "height": "180", "weight": "100",
                       "cap_num": cap_num}}


def _side(prefix, names):
    return [_entry(i + 1, f"{prefix}{i + 1}", "", f"{prefix} P{i + 1}", cap=(i == 4)) for i in range(23)]


def _game(**over):
    g = {
        "game_id": 1, "game_status": 0, "start_time_plan": KO,
        "games": {"name": "リポビタンDチャレンジカップ2026"},
        "stadium": {"name": "秩父宮ラグビー場"},
        "home_team2": _team("日本代表 （別府合宿参加メンバー）", "Japan"),
        "away_team2": _team("フィジー代表（LDCC2026）", "Fiji"),
        "referee": "ニカ・アマシュケリ（ジョージア協会）", "weather": "雨", "pitch": "良い",
        "broadcast_text": "日本テレビ系全国ネット,https://a\r\n／\r\nJ SPORTS 1,https://b",
        "info": {"home_entry_list": _side("J", None), "away_entry_list": _side("F", None)},
    }
    g.update(over)
    return g


ENTRY = {"competition_title": "リポビタンDチャレンジカップ2026", "link": "/braveblossoms/match/20261024/", "id": 1,
         "home": "日本代表", "away": "フィジー代表"}


def test_clean_team_name_and_sides():
    assert ma._clean_team_name("日本代表 （別府合宿参加メンバー）") == "日本代表"
    assert ma._clean_team_name("フィジー代表（LDCC2026）") == "フィジー代表"
    jp, opp, side = ma.sides(_game())
    assert side == "home" and "フィジー" in opp["name"]
    g = _game(home_team2=_team("ウェールズ代表", "Wales"), away_team2=_team("日本代表", "Japan"))
    assert ma.sides(g)[2] == "away"


def test_broadcast_lines():
    assert ma.broadcast_lines(_game()["broadcast_text"]) == ["日本テレビ系全国ネット", "J SPORTS 1"]


def test_target_entries_window():
    idx = [dict(ENTRY), {**ENTRY, "link": "/x/20260101/"}, {**ENTRY, "home": "JAPAN XV", "away": "X"}]
    got = ma.target_entries(idx, date(2026, 10, 22))
    assert len(got) == 1 and got[0]["link"].endswith("20261024/")
    assert ma.target_entries(idx, date(2026, 11, 20)) == []


def test_parse_roster_table_captain_and_caps():
    html = ("<table><tr><td>番号</td><td>名前</td><td>所属</td><td>出身</td><td>身長</td><td>体重</td><td>生年</td><td>キャップ</td></tr>"
            "<tr><td>5</td><td><p>ワーナー・ディアンズ ◎</p><p>Warner DEARNS</p></td><td><p>東芝</p><p>T</p></td>"
            "<td><p>流経大柏高校</p><p>R</p></td><td>201</td><td>117</td><td>2002/4/11</td><td>37</td></tr>"
            "<tr><td>6</td><td><p>ハ ミ</p><p>Hami X</p></td><td><p>A</p></td><td><p>ボーイズ高校[NZ]</p></td><td>1</td><td>2</td><td>d</td><td>0</td></tr></table>")
    r = ma.parse_roster_table(html)
    assert r["WARNER DEARNS"]["captain"] and r["WARNER DEARNS"]["caps"] == 37
    assert r["WARNER DEARNS"]["name"] == "ワーナー・ディアンズ"
    assert r["HAMI X"]["school"] == "ボーイズ高校" and r["HAMI X"]["caps"] == 0


def test_lineup_ready_requires_23_each():
    assert ma.lineup_ready(_game())
    g = _game()
    g["info"]["away_entry_list"] = g["info"]["away_entry_list"][:10]
    assert not ma.lineup_ready(g)


def test_build_preview_content_and_slug():
    art = ma.build_preview(_game(), ENTRY, roster={}, prev_game=None, links={"日本代表": "/national-teams/japan/"})
    assert art.filename() == "japan-vs-fiji-2026-10-24-preview.md"
    assert not art.draft
    for s in ("14:50キックオフ", "秩父宮ラグビー場", "日本テレビ系全国ネット／J SPORTS 1", "ニカ・アマシュケリ", "[日本代表](/national-teams/japan/)"):
        assert s in art.body
    assert "キャップ数は協会の登録メンバー発表の確認が取れ次第" in art.body  # roster 取得失敗時の注記


def test_build_preview_none_before_lineup():
    g = _game()
    g["info"]["home_entry_list"] = []
    assert ma.build_preview(g, ENTRY, roster={}, prev_game=None, links={}) is None


def test_starter_changes_counts_new_starters():
    prev = _game()
    cur = _game()
    cur["info"]["home_entry_list"][0] = _entry(1, "新", "人", "New Guy")
    ch = ma.starter_changes(ma.entries(prev, "home"), ma.entries(cur, "home"))
    assert ch["changed"] == 1 and ch["in"] == ["新人"]


def test_build_review_only_when_finished_and_is_draft():
    assert ma.build_review(_game(), ENTRY, links={}) is None
    g = _game(game_status=2, home_team_points=20, away_team_points=15,
              home_team_first_points=10, away_team_first_points=12)
    art = ma.build_review(g, ENTRY, links={})
    assert art.draft and "20-15" in art.title and art.filename() == "japan-vs-fiji-2026-10-24-review.md"
    assert "日本代表 10-12 フィジー代表" in art.body


def test_run_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(ma.jrfu, "_get_json", lambda url: [ENTRY])
    monkeypatch.setattr(ma, "fetch_game", lambda gid: _game())
    monkeypatch.setattr(ma, "fetch_japan_roster", lambda opp: {})
    monkeypatch.setattr(ma.jrfu, "_SLEEP", 0)
    first = ma.run(today=date(2026, 10, 23), news_dir=tmp_path)
    assert [k for k, _ in first] == ["preview"]
    assert (tmp_path / "japan-vs-fiji-2026-10-24-preview.md").read_text(encoding="utf-8").startswith("---\ntitle:")
    assert ma.run(today=date(2026, 10, 23), news_dir=tmp_path) == []
