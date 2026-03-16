import csv
import os
import re
from datetime import datetime

# 設定
MASTER_CSV = 'data_sources/final_master_data_v25.csv'
SUPPLEMENT_SOURCES = [
    'data_sources/national_representatives.csv',
    'data_sources/international_representatives_raw_v2.csv',
    'data_sources/final_master_data_v25_wikipedia_formal (1).csv'
]
OUTPUT_CSV = 'data_sources/final_master_data_v25_integrated.csv'
CURRENT_YEAR = 2026

def get_age(birth_date_str):
    if not birth_date_str or str(birth_date_str).lower() == 'nan' or birth_date_str == '---':
        return None
    try:
        b_str = str(birth_date_str).strip()
        date_sep = '-' if '-' in b_str else '.'
        if len(b_str) == 4 and b_str.isdigit():
            return CURRENT_YEAR - int(b_str)
        
        # 2004.. のような形式
        if '..' in b_str:
            year_match = re.match(r'^(\d{4})', b_str)
            if year_match: return CURRENT_YEAR - int(year_match.group(1))

        birth_date = datetime.strptime(b_str[:10], f'%Y{date_sep}%m{date_sep}%d')
        today = datetime.today()
        # 簡易計算（月日考慮）
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except:
        match = re.match(r'^(\d{4})', str(birth_date_str))
        if match: return CURRENT_YEAR - int(match.group(1))
        return None

def main():
    # 補完用データのロード (名前をキーに生日と代表情報を格納)
    supplement_data = {}
    
    print("Loading supplement sources...")
    for source in SUPPLEMENT_SOURCES:
        if not os.path.exists(source):
            print(f"Warning: {source} not found. Skipping.")
            continue
            
        with open(source, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 英語名を取得
                name_en = row.get('name_en') or row.get('英語名')
                if not name_en: continue
                name_en = name_en.strip().lower()
                
                if name_en not in supplement_data:
                    supplement_data[name_en] = {'birth_date': None, 'caps': None, 'country': None}
                
                # 生日の補完 (v25_wikipedia_formal等に存在する可能性がある)
                bday = row.get('生年月日') or row.get('birth_date')
                if bday and bday != '---' and not supplement_data[name_en]['birth_date']:
                    supplement_data[name_en]['birth_date'] = bday
                
                # 代表情報の補完
                rep_team = row.get('representative_team')
                caps = row.get('latest_caps') or row.get('caps')
                if rep_team:
                    current_caps = supplement_data[name_en]['caps'] or ""
                    new_caps = f"{rep_team}代表"
                    if caps: new_caps += f" ({caps} caps)"
                    
                    if not current_caps or rep_team not in current_caps:
                        supplement_data[name_en]['caps'] = (current_caps + " " + new_caps).strip()
                        supplement_data[name_en]['country'] = rep_team

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
            name_en = (row.get('英語名') or "").strip().lower()
            
            if name_en in supplement_data:
                supp = supplement_data[name_en]
                
                # 生日の補完
                if (not row['生年月日'] or row['生年月日'] == '---') and supp['birth_date']:
                    row['生年月日'] = supp['birth_date']
                    row['年齢'] = str(get_age(supp['birth_date']) or "")
                    supplemented_count += 1
                
                # 代表キャップの補完・強化
                if (not row['代表キャップ数'] or row['代表キャップ数'] == '0' or row['代表キャップ数'] == '') and supp['caps']:
                    row['代表キャップ数'] = supp['caps']
                    caps_updated_count += 1
                elif supp['caps'] and supp['caps'] not in row['代表キャップ数']:
                    # 既にデータがある場合は追記（重複注意）
                    if '代表' not in row['代表キャップ数']:
                        row['代表キャップ数'] = supp['caps']
                    else:
                        # 既存の代表チームと異なる場合に追記
                        pass

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
