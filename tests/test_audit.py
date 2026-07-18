"""P3-3: pipeline.audit のテスト（network不使用、requests をモック）。

完了条件（05: kana未設定リスト・null率レポート・リンク切れチェック）:
  - name_kana が null の外国籍選手のうち kana_overrides.json に未登録のものだけを検出する
  - null率がリーグごとに算出される
  - リンク切れチェックは4xx/5xxまたは例外を「疑い」として拾う（実ネットワークは使わない）
  - data/master/ 配下には一切書き込まない（並行実行中の別セッションのデータを壊さない）
"""
from pathlib import Path

from pipeline import audit, io


def _player(pid, *, league="top14", nationality=None, name_kana=None, team_id="t1"):
    return dict(id=pid, source="test", source_url=f"https://example.test/{pid}", scraped_at="x",
                name_en=f"Player {pid}", name_ja=None, name_kana=name_kana, slug=pid,
                league=league, team_id=team_id, nationality=nationality or [], caps=None,
                position=None, height_cm=None, weight_kg=None, birthdate=None, image_url=None)


def _team(tid, *, league="top14"):
    return dict(id=tid, league=league, name_en=tid,
                source_url=f"https://example.test/team-{tid}", scraped_at="x")


def test_kana_missing_excludes_japanese_and_overridden():
    players_by_league = {
        "top14": [
            _player("a", nationality=["FR"], name_kana=None),  # missing
            _player("b", nationality=["JP"], name_kana=None),  # JP: excluded
            _player("c", nationality=["FR"], name_kana="デュポン"),  # already set
            _player("d", nationality=["FR"], name_kana=None),  # in overrides
        ],
    }
    result = audit.kana_missing(players_by_league, overrides={"d": "some kana"})
    assert [it["id"] for it in result["top14"]] == ["a"]


def test_kana_missing_returns_empty_dict_when_none_missing():
    players_by_league = {"top14": [_player("a", nationality=["JP"])]}
    assert audit.kana_missing(players_by_league, overrides={}) == {}


def test_null_rate_computes_fraction_per_field():
    players_by_league = {
        "top14": [
            _player("a"),  # position/height/weight/birthdate/image_url all None, name_kana None
            dict(_player("b"), position="PR", height_cm=180, weight_kg=100,
                 birthdate="1995-01-01", image_url="https://example.test/x.jpg", name_kana="x"),
        ],
    }
    rates = audit.null_rate(players_by_league)
    assert rates["top14"] == {
        "name_kana": 0.5, "position": 0.5, "height_cm": 0.5,
        "weight_kg": 0.5, "birthdate": 0.5, "image_url": 0.5,
    }


def test_null_rate_skips_empty_league():
    assert audit.null_rate({"top14": []}) == {}


def test_sample_urls_includes_all_teams_and_dedupes():
    players_by_league = {"top14": [_player("a"), _player("b")]}
    teams = [_team("t1"), _team("t1")]  # duplicate source_url
    urls = audit.sample_urls(players_by_league, teams, sample_per_league=10)
    labels = [u[0] for u in urls]
    assert labels.count("team:t1") == 1
    assert "player:a" in labels and "player:b" in labels


def test_sample_urls_caps_players_per_league():
    players_by_league = {"top14": [_player(str(i)) for i in range(30)]}
    urls = audit.sample_urls(players_by_league, teams=[], sample_per_league=5)
    assert len(urls) == 5


def test_sample_urls_deterministic_with_seed():
    players_by_league = {"top14": [_player(str(i)) for i in range(30)]}
    a = audit.sample_urls(players_by_league, teams=[], sample_per_league=5, seed=1)
    b = audit.sample_urls(players_by_league, teams=[], sample_per_league=5, seed=1)
    assert a == b


def test_check_links_flags_4xx_and_exceptions(monkeypatch):
    import requests

    class FakeResp:
        def __init__(self, status_code):
            self.status_code = status_code

    def fake_head(url, timeout=None, allow_redirects=True):
        if url == "https://ok.test":
            return FakeResp(200)
        if url == "https://missing.test":
            return FakeResp(404)
        raise requests.RequestException("boom")

    monkeypatch.setattr(requests, "head", fake_head)
    broken = audit.check_links([
        ("ok", "https://ok.test"),
        ("missing", "https://missing.test"),
        ("error", "https://error.test"),
    ])
    assert len(broken) == 2
    assert any("missing.test" in b and "status=404" in b for b in broken)
    assert any("error.test" in b and "error=RequestException" in b for b in broken)


def test_check_links_falls_back_to_get_on_405(monkeypatch):
    import requests

    class FakeResp:
        def __init__(self, status_code):
            self.status_code = status_code

    def fake_head(url, timeout=None, allow_redirects=True):
        return FakeResp(405)

    def fake_get(url, timeout=None, allow_redirects=True):
        return FakeResp(200)

    monkeypatch.setattr(requests, "head", fake_head)
    monkeypatch.setattr(requests, "get", fake_get)
    broken = audit.check_links([("x", "https://head-unsupported.test")])
    assert broken == []


def test_build_markdown_status_ok_when_no_findings():
    md = audit.build_markdown(kana={}, nulls={"top14": {"name_kana": 0.0}}, broken=[], link_checked=5)
    assert md.startswith("# 週次監査レポート（OK）")
    assert "なし" in md


def test_build_markdown_status_needs_attention_and_truncates():
    kana = {"top14": [{"id": f"p{i}", "name": f"Player {i}"} for i in range(25)]}
    md = audit.build_markdown(kana=kana, nulls={}, broken=["team:t1: https://x (status=404)"],
                               link_checked=10)
    assert md.startswith("# 週次監査レポート（要確認）")
    assert "合計 25 件" in md
    assert "...ほか 5 件" in md
    assert "status=404" in md


def _setup_master(monkeypatch, tmp_path):
    master_dir = tmp_path / "master"
    monkeypatch.setattr(io, "MASTER_DIR", master_dir)
    monkeypatch.setattr(io, "META_DIR", master_dir / "_meta")
    monkeypatch.setattr(io, "MANUAL_DIR", tmp_path / "manual")
    io.write_records(io.players_path("top14"), [
        _player("a", nationality=["FR"], name_kana=None),
    ])
    io.write_records(io.teams_path("top14"), [_team("t1")])
    return master_dir


def test_main_writes_report_and_does_not_touch_master(monkeypatch, tmp_path):
    master_dir = _setup_master(monkeypatch, tmp_path)
    monkeypatch.setattr(audit, "ALL_LEAGUES", ["top14"])
    before = sorted(p.relative_to(master_dir) for p in master_dir.rglob("*") if p.is_file())

    out_path = tmp_path / "audit_report.md"
    rc = audit.main(["--out", str(out_path), "--skip-link-check"])

    assert rc == 0
    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "週次監査レポート" in content
    assert "top14" in content

    after = sorted(p.relative_to(master_dir) for p in master_dir.rglob("*") if p.is_file())
    assert after == before  # data/master/ 配下は一切変更されない


def test_main_prints_has_findings_line(monkeypatch, tmp_path, capsys):
    _setup_master(monkeypatch, tmp_path)
    monkeypatch.setattr(audit, "ALL_LEAGUES", ["top14"])
    out_path = tmp_path / "audit_report.md"
    audit.main(["--out", str(out_path), "--skip-link-check"])
    out = capsys.readouterr().out
    assert "[audit] has_findings=true" in out
