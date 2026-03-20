import pandas as pd
import numpy as np
from datetime import datetime
import os

INPUT_CSV_PATH = 'data_sources/final_master_data_v25_consolidated.csv'
OUTPUT_CSV_PATH = 'data_sources/final_master_data_v27_normalized.csv'
BACKUP_PATH = 'data_sources/final_master_data_v27_normalized.csv.bak'

def calculate_age(birth_date_str):
    if not birth_date_str or str(birth_date_str).lower() == 'nan' or birth_date_str == '---' or birth_date_str == '':
        return None
    try:
        # Expected formats: YYYY.MM.DD or YYYY/MM/DD
        cleaned_date = str(birth_date_str).replace('/', '.').replace('-', '.')
        birth_date = datetime.strptime(cleaned_date, '%Y.%m.%d')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except Exception as e:
        # Handle cases like "1996.." or other partial dates
        try:
            year_match = str(birth_date_str)[:4]
            if year_match.isdigit():
                return datetime.now().year - int(year_match)
        except:
            pass
        return None

def deduplicate():
    if not os.path.exists(INPUT_CSV_PATH):
        print(f"File not found: {INPUT_CSV_PATH}")
        return

    # Backup existing output if it exists
    if os.path.exists(OUTPUT_CSV_PATH):
        import shutil
        shutil.copy2(OUTPUT_CSV_PATH, BACKUP_PATH)
        print(f"Backup created: {BACKUP_PATH}")

    df = pd.read_csv(INPUT_CSV_PATH)
    print(f"Original row count: {len(df)}")
    
    # カラム名の正規化 (日本語 -> 英語)
    column_map = {
        '英語名': 'Player_Name',
        '選手名': 'Full_Name',
        '選手名_カタカナ': '選手名_カタカナ',
        '生年月日': 'Birth_Date',
        '年齢': 'Age',
        '身長': 'Height',
        '体重': 'Weight',
        'ポジション': 'Position',
        '所属チーム': 'Current_Team',
        'リーグ': 'League',
        '代表キャップ数': 'Representative_Caps',
        'Scraped_Url': 'Scraped_Url',
        'キャリア遍歴': 'キャリア遍歴',
        '高校': 'High_School',
        '大学': 'University'
    }
    df = df.rename(columns=column_map)
    print(f"Normalized columns: {df.columns.tolist()}")

    # 1. Representative_Caps の URL 混入を修正
    def clean_caps(val):
        v = str(val).strip()
        if 'all.rugby' in v or 'http' in v:
            return ""
        return val
    
    if 'Representative_Caps' in df.columns:
        df['Representative_Caps'] = df['Representative_Caps'].apply(clean_caps)

    # 2. 年齢の再計算
    def update_age(row):
        b_date = row.get('Birth_Date')
        age = calculate_age(b_date)
        if age is not None:
            return age
        return row.get('Age', np.nan)
    
    df['Age'] = df.apply(update_age, axis=1)

    # 3. 重複排除 (Scraped_Url をキーにする)
    if 'Scraped_Url' in df.columns:
        df['Scraped_Url'] = df['Scraped_Url'].astype(str).str.strip().str.lower()
        df.loc[df['Scraped_Url'] == 'nan', 'Scraped_Url'] = np.nan
        
        df['nan_count'] = df.isnull().sum(axis=1)
        
        # URL があるものと無いもので分ける
        mask = df['Scraped_Url'].notna()
        with_url = df[mask].copy()
        no_url = df[~mask].copy()

        # URL ごとにグループ化し、欠損値が最も少ない行を選択
        deduped_with_url = with_url.sort_values('nan_count', ascending=False).drop_duplicates(subset=['Scraped_Url'], keep='last')
        
        final_df = pd.concat([deduped_with_url, no_url], ignore_index=True)
        final_df = final_df.drop(columns=['nan_count'])
    else:
        print("ERROR: Scraped_Url column missing!")
        final_df = df

    print(f"Deduped row count: {len(final_df)}")
    
    # 保存 (カラム順序を固定)
    cols_order = [
        'Player_Name', 'Full_Name', '選手名_カタカナ', 'Position', 'Current_Team', 'League', 
        'Height', 'Weight', 'Birth_Date', 'Age', 'Representative_Caps', 'Scraped_Url', 
        'キャリア遍歴', 'High_School', 'University'
    ]
    existing_cols = [c for c in cols_order if c in final_df.columns]
    final_df = final_df[existing_cols]

    final_df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"Saved to {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    deduplicate()
