import pandas as pd
import json
import os
import shutil
import re

# プロジェクトのルートディレクトリを絶対パスで定義
PROJECT_ROOT = '/Users/ktamatzmoto/Desktop/rugbypicks'
CSV_PATH = os.path.join(PROJECT_ROOT, 'data_sources/final_master_data_v27_normalized.csv')
TEAM_NAMES_JP_PATH = os.path.join(PROJECT_ROOT, 'data/team_names_jp.json')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'src/content/players')
JSON_OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'public/data/players.json')

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def load_league_mapping():
    """チーム名からリーグ名への物理マッピングを作成"""
    mapping = {}
    if not os.path.exists(TEAM_NAMES_JP_PATH):
        print(f"Warning: {TEAM_NAMES_JP_PATH} not found.")
        return mapping
        
    with open(TEAM_NAMES_JP_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for league, teams in data.items():
            for official_en, team_info in teams.items():
                # 英語名、日本語名、エイリアスをすべて登録
                mapping[official_en.lower()] = league
                if 'jp' in team_info:
                    mapping[team_info['jp'].lower()] = league
                if 'aliases' in team_info:
                    for alias in team_info['aliases']:
                        mapping[alias.lower()] = league
    return mapping

def clean_team_name(team):
    """所属チーム名から括弧書きなどを除去"""
    if not team or pd.isna(team): return ""
    # 全角・半角の括弧とその中身を除去
    t = re.sub(r'（.*）|\(.*\)', '', str(team)).strip()
    return t

def generate_markdown():
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        return

    # リーグマッピングの構築
    league_map = load_league_mapping()

    # 既存のファイルを削除してクリーンアップ
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(CSV_PATH)
    players_json = []
    used_slugs = set()

    for _, row in df.iterrows():
        # 基本情報の抽出
        name_en = str(row.get('Player_Name', '') or row.get('Full_Name', '')).strip()
        name_ja = str(row.get('選手名_カタカナ', '') or row.get('Full_Name', '')).strip()
        
        # スラッグの生成（重複対応）
        base_slug = str(row.get('Scraped_Url', ''))
        if base_slug and 'all.rugby/player/' in base_slug:
            slug = base_slug.split('/')[-1]
        else:
            slug = name_en.lower().replace(' ', '-')
        
        if not slug or slug == '-' or slug == 'nan':
            slug = "player-" + str(_)
            
        original_slug = slug
        counter = 1
        while slug in used_slugs:
            counter += 1
            slug = f"{original_slug}-{counter}"
        used_slugs.add(slug)

        position = str(row.get('Position', '')).strip()
        height = str(row.get('Height', '')).replace('cm', '').strip()
        weight = str(row.get('Weight', '')).replace('kg', '').strip()
        birth_date = str(row.get('Birth_Date', '')).strip()
        age_val = row.get('Age')
        if pd.isna(age_val) or str(age_val).lower() == 'nan':
            age_val = "null"
        
        nationality = str(row.get('Nationality', '') or row.get('Country', '') or "").strip()
        birthplace = str(row.get('Birth_Place_Scraped', '')).strip()
        
        # リーグ属性の物理的補完（マッピング優先）
        csv_league = str(row.get('League', '')).strip().lower()
        current_team = str(row.get('Current_Team', '')).strip()
        cleaned_team = clean_team_name(current_team)
        
        lookup_league = league_map.get(cleaned_team.lower(), "nan")
        if lookup_league != "nan":
            final_league = lookup_league
        else:
            final_league = csv_league if csv_league and csv_league != 'nan' else "nan"
            
        # name_jaのクレンジング
        if name_ja.lower() == 'nan':
            name_ja = ""
            
        caps = str(row.get('Representative_Caps', '')).strip()
        if caps == 'nan' or caps == '0.0' or caps == '0':
            caps = ""
        
        scraped_url = str(row.get('Scraped_Url', '')).strip()
        career_history = str(row.get('キャリア遍歴', '')).strip()
        if career_history == 'nan':
            career_history = ""
            
        high_school = str(row.get('High_School', '')).strip()
        if high_school == 'nan': high_school = ""
        university = str(row.get('University', '')).strip()
        if university == 'nan': university = ""

        # Ageの数値化（"30 y/o"などの文字列に対応）
        age_clean = None
        age_val = row.get('Age')
        if pd.notna(age_val) and str(age_val).lower() != 'nan' and str(age_val).strip() != "":
            try:
                # 数字のみを抽出
                age_match = re.search(r'(\d+)', str(age_val))
                if age_match:
                    age_clean = int(age_match.group(1))
            except:
                pass
        
        # Markdown出力用の値（数値または null）
        age_for_md = age_clean if age_clean is not None else "null"

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
age: {age_for_md}
country: "{nationality}"
birth_place_scraped: "{birthplace}"
league: "{final_league}"
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
                "age": age_clean,
                "country": nationality,
                "league": final_league,
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
    print(f"Verification: {len(used_slugs)} unique slugs used.")

if __name__ == "__main__":
    generate_markdown()
