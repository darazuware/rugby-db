import pandas as pd
import json
import os
import shutil
import re

# プロジェクトのルートディレクトリを絶対パスで定義
PROJECT_ROOT = '/Users/ktamatzmoto/Desktop/rugbypicks'
CSV_PATH = os.path.join(PROJECT_ROOT, 'data_sources/final_master_data_v27_normalized.csv')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'src/content/players')
JSON_OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'public/data/players.json')

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def generate_markdown():
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        return

    # 既存のファイルを削除してクリーンアップ
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(CSV_PATH)
    players_json = []

    for _, row in df.iterrows():
        # 基本情報の抽出
        name_en = str(row.get('Player_Name', '') or row.get('Full_Name', '')).strip()
        name_ja = str(row.get('選手名_カタカナ', '')).strip()
        slug = str(row.get('Scraped_Url', '')).split('/')[-1] if pd.notna(row.get('Scraped_Url')) else ""
        
        if not slug or slug.lower() == 'nan':
            # slugがない場合は名前から生成
            slug = name_en.lower().replace(' ', '-')
            if not slug or slug == '-':
                continue

        position = str(row.get('Position', '')).strip()
        height = str(row.get('Height', '')).replace('cm', '').strip()
        weight = str(row.get('Weight', '')).replace('kg', '').strip()
        birth_date = str(row.get('Birth_Date', '')).strip()
        age_val = row.get('Age')
        if pd.isna(age_val):
            age_val = "null"
        
        nationality = str(row.get('Country', '') or row.get('国籍', '')).strip()
        birthplace = str(row.get('Birth_Place_Scraped', '')).strip()
        league = str(row.get('League', '')).strip()
        current_team = str(row.get('Current_Team', '')).strip()
        caps = str(row.get('Representative_Caps', '')).strip()
        if caps == 'nan' or caps == '0.0' or caps == '0':
            caps = ""
        
        scraped_url = str(row.get('Scraped_Url', '')).strip()
        career_history = str(row.get('キャリア遍歴', '')).strip()
        if career_history == 'nan':
            career_history = ""
            
        # 学歴情報の抽出
        high_school = str(row.get('High_School', '')).strip()
        if high_school == 'nan': high_school = ""
        university = str(row.get('University', '')).strip()
        if university == 'nan': university = ""

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
birth_place_scraped: "{birthplace}"
league: "{league}"
team: "{current_team}"
caps: "{caps}"
high_school: "{high_school}"
university: "{university}"
scraped_url: "{scraped_url}"
---

## キャリア遍歴
{career_history}
"""
        
        file_path = os.path.join(OUTPUT_DIR, f"{slug}.md")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # JSON用データの作成
        players_json.append({
            "slug": slug,
            "data": {
                "title": f"{name_en} | {name_ja}",
                "name_en": name_en,
                "name_ja": name_ja,
                "position": position,
                "height": height,
                "weight": weight,
                "age": None if age_val == "null" else int(float(age_val)),
                "country": nationality,
                "league": league,
                "team": current_team,
                "caps": caps,
                "high_school": high_school,
                "university": university
            }
        })

    # players.json の出力
    os.makedirs(os.path.dirname(JSON_OUTPUT_PATH), exist_ok=True)
    with open(JSON_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(players_json, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(df)} player files and {JSON_OUTPUT_PATH}")

if __name__ == "__main__":
    generate_markdown()
