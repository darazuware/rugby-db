import csv
import os
import re
from datetime import datetime
from team_utils import linkify_career

# 設定
CSV_PATH = 'data_sources/top14_full.csv'
OUTPUT_DIR = 'src/content/players'
LEAGUE = 'top14'
CURRENT_YEAR = 2026

def calculate_age(birth_date_str):
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

def main():
    if not os.path.exists(CSV_PATH):
        print(f"CSV not found: {CSV_PATH}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    count = 0
    with open(CSV_PATH, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Slug 生成
            name_en = row['英語名']
            scraped_url = row.get('Scraped_Url', '')
            url_id = scraped_url.split('/')[-1] if scraped_url else f"player-t14-{i+20000}"
            slug = f"{url_id}-t14"
            
            birth_date = row['生年月日'].replace('.', '-')
            age = calculate_age(row['生年月日'])
            country = row['International_Caps']
            
            # キャリア集約
            career_parts = row['キャリア遍歴'].split(' -> ')
            parsed = []
            for cp in career_parts:
                match = re.search(r'^(.+?) \(([\d\s\?\*]+) - ([\d\s\?\*]*)\)$', cp.strip())
                if not match:
                    match = re.search(r'^(.+?) \(([\d\s\?\*]+)\)$', cp.strip())
                
                if match:
                    team = match.group(1).strip()
                    s_nums = re.findall(r'\d+', match.group(2))
                    e_nums = re.findall(r'\d+', match.group(3)) if len(match.groups()) > 2 else s_nums
                    start_val = int(s_nums[0]) if s_nums else 9999
                    end_val = int(e_nums[0]) if e_nums else start_val
                    parsed.append({'team': team, 'start': start_val, 'end': end_val})
            
            if not parsed:
                career_md = "\n".join([f"- {c.strip()}" for c in career_parts])
                joined_year = None
            else:
                summary_dict = {}
                for entry in parsed:
                    t = entry['team']
                    if t not in summary_dict:
                        summary_dict[t] = {'start': entry['start'], 'end': entry['end']}
                    else:
                        summary_dict[t]['start'] = min(summary_dict[t]['start'], entry['start'])
                        summary_dict[t]['end'] = max(summary_dict[t]['end'], entry['end'])
                
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
                career_md = "\n".join(lines)
                joined_year = result_list[-1]['start']

            # キャリア履歴のチーム名をリンク化
            linked_career_md = linkify_career(career_md)

            content = f"""---
title: "{row['選手名']}"
name_en: "{row['英語名']}"
position: "{row['ポジション']}"
team: "{row['所属チーム']}"
height: "{row['身長']}"
weight: "{row['体重']}"
birth_date: "{birth_date}"
age: {age if age is not None else 'null'}
high_school: ""
university: ""
caps: "{row['代表キャップ数']}"
league: "{LEAGUE}"
joined_year: {joined_year if joined_year is not None else 'null'}
country: "{country}"
---

{linked_career_md}
"""
            with open(os.path.join(OUTPUT_DIR, f"{slug}.md"), 'w', encoding='utf-8') as wf:
                wf.write(content)
            count += 1

    print(f"Generated {count} Markdown files in {OUTPUT_DIR} from {CSV_PATH}")

if __name__ == "__main__":
    main()
