import json
import os
import shutil

# Files
MAIN_DB = 'data/unified_player_database_final.json'
WIKI_DATA = 'player_history_deep.json'
YOUTH_DATA = 'foreign_youth_data.json'
BACKUP_DB = 'unified_player_database_final.json.bak'

def main():
    print("Starting Deep Data Merge...")
    
    # Load Main DB
    if not os.path.exists(MAIN_DB):
        print(f"Error: {MAIN_DB} not found.")
        return

    # Backup
    shutil.copy2(MAIN_DB, BACKUP_DB)
    print(f"Backed up main DB to {BACKUP_DB}")

    with open(MAIN_DB, 'r', encoding='utf-8') as f:
        players = json.load(f)
        
    # Load Deep Data
    wiki_map = {}
    if os.path.exists(WIKI_DATA):
        with open(WIKI_DATA, 'r', encoding='utf-8') as f:
            wiki_map = json.load(f)
            print(f"Loaded {len(wiki_map)} Wikipedia records.")
            
    youth_map = {}
    if os.path.exists(YOUTH_DATA):
        with open(YOUTH_DATA, 'r', encoding='utf-8') as f:
            youth_map = json.load(f)
            print(f"Loaded {len(youth_map)} Foreign Youth records.")

    # Merge
    updates = 0
    for p in players:
        pid = p.get('id')
        
        # 1. Wiki Data (Junior High, Rugby School)
        if pid in wiki_map:
            w = wiki_map[pid]
            # Wiki data structure: {'data': {'junior_high': ..., 'rugby_school': ..., 'minor_rep': []}}
            if 'data' in w:
                d = w['data']
                
                # Junior High
                if d.get('junior_high'):
                    p['junior_high'] = d['junior_high']
                    updates += 1
                
                # Rugby School
                if d.get('rugby_school'):
                    p['rugby_school'] = d['rugby_school']
                    updates += 1
                    
                # Minor Reps
                if d.get('minor_rep'):
                    # Append to representative_history or create new field
                    # Let's create 'extra_history' list
                    if 'extra_history' not in p: p['extra_history'] = []
                    for rep in d['minor_rep']:
                        if rep not in p['extra_history']:
                            p['extra_history'].append(rep)
                    updates += 1

        # 2. Youth Data (U20, etc)
        if str(pid) in youth_map:
            y = youth_map[str(pid)]
            # Structure: {'u20_teams': ['New Zealand U20', ...]}
            if 'u20_teams' in y:
                teams = y['u20_teams']
                if teams:
                    if 'extra_history' not in p: p['extra_history'] = []
                    for t in teams:
                        if t not in p['extra_history']:
                            p['extra_history'].append(t)
                    updates += 1
                    
    # Save
    with open(MAIN_DB, 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=2)
        
    print(f"Merge Complete! Updated {updates} fields in player records.")

if __name__ == "__main__":
    main()
