"""P1-5/P1-6: all.rugby スクレイパー（Top14 / Super Rugby Pacific）の
パース + transform をオフラインHTMLで検証。"""
import pathlib

import pytest

from pipeline.scrape import all_rugby
from pipeline.transform import normalize

FX = pathlib.Path(__file__).parent / "fixtures"


def _read(name):
    return (FX / name).read_text(encoding="utf-8")


def test_parse_tournament_table():
    slugs, rows = all_rugby.parse_tournament_table(_read("ar_tournament_table.html"))
    assert len(slugs) == 14
    assert "bayonne" in slugs and "toulouse" in slugs
    # シーズン序盤（数値空欄）でも slug は取れ、行 raw は team_id を持つ
    assert all("team_id" in r for r in rows)


def test_parse_squad():
    squad = all_rugby.parse_squad(_read("ar_squad.html"))
    assert len(squad) > 40
    slugs = [p["slug"] for p in squad]
    assert len(slugs) == len(set(slugs))  # クラブ内で重複なし
    first = squad[0]
    assert first["name_en"] and first["position"]
    assert "kg" in (first["weight_raw"] or "")


def test_player_allrugby_transform():
    squad = all_rugby.parse_squad(_read("ar_squad.html"))
    raw = next(p for p in squad if p["height_raw"] and "m" in p["height_raw"])
    player, _ = normalize.player_allrugby(raw, league="top14", team_id="bayonne")
    assert player is not None
    assert player["id"] == f"ar_{raw['slug']}"
    assert player["league"] == "top14" and player["team_id"] == "bayonne"
    assert 150 <= player["height_cm"] <= 230
    assert 60 <= player["weight_kg"] <= 170


def test_player_allrugby_null_height():
    # '-' の身長体重は null 化してもレコードは通る
    raw = {"slug": "x-y", "name_en": "X Y", "position": "Prop",
           "height_raw": "-", "weight_raw": "-"}
    player, _ = normalize.player_allrugby(raw, league="top14", team_id="bayonne")
    assert player is not None
    assert player["height_cm"] is None and player["weight_kg"] is None


def test_team_allrugby_uses_slug_id():
    team, _ = normalize.team_allrugby(
        {"slug": "bayonne", "name_ja": "バイヨンヌ", "roster_ids": ["ar_a", "ar_b"]},
        league="top14",
    )
    assert team["id"] == "bayonne"  # migrate_legacy と同じ team_id 規約
    assert team["name_ja"] == "バイヨンヌ"
    assert team["roster_ids"] == ["ar_a", "ar_b"]


def test_parse_player_bio_enrich():
    # フィクスチャの末尾チームは "2026" までの表記だが、実際は在籍中（現在年と
    # 一致するため to=None に正規化される想定）。過去年は現在年扱いされない。
    bio = all_rugby.parse_player_bio(_read("ar_player.html"), now_year=2030)
    assert "France" in bio["nationality"]
    teams = [c["team"] for c in bio["career"]]
    assert "Stade Toulousain" in teams
    tou = next(c for c in bio["career"] if c["team"] == "Stade Toulousain")
    assert tou["from"] == "2017" and tou["to"] == "2026"


def test_parse_player_bio_current_team_to_nulled():
    # 取得時点の年（now_year）と末尾チームの to が一致する場合は在籍中とみなし
    # to を None 化する（all.rugby は在籍中チームにも "present" マーカーを出さない）。
    bio = all_rugby.parse_player_bio(_read("ar_player.html"), now_year=2026)
    tou = next(c for c in bio["career"] if c["team"] == "Stade Toulousain")
    assert tou["from"] == "2017" and tou["to"] is None
    # 過去のチームは変更されない
    cas = next(c for c in bio["career"] if c["team"] == "Castres Olympique")
    assert cas["from"] == "2014" and cas["to"] == "2017"


def test_super_rugby_tournament_registered():
    # P1-6: super-rugby-pacific が実ページ確認済みキーで TOURNAMENTS に登録され、
    # league は run.py の SCRAPERS / ALL_LEAGUES と一致する "super-rugby"。
    cfg = all_rugby.TOURNAMENTS["super-rugby-pacific"]
    assert cfg["key"] == "super-rugby-pacific"
    assert cfg["league"] == "super-rugby"


