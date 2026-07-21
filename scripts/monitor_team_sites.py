#!/usr/bin/env python3
"""リーグワン全チーム公式HPの監視CLI。

  python3 scripts/monitor_team_sites.py --discover   # 公式サイトURLを取得して teams master へ反映
  python3 scripts/monitor_team_sites.py              # 全チーム公式HPを巡回し新着差分を表示
  python3 scripts/monitor_team_sites.py --division league-one-d1
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.scrape import team_sites  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="リーグワン公式HP監視")
    ap.add_argument("--discover", action="store_true", help="公式サイトURLを取得して master へ反映")
    ap.add_argument("--division", action="append", choices=list(team_sites.DIVISIONS))
    ap.add_argument("--limit", type=int, default=None, help="巡回チーム数の上限（動作確認用）")
    ap.add_argument(
        "--sources-only",
        action="store_true",
        help="リーグワン公式・日本協会・World Rugby のみ巡回（軽量・高頻度チェック用）",
    )
    ap.add_argument("--teams-only", action="store_true", help="チーム公式HPのみ巡回")
    args = ap.parse_args()

    divisions = args.division or list(team_sites.DIVISIONS)

    if args.discover:
        result = team_sites.discover_official_urls(divisions)
        for team in result["teams"]:
            print(f"{team['league']:15s} {team['name']:24s} {team['official_url']}")
        for warning in result["warnings"]:
            print(f"WARN {warning}", file=sys.stderr)
        print(f"\n公式サイトURL: {len(result['teams'])}件")
        return 0

    report = team_sites.monitor(
        divisions,
        limit=args.limit,
        teams=not args.sources_only,
        sources=not args.teams_only,
    )

    # 読者の関心が最も高い選手動向を先頭に出す。
    label = {"roster": "選手動向", "squad": "代表招集", "injury": "負傷・復帰"}
    if report.get("highlights"):
        print("=== 注目ニュース（選手の加入・退団・代表招集） ===")
        for item in report["highlights"]:
            print(f"  [{label[item['category']]}] {item['date']} {item['source']}")
            print(f"    {item['title'][:70]}")
            print(f"    {item['url']}")
        print()

    total_new = 0
    renames: list[tuple[str, dict]] = []
    for team in report["teams"]:
        mark = {"ok": "OK", "unreachable": "NG"}[team["status"]]
        note = "初回スナップショット" if team["first_run"] else f"新着{len(team['new_items'])}件"
        print(f"[{mark}] {team['name']:24s} 記事{team['item_count']:3d}件 / {note}")
        for item in team["new_items"][:10]:
            total_new += 1
            print(f"       - {item['date']} {item['title'][:60]}")
            print(f"         {item['url']}")
        renames.extend((team["name"], i) for i in team["rename_signals"])

    for src in report.get("sources", []):
        mark = {"ok": "OK", "unreachable": "NG"}[src["status"]]
        note = "初回スナップショット" if src.get("first_run") else f"新着{len(src['new_items'])}件"
        print(f"[{mark}] {src['name']:24s} 記事{src.get('item_count', 0):3d}件 / {note}")
        for item in src["new_items"][:10]:
            total_new += 1
            print(f"       - {item['date']} {item['title'][:60]}")
            print(f"         {item['url']}")
        renames.extend((src["name"], i) for i in src["rename_signals"])
    if renames:
        print("\n=== 改称・エンブレム関連の告知（表示名の更新要否を確認） ===")
        for source, item in renames:
            print(f"  [{source}] {item['date']} {item['title'][:70]}")
            print(f"    {item['url']}")
    for warning in report["warnings"]:
        print(f"WARN {warning}", file=sys.stderr)
    print(f"\n{report['checked_at']} / 対象{len(report['teams'])}チーム / 新着{total_new}件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
