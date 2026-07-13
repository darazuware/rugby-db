"""P1-5: all.rugby スクレイパー（Top14）のパース + transform をオフラインHTMLで検証。"""
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


def test_enriched_career_validates():
    raw = {"slug": "antoine-dupont", "name_en": "Antoine DUPONT", "position": "Scrum-half",
           "height_raw": "1.77 m", "weight_raw": "80 kg"}
    raw.update(all_rugby.parse_player_bio(_read("ar_player.html")))
    player, _ = normalize.player_allrugby(raw, league="top14", team_id="toulouse")
    assert player is not None
    assert player["nationality"] == ["France"]
    assert player["career"][1]["from"] == 2017  # 文字列→int 変換される
