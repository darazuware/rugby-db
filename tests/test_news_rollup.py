"""news_rollup: 週次まとめは字数を問わず月次へ統合、月次が薄ければ noindex、手修正済みの月は触らない。"""
import json

from pipeline import news_rollup as nr


def _setup(tmp_path, monkeypatch, frozen=()):
    news = tmp_path / "news"
    news.mkdir()
    (tmp_path / "redirects.json").write_text("{}", encoding="utf-8")
    (tmp_path / "frozen.json").write_text(json.dumps(list(frozen)), encoding="utf-8")
    monkeypatch.setattr(nr, "NEWS_DIR", news)
    monkeypatch.setattr(nr, "REDIRECTS", tmp_path / "redirects.json")
    monkeypatch.setattr(nr, "FROZEN", tmp_path / "frozen.json")
    monkeypatch.setattr(nr, "ROLLUP_DIR", tmp_path / "meta")
    monkeypatch.setattr(nr, "ROOT", tmp_path)
    monkeypatch.setattr(nr.news_verify, "rollup_line_ok", lambda e: True)
    return news


def _weekly(news, slug, n, pub="2026-10-05"):
    lines = "\n".join(f"- [Player {i} LONGNAME](/teams/urc/x/#p-{i})が[チームX](/teams/urc/x/)に加入" for i in range(n))
    (news / f"{slug}.md").write_text(
        f'---\ntitle: "w"\npubDate: {pub}\ntags: ["URC", "加入"]\ndraft: false\n---\n\n{lines}\n', encoding="utf-8")


def test_weekly_rolled_up_regardless_of_length_and_thin_month_noindexed(tmp_path, monkeypatch):
    news = _setup(tmp_path, monkeypatch)
    _weekly(news, "urc-join-weekly-2026-W41", 100)
    _weekly(news, "urc-join-weekly-2026-W42", 1, pub="2026-11-02")
    nr.run()
    assert not (news / "urc-join-weekly-2026-W41.md").exists()
    oct_ = (news / "transfers-roundup-2026-10.md").read_text(encoding="utf-8")
    nov = (news / "transfers-roundup-2026-11.md").read_text(encoding="utf-8")
    assert "noindex: true" not in oct_
    assert "noindex: true" in nov
    r = json.loads((tmp_path / "redirects.json").read_text(encoding="utf-8"))
    assert r["/news/urc-join-weekly-2026-w41"] == "/news/transfers-roundup-2026-10/"


def test_frozen_month_untouched(tmp_path, monkeypatch):
    news = _setup(tmp_path, monkeypatch, frozen=["2026-09"])
    _weekly(news, "urc-join-weekly-2026-W38", 3, pub="2026-09-14")
    nr.run()
    assert (news / "urc-join-weekly-2026-W38.md").exists()
    assert not (news / "transfers-roundup-2026-09.md").exists()
