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
    scraped_url = row.get('Scraped_Url', '')
    name_en = row.get('Full_Name', '') or row.get('英語名', '')
    
    slug = PlayerDataProcessor.generate_player_slug(name_en, index + 1, scraped_url)
    
    # Helper to clean nan
    def clean_val(val, default=''):
        v = str(val).strip()
        if not v or v.lower() == 'nan':
            return default
        return v

    # 既存のロジックでメタデータを抽出
    name_ja = clean_val(row.get('選手名_カタカナ', '') or row.get('選手名', ''))
    position = clean_val(row.get('Position', '') or row.get('ポジション', ''))
    height = clean_val(row.get('Height', '') or row.get('身長', ''), '0')
    weight = clean_val(row.get('Weight', '') or row.get('体重', ''), '0')
    birth_date = clean_val(row.get('Birth_Date', '') or row.get('生年月日', ''))
    age = row.get('Age', '') or row.get('年齢', '')
    nationality = clean_val(row.get('Nationality', '') or row.get('国籍', ''))
    league = clean_val(row.get('League', '') or row.get('リーグ', ''))
    current_team = clean_val(row.get('Current_Team', '') or row.get('所属チーム', ''))
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
        
    # Markdown生成
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
    
    print(f"Generating markdown for {len(df)} players...")
    count = 0
    for i, row in df.iterrows():
        try:
            generate_markdown(row, i)
            count += 1
        except Exception as e:
            print(f"Error at index {i}: {e}")
            
    print(f"Successfully generated {count} player pages.")

if __name__ == "__main__":
    main()