def test_super_rugby_registered_in_run_scrapers():
    from pipeline import run

    assert "super-rugby" in run.SCRAPERS
    assert "super-rugby" in run.ALL_LEAGUES


def test_enriched_career_validates():
    raw = {"slug": "antoine-dupont", "name_en": "Antoine DUPONT", "position": "Scrum-half",
           "height_raw": "1.77 m", "weight_raw": "80 kg"}
    raw.update(all_rugby.parse_player_bio(_read("ar_player.html")))
    player, _ = normalize.player_allrugby(raw, league="top14", team_id="toulouse")
    assert player is not None
    assert player["nationality"] == ["France"]
    assert player["career"][1]["from"] == 2017  # 文字列→int 変換される


# ---------------------------------------------------------------------------
# URC / Premiership フルスコッド収集（with_caps）
# ---------------------------------------------------------------------------

def test_star_tournaments_registered():
    # 実ページ確認済みキー（all_rugby.TOURNAMENTS のコメント参照）
    assert all_rugby.TOURNAMENTS["urc"] == {"key": "urc", "league": "urc"}
    assert all_rugby.TOURNAMENTS["premiership"] == {
        "key": "premiership", "league": "premiership"}


def test_star_registered_in_run_scrapers():
    from pipeline import run

    for lg in ("urc", "premiership"):
        assert lg in run.SCRAPERS
        assert lg in run.ALL_LEAGUES


def test_parse_sporting_nationality():
    html = _read("ar_player_caps.html")
    assert all_rugby.parse_sporting_nationality(html) == "Canada"
    # Sporting nationality に対する通算試合数（TEAM 集計）と組み合わせて
    # テストキャップを機械的に判定できる
    assert all_rugby.parse_player_caps(html, "Canada") == 21


def test_parse_sporting_nationality_missing():
    assert all_rugby.parse_sporting_nationality("<html><body></body></html>") is None


def _star_fixture_pages():
    table = """
    <table>
      <tr><th>#</th><th>Club</th><th>PTS</th><th>PL</th><th>W</th><th>D</th><th>L</th></tr>
      <tr><td>1</td><td><a href="/club/testclub">Test Club</a></td>
          <td>10</td><td>3</td><td>2</td><td>1</td><td>0</td></tr>
    </table><p>Season 2025 / 2026</p>"""
    squad = """
    <table>
      <tr><th></th><th>Name</th><th>Position</th><th>Height</th><th>Weight</th></tr>
      <tr><td></td><td><a href="/player/jp-taro">Taro JP</a>Taro JP</td>
          <td>Prop</td><td>1.80 m</td><td>110 kg</td></tr>
      <tr><td></td><td><a href="/player/cap-holder">Cap HOLDER</a>Cap HOLDER</td>
          <td>Fly-half</td><td>1.78 m</td><td>88 kg</td></tr>
      <tr><td></td><td><a href="/player/no-star">No STAR</a>No STAR</td>
          <td>Wing</td><td>1.82 m</td><td>90 kg</td></tr>
    </table>"""
    jp = """
    <div class="bio">
      <div><span class="gras">Nationality #1</span> <img alt="Drapeau Japan" src="/x.png"></div>
      <div><span class="gras">Sporting nationality</span> <img alt="Drapeau Japan" src="/x.png"></div>
    </div>"""
    cap = """
    <div class="bio">
      <div><span class="gras">Nationality #1</span> <img alt="Drapeau Ireland" src="/x.png"></div>
      <div><span class="gras">Sporting nationality</span> <img alt="Drapeau Ireland" src="/x.png"></div>
    </div>
    <table class="JOverall">
      <tr><th></th><th>TEAM</th><th>Matches</th><th>W/D/L</th></tr>
      <tr><td></td><td>Test Club</td><td>50</td><td>30 0 20</td></tr>
      <tr><td></td><td>Ireland</td><td>25</td><td>20 0 5</td></tr>
    </table>"""
    nostar = """
    <div class="bio">
      <div><span class="gras">Nationality #1</span> <img alt="Drapeau Ireland" src="/x.png"></div>
      <div><span class="gras">Sporting nationality</span> <img alt="Drapeau Ireland" src="/x.png"></div>
    </div>
    <table class="JOverall">
      <tr><th></th><th>TEAM</th><th>Matches</th><th>W/D/L</th></tr>
      <tr><td></td><td>Test Club</td><td>10</td><td>5 0 5</td></tr>
    </table>"""
    return {
        "https://all.rugby/tournament/urc/table": table,
        "https://all.rugby/club/testclub/squad": squad,
        "https://all.rugby/player/jp-taro": jp,
        "https://all.rugby/player/cap-holder": cap,
        "https://all.rugby/player/no-star": nostar,
    }


