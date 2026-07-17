"""P1-4b: 人物同一性突合 pipeline.merge_persons のテスト（fixture のみ、network 不使用）。

完了条件:
  - 代表選手（national の ar_ ID）とリーグ所属（lo_ ID）の重複候補が列挙される
  - player_merges 適用後に重複が0になる
"""
from pipeline import merge_persons


def _lo(pid="lo_483678", name_en="Kotaro Matsushima", birthdate="1993-02-26", **kw):
    base = dict(id=pid, source="league-one.jp",
                source_url="https://league-one.jp/player/483678", scraped_at="x",
                name_en=name_en, name_ja=None, name_kana=None, slug=pid,
                league="league-one-d1", team_id="t1", birthdate=birthdate,
                nationality=[], caps=None, merged_from=[])
    base.update(kw)
    return base


def _nat(pid="ar_kotaro-matsushima", name_en="Kotaro  Matsushima",
         birthdate="1993-02-26", **kw):
    base = dict(id=pid, source="all.rugby",
                source_url="https://all.rugby/player/kotaro-matsushima", scraped_at="x",
                name_en=name_en, name_ja=None, name_kana=None, slug="kotaro-matsushima",
                league="national", team_id="japan", birthdate=birthdate,
                nationality=["JP"], caps={"team": "Japan", "count": 42, "source_url": None},
                merged_from=[])
    base.update(kw)
    return base


def _by_league():
    return {"league-one-d1": [_lo()], "national": [_nat()]}


def test_national_duplicate_is_listed_as_candidate():
    cands = merge_persons.find_candidates(_by_league())
    assert len(cands) == 1
    members = {m["id"] for m in cands[0]["members"]}
    assert members == {"lo_483678", "ar_kotaro-matsushima"}
    # 代表(national)を含む候補として拾える
    assert any(m["league"] == "national" for m in cands[0]["members"])


def test_resolved_merge_removes_candidate():
    merges = {"ar_kotaro-matsushima": "lo_483678"}
    # merges 済みは候補から除外される（03 cross_person 連動）
    assert merge_persons.find_candidates(_by_league(), merges) == []


def test_apply_merges_dedups_and_enriches_canonical():
    by_league = _by_league()
    merges = {"ar_kotaro-matsushima": "lo_483678"}
    report = merge_persons.apply_merges(by_league, merges)

    assert report.applied == ["ar_kotaro-matsushima -> lo_483678"]
    # 重複レコードは master から除外
    assert by_league["national"] == []
    # 適用後に重複候補が0
    assert merge_persons.find_candidates(by_league, merges) == []
    assert merge_persons.find_candidates(by_league) == []

    canonical = by_league["league-one-d1"][0]
    assert canonical["merged_from"] == ["ar_kotaro-matsushima"]
    # canonical が持たない代表情報を補完（既存値は上書きしない）
    assert canonical["caps"] == {"team": "Japan", "count": 42, "source_url": None}
    assert canonical["nationality"] == ["JP"]


def test_apply_does_not_overwrite_existing_canonical_values():
    lo = _lo(nationality=["JP"], caps={"team": "Japan", "count": 10, "source_url": None})
    by_league = {"league-one-d1": [lo], "national": [_nat()]}
    merge_persons.apply_merges(by_league, {"ar_kotaro-matsushima": "lo_483678"})
    # 既存の canonical.caps は上書きされない（保守的マージ）
    assert by_league["league-one-d1"][0]["caps"]["count"] == 10


def test_apply_reports_missing_canonical():
    by_league = _by_league()
    report = merge_persons.apply_merges(by_league, {"ar_kotaro-matsushima": "lo_UNKNOWN"})
    assert report.missing_canonical == ["ar_kotaro-matsushima -> lo_UNKNOWN"]
    # canonical が無い場合は何も変更しない
    assert len(by_league["national"]) == 1
