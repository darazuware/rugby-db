import pandas as pd
import datetime
import os
import re

# 定数
CSV_PATH = "data_sources/final_master_data_v27_normalized.csv"
OUTPUT_PATH = "data_sources/final_master_data_v27_normalized.csv"  # 上書き
REFERENCE_DATE = datetime.date(2026, 3, 20)

# 修正用マッピング
TEAM_FIX_MAP = {
    "The Bath Rugby rugby team for 2025/2026": {"league": "premiership", "team": "Bath Rugby"},
    "The Crusaders rugby team for 2025/2026": {"league": "super-rugby", "team": "Crusaders"},
    "The Northampton Saints rugby team for 2025/2026": {"league": "premiership", "team": "Northampton Saints"},
    "The Stade Toulousain rugby team for 2025/2026": {"league": "top14", "team": "Stade Toulousain"}
}

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
    
    # 列名の推定
    name_col = None
    bday_col = None
    
    potential_name_cols = ['Name', 'Player', 'full_name']
    potential_bday_cols = ['Birthday', 'Date of Birth', 'DOB', 'birth_date']
    
    for col in df.columns:
        if col in potential_name_cols: name_col = col
        if col in potential_bday_cols: bday_col = col
        
    if not name_col or not bday_col:
        print(f"Warning: Could not identify columns in {file_path}. Columns: {df.columns.tolist()}")
        return {}
        
    # Name -> Birthday の辞書作成 (小文字化してマッチング)
    return {str(row[name_col]).lower().strip().replace('"', ''): str(row[bday_col]).strip().replace('"', '') for _, row in df.iterrows()}

def main():
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found.")
        return

    print(f"Loading {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)

    # 誕生日データの読み込み
    birthdays = {}
    birthday_files = [
        "data_sources/northampton_birthdays.csv",
        "data_sources/bath_birthdays.csv",
        "data_sources/prem_all_birthdays.csv"
    ]
    for bf in birthday_files:
        birthdays.update(load_birthdays(bf))

    count = 0
    match_count = 0
    rescue_count = 0
    
    for idx, row in df.iterrows():
        current_team = str(row.get('Current_Team', '')).strip()
        
        if current_team in TEAM_FIX_MAP:
            fix = TEAM_FIX_MAP[current_team]
            player_name_raw = str(row.get('Player_Name', '')).strip()
            player_name = player_name_raw.lower()
            
            # 誕生日補完
            bday = None
            if player_name in birthdays:
                bday = birthdays[player_name]
                match_count += 1
            else:
                # 念のため Height に入っていた誕生日を救出 (形式: 11/05/2002)
                h_val = str(row.get('Height', '')).strip()
                if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', h_val):
                    try:
                        d, m, y = h_val.split('/')
                        bday = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                        rescue_count += 1
                    except:
                        pass
            
            # 値のセット
            df.at[idx, 'League'] = fix['league']
            df.at[idx, 'Current_Team'] = fix['team']
            df.at[idx, 'Height'] = ""
            df.at[idx, 'Weight'] = ""
            
            if bday:
                df.at[idx, 'Birth_Date'] = bday
                df.at[idx, 'Age'] = calculate_age(bday)
                # print(f"Fixed {player_name_raw}: {bday}")
            
            count += 1

    if count > 0:
        print(f"Total processed: {count}")
        print(f"Matched from CSVs: {match_count}")
        print(f"Rescued from Height: {rescue_count}")
        # バックアップ作成
        os.system(f"cp {CSV_PATH} {CSV_PATH}.bak_repair")
        df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"Successfully saved to {OUTPUT_PATH}")
    else:
        print("No corrupted rows found.")

if __name__ == "__main__":
    main()