def test_collect_with_caps_keeps_full_squad(monkeypatch):
    # 2026-07-26: フルスコッド化。日本人/キャップ保持者による絞り込みはせず全員収集するが、
    # with_caps=True の場合は代表テストキャップの取得は引き続き行う。
    pages = _star_fixture_pages()
    monkeypatch.setattr(all_rugby, "_get", lambda url: pages.get(url))
    monkeypatch.setattr(all_rugby, "_SLEEP", 0)

    result = all_rugby.collect("urc", with_caps=True)

    ids = [p["id"] for p in result["players"]]
    # 絞り込みなし: 無キャップの非日本人選手も含め squad 全員が収集される
    assert ids == ["ar_jp-taro", "ar_cap-holder", "ar_no-star"]
    cap_holder = next(p for p in result["players"] if p["id"] == "ar_cap-holder")
    assert cap_holder["caps"] == {
        "team": "Ireland", "count": 25,
        "source_url": "https://all.rugby/player/cap-holder"}
    no_star = next(p for p in result["players"] if p["id"] == "ar_no-star")
    assert no_star["caps"] is None  # JOverall の TEAM 集計に Ireland 行が無く判定不能のため未設定
    assert all(p["league"] == "urc" and p["team_id"] == "testclub"
               for p in result["players"])

    # チームは全件・full（フルスコッド化）、roster_ids は収集選手全員
    assert len(result["teams"]) == 1
    team = result["teams"][0]
    assert team["roster_mode"] == "full"
    assert team["roster_ids"] == ["ar_jp-taro", "ar_cap-holder", "ar_no-star"]

    # 順位表は全チーム分
    assert len(result["standings"]) == 1
    assert result["standings"][0]["season"] == "2025-26"
    assert result["standings"][0]["rows"][0]["team_id"] == "testclub"


def test_standing_allrugby_blank_drawn_is_zero_when_arithmetic_checks():
    # all.rugby は引分0を空欄表示する（P4-6 実ページ確認）。W+L=PL のときのみ0扱い
    rows = [
        {"team_id": "a", "rank": "1", "points": "60", "played": "17",
         "won": "12", "drawn": "", "lost": "5"},           # 12+5=17 → drawn=0
        {"team_id": "b", "rank": "2", "points": "50", "played": "17",
         "won": "12", "drawn": "", "lost": "4"},           # 12+4≠17 → 除外
    ]
    standing, warnings = normalize.standing_allrugby(
        rows, league="urc", season="2025-26",
        source_url="https://all.rugby/tournament/urc/table")
    assert standing is not None
    assert [r["team_id"] for r in standing["rows"]] == ["a"]
    assert standing["rows"][0]["drawn"] == 0
    assert any("b" in w for w in warnings)


def test_collect_light_skips_squad_and_player_fetch(monkeypatch):
    """軽量モード（--only matches,standings）: トーナメント表ページ以外への GET を
    一切行わず standings のみ返す（players/teams は空）。club squad/選手個別ページ
    取得（本来数十〜数百リクエスト）を叩いたら即失敗させて検知する。"""
    pages = _star_fixture_pages()
    table_url = "https://all.rugby/tournament/urc/table"

    def fake_get(url):
        if url != table_url:
            pytest.fail(f"light モードで想定外のGET: {url}")
        return pages[table_url]

    monkeypatch.setattr(all_rugby, "_get", fake_get)
    monkeypatch.setattr(all_rugby, "_SLEEP", 0)

    result = all_rugby.collect("urc", with_caps=True, light=True)
    assert result["players"] == []
    assert result["teams"] == []
    assert result["matches"] == []
    assert len(result["standings"]) == 1
    assert result["standings"][0]["rows"][0]["team_id"] == "testclub"


# --- 重複掲載（他クラブ選手の混入）の解決: blues に Brumbies 選手が入った事例の回帰 ---

def test_parse_club_name():
    html = "<html><head><title>Blues rugby team players for 2025/2026 - All.Rugby</title></head></html>"
    assert all_rugby.parse_club_name(html) == "Blues"


