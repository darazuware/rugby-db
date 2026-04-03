#!/usr/bin/env python3
"""
Player data completeness audit.
Usage:
  python3 scripts/audit_players.py              # print summary table
  python3 scripts/audit_players.py --csv        # also write audit.csv with per-player gaps
  python3 scripts/audit_players.py --div top-kyushu  # filter to one division
  python3 scripts/audit_players.py --missing position  # list players missing a field
"""

import argparse
import csv
import glob
import os
import re
import sys
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYERS_DIR = os.path.join(BASE_DIR, 'src/content/players')

# Fields to audit and their display labels
# "key" fields are the most important ones (shown separately)
KEY_FIELDS = ['position', 'height', 'weight', 'team']
EXTRA_FIELDS = ['birth_date', 'age', 'university', 'high_school', 'country']
ALL_FIELDS = KEY_FIELDS + EXTRA_FIELDS


def is_empty(val: str) -> bool:
    if val is None:
        return True
    s = str(val).strip()
    return s in ('', 'null', '---', '[]', "''", '""')


def parse_frontmatter(path: str) -> dict:
    """Extract frontmatter fields from a markdown file."""
    result = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Extract YAML frontmatter block
        m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not m:
            return result
        for line in m.group(1).splitlines():
            kv = re.match(r'^(\w+):\s*(.+)$', line)
            if kv:
                key, val = kv.group(1), kv.group(2).strip().strip('"\'')
                result[key] = val
    except Exception:
        pass
    return result


def audit(div_filter=None):
    pattern = os.path.join(PLAYERS_DIR, '**/*.md')
    files = glob.glob(pattern, recursive=True)

    # division -> field -> {total, missing}
    stats = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'missing': 0}))
    # per-player missing fields
    player_gaps = []

    for fp in files:
        div = os.path.basename(os.path.dirname(fp))
        if div_filter and div != div_filter:
            continue
        fm = parse_frontmatter(fp)
        missing = []
        for field in ALL_FIELDS:
            stats[div][field]['total'] += 1
            val = fm.get(field, '')
            if is_empty(val):
                stats[div][field]['missing'] += 1
                missing.append(field)
        if missing:
            player_gaps.append({
                'file': os.path.relpath(fp, BASE_DIR),
                'div': div,
                'name': fm.get('name_ja') or fm.get('title', '?'),
                'missing': ','.join(missing),
            })

    return stats, player_gaps


def print_summary(stats):
    divs = sorted(stats.keys())
    # Header
    col_w = 14
    header = f"{'Division':<16}" + ''.join(f"{f:>{col_w}}" for f in ALL_FIELDS)
    print(header)
    print('-' * len(header))

    for div in divs:
        row = f"{div:<16}"
        for field in ALL_FIELDS:
            s = stats[div][field]
            total = s['total']
            missing = s['missing']
            if total == 0:
                row += f"{'N/A':>{col_w}}"
            else:
                pct = 100 * (total - missing) // total
                cell = f"{pct}% ({total-missing}/{total})"
                row += f"{cell:>{col_w}}"
        print(row)

    print()
    # Overall totals
    totals = defaultdict(lambda: {'total': 0, 'missing': 0})
    for div_data in stats.values():
        for field, s in div_data.items():
            totals[field]['total'] += s['total']
            totals[field]['missing'] += s['missing']
    row = f"{'TOTAL':<16}"
    for field in ALL_FIELDS:
        s = totals[field]
        total = s['total']
        missing = s['missing']
        pct = 100 * (total - missing) // total if total else 0
        cell = f"{pct}% ({total-missing}/{total})"
        row += f"{cell:>{col_w}}"
    print(row)


def write_csv(player_gaps, out_path):
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['div', 'name', 'missing', 'file'])
        writer.writeheader()
        writer.writerows(sorted(player_gaps, key=lambda r: (r['div'], r['name'])))
    print(f"\nWrote {len(player_gaps)} rows to {out_path}")


def list_missing(player_gaps, field):
    hits = [p for p in player_gaps if field in p['missing'].split(',')]
    print(f"\n{len(hits)} players missing '{field}':")
    for p in sorted(hits, key=lambda r: (r['div'], r['name'])):
        print(f"  [{p['div']}] {p['name']}")


def main():
    parser = argparse.ArgumentParser(description='Audit player data completeness')
    parser.add_argument('--csv', action='store_true', help='Write gaps to audit.csv')
    parser.add_argument('--div', help='Filter to one division')
    parser.add_argument('--missing', help='List players missing a specific field')
    args = parser.parse_args()

    stats, player_gaps = audit(div_filter=args.div)

    if not args.missing:
        print_summary(stats)

    if args.csv:
        out = os.path.join(BASE_DIR, 'audit.csv')
        write_csv(player_gaps, out)

    if args.missing:
        list_missing(player_gaps, args.missing)


if __name__ == '__main__':
    main()
