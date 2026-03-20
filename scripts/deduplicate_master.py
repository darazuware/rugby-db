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

def is_low_quality(caps_str):
    c = str(caps_str).strip()
    if c in ['', '0', '0.0', 'nan', 'none']: return True
    # 数字やカッコが含まれていない場合は低品質とみなす (例: "🇳🇿 New Zealand")
    if '(' not in c and not any(char.isdigit() for char in c):
        return True
    return False

def deduplicate():
    if not os.path.exists(INPUT_CSV_PATH):
        print(f"File not found: {INPUT_CSV_PATH}")
        return

    if os.path.exists(OUTPUT_CSV_PATH):
        import shutil
        shutil.copy2(OUTPUT_CSV_PATH, BACKUP_PATH)

    df = pd.read_csv(INPUT_CSV_PATH)
    print(f"Original v25 row count: {len(df)}")
    
    # 1. 代表歴マッピング作成 (High Precision)
    caps_by_name = {}
    if os.path.exists(SOURCE_REPRESENTATIVES_PATH):
        rep_df = pd.read_csv(SOURCE_REPRESENTATIVES_PATH)
        for _, row in rep_df.iterrows():
            name = normalize_name(row.get('name_en'))
            team = str(row.get('representative_team', '')).strip()
            count = str(row.get('latest_caps', '0')).strip()
            if name and team and count != '0' and count != 'nan':
                flag = FLAG_MAP.get(team, '')
                caps_str = f"{flag} {team} ({int(float(count))})"
                caps_by_name[name] = caps_str

    # 2. 代表歴マッピング作成 (Legacy match)
    caps_by_url = {}
    if os.path.exists(SOURCE_V17_PATH):
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
        
        if is_low_quality(current_caps):
            if name_norm in caps_by_name:
                return caps_by_name[name_norm]
            if url in caps_by_url:
                rescued = caps_by_url[url]
                if not is_low_quality(rescued):
                    return rescued
        return row.get('代表キャップ数')

    df['代表キャップ数'] = df.apply(rescue_caps, axis=1)

    # 正規化
    column_map = {
        '英語名': 'Player_Name', '選手名': 'Full_Name', '選手名_カタカナ': '選手名_カタカナ',
        '生年月日': 'Birth_Date', '年齢': 'Age', '身長': 'Height', '体重': 'Weight',
        'ポジション': 'Position', '所属チーム': 'Current_Team', 'リーグ': 'League',
        '代表キャップ数': 'Representative_Caps', 'Scraped_Url': 'Scraped_Url',
        'キャリア遍歴': 'キャリア遍歴', '高校': 'High_School', '大学': 'University'
    }
    df = df.rename(columns=column_map)

    # クレンジング
    def clean_caps(val):
        v = str(val).strip()
        if 'all.rugby' in v or 'http' in v: return ""
        if v == 'nan' or v == '0' or v == '0.0': return ""
        return val
    
    if 'Representative_Caps' in df.columns:
        df['Representative_Caps'] = df['Representative_Caps'].apply(clean_caps)

    # 重複排除
    if 'Scraped_Url' in df.columns:
        df['Scraped_Url'] = df['Scraped_Url'].astype(str).str.strip().str.lower()
        df.loc[df['Scraped_Url'] == 'nan', 'Scraped_Url'] = np.nan
        df['nan_count'] = df.isnull().sum(axis=1)
        mask = df['Scraped_Url'].notna()
        with_url = df[mask].copy()
        no_url = df[~mask].copy()
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