def test_current_club_future_end_year_counts_as_current():
    career = [{"team": "A", "from": "2024", "to": "2025"}, {"team": "B", "from": "2026", "to": "2027"}]
    assert all_rugby.current_club(career, now_year=2026) == "B"
    assert all_rugby.current_club([{"team": "A", "from": "2020", "to": "2024"}], now_year=2026) is None


def test_resolve_duplicate_members_uses_current_club():
    squads = {
        "blues": [{"slug": "barrett"}, {"slug": "valetini"}, {"slug": "japan-bound"}],
        "brumbies": [{"slug": "valetini"}, {"slug": "japan-bound"}, {"slug": "lonely"}],
    }
    names = {"blues": "Blues", "brumbies": "Brumbies"}
    careers = {
        "valetini": [{"team": "Brumbies", "from": "2017", "to": None}],
        "japan-bound": [{"team": "Blues", "from": "2024", "to": "2024"},
                        {"team": "Hanazono Kintetsu Liners", "from": "2024", "to": None}],
    }
    resolved, warns = all_rugby.resolve_duplicate_members(squads, names, lambda s: careers.get(s, []))
    assert resolved == {"valetini": "brumbies"}  # 最初のクラブ(blues)ではなく現所属
    assert len(warns) == 1 and "japan-bound" in warns[0]  # 一意に決まらない選手は除外


def test_roster_repair_plan_moves_and_drops():
    from pipeline import roster_repair
    players = [{"id": f"ar_{s}", "team_id": t} for s, t in
               [("v", "blues"), ("j", "blues"), ("b", "blues"), ("x", "blues"), ("loan", "blues"),
                ("o1", "blues"), ("o2", "blues"), ("o3", "blues"), ("o4", "blues"), ("o5", "blues")]]
    teams = [{"id": "blues", "roster_ids": [p["id"] for p in players]}, {"id": "brumbies", "roster_ids": []}]
    pages_of = {"v": ["blues", "brumbies"], "j": ["blues", "brumbies", "chiefs"]}
    careers = {
        "v": [{"team": "Brumbies", "to": None}],                       # 重複掲載→現所属へ付け替え
        "j": [{"team": "Hanazono Kintetsu Liners", "to": None}],       # 3ページ掲載・リーグ外→除外
        "b": [{"team": "Blues", "to": None}],
        "x": [{"team": "Aviron Bayonnais", "to": None}],               # 単一掲載・在籍歴なし→除外
        "loan": [{"team": "Blues", "from": "2024", "to": "2028"},
                 {"team": "Bedford Town", "to": None}],                # 在籍歴あり(ローン)→触らない
    }
    names = {"blues": ["Blues"], "brumbies": ["Brumbies"]}
    pl = roster_repair.plan(players, league_clubs={"blues", "brumbies"}, pages_of=pages_of,
                            names=names, career_of=lambda s: careers.get(s, []))
    assert pl["move"] == {"ar_v": ("blues", "brumbies")}
    assert set(pl["drop"]) == {"ar_j", "ar_x"}
    out = roster_repair.apply_plan(players, teams, pl)
    assert {p["id"] for p in out} == {p["id"] for p in players} - {"ar_j", "ar_x"}
    assert teams[1]["roster_ids"] == ["ar_v"] and "ar_v" not in teams[0]["roster_ids"]


def test_roster_repair_skips_team_when_most_would_drop():
    from pipeline import roster_repair
    players = [{"id": f"ar_p{i}", "team_id": "edinburgh"} for i in range(4)]
    careers = {f"p{i}": [{"team": "Edimbourg Rugby", "to": None}] for i in range(4)}
    pl = roster_repair.plan(players, league_clubs={"edinburgh"}, pages_of={},
                            names={"edinburgh": ["Edinburgh"]}, career_of=lambda s: careers[s])
    assert pl["drop"] == {} and pl["skipped_teams"] == ["edinburgh"]


def test_team_names_uses_majority_current_club():
    from pipeline import roster_repair
    careers = [[{"team": "Edimbourg Rugby", "to": None}]] * 3 + [[]]
    assert roster_repair.team_names("edinburgh", "Edinburgh", careers) == ["Edinburgh", "Edimbourg Rugby"]


