"""P3-2: pipeline.notify のテスト（network不使用、requests.post をモック）。"""
from pipeline import notify


def test_build_payload_success_includes_all_sections():
    payload = notify.build_payload(
        status="success", title="daily_update 成功",
        details=["top14: 選手1106件"], news=["top14-join-a-2026-07-18.md"],
        warnings=["top14 standings: team=x の数値欠落のため行を除外"],
    )
    embed = payload["embeds"][0]
    assert embed["title"] == "daily_update 成功"
    assert embed["color"] == notify.COLOR_SUCCESS
    assert "top14: 選手1106件" in embed["description"]
    assert "top14-join-a-2026-07-18.md" in embed["description"]
    assert "warning (1件)" in embed["description"]


def test_build_payload_failure_color():
    payload = notify.build_payload(status="failure", title="失敗", details=[], news=[], warnings=[])
    assert payload["embeds"][0]["color"] == notify.COLOR_FAILURE
    assert payload["embeds"][0]["description"] == "(詳細なし)"


def test_build_payload_truncates_long_lists():
    warnings = [f"warn-{i}" for i in range(30)]
    payload = notify.build_payload(status="success", title="t", details=[], news=[], warnings=warnings)
    desc = payload["embeds"][0]["description"]
    assert "...ほか 10 件" in desc


def test_send_skips_without_webhook(monkeypatch, capsys):
    monkeypatch.delenv(notify.WEBHOOK_ENV, raising=False)
    ok = notify.send({"embeds": []})
    assert ok is False
    assert "未設定のため送信をスキップ" in capsys.readouterr().err


def test_send_posts_to_webhook(monkeypatch):
    calls = []

    class FakeResp:
        status_code = 204

        def raise_for_status(self):
            pass

    def fake_post(url, json=None, timeout=None):
        calls.append((url, json, timeout))
        return FakeResp()

    monkeypatch.setattr(notify.requests, "post", fake_post)
    ok = notify.send({"embeds": []}, webhook_url="https://discord.test/webhook")
    assert ok is True
    assert calls[0][0] == "https://discord.test/webhook"


def test_send_returns_false_on_error(monkeypatch, capsys):
    def fake_post(url, json=None, timeout=None):
        raise RuntimeError("boom")

    monkeypatch.setattr(notify.requests, "post", fake_post)
    ok = notify.send({"embeds": []}, webhook_url="https://discord.test/webhook")
    assert ok is False
    assert "boom" in capsys.readouterr().err


def test_parse_log_extracts_diff_and_warn_lines():
    log = "\n".join([
        "[skip] national: スクレイパー未実装（P1-3以降）",
        "[warn] top14 standings: team=x の数値欠落のため行を除外",
        "[diff] top14: signings=1 transfers=0 departures=0 first_caps=0 caps_updates=0 rounds=1",
        "[error] dup_id: a",
        "master 更新完了",
    ])
    details, warnings = notify.parse_log(log)
    assert details == ["top14: signings=1 transfers=0 departures=0 first_caps=0 caps_updates=0 rounds=1"]
    assert warnings == [
        "top14 standings: team=x の数値欠落のため行を除外",
        "dup_id: a",
    ]


def test_read_news_list(tmp_path):
    p = tmp_path / "news_changed.txt"
    p.write_text("src/content/news/top14-join-a-2026-07-18.md\n\n  \n", encoding="utf-8")
    assert notify.read_news_list(p) == ["src/content/news/top14-join-a-2026-07-18.md"]
    assert notify.read_news_list(tmp_path / "missing.txt") == []
