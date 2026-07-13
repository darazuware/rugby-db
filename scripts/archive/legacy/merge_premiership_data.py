import pandas as pd
import json
import os
import re

# パス設定
RAW_CSV = "data_sources/gallagher_premiership_players_raw.csv"
WIKI_CSV = "data_sources/premiership_wikipedia_fullnames.csv"
KATAKANA_JSON = "scripts/katakana_mapping.json"
OUTPUT_CSV = "data_sources/gallagher_premiership_players.csv"

def load_katakana_map():
    if os.path.exists(KATAKANA_JSON):
        with open(KATAKANA_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def fuzzy_match(name_raw, wiki_df):
    """
    イニシャル名 (A. Barbeary) とWikipediaのフルネーム (Alfie Barbeary) をマッチング
    """
    if not isinstance(name_raw, str): return None
    
    parts = name_raw.split('. ')
    if len(parts) < 2: return None
    
    initial = parts[0]
    last_name = parts[1]
    
    # 同じチームのWikipedia選手から探す
    # (チーム名は完全に一致していることが前提)
    potential_matches = wiki_df[wiki_df['name_en'].str.contains(last_name, case=False, na=False)]
    
    for _, row in potential_matches.iterrows():
        wiki_name = row['name_en']
        if wiki_name.startswith(initial):
            return wiki_name
            
    return None

def main():
    if not os.path.exists(RAW_CSV) or not os.path.exists(WIKI_CSV):
        print("Missing input files.")
        return

    df_raw = pd.read_csv(RAW_CSV)
    df_wiki = pd.read_csv(WIKI_CSV)
    katakana_map = load_katakana_map()
    
    print(f"Loaded {len(df_raw)} raw players and {len(df_wiki)} wiki players.")
    
    results = []
    matches = 0
    
    for _, row in df_raw.iterrows():
        name_en = row['name_en']
        team = row['team']
        pos = row['position']
        
        # マッチング試行
        full_name = fuzzy_match(name_en, df_wiki[df_wiki['team'] == team])
        
        final_name = full_name if full_name else name_en
        if full_name: matches += 1
        
        # カタカナ名の取得
        name_jp = katakana_map.get(final_name.upper(), "")
        
        # v25形式のカラム構築 (一部は空欄または推論)
        results.append({
            "title": name_jp or final_name, # 日本語名があればそれ、なければ英語名
            "title_en": final_name,
            "position": pos,
            "team_name": team,
            "height": "",
            "weight": "",
            "birthday": "",
            "age": "",
            "school": "",
            "shusshin": "",
            "shikaku": "",
            "type": "A", # プレミアシップは基本的にAタイプ
            "url": "",
            "career_history": f"{team} (2025 - )",
            "caps": "",
            "representative_team": row.get('nationality', ""), # Wikipediaから引き継ぐ
            "scraped_url": "",
            "career_history_en": f"{team} (2025 - )",
            "name_en": final_name,
            "name_jp": name_jp,
            "league": "premiership"
        })
        
    df_final = pd.DataFrame(results)
    df_final.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    
    print(f"Saved {len(df_final)} players to {OUTPUT_CSV} (Matches: {matches})")

if __name__ == "__main__":
    main()