def test_pick_club_uses_any_active_entry():
    # SR選手が NPC 州代表も在籍中（career 末尾は州代表）でも、SR クラブ側に決まる
    career = [{"team": "Chiefs", "from": "2022", "to": "2028"},
              {"team": "Waikato Mooloos", "from": "2025", "to": None}]
    names = {"chiefs": ["Chiefs"], "blues": ["Blues"]}
    assert all_rugby.pick_club(["blues", "chiefs"], names, career) == "chiefs"
    assert all_rugby.pick_club(["blues", "chiefs"], names, [{"team": "Kobe Steelers", "to": None}]) is None


def test_pick_club_prefers_newest_when_two_active():
    career = [{"team": "Fijian Drua", "from": "2022", "to": "2026"},
              {"team": "Sale Sharks", "from": "2026", "to": "2028"}]
    names = {"fijian-drua": ["Fijian Drua"], "sale": ["Sale"]}
    assert all_rugby.pick_club(["fijian-drua", "sale"], names, career) == "sale"


def test_roster_repair_relocates_instead_of_dropping_known_pro():
    from pipeline import roster_repair
    players = [{"id": "ar_s", "team_id": "pau"}] + [{"id": f"ar_o{i}", "team_id": "pau"} for i in range(3)]
    careers = {"s": [{"team": "Aviron Bayonnais", "from": "2024", "to": None}],
               **{f"o{i}": [{"team": "Section Paloise", "to": None}] for i in range(3)}}
    names = {"pau": ["Pau", "Section Paloise"], "bayonne": ["Bayonne", "Aviron Bayonnais"],
             "bath": ["Bath"]}
    pl = roster_repair.plan(players, league_clubs={"pau", "bayonne"}, pages_of={},
                            names=names, career_of=lambda s: careers[s],
                            club_league={"pau": "top14", "bayonne": "top14", "bath": "premiership"})
    assert pl["move"] == {"ar_s": ("pau", "bayonne")} and pl["drop"] == {}
    pl2 = roster_repair.plan([{"id": "ar_s", "team_id": "bath"}] + [{"id": f"ar_o{i}", "team_id": "bath"} for i in range(3)],
                             league_clubs={"bath"}, pages_of={}, names=names,
                             career_of=lambda s: careers[s] if s == "s" else [{"team": "Bath Rugby", "to": None}],
                             club_league={"pau": "top14", "bayonne": "top14", "bath": "premiership"})
    assert pl2["relocate"] == {"ar_s": ("bath", "bayonne", "top14")}


def test_roster_repair_keeps_multi_page_player_without_career_info():
    from pipeline import roster_repair
    players = [{"id": "ar_n", "team_id": "northampton"}, {"id": "ar_m", "team_id": "northampton"}]
    pages_of = {"n": ["exeter", "northampton"], "m": ["exeter", "northampton"]}
    careers = {"n": [], "m": [{"team": "Northampton Saints", "from": "2022", "to": "2025"},
                              {"team": "Ampthill Rugby", "from": "2025", "to": None}]}
    names = {"exeter": ["Exeter"], "northampton": ["Northampton (Saints)"]}
    pl = roster_repair.plan(players, league_clubs={"exeter", "northampton"}, pages_of=pages_of,
                            names=names, career_of=lambda s: careers[s])
    assert pl["move"] == {} and pl["drop"] == {}  # 2ページ間で決められない→維持
    pl3 = roster_repair.plan([{"id": "ar_n", "team_id": "northampton"},
                              {"id": "ar_a", "team_id": "northampton"}, {"id": "ar_b", "team_id": "northampton"}],
                             league_clubs={"exeter", "northampton", "bath"},
                             pages_of={"n": ["exeter", "northampton", "bath"]}, names=names,
                             career_of=lambda s: [])
    assert set(pl3["drop"]) == {"ar_n"}  # 3ページ以上・在籍情報なし→混入として除外


def test_allowed_by_corrections():
    corr = {"valetini": {"club": "brumbies"}, "choat": {"club": None}}
    assert all_rugby.allowed_by_corrections("valetini", "brumbies", corr)
    assert not all_rugby.allowed_by_corrections("valetini", "blues", corr)
    assert not all_rugby.allowed_by_corrections("choat", "hurricanes", corr)
    assert all_rugby.allowed_by_corrections("barrett", "blues", corr)
