#!/usr/bin/env python3
"""監視レポートのうち、読者の関心が高いものだけを Discord に通知する。

選手の加入・退団・代表招集・負傷復帰（highlights）と、表示名の更新が必要になる
改称告知だけを送る。単なる新着記事では通知しない（通知疲れを避けるため）。

  python3 scripts/notify_monitor.py            # 直近のレポートから通知
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import io, notify  # noqa: E402
from pipeline.scrape import team_sites  # noqa: E402

_LABEL = {"roster": "選手動向", "squad": "代表招集", "injury": "負傷・復帰"}


def _latest_report() -> dict:
    reports = sorted(team_sites.REPORT_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if not reports:
        return {}
    return io.read_json(reports[-1], default={}) or {}


def main() -> int:
    report = _latest_report()
    highlights = report.get("highlights", [])
    renames = [
        (team["name"], item)
        for team in report.get("teams", [])
        for item in team.get("rename_signals", [])
    ] + [
        (src["name"], item)
        for src in report.get("sources", [])
        for item in src.get("rename_signals", [])
    ]

    if not highlights and not renames:
        print("[notify_monitor] 通知対象なし")
        return 0

    lines = []
    for item in highlights:
        lines.append(f"[{_LABEL[item['category']]}] {item['source']} — {item['title'][:60]}")
        lines.append(item["url"])
    for source, item in renames:
        lines.append(f"[改称] {source} — {item['title'][:60]}")
        lines.append(item["url"])

    payload = notify.build_payload(
        status="success",
        title=f"公式サイト新着 {len(highlights)}件 / 改称告知 {len(renames)}件",
        details=lines,
        news=[],
        warnings=[],
    )
    notify.send(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
