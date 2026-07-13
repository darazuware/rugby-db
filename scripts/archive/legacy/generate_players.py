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
        return str(int(vf))
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

def generate_markdown_from_csv(csv_path, sub_dir, category, used_slugs, processed_keys):
    if not os.path.exists(csv_path):
        print(f"Warning: CSV file not found at {csv_path}. Skipping.")
        return []

    # リーグマッピングの構築
    league_map = load_league_mapping()

    # 出力ディレクトリの作成
    output_path = os.path.join(OUTPUT_DIR, sub_dir)
    os.makedirs(output_path, exist_ok=True)

    df = pd.read_csv(csv_path)
    players_json = []
    print(f"Loading {csv_path} with {len(df)} players...")
    
    for _, row in df.iterrows():
        # 基本情報の抽出
        name_en = PlayerDataProcessor.get_safe_attr(row, 'Player_Name', default=PlayerDataProcessor.get_safe_attr(row, 'Full_Name'))
        name_ja = PlayerDataProcessor.get_safe_attr(row, 'Full_Name')
        if not name_ja:
            name_ja = PlayerDataProcessor.get_safe_attr(row, '選手名_カタカナ')
        
        if not name_en: name_en = "Unknown Player"
        if not name_ja: name_ja = name_en

        current_team = PlayerDataProcessor.get_safe_attr(row, 'Current_Team')
        cleaned_team = clean_team_name(current_team)

        # グローバル重複排除チェック (同姓同名かつ同チームは同一人物とみなす)
        player_key = (name_ja.strip(), cleaned_team.strip())
        if player_key in processed_keys:
            continue
        processed_keys.add(player_key)

        scraped_url = PlayerDataProcessor.get_safe_attr(row, 'Scraped_Url').lower()
        birth_date = PlayerDataProcessor.get_safe_attr(row, 'Birth_Date')

        # 強力な重複排除 (URL または 氏名+生年月日で同一人物とみなす)
        if scraped_url and scraped_url in used_slugs: # URLをキーに再利用
            continue
        
        player_id_key = f"{name_ja}_{birth_date}"
        if player_id_key in processed_keys:
            continue
        
        if scraped_url:
            used_slugs.add(scraped_url) # URLを重複チェック用に流用
        processed_keys.add(player_id_key)

        # スラッグの生成
        slug = ""
        if scraped_url and 'all.rugby/player/' in scraped_url:
            slug = scraped_url.split('/')[-1]
        elif scraped_url and ('rugby-japan.jp/match/' in scraped_url or 'momotaros.jp' in scraped_url):
            import hashlib
            seed = scraped_url if scraped_url else f"{name_ja}-{category}"
            slug_hash = hashlib.md5(seed.encode()).hexdigest()[:8]
            slug = f"player-{slug_hash}"
        else:
            is_valid_en = name_en and name_en != "---" and name_en != "Unknown Player"
            if is_valid_en:
                slug = name_en.lower().replace(' ', '-')
            else:
                import hashlib
                slug_hash = hashlib.md5(f"{name_ja}-{category}".encode()).hexdigest()[:8]
                slug = f"player-{slug_hash}"
        
        if not slug or slug.strip() == "" or slug.strip("-") == "":
            slug = "player-" + hashlib.md5(f"{name_ja}-{category}".encode()).hexdigest()[:8]
            
        original_slug = slug
        counter = 1
        # used_slugs は URL と スラッグの両方を管理することになるが、衝突は希
        while slug in used_slugs:
            counter += 1
            slug = f"{original_slug}-{counter}"
        
        used_slugs.add(slug)
        
        league_val = PlayerDataProcessor.get_safe_attr(row, 'League').lower()
        
        lookup_league = league_map.get(cleaned_team.lower(), "nan")
        if lookup_league != "nan":
            final_league = lookup_league
        else:
            final_league = league_val if league_val else "nan"

        nationality = PlayerDataProcessor.get_safe_attr(row, 'Nationality')
        birthplace = PlayerDataProcessor.get_safe_attr(row, 'Birth_Place_Scraped')
        caps = PlayerDataProcessor.get_safe_attr(row, 'Representative_Caps')
        
        career_history_raw = PlayerDataProcessor.get_safe_attr(row, 'キャリア遍歴')
        career_history = PlayerDataProcessor.consolidate_career_history(career_history_raw)
        yearly_career = PlayerDataProcessor.get_yearly_career(career_history_raw, nationality)
        career_history_json = json.dumps(yearly_career, ensure_ascii=False).replace("'", "''")

        high_school = PlayerDataProcessor.get_safe_attr(row, 'High_School')
        university = PlayerDataProcessor.get_safe_attr(row, 'University')
        junior_high = PlayerDataProcessor.get_safe_attr(row, 'Junior_High_School')
        rugby_school = PlayerDataProcessor.get_safe_attr(row, 'Rugby_School')
        
        l1_caps = PlayerDataProcessor.get_safe_attr(row, 'League_One_Caps')

        # Ageの算出
        age_clean = None
        age_csv = row.get('Age')
        if pd.notna(age_csv) and str(age_csv).lower() != 'nan' and str(age_csv).strip() != "":
            try:
                age_match = re.search(r'(\d+)', str(age_csv))
                if age_match: age_clean = int(age_match.group(1))
            except: pass
        
        # birth_dateの取得とクリーンアップ
        birth_date = PlayerDataProcessor.get_safe_attr(row, 'Birth_Date')
        if age_clean is None and birth_date and birth_date != 'nan':
            age_clean = calculate_age(birth_date)
        
        age_for_md = age_clean if age_clean is not None else "null"

        # position, height, weightの取得とクリーンアップ
        position = PlayerDataProcessor.get_safe_attr(row, 'Position')
        height = validate_and_clean_stat(PlayerDataProcessor.get_safe_attr(row, 'Height'), 'height')
        weight = validate_and_clean_stat(PlayerDataProcessor.get_safe_attr(row, 'Weight'), 'weight')

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
junior_high_school: "{junior_high}"
rugby_school: "{rugby_school}"
scraped_url: "{scraped_url}"
league_one_caps: "{l1_caps}"
career_history_json: '{career_history_json}'
category: "{category}"
---

