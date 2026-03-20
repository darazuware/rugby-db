import pandas as pd
import numpy as np
from datetime import datetime
import os
import re

INPUT_CSV_PATH = 'data_sources/final_master_data_v26_mlr_integrated.csv'
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

def get_best_value(row, col_choices):
    """複数の候補カラムから最初に有効な値を持つものを物理取得"""
    for col in col_choices:
        if col in row:
            val = row.get(col)
            if pd.notna(val) and str(val).strip() != "" and str(val).lower() != "nan":
                return str(val).strip()
    return ""

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
        # 英語名の候補
        name_en = get_best_value(row, ['英語名', 'Full_Name', 'Player_Name'])
        name_norm = normalize_name(name_en)
        current_caps = get_best_value(row, ['代表キャップ数', 'Representative_Caps', 'International_Caps'])
        
        if is_low_quality(current_caps):
            if name_norm in caps_by_name:
                return caps_by_name[name_norm]
            if url in caps_by_url:
                rescued = caps_by_url[url]
                if not is_low_quality(rescued):
                    return rescued
        return current_caps

    # 新しいDataFrame用のリスト
    processed_rows = []
    for _, row in df.iterrows():
        new_row = {
            'Player_Name': get_best_value(row, ['英語名', 'Full_Name', 'Player_Name']),
            'Full_Name': get_best_value(row, ['選手名', 'Full_Name']),
            '選手名_カタカナ': get_best_value(row, ['選手名_カタカナ', '選手名']),
            'Position': get_best_value(row, ['ポジション', 'Position']),
            'Current_Team': get_best_value(row, ['所属チーム', 'Current_Team']),
            'League': get_best_value(row, ['リーグ', 'League']),
            'Height': get_best_value(row, ['身長', 'Height']),
            'Weight': get_best_value(row, ['体重', 'Weight']),
            'Birth_Date': get_best_value(row, ['生年月日', 'Birth_Date']),
            'Age': get_best_value(row, ['年齢', 'Age']),
            'Scraped_Url': get_best_value(row, ['Scraped_Url', 'URL']),
            'キャリア遍歴': get_best_value(row, ['キャリア遍歴', 'Full_Career']),
            'High_School': get_best_value(row, ['高校', 'High_School']),
            'University': get_best_value(row, ['大学', 'University']),
            'Representative_Caps': rescue_caps(row)
        }
        processed_rows.append(new_row)

    final_df = pd.DataFrame(processed_rows)

    # 重複排除
    if 'Scraped_Url' in final_df.columns:
        final_df['Scraped_Url'] = final_df['Scraped_Url'].astype(str).str.strip().str.lower()
        # 有効なURLを持つものと持たないものに分離
        mask = (final_df['Scraped_Url'] != "") & (final_df['Scraped_Url'] != "nan")
        with_url = final_df[mask].copy()
        no_url = final_df[~mask].copy()
        
        # URLがある場合はURLで重複排除（データの物理的に充実している方を残す）
        with_url['nan_count'] = with_url.isnull().sum(axis=1)
        deduped_with_url = with_url.sort_values('nan_count', ascending=True).drop_duplicates(subset=['Scraped_Url'], keep='first')
        deduped_with_url = deduped_with_url.drop(columns=['nan_count'])
        
        # 名前でさらなる重複排除（URLがない場合）
        no_url['name_norm'] = no_url['Player_Name'].apply(normalize_name)
        no_url['nan_count'] = no_url.isnull().sum(axis=1)
        deduped_no_url = no_url.sort_values('nan_count', ascending=True).drop_duplicates(subset=['name_norm'], keep='first')
        deduped_no_url = deduped_no_url.drop(columns=['nan_count', 'name_norm'])
        
        final_df = pd.concat([deduped_with_url, deduped_no_url], ignore_index=True)
    else:
        final_df = final_df

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
