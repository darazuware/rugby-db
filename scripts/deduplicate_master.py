import pandas as pd
import numpy as np
from datetime import datetime
import os
import re

INPUT_CSV_PATH = 'data_sources/final_master_data_v25_consolidated.csv'
SOURCE_V17_PATH = 'data_sources/final_master_data_v17_consolidated.csv'
SOURCE_REPRESENTATIVES_PATH = 'data_sources/national_representatives.csv'
OUTPUT_CSV_PATH = 'data_sources/final_master_data_v27_normalized.csv'
BACKUP_PATH = 'data_sources/final_master_data_v27_normalized.csv.bak'

FLAG_MAP = {
    'New Zealand': '🇳🇿', 'South Africa': '🇿🇦', 'Australia': '🇦🇺', 'France': '🇫🇷',
    'Ireland': '🇮🇪', 'Japan': '🇯🇵', 'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Wales': '🏴󠁧󠁢󠁷󠁬󠁳󠁿',
    'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'Italy': '🇮🇹', 'Argentina': '🇦🇷', 'Fiji': '🇫🇯',
    'Samoa': '🇼🇸', 'Tonga': '🇹🇴', 'Georgia': '🇬🇪', 'USA': '🇺🇸', 'Russia': '🇷🇺',
    'Uruguay': '🇺🇾', 'Portugal': '🇵🇹', 'Romania': '🇷🇴', 'Namibia': '🇳🇦', 'Chile': '🇨🇱',
    'Canada': '🇨🇦', 'Spain': '🇪🇸'
}

def normalize_name(name):
    if not name or pd.isna(name): return ""
    return re.sub(r'[^a-zA-Z]', '', str(name)).lower()

def calculate_age(birth_date_str):
    if not birth_date_str or str(birth_date_str).lower() == 'nan' or birth_date_str == '---' or birth_date_str == '':
        return None
    try:
        cleaned_date = str(birth_date_str).replace('/', '.').replace('-', '.')
        birth_date = datetime.strptime(cleaned_date, '%Y.%m.%d')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except Exception as e:
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

    # Backup existing output
    if os.path.exists(OUTPUT_CSV_PATH):
        import shutil
        shutil.copy2(OUTPUT_CSV_PATH, BACKUP_PATH)
        print(f"Backup created: {BACKUP_PATH}")

    df = pd.read_csv(INPUT_CSV_PATH)
    print(f"Original v25 row count: {len(df)}")
    
    # === 1. 代表歴の救出プロトコル A (Rescue from national_representatives.csv) ===
    # このファイルは名前ベースでのマッチングが必要。
    caps_by_name = {}
    if os.path.exists(SOURCE_REPRESENTATIVES_PATH):
        print(f"Rescuing caps from {SOURCE_REPRESENTATIVES_PATH} (High Precision)...")
        rep_df = pd.read_csv(SOURCE_REPRESENTATIVES_PATH)
        # name_en, representative_team, latest_caps を使用
        for _, row in rep_df.iterrows():
            name = normalize_name(row.get('name_en'))
            team = str(row.get('representative_team', '')).strip()
            count = str(row.get('latest_caps', '0')).strip()
            if name and team and count != '0' and count != 'nan':
                flag = FLAG_MAP.get(team, '')
                caps_str = f"{flag} {team} ({int(float(count))})"
                caps_by_name[name] = caps_str
        print(f"Loaded {len(caps_by_name)} representative records.")

    # === 2. 代表歴の救出プロトコル B (Rescue from v17) ===
    # URLベース
    caps_by_url = {}
    if os.path.exists(SOURCE_V17_PATH):
        print(f"Rescuing caps from {SOURCE_V17_PATH} (Legacy match)...")
        v17_df = pd.read_csv(SOURCE_V17_PATH)
        v17_caps_col = '代表キャップ数' if '代表キャップ数' in v17_df.columns else None
        if v17_caps_col:
            v17_df['Scraped_Url'] = v17_df['Scraped_Url'].astype(str).str.strip().str.lower()
            caps_by_url = v17_df.set_index('Scraped_Url')[v17_caps_col].to_dict()

    # マージ実行
    def rescue_caps(row):
        url = str(row.get('Scraped_Url', '')).strip().lower()
        name_norm = normalize_name(row.get('英語名'))
        current_caps = str(row.get('代表キャップ数', '')).strip()
        
        # もし現在の代表歴が空、0、または nan であれば
        if current_caps in ['', '0', '0.0', 'nan', 'none']:
            # A: 名前ベース (高精度数値) を優先
            if name_norm in caps_by_name:
                return caps_by_name[name_norm]
            # B: URLベース (既存記述) を次善策
            if url in caps_by_url:
                rescued = caps_by_url[url]
                if rescued and str(rescued).lower() != 'nan' and str(rescued) != '0':
                    return rescued
        return row.get('代表キャップ数')

    df['代表キャップ数'] = df.apply(rescue_caps, axis=1)

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

    # 代表キャップのURL混入・不正値クレンジング
    def clean_caps(val):
        v = str(val).strip()
        if 'all.rugby' in v or 'http' in v: return ""
        if v == 'nan' or v == '0' or v == '0.0': return ""
        return val
    
    if 'Representative_Caps' in df.columns:
        df['Representative_Caps'] = df['Representative_Caps'].apply(clean_caps)

    # 年齢の再計算
    def update_age(row):
        b_date = row.get('Birth_Date')
        age = calculate_age(b_date)
        if age is not None: return age
        return row.get('Age', np.nan)
    
    df['Age'] = df.apply(update_age, axis=1)

    # 重複排除
    if 'Scraped_Url' in df.columns:
        df['Scraped_Url'] = df['Scraped_Url'].astype(str).str.strip().str.lower()
        df.loc[df['Scraped_Url'] == 'nan', 'Scraped_Url'] = np.nan
        df['nan_count'] = df.isnull().sum(axis=1)
        mask = df['Scraped_Url'].notna()
        with_url = df[mask].copy()
        no_url = df[~mask].copy()
        # 欠損が少ない方を優先
        deduped_with_url = with_url.sort_values('nan_count', ascending=True).drop_duplicates(subset=['Scraped_Url'], keep='first')
        final_df = pd.concat([deduped_with_url, no_url], ignore_index=True)
        final_df = final_df.drop(columns=['nan_count'])
    else:
        final_df = df

    print(f"Final row count: {len(final_df)}")
    
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
