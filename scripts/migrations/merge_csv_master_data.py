
import json
import csv
import re
import os
import unicodedata

JSON_DB_PATH = 'data/unified_player_database_final.json'
CSV_PATH = 'data_sources/final_master_data_v17_consolidated.csv'
OUTPUT_PATH = 'data/unified_player_database_final.json'

def normalize_name(name):
    """Normalize name for matching (lowercase, no special chars)."""
    if not name: return ""
    name = str(name).lower()
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', '_', name) # match slug style
    return name.strip()

def load_json_db():
    if not os.path.exists(JSON_DB_PATH):
        print(f"Error: {JSON_DB_PATH} not found.")
        return {}
    with open(JSON_DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_db(data):
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("--- Starting CSV Master Data Merge ---")
    
    # 1. Load JSON
    json_data = load_json_db()
    if not json_data: return

    # Create a lookup map for JSON data: standardized_name -> player_id
    # This allows fast matching.
    name_to_id_map = {}
    for pid, pdata in json_data.items():
        # Try both EN and JA names
        en_norm = normalize_name(pdata.get('name_en'))
        ja_norm = normalize_name(pdata.get('name_ja'))
        if en_norm: name_to_id_map[en_norm] = pid
        if ja_norm: name_to_id_map[ja_norm] = pid

    updated_count = 0
    
    # 2. Iterate CSV and Update
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name_en = row.get('英語名')
                name_ja = row.get('選手名')
                
                # Try to find match
                target_id = None
                
                # Strategy 1: Match by English Name
                norm_en = normalize_name(name_en)
                if norm_en in name_to_id_map:
                    target_id = name_to_id_map[norm_en]
                
                # Strategy 2: Match by Japanese Name
                if not target_id:
                    norm_ja = normalize_name(name_ja)
                    if norm_ja in name_to_id_map:
                        target_id = name_to_id_map[norm_ja]
                
                if target_id:
                    # UPDATE JSON with CSV MASTER DATA
                    p = json_data[target_id]
                    
                    # Name (Critical Fix)
                    if name_ja: p['name_ja'] = name_ja
                    if name_en: p['name_en'] = name_en
                    
                    # School (Master Source)
                    hs = row.get('高校')
                    univ = row.get('大学')
                    if hs and hs != '-': p['high_school'] = hs
                    if univ and univ != '-': p['university'] = univ
                    
                    # DOB
                    dob = row.get('生年月日')
                    if dob and dob != '-': p['birthdate'] = dob
                    
                    # Team (Master Source)
                    team_ja = row.get('所属チーム')
                    if team_ja and team_ja != '-': p['team'] = team_ja

                    # Category
                    cat = row.get('カテゴリ')
                    if cat: p['category'] = cat
                    
                    # Position (Optional override, maybe safe to keep scraped?)
                    # Let's trust CSV for Position too if available
                    pos = row.get('ポジション')
                    if pos and pos != '-': p['position'] = pos

                    # Height/Weight (Trust CSV)
                    ht = row.get('身長')
                    wt = row.get('体重')
                    if ht and ht != '-': p['height'] = ht
                    if wt and wt != '-': p['weight'] = wt
                    
                    updated_count += 1
                else:
                    # OPTIONAL: Add new player from CSV if not in JSON?
                    # For now, let's stick to updating existing to be safe
                    # print(f"Skipping CSV player not in DB: {name_en}")
                    pass

    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # 3. Save
    save_json_db(json_data)
    print(f"Merge Complete. Updated {updated_count} players using CSV master data.")

if __name__ == "__main__":
    main()
