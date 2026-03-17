import csv
import os
import re
from datetime import datetime

# 設定
MASTER_CSV = 'data_sources/final_master_data_v25.csv'
SUPPLEMENT_SOURCES = [
    'data_sources/northampton_birthdays.csv',
    'data_sources/prem_itsrugby_birthdays.csv',
    'data_sources/national_representatives.csv',
    'data_sources/harlequins_birthdays.csv',
    'data_sources/bath_birthdays.csv',
    'data_sources/gloucester_birthdays.csv',
    'data_sources/prem_all_birthdays.csv',
    'data_sources/international_representatives_raw_v2.csv',
    'data_sources/final_master_data_v25_wikipedia_formal (1).csv'
]

OUTPUT_CSV = 'data_sources/final_master_data_v25_integrated.csv'
CURRENT_YEAR = 2026

def get_age(birth_date_str):
    if not birth_date_str or str(birth_date_str).lower() == 'nan' or birth_date_str == '---':
        return None
    try:
        # "2006-XX-XX" を "2006-01-01" に補完
        b_str = str(birth_date_str).strip().replace('XX', '01').replace('xx', '01')
        
        # DD/MM/YYYY 形式を YYYY-MM-DD に変換
        if '/' in b_str and b_str.count('/') == 2:
            parts = b_str.split('/')
            if len(parts[0]) <= 2 and len(parts[2]) == 4: # DD/MM/YYYY
                b_str = f"{parts[2]}-{parts[1]}-{parts[0]}"
            elif len(parts[0]) == 4: # YYYY/MM/DD
                b_str = b_str.replace('/', '-')

        date_sep = '-' if '-' in b_str else '.'
        if len(b_str) == 4 and b_str.isdigit():
            return CURRENT_YEAR - int(b_str)
        
        # 2004.. のような形式
        if '..' in b_str:
            year_match = re.match(r'^(\d{4})', b_str)
            if year_match: return CURRENT_YEAR - int(year_match.group(1))

        # フォーマット解析
        birth_date = datetime.strptime(b_str[:10], f'%Y{date_sep}%m{date_sep}%d')
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except:
        match = re.match(r'^(\d{4})', str(birth_date_str))
        if match: return CURRENT_YEAR - int(match.group(1))
        return None

def normalize_name(name):
    # '-' をスペースに置き換え、'.'を削除
    return name.strip().lower().replace('.', '').replace('-', ' ').split()

def is_match(name1, name2):
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    
    if not n1 or not n2: return False
    if n1 == n2: return True
    
    # 苗字（最後の要素）が一致するか
    if n1[-1] == n2[-1]:
        # イニシャル一致
        if n1[0][0] == n2[0][0]:
            return True
            
    # 複合姓のケース（例: Ainsworth-Cave vs Ainsworth Cave）
    if n1[-1] in n2[-1] or n2[-1] in n1[-1]:
         if n1[0][0] == n2[0][0]:
            return True
    
    return False

def main():
    # 補完用データのロード (名前をキーに生日と代表情報を格納)
    supplement_data = [] # リストに変更してループでマッチング
    
    print("Loading supplement sources...")
    for source in SUPPLEMENT_SOURCES:
        if not os.path.exists(source):
            print(f"Warning: {source} not found. Skipping.")
            continue
            
        with open(source, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 英語名を取得
                name_en = row.get('name_en') or row.get('英語名') or row.get('Name')
                if not name_en: continue
                
                bday = row.get('生年月日') or row.get('birth_date') or row.get('DOB') or row.get('Birthday')
                rep_team = row.get('representative_team')
                caps = row.get('latest_caps') or row.get('caps')
                
                entry = {
                    'name': name_en.strip().lower(),
                    'birth_date': bday if bday and bday != '---' else None,
                    'caps': None,
                    'country': rep_team
                }
                
                if rep_team:
                    entry['caps'] = f"{rep_team}代表"
                    if caps: entry['caps'] += f" ({caps} caps)"
                
                supplement_data.append(entry)

    print(f"Loaded {len(supplement_data)} supplement entries.")
    # マスターCSVの読み込みと補完
    print(f"Reading master CSV: {MASTER_CSV}")
    updated_rows = []
    headers = []
    supplemented_count = 0
    caps_updated_count = 0

    with open(MASTER_CSV, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for row in reader:
            name_en_master = (row.get('英語名') or "").strip().lower()
            if not name_en_master: 
                updated_rows.append(row)
                continue
            
            # マッチする補完データを探す
            for supp in supplement_data:
                if is_match(name_en_master, supp['name']):
                    # 生日の補完
                    if (not row.get('生年月日') or row.get('生年月日') == '---') and supp['birth_date']:
                        row['生年月日'] = supp['birth_date']
                        row['年齢'] = str(get_age(supp['birth_date']) or "")
                        supplemented_count += 1
                        # print(f"Supplemented: {name_en_master} -> {supp['birth_date']}")
                    
                    # 代表キャップの補完
                    if (not row.get('代表キャップ数') or row.get('代表キャップ数') == '0' or row.get('代表キャップ数') == '') and supp['caps']:
                        row['代表キャップ数'] = supp['caps']
                        caps_updated_count += 1
                    
                    # 最初のマッチで終了 (生日がある場合)
                    if supp['birth_date']: break

            updated_rows.append(row)

    # 結果の書き出し
    print(f"Writing integrated CSV to: {OUTPUT_CSV}")
    with open(OUTPUT_CSV, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"SUCCESS!")
    print(f"- Supplemented Birthdays: {supplemented_count}")
    print(f"- Updated Caps: {caps_updated_count}")
    print(f"- Total Rows: {len(updated_rows)}")

if __name__ == "__main__":
    main()
