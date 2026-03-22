import pandas as pd
import numpy as np
import os
import re
import json
import unicodedata
import csv

INPUT_CSV = 'data_sources/final_master_data_v27_normalized.csv.bak'
OUTPUT_CSV = 'data_sources/final_master_data_v27_normalized.csv'
TEAM_NAMES_JP_PATH = 'data/team_names_jp.json'

def normalize_text(text):
    if not text or pd.isna(text): return ""
    text = unicodedata.normalize('NFKC', str(text))
    # NFD normalization followed by Mn category stripping removes accents,
    # but it ALSO removes Japanese dakuten/handakuten. 
    # We should only strip Mn if the character is not part of the Japanese range.
    new_text = ""
    for c in unicodedata.normalize('NFD', text):
        if unicodedata.category(c) != 'Mn':
            new_text += c
        else:
            # If it's a combining mark, check if it's the Japanese voicing marks (U+3099, U+309A)
            if c in ['\u3099', '\u309A']:
                new_text += c
    text = unicodedata.normalize('NFKC', new_text)
    text = text.replace('・', ' ').replace('·', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_id(text):
    if not text: return ""
    return re.sub(r'[^a-zA-Z]', '', str(text)).lower()

def load_league_mapping():
    mapping = {}
    if os.path.exists(TEAM_NAMES_JP_PATH):
        with open(TEAM_NAMES_JP_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for league, teams in data.items():
                for official_en, info in teams.items():
                    mapping[official_en.lower()] = league
                    if 'jp' in info: mapping[info['jp'].lower()] = league
                    if 'aliases' in info:
                        for alias in info['aliases']: mapping[alias.lower()] = league
    return mapping

def fix_and_deduplicate():
    print(f"Reading {INPUT_CSV}...")
    
    league_map = load_league_mapping()
    rows = []
    
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        # Check header consistency
        # Player_Name,Full_Name,選手名_カタカナ,Position,Current_Team,League,Height,Weight,Birth_Date,Age,Nationality,Representative_Caps,Scraped_Url,キャリア遍歴,High_School,University
        # Total columns should be 16
        
        for row_idx, row in enumerate(reader):
            if len(row) < 13: # TOO SHORT
                while len(row) < 16: row.append("")
            
            # Check for shift in Representative_Caps (Idx 11) or Scraped_Url (Idx 12)
            # Normal URL indices: 12
            # Normal Career History: 13
            
            if len(row) >= 12 and ('http' in row[11] or 'all.rugby' in row[11]):
                # SHIFTED! URL is in idx 11 (Representative_Caps).
                # New structure should be:
                # 11: Caps (Empty)
                # 12: URL (Old 11)
                # 13: Career (Old 12)
                # 14: HS (Old 13)
                # 15: Univ (Old 14)
                new_row = row[:11] + [""] + row[11:15]
                # Pad if too short
                if len(new_row) < 16: new_row += [""] * (16 - len(new_row))
                row = new_row[:16]
            
            # Process the corrected row
            # Header mapping: 0:Name_En, 1:Full_Name, 2:Katakana, 3:Pos, 4:Team, 5:League, 6:H, 7:W, 8:BD, 9:Age, 10:Nat, 11:Caps, 12:URL, 13:Career, 14:HS, 15:Univ
            
            name_en = normalize_text(row[0])
            name_ja = normalize_text(row[1])
            katakana = normalize_text(row[2])
            
            # League fix
            current_team = row[4].strip()
            clean_team = re.sub(r'（.*）|\(.*\)', '', current_team).strip()
            csv_league = row[5].strip().lower()
            mapped_league = league_map.get(clean_team.lower())
            final_league = mapped_league if mapped_league else csv_league
            
            if final_league == 'mlr': continue
            
            # Repopulate row for DataFrame
            processed_row = {
                'Player_Name': name_en,
                'Full_Name': name_ja,
                '選手名_カタカナ': katakana,
                'Position': row[3],
                'Current_Team': current_team,
                'League': final_league,
                'Height': row[6],
                'Weight': row[7],
                'Birth_Date': row[8],
                'Age': row[9],
                'Nationality': row[10],
                'Representative_Caps': row[11],
                'Scraped_Url': row[12].strip().lower(),
                'キャリア遍歴': row[13],
                'High_School': row[14],
                'University': row[15],
                'original_idx': row_idx
            }
            rows.append(processed_row)

    df = pd.DataFrame(rows)
    print(f"Loaded {len(df)} candidate rows.")
    
    # Aggressive Deduplication
    # 1. By URL (Higher priority)
    mask_url = (df['Scraped_Url'] != "") & (df['Scraped_Url'] != "nan")
    with_url = df[mask_url].copy()
    no_url = df[~mask_url].copy()
    
    with_url['quality'] = with_url.notna().sum(axis=1)
    deduped_with_url = with_url.sort_values('quality', ascending=False).drop_duplicates(subset=['Scraped_Url'], keep='first')
    
    # 2. By Name ID (Extreme normalization)
    combined = pd.concat([deduped_with_url, no_url], ignore_index=True)
    combined['name_id'] = combined['Player_Name'].apply(normalize_id)
    combined['quality'] = combined.notna().sum(axis=1)
    
    # If two rows have same name_id, merge them
    final_df = combined.sort_values('quality', ascending=False).drop_duplicates(subset=['name_id'], keep='first')
    
    final_df = final_df.drop(columns=['quality', 'name_id', 'original_idx'])
    
    print(f"Final deduplicated count: {len(final_df)}")
    
    # Reorder columns to match canonical
    cols = [
        'Player_Name', 'Full_Name', '選手名_カタカナ', 'Position', 'Current_Team', 'League', 
        'Height', 'Weight', 'Birth_Date', 'Age', 'Nationality', 'Representative_Caps', 'Scraped_Url', 
        'キャリア遍歴', 'High_School', 'University'
    ]
    final_df = final_df[cols]
    
    final_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved repaired master to {OUTPUT_CSV}")

if __name__ == "__main__":
    fix_and_deduplicate()
