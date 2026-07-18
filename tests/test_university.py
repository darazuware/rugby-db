"""P5-5: 大学ラグビー部員名簿スクレイパーをオフラインのHTMLフィクスチャで検証
（ネットワークアクセスなし）。"""
import pathlib

from pipeline.scrape import university as u
from pipeline.transform import normalize

FX = pathlib.Path(__file__).parent / "fixtures"


def _lines():
    html = (FX / "univ_member_list.html").read_text(encoding="utf-8")
    return u._flatten(html)


def test_extract_records_finds_players_with_grade_and_position():
    recs = u._extract_records(_lines())
    names = {r["kanji"] for r in recs}
    assert names == {"山田 太郎", "藤田 健太", "鈴木 一郎"}


def test_extract_records_excludes_staff():
    recs = u._extract_records(_lines())
    assert "太田 賢一" not in {r["kanji"] for r in recs}


def test_extract_records_excludes_romaji_only_foreign_player():
    # ローマ字表記の選手(Thomas Nicholas Pappas)は漢字氏名パターンに一致しないため
    # そのままでは拾えない。かつ、その選手のかな氏名が隣接する日本人選手の
    # 漢字氏名に誤って組み合わされないことを確認する（実データ: 慶應義塾大学で確認）。
    recs = u._extract_records(_lines())
    by_kanji = {r["kanji"]: r for r in recs}
    assert "とーますにこらすぱぱす" not in {r["kana"] for r in recs}
    assert by_kanji["藤田 健太"]["kana"] == "ふじたけんた"


def test_extract_records_parses_combined_grade_and_school_line():
    recs = u._extract_records(_lines())
    by_kanji = {r["kanji"]: r for r in recs}
    fujita = by_kanji["藤田 健太"]
    assert fujita["grade"] == 3
    assert fujita["school_raw"] == "桐蔭学園高等学校"
    suzuki = by_kanji["鈴木 一郎"]
    assert suzuki["grade"] == 2
    assert suzuki["school_raw"] == "東海大学付属高輪台高等学校"


def test_extract_records_does_not_borrow_neighboring_school():
    # 山田太郎自身のブロックには出身校の記載が無い -> 隣の藤田健太の出身校を
    # 誤って借用しない（_FIELD_WINDOW による近傍制限）。
    recs = u._extract_records(_lines())
    yamada = next(r for r in recs if r["kanji"] == "山田 太郎")
    assert yamada["school_raw"] is None
    assert yamada["height_cm"] == "176" and yamada["weight_kg"] == "79"


def test_player_university_builds_valid_player_with_univ_and_hs_education():
    rec = {"kanji": "藤田 健太", "kana": "ふじたけんた", "grade": 3, "position": "SO",
           "school_raw": "桐蔭学園高等学校", "height_cm": "172", "weight_kg": "74"}
    player, warns = normalize.player_university(
        rec, team_name="早稲田大学", division="kanto_taikosen_a",
        source_url="https://www.wasedarugby.com/list/member/")
    assert player is not None
    assert player["id"] == "univ_早稲田大学__藤田健太"
    assert player["league"] == "university" and player["team_id"] is None
    assert player["squad"] == "kanto_taikosen_a"
    assert player["is_minor"] is False
    assert player["birthdate"] is None  # 10: 学生の生年月日は収集しない
    assert player["instagram"] is None and player["image_url"] is None
    types = {(e["name_raw"], e["type"]) for e in player["education"]}
    assert types == {("早稲田大学", "univ"), ("桐蔭学園高等学校", "hs")}
    assert all(e["school_id"] is None for e in player["education"])  # migrate_schools待ち


def test_player_university_requires_kanji_name():
    rec = {"kanji": None, "kana": "ふじたけんた", "grade": 3, "position": "SO"}
    player, warns = normalize.player_university(
        rec, team_name="早稲田大学", division="kanto_taikosen_a",
        source_url="https://www.wasedarugby.com/list/member/")
    assert player is None
    assert warns


def test_univ_grad_year_computed_from_current_grade():
    # 2026年7月(年度=2026) に4年生 -> 2027年3月卒業見込み
    assert normalize._univ_grad_year(4, "2026-07-18T12:00:00+09:00") == 2027
    assert normalize._univ_grad_year(1, "2026-07-18T12:00:00+09:00") == 2030
    assert normalize._univ_grad_year(None, "2026-07-18T12:00:00+09:00") is None


def test_univ_hs_grad_year_computed_from_current_grade():
    # 4年生(2026年度)は2023年4月に大学入学=2023年3月に高校卒業
    assert normalize._univ_hs_grad_year(4, "2026-07-18T12:00:00+09:00") == 2023


def test_dedupe_players_drops_duplicate_ids():
    warnings: list[str] = []
    players = [
        {"id": "univ_a__b"}, {"id": "univ_a__b"}, {"id": "univ_a__c"},
    ]
    out = u._dedupe_players(players, warnings)
    assert [p["id"] for p in out] == ["univ_a__b", "univ_a__c"]
    assert any("id重複" in w for w in warnings)


def test_university_registered_in_run_scrapers():
    from pipeline import run

    assert "university" in run.SCRAPERS
    assert "university" in run.ALL_LEAGUES


def test_divisions_cover_the_six_scopes():
    assert set(u.DIVISIONS) == {
        "kanto_taikosen_a", "kanto_taikosen_b",
        "kanto_league_1", "kanto_league_2",
        "kansai_a", "kansai_b",
    }
    for div in u.DIVISIONS.values():
        assert div["teams"]  # 各区分に最低1校は登録されている


def test_extract_roster_members_returns_empty_without_api_key(monkeypatch):
    from pipeline import llm_fallback

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert llm_fallback.extract_roster_members("氏名 山田太郎", "早稲田大学") == []
