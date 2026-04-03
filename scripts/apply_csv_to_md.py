#!/usr/bin/env python3
"""
CSV → Markdownファイル 汎用アップデーター

スクレイピングスクリプトが出力したCSVを読み込み、
既存のmdファイルの空フィールドを上書きする。

使い方:
  # top-eastのCSVをmdに反映（position/height/weightを補完）
  python3 scripts/apply_csv_to_md.py --csv data_sources/top_east_players.csv --div top-east

  # top-kyushuのCSVをmdに反映
  python3 scripts/apply_csv_to_md.py --csv data_sources/top_kyushu_players.csv --div top-kyushu

  # top-west-a
  python3 scripts/apply_csv_to_md.py --csv data_sources/top_west_players.csv --div top-west-a

  # 確認のみ（ファイルを変更しない）
  python3 scripts/apply_csv_to_md.py --csv data_sources/top_east_players.csv --div top-east --dry-run

  # 変更ログをCSVに保存
  python3 scripts/apply_csv_to_md.py --csv data_sources/top_east_players.csv --div top-east --log changes.csv

CSVの列名はどちらの形式にも対応:
  - top-east形式: name_ja, position, height, weight, birth_date, university, high_school ...
  - top-kyushu形式: Full_Name, Position, Height, Weight, University ...
"""

import argparse
import csv
import glob
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYERS_DIR = os.path.join(BASE_DIR, 'src/content/players')

# CSVの列名→mdフィールド名のマッピング（大文字小文字両対応）
FIELD_MAP = {
    # top-east / top-west 形式
    'name_ja': 'name_ja',
    'title': 'name_ja',  # フォールバック用
    'position': 'position',
    'height': 'height',
    'weight': 'weight',
    'birth_date': 'birth_date',
    'age': 'age',
    'university': 'university',
    'high_school': 'high_school',
    'junior_high_school': 'junior_high_school',
    'birth_place_scraped': 'birth_place_scraped',
    'country': 'country',
    'team': 'team',
    # top-kyushu 形式（大文字）
    'full_name': 'name_ja',
    'Full_Name': 'name_ja',
    'Position': 'position',
    'Height': 'height',
    'Weight': 'weight',
    'University': 'university',
    'Age': 'age',
    'Team': 'team',
}

# 補完対象フィールド（空のときだけ更新する）
UPDATABLE_FIELDS = {
    'position', 'height', 'weight', 'birth_date', 'age',
    'university', 'high_school', 'junior_high_school',
    'birth_place_scraped', 'country', 'team',
}


def is_empty(val: str) -> bool:
    return str(val).strip() in ('', 'null', '---', "''", '""', 'None')


def parse_frontmatter(path: str) -> tuple[dict, str]:
    """フロントマターを解析して (fields, full_content) を返す"""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    fields = {}
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            kv = re.match(r'^(\w+):\s*(.+)$', line)
            if kv:
                key = kv.group(1)
                val = kv.group(2).strip().strip('"\'')
                fields[key] = val
    return fields, content


def set_field(content: str, field: str, value: str) -> str:
    """フロントマター内のフィールド値を置換する"""
    # height/weight は整数に丸める
    if field in ('height', 'weight'):
        try:
            value = str(round(float(value)))
        except (ValueError, TypeError):
            pass

    # ageはquoteなしの数値フィールド
    if field == 'age':
        try:
            int_val = str(int(float(value)))
            pattern = rf'^(age:\s*)(.+)$'
            return re.sub(pattern, rf'\g<1>{int_val}', content, flags=re.MULTILINE)
        except (ValueError, TypeError):
            return content

    # 通常の文字列フィールド
    pattern = rf'^({re.escape(field)}:\s*")[^"]*(")'
    if re.search(pattern, content, re.MULTILINE):
        return re.sub(pattern, rf'\g<1>{value}\g<2>', content, flags=re.MULTILINE)
    return content


def normalize_name(name: str) -> str:
    """名前を正規化（スペース除去・全角統一）"""
    return name.replace(' ', '').replace('　', '').replace('-', '').strip()


