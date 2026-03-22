import pandas as pd
import json
import os

PROJECT_ROOT = '/Users/ktamatzmoto/Desktop/rugbypicks'
CSV_PATH = os.path.join(PROJECT_ROOT, 'data_sources/final_master_data_v27_normalized.csv')
MAPPING_PATH = os.path.join(PROJECT_ROOT, 'scripts/katakana_mapping.json')

def enrich_names():
    print(f"Loading CSV from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    
    print(f"Loading mapping from {MAPPING_PATH}...")
    with open(MAPPING_PATH, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    enriched_count = 0
    for idx, row in df.iterrows():
        name_en = str(row.get('Player_Name', '')).strip()
        name_ja = str(row.get('Full_Name', '')).strip()
        
        # 日本語名が空、または 'nan' の場合
        if not name_ja or name_ja.lower() == 'nan':
            if name_en in mapping:
                df.at[idx, 'Full_Name'] = mapping[name_en]
                enriched_count += 1
                
        # 選手名_カタカナ も同様に補完
        katakana = str(row.get('選手名_カタカナ', '')).strip()
        if not katakana or katakana.lower() == 'nan':
             if name_en in mapping:
                df.at[idx, '選手名_カタカナ'] = mapping[name_en]

    if enriched_count > 0:
        print(f"Successfully enriched {enriched_count} players with Japanese names.")
        df.to_csv(CSV_PATH, index=False)
        print(f"Saved enriched CSV to {CSV_PATH}")
    else:
        print("No new names to enrich found.")

if __name__ == "__main__":
    enrich_names()
