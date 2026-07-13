import json
import os

JSON_DB_PATH = 'data/unified_player_database_final.json'
ALL_RUGBY_DB_PATH = 'data/allrugby_player_stats.json'

def load_json(path):
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("--- Starting Career History Merge ---")

    # 1. Load Databases
    final_db = load_json(JSON_DB_PATH)
    all_rugby_db = load_json(ALL_RUGBY_DB_PATH)

    if not final_db or not all_rugby_db:
        print("Failed to load databases.")
        return

    updated_count = 0
    
    # Handle list vs dict
    if isinstance(final_db, list):
        # Convert to dict for easier processing if needed, or just iterate
        pass 
    elif isinstance(final_db, dict):
        final_db = list(final_db.values()) # We usually work with list of players?
        # Wait, previous scripts seem to handle both or expect dict.
        # merge_csv_master_data.py expects a dict: for pid, pdata in json_data.items()
        pass

    # Re-loading as dict if it was saved as dict by merge_csv_master_data.py
    # Let's check the structure of final_db again. 
    # The grep output showed "lo_484865": { ... } structure, so it is a DICT.
    
    final_db_dict = final_db if isinstance(final_db, dict) else {p['id']: p for p in final_db}

    for pid, player in final_db_dict.items():
        # Get All.Rugby ID
        ar_id = player.get('all_rugby_id')
        
        # If no ID, try to match by name (fallback)? 
        # For now, rely on ID as it's safer.
        
        if ar_id:
            # ar_id might be int or str in final_db, keys in all_rugby_db are strings
            ar_key = str(ar_id)
            
            if ar_key in all_rugby_db:
                ar_data = all_rugby_db[ar_key]
                career_path = ar_data.get('career_path', [])
                
                # Check if we should update
                current_career = player.get('career_history', [])
                
                # If current is empty or string (some scripts use string "A -> B"), format it
                if not current_career or current_career == []:
                    if career_path:
                        # Ensure it's a list for consistency with other parts or string?
                        # JSON grep showed: "career_history": []
                        # Generator likely expects a list of objects or a string.
                        # Generator console_career_history expects a STRING ' -> ' joined?
                        # view_file of generator: consolidate_career_history(career_string) ... parts = career_string.split(' -> ')
                        # So it expects a String!
                        
                        player['career_history'] = ' -> '.join(career_path)
                        updated_count += 1
                        # print(f"Updated {player.get('name_en')} history: {len(career_path)} entries")
                    
                # Also update stats if 0
                current_caps = player.get('representative_caps')
                if not current_caps or current_caps == 0:
                     # e.g. "NZ代表(89)"
                     # AllRugby doesn't show caps text directly, but maybe matches played?
                     pass

    print(f"Merge Complete. Updated career history for {updated_count} players.")
    
    # Save back
    save_json(final_db_dict, JSON_DB_PATH)

if __name__ == "__main__":
    main()
