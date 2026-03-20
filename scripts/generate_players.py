import pandas as pd
import os
import re
import shutil
import glob
import json
import subprocess
from datetime import datetime
from team_utils import get_team_info, get_team_link
from player_utils import PlayerDataProcessor

# 設定
CSV_PATH = 'data_sources/final_master_data_v27_normalized.csv'
OUTPUT_DIR = 'src/content/players/'

def generate_markdown(row, index):
    # player_utils の共通ロジックを使用
    scraped_url = str(row.get('Scraped_Url', '')).strip()
    name_en = str(row.get('Full_Name', '') or row.get('英語名', '') or row.get('Player_Name', '')).strip()
    
    # スラッグ生成 (Scraped_Url があれば優先される)
    slug = PlayerDataProcessor.generate_player_slug(name_en, index + 1, scraped_url)
    
    # Helper to clean nan
    def clean_val(val, default=''):
        v = str(val).strip()
        if not v or v.lower() == 'nan' or v == '---':
            return default
        return v

    # 既存のロジックでメタデータを抽出
    name_ja = clean_val(row.get('選手名_カタカナ', '') or row.get('選手名', ''))
    position = clean_val(row.get('Position', '') or row.get('ポジション', ''))
    height = clean_val(row.get('Height', '') or row.get('身長', ''), '0')
    weight = clean_val(row.get('Weight', '') or row.get('体重', ''), '0')
    birth_date = clean_val(row.get('Birth_Date', '') or row.get('生年月日', ''))
    age = row.get('Age', '')
    nationality = clean_val(row.get('Nationality', '') or row.get('国籍', ''))
    league_raw = clean_val(row.get('League', '') or row.get('リーグ', ''))
    
    # リーグ名の正規化 (Astro 側の URL/slug 形式に統一)
    league_map = {
        'League One': 'league-one',
        'LeagueOne': 'league-one',
        'Super Rugby': 'super-rugby',
        'Top 14': 'top14',
        'Top14': 'top14',
        'URC': 'urc',
        'MLR': 'mlr',
        'Premiership': 'premiership'
    }
    league = league_map.get(league_raw, league_raw.lower().replace(' ', '-'))
    
    # チーム名の正規化 (team_utils を使用)
    from team_utils import get_team_info
    raw_team = clean_val(row.get('Current_Team', '') or row.get('所属チーム', ''))
    team_info = get_team_info(raw_team)
    current_team = team_info['jp'] if team_info else raw_team
    
    caps = clean_val(row.get('Representative_Caps', '') or row.get('代表キャップ数', ''), '0')
    
    # スコアや戦績などの詳細 (Text_Detail, Carrier)
    history = row.get('キャリア遍歴', '') or row.get('Full_Career', '')
    
    # 数値変換 (Astro Schema 整合性)
    try:
        age_val = float(age) if age and str(age).lower() != 'nan' else 'null'
        if age_val != 'null':
            age_val = int(age_val)
    except:
        age_val = 'null'
        
    # 出身地データ (マージ後の列)
    birthplace = clean_val(row.get('birth_place_scraped', ''))
    
    if "beauden-barrett" in str(slug).lower() or "beauden" in name_en.lower():
        print(f"DEBUG [Beauden]: slug={slug}, team={current_team}, league={league}, url={scraped_url}")

    if "zander-fagerson" in str(scraped_url).lower():
        print(f"DEBUG [Zander]: slug={slug}, birthplace={birthplace}, team={current_team}, url={scraped_url}")

    # Markdown生成
    # ... (content strings)
    content = f"""---
title: "{name_en} | {name_ja}"
name_en: "{name_en}"
name_ja: "{name_ja}"
slug: "{slug}"
position: "{position}"
height: "{height}"
weight: "{weight}"
birth_date: "{birth_date}"
age: {age_val}
country: "{nationality}"
birth_place_scraped: "{birthplace}"
league: "{league}"
team: "{current_team}"
caps: "{caps}"
scraped_url: "{scraped_url}"
---

## キャリア遍歴
{history}
"""
    
    file_path = os.path.join(OUTPUT_DIR, f"{slug}.md")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return slug

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    else:
        # 幽霊ページ削除
        shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR)
        
    print(f"Loading CSV from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    
    # マッピング用辞書の初期化
    birthplace_map = {}
    nat_map = {}
    
    # スクレイピング済みの出身地データ
    SCRAPED_CSV = 'data_sources/overseas_birthplaces_scraped.csv'
    if os.path.exists(SCRAPED_CSV):
        print(f"Loading scraped birthplace data from {SCRAPED_CSV}...")
        scraped_df = pd.read_csv(SCRAPED_CSV)
        # 正規化
        scraped_df['scraped_url'] = scraped_df['scraped_url'].astype(str).str.strip().str.lower()
        
        # 辞書作成
        for _, row_s in scraped_df.iterrows():
            url = row_s['scraped_url']
            if url and url != 'nan':
                birthplace_map[url] = str(row_s.get('place_of_birth', '')).strip()
                nat_map[url] = str(row_s.get('scraped_nationality', '')).strip()
        
        print(f"Loaded {len(birthplace_map)} birthplace mappings.")

    print(f"Generating markdown for {len(df)} players...")
    count = 0
    for i, row in df.iterrows():
        try:
            # 各行にマッピングデータを注入
            s_url = str(row.get('Scraped_Url', '')).strip().lower()
            row_dict = row.to_dict()
            if s_url in birthplace_map:
                row_dict['birth_place_scraped'] = birthplace_map[s_url]
                if nat_map[s_url] and nat_map[s_url].lower() != 'nan':
                     row_dict['Nationality'] = nat_map[s_url]
            
            generate_markdown(row_dict, i)
            count += 1
        except Exception as e:
            print(f"Error at index {i}: {e}")
            
    print(f"Successfully generated {count} player pages.")

if __name__ == "__main__":
    main()
