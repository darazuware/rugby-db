import pandas as pd
import json
import os
import shutil
import re
from datetime import datetime
from player_utils import PlayerDataProcessor

# 物理基準日 (2026-03-20)
REFERENCE_DATE = datetime(2026, 3, 20)

# プロジェクトのルートディレクトリを絶対パスで定義
PROJECT_ROOT = '/Users/ktamatzmoto/Desktop/rugbypicks'
CSV_PATH = os.path.join(PROJECT_ROOT, 'data_sources/final_master_data_v27_normalized.csv')
TEAM_NAMES_JP_PATH = os.path.join(PROJECT_ROOT, 'data/team_names_jp.json')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'src/content/players')
JSON_OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'public/data/players.json')

def validate_and_clean_stat(val, type_name='height'):
    if not val or pd.isna(val): return ""
    v_str = str(val).strip()
    if '/' in v_str: return ""
    v_clean = re.sub(r'[^0-9.]', '', v_str)
    if not v_clean: return ""
    try:
        vf = float(v_clean)
        if type_name == 'height':
            if vf < 140 or vf > 220: return ""
        else:
            if vf < 50 or vf > 160: return ""
        return str(vf)
    except:
        return ""

def calculate_age(birth_date_str):
    """生年月日（YYYY.MM.DD or YYYY-MM-DD）から年齢を算出"""
    if not birth_date_str or pd.isna(birth_date_str):
        return None
    try:
        # 形式の正規化（ドットをハイフンに置換）
        date_str = str(birth_date_str).replace('.', '-').strip()
        # YYYY-MM-DD
        birth_date = datetime.strptime(date_str, '%Y-%m-%d')
        age = REFERENCE_DATE.year - birth_date.year - ((REFERENCE_DATE.month, REFERENCE_DATE.day) < (birth_date.month, birth_date.day))
        return age
    except Exception as e:
        # YYYYのみの場合などのフォールバック
        match = re.search(r'(\d{4})', str(birth_date_str))
        if match:
            year = int(match.group(1))
            return REFERENCE_DATE.year - year
    return None

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
    missing_nationality = []

    for _, row in df.iterrows():
        # 基本情報の抽出 (PlayerDataProcessor.get_safe_attr を使用して NaN 漏れを物理排除)
        name_en = PlayerDataProcessor.get_safe_attr(row, 'Player_Name', default=PlayerDataProcessor.get_safe_attr(row, 'Full_Name'))
        name_ja = PlayerDataProcessor.get_safe_attr(row, 'Full_Name')
        if not name_ja:
            name_ja = PlayerDataProcessor.get_safe_attr(row, '選手名_カタカナ')
        
        # 名前がいずれも空の場合の最終防御
        if not name_en:
            name_en = "Unknown Player"
        if not name_ja:
            name_ja = name_en

        scraped_url = PlayerDataProcessor.get_safe_attr(row, 'Scraped_Url').lower()
        
        # スラッグの生成（重複対応）
        if scraped_url and 'all.rugby/player/' in scraped_url:
            slug = scraped_url.split('/')[-1]
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
        
        league_val = PlayerDataProcessor.get_safe_attr(row, 'League').lower()
        if league_val == 'mlr':
            continue

        position = PlayerDataProcessor.get_safe_attr(row, 'Position')
        height = validate_and_clean_stat(row.get('Height', ''), 'height')
        weight = validate_and_clean_stat(row.get('Weight', ''), 'weight')
        birth_date = PlayerDataProcessor.get_safe_attr(row, 'Birth_Date')
        
        # リーグ属性の物理的補完（マッピング優先）
        current_team = PlayerDataProcessor.get_safe_attr(row, 'Current_Team')
        cleaned_team = clean_team_name(current_team)
        
        lookup_league = league_map.get(cleaned_team.lower(), "nan")
        if lookup_league != "nan":
            final_league = lookup_league
        else:
            final_league = league_val if league_val else "nan"

        nationality = PlayerDataProcessor.get_safe_attr(row, 'Nationality')
        if not nationality:
            missing_nationality.append({
                "name_en": name_en,
                "name_ja": name_ja,
                "team": current_team,
                "league": final_league,
                "url": scraped_url
            })
            
        birthplace = PlayerDataProcessor.get_safe_attr(row, 'Birth_Place_Scraped')
        caps = PlayerDataProcessor.get_safe_attr(row, 'Representative_Caps')
        if caps == '0.0' or caps == '0':
            caps = ""
        
        career_history_raw = PlayerDataProcessor.get_safe_attr(row, 'キャリア遍歴')
        career_history = PlayerDataProcessor.consolidate_career_history(career_history_raw)
        high_school = PlayerDataProcessor.get_safe_attr(row, 'High_School')
        university = PlayerDataProcessor.get_safe_attr(row, 'University')

        # Ageの数値化（または生年月日からの動的算出）
        age_clean = None
        age_csv = row.get('Age')
        if pd.notna(age_csv) and str(age_csv).lower() != 'nan' and str(age_csv).strip() != "":
            try:
                # 数字のみを抽出
                age_match = re.search(r'(\d+)', str(age_csv))
                if age_match:
                    age_clean = int(age_match.group(1))
            except:
                pass
        
        # CSVに年齢がない場合、生年月日から算出を試みる
        if age_clean is None and birth_date and birth_date != 'nan':
            age_clean = calculate_age(birth_date)
        
        # Markdown出力用の値（数値または null）
        age_for_md = age_clean if age_clean is not None else "null"

        # Markdown生成
        title_str = f"{name_en}"
        if name_ja and name_ja != name_en:
            title_str += f" | {name_ja}"
            
        content = f"""---
title: "{title_str}"
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

    # 国籍欠落レポートの出力
    REPORT_PATH = os.path.join(PROJECT_ROOT, 'data/missing_nationality_report.txt')
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write("=== Missing Nationality Report ===\n")
        f.write(f"Total: {len(missing_nationality)}\n\n")
        for p in missing_nationality:
            f.write(f"Name: {p['name_en']} ({p['name_ja']}) | Team: {p['team']} ({p['league']}) | URL: {p['url']}\n")
    
    print(f"Generated {len(df)} player files and {JSON_OUTPUT_PATH}")
    print(f"Verification: {len(used_slugs)} unique slugs used.")
    print(f"Nationality report generated at {REPORT_PATH}")

if __name__ == "__main__":
    generate_markdown()