def load_csv(csv_path: str) -> list[dict]:
    """CSVを読み込み、nameキーを正規化して返す"""
    rows = []
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # name_jaキーを統一
            name_raw = (
                row.get('name_ja') or row.get('Full_Name') or
                row.get('title') or ''
            ).strip()
            if not name_raw:
                continue
            row['_name_normalized'] = normalize_name(name_raw)
            rows.append(row)
    return rows


def build_name_index(csv_rows: list[dict]) -> dict[str, dict]:
    """正規化した名前 → CSVデータ の辞書を作成"""
    index = {}
    for row in csv_rows:
        key = row['_name_normalized']
        if key:
            index[key] = row
    return index


def process_division(div: str, csv_index: dict, dry_run: bool) -> list[dict]:
    """ディビジョンのmdファイルを処理してchangeリストを返す"""
    md_dir = os.path.join(PLAYERS_DIR, div)
    if not os.path.isdir(md_dir):
        print(f'ERROR: directory not found: {md_dir}')
        sys.exit(1)

    md_files = sorted(glob.glob(os.path.join(md_dir, '*.md')))
    changes = []

    for fp in md_files:
        fields, content = parse_frontmatter(fp)
        name_raw = fields.get('name_ja') or fields.get('title', '')
        key = normalize_name(name_raw)

        csv_row = csv_index.get(key)
        if not csv_row:
            continue  # CSV側に該当なし

        new_content = content
        file_changes = []

        for csv_col, md_field in FIELD_MAP.items():
            if md_field not in UPDATABLE_FIELDS:
                continue
            csv_val = csv_row.get(csv_col, '').strip()
            if not csv_val or is_empty(csv_val):
                continue
            md_val = fields.get(md_field, '')
            if not is_empty(md_val):
                continue  # mdに値がある場合はスキップ

            new_content = set_field(new_content, md_field, csv_val)
            file_changes.append({
                'file': os.path.relpath(fp, BASE_DIR),
                'name': name_raw,
                'field': md_field,
                'old': md_val,
                'new': csv_val,
            })

        if file_changes:
            changes.extend(file_changes)
            if not dry_run:
                with open(fp, 'w', encoding='utf-8') as f:
                    f.write(new_content)

    return changes


def main():
    parser = argparse.ArgumentParser(description='Apply CSV data to player markdown files')
    parser.add_argument('--csv', required=True, help='Source CSV file path')
    parser.add_argument('--div', required=True,
                        help='Division directory name (e.g. top-east, top-kyushu, top-west-a)')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without writing files')
    parser.add_argument('--log', default='', help='Save change log to this CSV path')
    args = parser.parse_args()

    csv_path = args.csv if os.path.isabs(args.csv) else os.path.join(BASE_DIR, args.csv)
    if not os.path.exists(csv_path):
        print(f'ERROR: CSV not found: {csv_path}')
        sys.exit(1)

    print(f'Loading CSV: {csv_path}')
    csv_rows = load_csv(csv_path)
    csv_index = build_name_index(csv_rows)
    print(f'  {len(csv_index)} players in CSV')

    mode = '[DRY RUN] ' if args.dry_run else ''
    print(f'{mode}Processing division: {args.div}')
    changes = process_division(args.div, csv_index, args.dry_run)

    # サマリ表示
    field_counts: dict[str, int] = {}
    for c in changes:
        field_counts[c['field']] = field_counts.get(c['field'], 0) + 1

    print(f'\n{mode}Results: {len(changes)} fields updated')
    for field, count in sorted(field_counts.items(), key=lambda x: -x[1]):
        print(f'  {field}: {count} players')

    if args.dry_run:
        print('\nSample changes:')
        for c in changes[:10]:
            print(f'  [{c["name"]}] {c["field"]}: "" → "{c["new"]}"')

    if args.log:
        log_path = args.log if os.path.isabs(args.log) else os.path.join(BASE_DIR, args.log)
        with open(log_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['file', 'name', 'field', 'old', 'new'])
            writer.writeheader()
            writer.writerows(changes)
        print(f'\nChange log saved to: {log_path}')


if __name__ == '__main__':
    main()
