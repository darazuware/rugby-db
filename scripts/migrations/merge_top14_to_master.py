import json
import os

def merge():
    # Load files
    with open('data/top14_players_enriched.json', 'r') as f:
        top14_players = json.load(f)
    
    with open('data/top14_name_map.json', 'r') as f:
        name_map = json.load(f)
        
    master_db_path = 'data/unified_player_database_final.json'
    if os.path.exists(master_db_path):
        with open(master_db_path, 'r') as f:
            master_db = json.load(f)
    else:
        master_db = {}

    if isinstance(master_db, list):
        # Convert list to dict if needed (backward compatibility)
        new_db = {}
        for p in master_db:
            p_id = p.get('id') or p.get('slug')
            if p_id: new_db[p_id] = p
        master_db = new_db

    new_players_count = 0
    updated_players_count = 0
    
    for p in top14_players:
        # Apply name translation
        if p['en_name'] in name_map:
            p['name_ja'] = name_map[p['en_name']]
        
        # Prepare merged object
        p_slug = p['slug']
        player_obj = {
            "id": p_slug,
            "source": "top_14",
            "name_en": p['en_name'],
            "name_ja": p.get('name_ja', p['en_name']),
            "league": "Top 14",
            "team": p.get('team_ja', p.get('team_en', '')),
            "position": p.get('position_ja') or p.get('position_en', ''),
            "height": p.get('height', ''),
            "weight": p.get('weight', ''),
            "birthdate": p.get('birthday', ''),
            "age": p.get('age', ''),
            "nationality": p.get('nationality', ''),
            "representative_caps": str(p.get('caps', '0')),
            "url": p['all_rugby_url'],
            "career_history": p.get('career_history', []),
            "all_rugby_stats": p.get('stats', {}),
            "image_url": p.get('image_url', ''),
            "category": "A" # Default for rich display
        }
        
        if p_slug in master_db:
            master_db[p_slug].update(player_obj)
            updated_players_count += 1
        else:
            master_db[p_slug] = player_obj
            new_players_count += 1
            
    # Save merged database
    with open(master_db_path, 'w', encoding='utf-8') as f:
        json.dump(master_db, f, ensure_ascii=False, indent=2)
        
    print(f"Merge Complete:")
    print(f"- New players added: {new_players_count}")
    print(f"- Existing players updated: {updated_players_count}")
    print(f"- Total players in database: {len(master_db)}")

if __name__ == "__main__":
    merge()
