"""P1-5/P1-6: all.rugby スクレイパー（Top14 / Super Rugby Pacific）の
パース + transform をオフラインHTMLで検証。"""
import pathlib

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
    bio = all_rugby.parse_player_bio(_read("ar_player.html"))
    assert "France" in bio["nationality"]
    teams = [c["team"] for c in bio["career"]]
    assert "Stade Toulousain" in teams
    tou = next(c for c in bio["career"] if c["team"] == "Stade Toulousain")
    assert tou["from"] == "2017" and tou["to"] == "2026"


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
# P4-6: URC / Premiership 部分収集（collect_star）
# ---------------------------------------------------------------------------

def test_star_tournaments_registered():
    # 実ページ確認済みキー（all_rugby.STAR_TOURNAMENTS のコメント参照）
    assert all_rugby.STAR_TOURNAMENTS["urc"] == {"key": "urc", "league": "urc"}
    assert all_rugby.STAR_TOURNAMENTS["premiership"] == {
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


def test_collect_star_filters_players(monkeypatch):
    pages = _star_fixture_pages()
    monkeypatch.setattr(all_rugby, "_get", lambda url: pages.get(url))
    monkeypatch.setattr(all_rugby, "_SLEEP", 0)

    result = all_rugby.collect_star("urc")

    ids = [p["id"] for p in result["players"]]
    # 日本人（bio 国籍に Japan）と代表テストキャップ保持者のみ。無キャップ非日本人は除外
    assert ids == ["ar_jp-taro", "ar_cap-holder"]
    cap_holder = next(p for p in result["players"] if p["id"] == "ar_cap-holder")
    assert cap_holder["caps"] == {
        "team": "Ireland", "count": 25,
        "source_url": "https://all.rugby/player/cap-holder"}
    assert all(p["league"] == "urc" and p["team_id"] == "testclub"
               for p in result["players"])

    # チームは全件・partial（03: roster_sym 免除）、roster_ids は収集選手のみ
    assert len(result["teams"]) == 1
    team = result["teams"][0]
    assert team["roster_mode"] == "partial"
    assert team["roster_ids"] == ["ar_jp-taro", "ar_cap-holder"]

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