## キャリア遍歴
{career_history}
"""
        
        file_path = os.path.join(output_path, f"{slug}.md")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        players_json.append({
            "slug": slug,
            "category": category,
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
                "category": category
            }
        })
    return players_json

def main():
    # 既存の出力ディレクトリをクリーンアップ
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_players_json = []
    used_slugs = set()
    processed_keys = set() # (name_ja, team) のペアで物理管理

    # 1. Pro
    pro_players = generate_markdown_from_csv(CSV_PATH, 'pro', 'pro', used_slugs, processed_keys)
    all_players_json.extend(pro_players)

    # 2. High School
    HS_CSV_PATH = os.path.join(PROJECT_ROOT, 'data_sources/high_school_players.csv')
    hs_players = generate_markdown_from_csv(HS_CSV_PATH, 'high-school', 'high-school', used_slugs, processed_keys)
    all_players_json.extend(hs_players)

    # 3. University
    UNI_CSV_PATH = os.path.join(PROJECT_ROOT, 'data_sources/university_players.csv')
    uni_players = generate_markdown_from_csv(UNI_CSV_PATH, 'university', 'university', used_slugs, processed_keys)
    all_players_json.extend(uni_players)

    # 4. Top East
    TOP_EAST_CSV_PATH = os.path.join(PROJECT_ROOT, 'data_sources/top_east_players.csv')
    if os.path.exists(TOP_EAST_CSV_PATH):
        top_east_players = generate_markdown_from_csv(TOP_EAST_CSV_PATH, 'top-east', 'top-east', used_slugs, processed_keys)
        all_players_json.extend(top_east_players)

    # 5. Top Kyushu
    TOP_KYUSHU_CSV_PATH = os.path.join(PROJECT_ROOT, 'data_sources/top_kyushu_players.csv')
    if os.path.exists(TOP_KYUSHU_CSV_PATH):
        top_kyushu_players = generate_markdown_from_csv(TOP_KYUSHU_CSV_PATH, 'top-kyushu', 'top-kyushu', used_slugs, processed_keys)
        all_players_json.extend(top_kyushu_players)

    # 6. Top West A
    TOP_WEST_CSV_PATH = os.path.join(PROJECT_ROOT, 'data_sources/top_west_players.csv')
    if os.path.exists(TOP_WEST_CSV_PATH):
        top_west_players = generate_markdown_from_csv(TOP_WEST_CSV_PATH, 'top-west-a', 'top-west-a', used_slugs, processed_keys)
        all_players_json.extend(top_west_players)

    # 7. Top West B/C
    TOP_WEST_BC_CSV_PATH = os.path.join(PROJECT_ROOT, 'data_sources/top_west_players_bc.csv')
    if os.path.exists(TOP_WEST_BC_CSV_PATH):
        df_bc = pd.read_csv(TOP_WEST_BC_CSV_PATH)
        for league_label in ['top-west-b', 'top-west-c']:
            df_subset = df_bc[df_bc['category'] == league_label]
            if not df_subset.empty:
                temp_csv = f"/tmp/{league_label}_temp.csv"
                df_subset.to_csv(temp_csv, index=False)
                players = generate_markdown_from_csv(temp_csv, league_label, league_label, used_slugs, processed_keys)
                all_players_json.extend(players)

    # players.json の出力
    os.makedirs(os.path.dirname(JSON_OUTPUT_PATH), exist_ok=True)
    with open(JSON_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_players_json, f, ensure_ascii=False, indent=2)
    
    print(f"Total players generated: {len(all_players_json)}")

if __name__ == "__main__":
    main()
