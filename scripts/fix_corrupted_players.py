import pandas as pd
import datetime
import os
import re
import json
import urllib.parse

# 定数
CSV_PATH = "data_sources/final_master_data_v27_normalized.csv"
OUTPUT_PATH = "data_sources/final_master_data_v27_normalized.csv"  # 上書き
TEAM_NAMES_JSON = "data/team_names_jp.json"
REFERENCE_DATE = datetime.date(2026, 3, 20)

# 修正用マッピング (既存の特殊ケース: SEO文言混入)
TEAM_FIX_MAP = {
    "The Bath Rugby rugby team for 2025/2026": {"league": "premiership", "team": "Bath Rugby"},
    "The Crusaders rugby team for 2025/2026": {"league": "super-rugby", "team": "Crusaders"},
    "The Northampton Saints rugby team for 2025/2026": {"league": "premiership", "team": "Northampton Saints"},
    "The Stade Toulousain rugby team for 2025/2026": {"league": "top14", "team": "Stade Toulousain"}
}

# 日本語サフィックスの正規表現 (例: 「（2025-26）」)
SUFFIX_PATTERN = re.compile(r'[ \(（]202[0-9]-[0-9]+[）\) ]')

def calculate_age(birth_date_str):
    if not birth_date_str or birth_date_str == "nan" or "XX" in str(birth_date_str):
        return ""
    try:
        # 1996-10-17 形式を想定
        birth_date = datetime.datetime.strptime(str(birth_date_str), "%Y-%m-%d").date()
        age = REFERENCE_DATE.year - birth_date.year - ((REFERENCE_DATE.month, REFERENCE_DATE.day) < (birth_date.month, birth_date.day))
        return f"{age} y/o"
    except:
        return ""

def load_birthdays(file_path):
    if not os.path.exists(file_path):
        return {}
    df = pd.read_csv(file_path)
    name_col, bday_col = None, None
    potential_name_cols = ['Name', 'Player', 'full_name']
    potential_bday_cols = ['Birthday', 'Date of Birth', 'DOB', 'birth_date']
    for col in df.columns:
        if col in potential_name_cols: name_col = col
        if col in potential_bday_cols: bday_col = col
    if not name_col or not bday_col:
        return {}
    return {str(row[name_col]).lower().strip().replace('"', ''): str(row[bday_col]).strip().replace('"', '') for _, row in df.iterrows()}

def load_team_mapping():
    with open(TEAM_NAMES_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    jp_to_en = {}
    for league, teams in data.items():
        for en_name, info in teams.items():
            jp_name = info.get('jp')
            if jp_name:
                jp_to_en[jp_name] = {"en": en_name, "league": league}
            for alias in info.get('aliases', []):
                jp_to_en[alias] = {"en": en_name, "league": league}
    return jp_to_en

def generate_slug(name):
    """Simple slug generator for English names"""
    s = name.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s)
    return s

def main():
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found.")
        return

    print(f"Loading {CSV_PATH}...")
    # csv.DictReaderを使うことで引用符の扱いをより堅牢にする
    df = pd.read_csv(CSV_PATH)
    jp_to_en = load_team_mapping()

    # 誕生日データの読み込み
    birthdays = {}
    birthday_files = ["data_sources/northampton_birthdays.csv", "data_sources/bath_birthdays.csv", "data_sources/prem_all_birthdays.csv"]
    for bf in birthday_files:
        birthdays.update(load_birthdays(bf))

    count = 0
    jp_fix_count = 0
    redirects = {}

    for idx, row in df.iterrows():
        current_team_raw = str(row.get('Current_Team', '')).strip().replace('"', '')
        
        # 1. 特殊ケース (SEO文言混入)
        if current_team_raw in TEAM_FIX_MAP:
            fix = TEAM_FIX_MAP[current_team_raw]
            player_name = str(row.get('Player_Name', '')).strip().lower()
            
            bday = birthdays.get(player_name)
            if not bday:
                h_val = str(row.get('Height', '')).strip()
                if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', h_val):
                    d, m, y = h_val.split('/')
                    bday = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
            
            df.at[idx, 'League'] = fix['league']
            df.at[idx, 'Current_Team'] = fix['team']
            df.at[idx, 'Height'] = ""
            df.at[idx, 'Weight'] = ""
            if bday:
                df.at[idx, 'Birth_Date'] = bday
                df.at[idx, 'Age'] = calculate_age(bday)
            count += 1
            continue

        # 2. 日本語サフィックス混入ケース (ルリーロ福岡（2025-26）等)
        if SUFFIX_PATTERN.search(current_team_raw):
            base_jp_name = SUFFIX_PATTERN.sub('', current_team_raw).strip()
            
            if base_jp_name in jp_to_en:
                mapping = jp_to_en[base_jp_name]
                en_name = mapping['en']
                league = mapping['league']
                
                # リダイレクト用データの収集 (bad_slug は日本語とシーズン表記をそのまま使用)
                bad_slug = current_team_raw.replace(' ', '-')
                good_slug = generate_slug(en_name)
                
                # 日本語URLパスの生成
                bad_path = f"/teams/{league}/{bad_slug}/"
                good_path = f"/teams/{league}/{good_slug}/"
                
                if bad_path not in redirects:
                    redirects[bad_path] = good_path
                    # エンコード版も追加
                    encoded_bad_slug = urllib.parse.quote(bad_slug)
                    if encoded_bad_slug != bad_slug:
                        encoded_bad_path = f"/teams/{league}/{encoded_bad_slug}/"
                        redirects[encoded_bad_path] = good_path

                df.at[idx, 'Current_Team'] = en_name
                df.at[idx, 'League'] = league
                jp_fix_count += 1
                count += 1
            else:
                # 辞書にない場合は警告を出してスキップ (クレンジング漏れ防止)
                # print(f"Warning: No mapping found for cleaned JP name: '{base_jp_name}' (Original: '{current_team_raw}')")
                pass

    if count > 0:
        print(f"Total fixed: {count} (JP Suffix: {jp_fix_count})")
        
        # バックアップ作成
        os.system(f"cp {CSV_PATH} {CSV_PATH}.bak_repair_v3")
        df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"Successfully saved to {OUTPUT_PATH}")

        # リダイレクト情報の出力 (後で redirects.json に追加するため)
        if redirects:
            with open("/tmp/new_redirects.json", "w", encoding="utf-8") as rf:
                json.dump(redirects, rf, indent=4, ensure_ascii=False)
            print(f"New redirects saved to /tmp/new_redirects.json ({len(redirects)} entries)")
    else:
        print("No corrupted rows found.")

if __name__ == "__main__":
    main()
