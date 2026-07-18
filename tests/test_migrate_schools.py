"""P5-1: 学校データ移行の純関数（正規化・slug化・SchoolRegistryの冪等性/衝突回避）。"""
from pipeline import migrate_schools as m
from pipeline.schemas import School


def test_normalize_school_name_collapses_whitespace_and_width():
    assert m.normalize_school_name("  昭和　高校  ") == "昭和 高校"
    assert m.normalize_school_name("ＡＢＣ高校") == "ABC高校"  # NFKC: 全角英数→半角
    assert m.normalize_school_name(None) == ""


def test_slugify_school_keeps_kanji_no_romanization():
    # 日本語校名はローマ字化しない（AIによる翻訳＝未確認の事実になるため）
    assert m.slugify_school("昭和高校") == "昭和高校"
    assert m.slugify_school("立命館大学") == "立命館大学"


def test_slugify_school_ascii():
    assert m.slugify_school("SaltLakeHighSchool") == "saltlakehighschool"
    assert m.slugify_school("CA Brive (Youth)") == "ca-brive-youth"


def test_slugify_school_empty_falls_back():
    assert m.slugify_school("") == "school"
    assert m.slugify_school("   ") == "school"


def test_school_registry_dedupes_same_name_and_type():
    reg = m.SchoolRegistry(existing=[])
    id1, is_new1 = reg.resolve("桐蔭学園高校", "hs")
    id2, is_new2 = reg.resolve("桐蔭学園高校", "hs")
    assert id1 == id2
    assert is_new1 is True
    assert is_new2 is False
    assert len(reg.records) == 1


def test_school_registry_separates_hs_and_univ_same_name():
    reg = m.SchoolRegistry(existing=[])
    hs_id, _ = reg.resolve("同志社", "hs")
    univ_id, _ = reg.resolve("同志社", "univ")
    assert hs_id != univ_id
    assert len(reg.records) == 2


def test_school_registry_id_collision_gets_suffix():
    reg = m.SchoolRegistry(existing=[])
    # 正規化後のslugが衝突するケース（type違いで別レコードだが slug base は同一）
    id1, _ = reg.resolve("Test School", "hs")
    id2, _ = reg.resolve("Test School", "univ")
    assert {id1, id2} == {"test-school", "test-school-2"}


def test_school_registry_is_idempotent_across_runs():
    existing = [{"id": "showa-hs", "name": "昭和高校", "name_kana": None,
                 "type": "hs", "pref": None, "source_url": None, "scraped_at": None}]
    reg = m.SchoolRegistry(existing=existing)
    sid, is_new = reg.resolve("昭和高校", "hs")
    assert sid == "showa-hs"
    assert is_new is False
    assert len(reg.records) == 1  # 既存レコードを引き継ぎ、重複登録しない


def test_school_schema_accepts_minimal_migrated_record():
    rec = {"id": "showa-hs", "name": "昭和高校", "name_kana": None,
           "type": "hs", "pref": None, "source_url": None, "scraped_at": None}
    model = School.model_validate(rec)
    assert model.id == "showa-hs" and model.pref is None
