#!/usr/bin/env python3
"""
Fix player markdown files:
1. Convert height/weight from float strings ("176.0") to int strings ("176")
2. Generate missing top-kyushu markdown files from CSV
3. Fix "---" placeholder values in top-east files
"""

import os
import re
import csv
import glob

BASE_DIR = '/home/user/rugby-db'
PLAYERS_DIR = os.path.join(BASE_DIR, 'src/content/players')


def fix_float_field(value: str) -> str:
    """Convert '176.0' -> '176', '104.5' -> '105', leave '' and non-float as-is."""
    if not value:
        return value
    try:
        f = float(value)
        return str(round(int(f)))
    except (ValueError, TypeError):
        return value


def fix_height_weight_in_file(filepath: str) -> bool:
    """Fix height/weight fields in a markdown file. Returns True if changed."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    def replace_field(field: str, text: str) -> str:
        pattern = rf'^({field}:\s*")([^"]+)(")$'
        def replacer(m):
            val = m.group(2)
            fixed = fix_float_field(val)
            return f'{m.group(1)}{fixed}{m.group(3)}'
        return re.sub(pattern, replacer, text, flags=re.MULTILINE)

    content = replace_field('height', content)
    content = replace_field('weight', content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def fix_placeholder_dash_in_file(filepath: str) -> bool:
    """Replace '---' placeholder values with '' in markdown files."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Replace fields like: field: "---"  ->  field: ""
    # But keep the title field's "---" as is if combined (e.g., "--- | 眞野拓也")
    def replace_dash(m):
        field = m.group(1)
        # Don't touch title if it has actual content after ---
        return f'{field}: ""'

    pattern = r'^((?:name_en|position|caps|league_one_caps|junior_high_school|rugby_school)):\s*"---"$'
    content = re.sub(pattern, replace_dash, content, flags=re.MULTILINE)

    # Fix title: "--- | 眞野拓也" -> extract the actual name
    def fix_title(m):
        name = m.group(1).strip()
        return f'title: "{name}"'

    content = re.sub(r'^title:\s*"---\s*\|\s*(.+)"$', fix_title, content, flags=re.MULTILINE)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def make_kyushu_md(row: dict) -> str:
    name = row['Full_Name'].strip()
    position = row['Position'].strip() if row['Position'].strip() else ''
    age = row['Age'].strip() if row['Age'].strip() else ''
    height = fix_float_field(row['Height'].strip()) if row['Height'].strip() else ''
    weight = fix_float_field(row['Weight'].strip()) if row['Weight'].strip() else ''
    university = row['University'].strip() if row['University'].strip() else ''
    team = row['Team'].strip() if row['Team'].strip() else ''
    scraped_url = row['Scraped_Url'].strip() if row['Scraped_Url'].strip() else ''

    age_val = f'{age}' if age else 'null'

    return f'''---
title: "{name}"
name_en: ""
name_ja: "{name}"
slug: "{name}"
position: "{position}"
height: "{height}"
weight: "{weight}"
birth_date: ""
age: {age_val}
country: ""
birth_place_scraped: ""
league: "top-kyushu"
team: "{team}"
caps: ""
high_school: ""
university: "{university}"
junior_high_school: ""
rugby_school: ""
scraped_url: "{scraped_url}"
league_one_caps: ""
career_history_json: '[]'
category: "top-kyushu"
---

## キャリア遍歴
'''


def main():
    # --- Step 1: Fix height/weight in ALL player markdown files ---
    print("=== Step 1: Fix height/weight formatting ===")
    all_md = glob.glob(os.path.join(PLAYERS_DIR, '**/*.md'), recursive=True)
    fixed_count = 0
    for fp in all_md:
        if fix_height_weight_in_file(fp):
            fixed_count += 1
            print(f'  Fixed: {fp}')
    print(f'Total files fixed (height/weight): {fixed_count}')

    # --- Step 2: Fix "---" placeholders in top-east ---
    print("\n=== Step 2: Fix '---' placeholders in top-east ===")
    east_md = glob.glob(os.path.join(PLAYERS_DIR, 'top-east/*.md'))
    placeholder_fixed = 0
    for fp in east_md:
        if fix_placeholder_dash_in_file(fp):
            placeholder_fixed += 1
    print(f'Total files fixed (placeholders): {placeholder_fixed}')

    # --- Step 3: Generate missing top-kyushu markdown files ---
    print("\n=== Step 3: Generate missing top-kyushu files ===")
    kyushu_dir = os.path.join(PLAYERS_DIR, 'top-kyushu')
    existing = set(os.path.splitext(f)[0] for f in os.listdir(kyushu_dir))

    csv_path = os.path.join(BASE_DIR, 'data_sources/top_kyushu_players.csv')
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    created = 0
    updated = 0
    for row in rows:
        name = row['Full_Name'].strip()
        if not name:
            continue

        filepath = os.path.join(kyushu_dir, f'{name}.md')
        content = make_kyushu_md(row)

        if name not in existing:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            created += 1
            print(f'  Created: {name}')
        else:
            # Update existing file: fix height/weight and fill missing fields
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_content = f.read()

            # Fix height/weight
            new_content = existing_content
            if fix_height_weight_in_file(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    new_content = f.read()

            # Fill in missing team if empty
            if row['Team'].strip():
                new_content = re.sub(
                    r'^(team:\s*")("\s*)$',
                    f'team: "{row["Team"].strip()}"',
                    new_content,
                    flags=re.MULTILINE
                )

            if new_content != existing_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                updated += 1

    print(f'Created: {created}, Updated: {updated}')
    print(f'\nDone! Total top-kyushu players now: {len(os.listdir(kyushu_dir))}')


if __name__ == '__main__':
    main()
