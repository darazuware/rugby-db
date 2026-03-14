import csv
import json
import os
import re
from datetime import datetime
import unicodedata

# 名前を正規化する関数 (アクセント除去、小文字化、空白トリム)
def normalize_name(name):
    if not name: return ""
    # アクセント記号の除去 (e.g., Giosuè -> Giosue)
    normalized = unicodedata.normalize('NFD', name)
    normalized = "".join([c for c in normalized if not unicodedata.combining(c)])
    # 全角スペースを半角に、連続するスペースを一つに
    normalized = normalized.replace('　', ' ')
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized.strip().lower()
def calculate_age(dob_str):
    if not dob_str or dob_str == "TBC":
        return ""
    try:
        # 形式の揺れに対応 (YYYY.MM.DD)
        if '.' in dob_str:
            birth_date = datetime.strptime(dob_str, "%Y.%m.%d")
        else:
            return ""
        today = datetime.today()
        return str(today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day)))
    except:
        return ""

# 日付形式の正規化 (YYYY.MM.DD)
def normalize_date(date_str):
    if not date_str: return ""
    date_str = date_str.strip()
    
    # Wikipedia format: (1991-09-18)18 September 1991(age 34)
    match = re.search(r'\((\d{4})-(\d{2})-(\d{2})\)', date_str)
    if match:
        return f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
    
    # 23/04/2001
    match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
    if match:
        return f"{match.group(3)}.{match.group(2).zfill(2)}.{match.group(1).zfill(2)}"
    
    # 21st December 2004
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    match = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+([a-zA-Z]+)\s+(\d{4})', date_str)
    if match:
        d, m_str, y = match.groups()
        if m_str in months:
            m = str(months.index(m_str) + 1).zfill(2)
            return f"{y}.{m}.{d.zfill(2)}"
            
    # Italian: 14 settembre 2001
    it_months = {"gennaio": "01", "febbraio": "02", "marzo": "03", "aprile": "04", "maggio": "05", "giugno": "06", "luglio": "07", "agosto": "08", "settembre": "09", "ottobre": "10", "novembre": "11", "dicembre": "12"}
    for m_it, m_num in it_months.items():
        if m_it in date_str.lower():
            match = re.search(r'(\d{1,2})\s+' + m_it + r'\s+(\d{4})', date_str.lower())
            if match:
                return f"{match.group(2)}.{m_num}.{match.group(1).zfill(2)}"
                
    return date_str # Fallback

# 数値（身長・体重）の抽出
def extract_number(s):
    if not s: return ""
    s = str(s).strip()
    
    # 1.86 m -> 186
    h_match = re.search(r'(\d)\.(\d{2})\s*m', s)
    if h_match:
        return h_match.group(1) + h_match.group(2)
        
    match = re.search(r'(\d+)', s)
    return match.group(1) if match else ""

def integrate_team_data(csv_rows, json_data, team_name):
    print(f"Integrating data for team: {team_name}")
    count = 0
    for player in json_data:
        # 名前でマッチング
        target_name = player.get('name') or player.get('full_name') or player.get('英語名')
        if not target_name: continue
        
        target_name_norm = normalize_name(target_name)
        target_names_set = set(target_name_norm.split())
        
        for row in csv_rows:
            csv_name_norm = normalize_name(row['英語名'])
            csv_names_set = set(csv_name_norm.split())
            
            # 条件1: 完全一致
            # 条件2: 姓名の単語セットが一致 (姓名逆転対応)
            if csv_name_norm == target_name_norm or (csv_names_set == target_names_set and len(csv_names_set) > 1):
                # データの更新 (空欄優先)
                if not row['身長'] or row['身長'] == "":
                    row['身長'] = extract_number(player.get('height'))
                if not row['体重'] or row['体重'] == "":
                    row['体重'] = extract_number(player.get('weight'))
                if not row['生年月日'] or row['生年月日'] == "":
                    row['生年月日'] = normalize_date(player.get('dob'))
                
                # 年齢の再計算
                if row['生年月日']:
                    row['年齢'] = calculate_age(row['生年月日'])
                
                # キャリア遍歴の追記 (Bio/CareerがあればText_Detailへ)
                bio = player.get('bio') or player.get('career')
                if bio and (not row['Text_Detail'] or len(row['Text_Detail']) < len(bio)):
                    row['Text_Detail'] = bio
                
                # 代表キャップ (HonoursがあればInternational_Capsへ)
                honours = player.get('honours')
                if honours and not row['International_Caps']:
                    row['International_Caps'] = honours
                    row['代表キャップ数'] = honours
                
                count += 1
                break
    print(f"Updated {count} players for {team_name}")

def main():
    csv_path = "data_sources/final_master_data_v25.csv"
    artifact_dir = "/Users/ktamatzmoto/.gemini/antigravity/brain/0a4cb5ef-2a47-4d0d-afe7-2dd511f55541"
    
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    # JSONファイルの読み込み
    teams = {
        "Benetton": "benetton_official_full.json",
        "Connacht": "connacht_official_full.json",
        "Dragons": "dragons_official_full.json",
        "Lions": "lions_wikipedia_details.json",
        "AllRugby": "scraped_missing_details.json"
    }
    
    current_year = datetime.today().year

    for team_name, file_name in teams.items():
        file_path = os.path.join(artifact_dir, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # AllRugby specific integration logic if needed
                if team_name == "AllRugby":
                    print("Integrating AllRugby supplementary data...")
                    count = 0
                    for player in data:
                        if player.get('not_found'): continue
                        
                        target_name_norm = normalize_name(player.get('name'))
                        target_names_set = set(target_name_norm.split())
                        
                        for row in rows:
                            csv_name_norm = normalize_name(row['英語名'])
                            csv_names_set = set(csv_name_norm.split())
                            
                            if csv_name_norm == target_name_norm or (csv_names_set == target_names_set and len(csv_names_set) > 1):
                                # Update fields
                                if not row['身長'] and player.get('height'):
                                    row['身長'] = player['height']
                                if not row['体重'] and player.get('weight'):
                                    row['体重'] = player['weight']
                                if not row['生年月日']:
                                    if player.get('dob'):
                                        row['生年月日'] = player['dob']
                                    elif player.get('age'):
                                        # Estimate birth year: 2026 - age (approx)
                                        birth_year = current_year - int(player['age'])
                                        row['生年月日'] = f"{birth_year}.01.01"
                                
                                # Recalculate age
                                if row['生年月日']:
                                    row['年齢'] = calculate_age(row['生年月日'])
                                count += 1
                                break
                    print(f"Updated {count} players from AllRugby")
                else:
                    integrate_team_data(rows, data, team_name)
        else:
            print(f"Skipping {team_name}, file not found: {file_name}")
            
    # CSVの保存
    with open(csv_path, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print("Integration complete.")

if __name__ == "__main__":
    main()
