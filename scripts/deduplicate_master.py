import pandas as pd
import numpy as np
from datetime import datetime
import os
import re
import json
import unicodedata

# 物理基準パス
INPUT_CSV_PATH = 'data_sources/final_master_data_v27_normalized.csv'
TEAM_NAMES_JP_PATH = 'data/team_names_jp.json'
SOURCE_REPRESENTATIVES_PATH = 'data_sources/national_representatives.csv'
OUTPUT_CSV_PATH = 'data_sources/final_master_data_v27_normalized.csv'
BACKUP_PATH = 'data_sources/final_master_data_v27_normalized.csv.bak_before_fix'

def normalize_text(text):
    if not text or pd.isna(text): return ""
    text = unicodedata.normalize('NFKC', str(text))
    
    # If the text contains Japanese characters (Hiragana/Katakana), 
    # skip the NFD-stripping logic to avoid losing voicing marks.
    if not re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text):
        # Only apply Mn stripping for non-Japanese text (e.g. Latin accents)
        new_text = ""
        for c in unicodedata.normalize('NFD', text):
            if unicodedata.category(c) != 'Mn':
                new_text += c
        text = unicodedata.normalize('NFKC', new_text)
    # Remove special dots and extra spaces
    text = text.replace('・', ' ').replace('·', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_id(text):
    """名前比較用の極限正規化（アルファベットのみ）"""
    if not text: return ""
    return re.sub(r'[^a-zA-Z]', '', str(text)).lower()

def load_league_mapping():
    """team_names_jp.json から チーム名 -> リーグ名 のマッピングを作成"""
    mapping = {}
    if os.path.exists(TEAM_NAMES_JP_PATH):
        with open(TEAM_NAMES_JP_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for league, teams in data.items():
                for official_en, info in teams.items():
                    mapping[official_en.lower()] = league
                    if 'jp' in info:
                        mapping[info['jp'].lower()] = league
                    if 'aliases' in info:
                        for alias in info['aliases']:
                            mapping[alias.lower()] = league
    return mapping

def validate_physical_stat(val, type_name='height'):
    if not val or pd.isna(val): return ""
    v_str = str(val).strip()
    if '/' in v_str: return ""
    v_clean = re.sub(r'[^0-9.]', '', v_str)
    if not v_clean: return ""
    try:
        vf = float(v_clean)
        if type_name == 'height':
            if vf < 3.0: vf *= 100
            if vf < 140 or vf > 220: return ""
        else:
            if vf < 50 or vf > 160: return ""
        return str(vf)
    except:
        return ""

def deduplicate():
    if not os.path.exists(INPUT_CSV_PATH):
        print(f"File not found: {INPUT_CSV_PATH}")
        return

    # バックアップの作成
    import shutil
    shutil.copy2(INPUT_CSV_PATH, BACKUP_PATH)

    df = pd.read_csv(INPUT_CSV_PATH)
    print(f"Original row count: {len(df)}")
    
    league_map = load_league_mapping()
    
    processed_rows = []
    for _, row in df.iterrows():
        # 基本情報の抽出と正規化
        name_en = normalize_text(row.get('Player_Name', ''))
        name_ja = normalize_text(row.get('Full_Name', ''))
        katakana = normalize_text(row.get('選手名_カタカナ', ''))
        
        # リーグの修正（MLR誤分類の救済）
        current_team = str(row.get('Current_Team', '')).strip()
        # 括弧書きを除去して検索
        clean_team = re.sub(r'（.*）|\(.*\)', '', current_team).strip()
        
        csv_league = str(row.get('League', '')).strip().lower()
        mapped_league = league_map.get(clean_team.lower())
        
        final_league = mapped_league if mapped_league else csv_league
        
        # 正真正銘の MLR は除外
        if final_league == 'mlr':
            continue

        # スラッグ重複の原因となる URL の正規化
        scraped_url = str(row.get('Scraped_Url', '')).strip().lower()
        if scraped_url == 'nan' or scraped_url == '':
            scraped_url = ""

        new_row = {
            'Player_Name': name_en,
            'Full_Name': name_ja,
            '選手名_カタカナ': katakana,
            'Position': row.get('Position'),
            'Current_Team': current_team,
            'League': final_league,
            'Height': validate_physical_stat(row.get('Height'), 'height'),
            'Weight': validate_physical_stat(row.get('Weight'), 'weight'),
            'Birth_Date': row.get('Birth_Date'),
            'Age': row.get('Age'),
            'Nationality': row.get('Nationality'),
            'Representative_Caps': row.get('Representative_Caps'),
            'Scraped_Url': scraped_url,
            'キャリア遍歴': row.get('キャリア遍歴'),
            'High_School': row.get('High_School'),
            'University': row.get('University')
        }
        processed_rows.append(new_row)

    final_df = pd.DataFrame(processed_rows)

    # 重複排除の実行
    # 1. URLがある場合はURLで重複排除
    final_df['Scraped_Url'] = final_df['Scraped_Url'].astype(str).str.strip().str.lower()
    mask_url = (final_df['Scraped_Url'] != "") & (final_df['Scraped_Url'] != "nan")
    
    with_url = final_df[mask_url].copy()
    no_url = final_df[~mask_url].copy()
    
    # 欠損値の少なさでソートして、URLで重複排除
    with_url['quality'] = with_url.notna().sum(axis=1)
    deduped_with_url = with_url.sort_values('quality', ascending=False).drop_duplicates(subset=['Scraped_Url'], keep='first')
    deduped_with_url = deduped_with_url.drop(columns=['quality'])
    
    # 2. URLがない、またはURLによる排除後のデータに対して名前で重複排除
    # 統合した全データに対して名前（極限正規化）でさらにマージを試みる
    combined = pd.concat([deduped_with_url, no_url], ignore_index=True)
    combined['name_id'] = combined['Player_Name'].apply(normalize_id)
    combined['quality'] = combined.notna().sum(axis=1)
    
    # 名前IDで重複排除（同じ名前IDでURLが異なる場合も、基本的には同一人物とみなして品質の高い方を残す）
    final_deduped = combined.sort_values('quality', ascending=False).drop_duplicates(subset=['name_id'], keep='first')
    final_deduped = final_deduped.drop(columns=['quality', 'name_id'])

    print(f"Final row count: {len(final_deduped)}")
    
    final_deduped.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"Saved optimized master to {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    deduplicate()
