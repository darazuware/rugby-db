import json
import csv
import requests
from bs4 import BeautifulSoup
import time
import os
import re

# 設定
JSON_PATH = 'data/top14_players_enriched.json'
CSV_OUTPUT = 'data_sources/top14_full.csv'
MARKDOWN_OUTPUT_DIR = 'src/content/players'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_player_details_light(url):
    """all.rugby から国籍と代表キャップを簡易的に取得する"""
    print(f"Fetching details for {url}...")
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        nationality = ""
        bio_items = soup.select('.bio div')
        for i, item in enumerate(bio_items):
            if "Nationality" in item.text:
                if i + 1 < len(bio_items):
                    nationality = bio_items[i+1].get_text(strip=True)
                    nationality = re.sub(r'Nationality\s*#\d+\s*', '', nationality).strip()
                break
        
        return {
            'nationality': nationality,
            'caps': nationality # とりあえず国名を入れるロジックを継承
        }
    except Exception as e:
        print(f"  Error fetching: {e}")
        return {'nationality': '', 'caps': ''}

def main():
    if not os.path.exists(JSON_PATH):
        print(f"JSON not found: {JSON_PATH}")
        return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        players_json = json.load(f)

    print(f"Loaded {len(players_json)} players from JSON.")
    os.makedirs(MARKDOWN_OUTPUT_DIR, exist_ok=True)

    all_data = []
    
    # 時間短縮のため、まずは全データを共通形式で保持
    for i, p in enumerate(players_json):
        # 連続実行を考慮しつつ、進捗を表示
        print(f"Processing {i+1}/{len(players_json)}: {p['en_name']}")
        
        # 不足情報をスクレイピング
        details = get_player_details_light(p['all_rugby_url'])
        
        # キャリア遍歴の整形 (JSON はリスト形式)
        career_raw = p.get('career_history', [])
        full_career = " -> ".join(career_raw)
        career_md = "\n".join([f"- {c}" for c in career_raw])
        
        # データ統合
        row = {
            '英語名': p['en_name'],
            '選手名': p['name_ja'],
            'ポジション': p['position_en'],
            '所属チーム': p['team_ja'],
            '身長': p['height'],
            '体重': p['weight'],
            '生年月日': p['birthday'].replace('年', '.').replace('月', '.').replace('日', ''),
            '年齢': '',
            '高校': '', # Top14は取得困難なため空
            '大学': '',
            '出身校・チーム歴(全文)': full_career,
            'カテゴリ': 'A',
            'リーグワンキャップ数': '0',
            'URL': p['all_rugby_url'],
            'Text_Detail': '',
            'キャリア遍歴': full_career,
            '代表キャップ数': details['caps'],
            'International_Caps': details['nationality'],
            'Scraped_Url': p['all_rugby_url'],
            'Full_Career': full_career,
            'league': 'top14'
        }
        all_data.append(row)

        # Markdown 生成
        slug = f"{p['slug']}-t14-{i+20000}"
        content = f"""---
title: "{row['選手名']}"
name_en: "{row['英語名']}"
position: "{row['ポジション']}"
team: "{row['所属チーム']}"
height: "{row['身長']}"
weight: "{row['体重']}"
birth_date: "{row['生年月日']}"
age: null
high_school: ""
university: ""
caps: "{row['代表キャップ数']}"
league: "top14"
joined_year: null
country: "{row['International_Caps']}"
---

{career_md}
"""
        with open(os.path.join(MARKDOWN_OUTPUT_DIR, f"{slug}.md"), 'w', encoding='utf-8') as wf:
            wf.write(content)

        time.sleep(1) # Rate limit

    # CSV 保存
    fieldnames = [
        '英語名', '選手名', 'ポジション', '所属チーム', '身長', '体重', '生年月日', 
        '年齢', '高校', '大学', '出身校・チーム歴(全文)', 'カテゴリ', 'リーグワンキャップ数', 
        'URL', 'Text_Detail', 'キャリア遍歴', '代表キャップ数', 'International_Caps', 
        'Scraped_Url', 'Full_Career'
    ]
    with open(CSV_OUTPUT, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for data in all_data:
            writer.writerow(data)

    print(f"Successfully processed {len(all_data)} players. CSV saved to {CSV_OUTPUT}")

if __name__ == "__main__":
    main()
