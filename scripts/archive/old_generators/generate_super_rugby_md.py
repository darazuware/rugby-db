import csv
import os
import re
from datetime import datetime
from team_utils import linkify_career

# 設定
CSV_PATH = 'data_sources/super_rugby_full.csv'
if not os.path.exists(CSV_PATH):
    CSV_PATH = 'data_sources/super_rugby_sample.csv' # フォールバック

OUTPUT_DIR = 'src/content/players'
CURRENT_YEAR = 2026

def calculate_age(birth_date_str):
    """生年月日(YYYY.MM.DD)から現在の年齢を算出する"""
    if not birth_date_str or str(birth_date_str).lower() == 'nan':
        return None
    try:
        date_str = birth_date_str.replace('.', '-')
        if len(date_str) == 4:
            return CURRENT_YEAR - int(date_str)
        birth_date = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except Exception:
        return None

def generate_slug(name_en, player_id):
    if not name_en or str(name_en).lower() == 'nan':
        return f"sr-player-{player_id}"
    slug = str(name_en).lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return f"{slug}-sr-{player_id}"

def format_career(career_str):
    if not career_str or str(career_str).lower() == 'nan':
        return "", None
    
    parts = [p.strip() for p in career_str.split('->')]
    parsed = []
    
    for p in parts:
        match = re.search(r'^(.+?) \(([\d\s\?\*]+) - ([\d\s\?\*]*)\)$', p)
        if not match:
            match = re.search(r'^(.+?) \(([\d\s\?\*]+)\)$', p)
        
        if match:
            team = match.group(1).strip()
            start_str = match.group(2).strip()
            end_str = match.group(3).strip() if len(match.groups()) > 2 else start_str
            
            s_nums = re.findall(r'\d+', str(start_str))
            e_nums = re.findall(r'\d+', str(end_str))
            
            start_val = int(s_nums[0]) if s_nums else 9999
            end_val = int(e_nums[0]) if e_nums else start_val
            
            parsed.append({
                'team': team,
                'start': start_val,
                'end': end_val
            })

    if not parsed:
        lines = [f"- {p}" for p in parts]
        return "\n".join(lines), None

    # チームごとに集約 (League One スタイル)
    summary_dict = {}
    for entry in parsed:
        t = entry['team']
        if t not in summary_dict:
            summary_dict[t] = {'start': entry['start'], 'end': entry['end']}
        else:
            summary_dict[t]['start'] = min(summary_dict[t]['start'], entry['start'])
            summary_dict[t]['end'] = max(summary_dict[t]['end'], entry['end'])

    # 開始年でソート
    result_list = []
    for team, data in summary_dict.items():
        result_list.append({'team': team, 'start': data['start'], 'end': data['end']})
    result_list.sort(key=lambda x: x['start'])

    lines = []
    for r in result_list:
        is_latest = (r == result_list[-1])
        if is_latest and r['end'] >= CURRENT_YEAR:
            lines.append(f"- {r['team']} ({r['start']} - )")
        elif r['start'] == r['end']:
            lines.append(f"- {r['team']} ({r['start']})")
        else:
            lines.append(f"- {r['team']} ({r['start']} - {r['end']})")

    return "\n".join(lines), result_list[-1]['start'] if result_list else None

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    processed_count = 0
    with open(CSV_PATH, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Slug 生成
            name_en = row['英語名']
            name_ja = row.get('選手名', name_en)
            scraped_url = row.get('Scraped_Url', '')
            url_id = scraped_url.split('/')[-1] if scraped_url else f"player-sr-{i+10000}"
            slug = f"{url_id}-sr"
            
            career_md, joined_year = format_career(row.get('Full_Career', ''))
            age = calculate_age(row.get('生年月日', ''))

            height = row.get('身長', '').replace('m', '').replace(' ', '')
            weight = row.get('体重', '').replace('kg', '').replace(' ', '')

            # キャリア履歴のチーム名をリンク化
            linked_career_md = linkify_career(career_md)

            content = f"""---
title: "{name_ja}"
name_en: "{name_en}"
position: "{row.get('ポジション', '')}"
team: "{row.get('所属チーム', '')}"
height: "{height}"
weight: "{weight}"
birth_date: "{row.get('生年月日', '')}"
age: {age if age is not None else 'null'}
high_school: "{row.get('高校', '')}"
university: "{row.get('大学', '')}"
caps: "{row.get('代表キャップ数', '')}"
league: "super-rugby"
joined_year: {joined_year if joined_year is not None else 'null'}
country: "{row.get('International_Caps', '')}"
---

{linked_career_md}
"""
            file_path = os.path.join(OUTPUT_DIR, f"{slug}.md")
            with open(file_path, 'w', encoding='utf-8') as wf:
                wf.write(content)
            processed_count += 1
                
    print(f"Generated {processed_count} Markdown files in {OUTPUT_DIR} from {CSV_PATH}")

if __name__ == "__main__":
    main()
