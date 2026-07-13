import json
import re

MASTER_DB = 'unified_player_database_full.json'
LIVE_DATA = 'live_player_data.json'
OUTPUT_DB = 'data/unified_player_database_final.json'

def normalize(name):
    if not name: return ""
    return str(name).replace(' ', '').replace('　', '').strip()

print("Loading databases...")
with open(MASTER_DB, 'r', encoding='utf-8') as f:
    master_players = json.load(f)

# live_data is keyed by player ID (string)
live_data = {}
try:
    with open(LIVE_DATA, 'r', encoding='utf-8') as f:
        live_data = json.load(f)
except FileNotFoundError:
    print("No live data found. Skipping merge.")
    exit()

print(f"Master players: {len(master_players)}")
print(f"Live fresh players: {len(live_data)}")

# Create lookup maps for Master DB
# 1. By ID (numeric part of URL)
# 2. By Kanji Name
# 3. By English Name
master_by_id = {}
master_by_name_ja = {}
master_by_name_en = {}

for p in master_players:
    # Extract ID from URL if possible
    url = p.get('url', '')
    if 'league-one.jp/player/' in url:
        pid = url.split('/')[-1]
        master_by_id[pid] = p
        
    if p.get('name_ja'):
        master_by_name_ja[normalize(p['name_ja'])] = p
    if p.get('name_en'):
        master_by_name_en[normalize(p['name_en']).lower()] = p

updates = 0
matches = 0

for pid, live_p in live_data.items():
    # Try to find match in Master
    match = None
    
    # Strat 1: ID Match
    if pid in master_by_id:
        match = master_by_id[pid]
    
    # Strat 2: Name Kanji Match
    elif normalize(live_p.get('name_ja')) in master_by_name_ja:
        match = master_by_name_ja[normalize(live_p.get('name_ja'))]
        
    if match:
        matches += 1
        # Update Data
        match['league_one_caps'] = live_p.get('league_one_caps', match.get('league_one_caps'))
        
        # Stats
        curr_stats = match.get('all_rugby_stats', {})
        curr_stats['matches_played'] = live_p.get('matches', curr_stats.get('matches_played'))
        curr_stats['tries'] = live_p.get('tries', curr_stats.get('tries'))
        curr_stats['points'] = live_p.get('points', curr_stats.get('points'))
        match['all_rugby_stats'] = curr_stats
        
        # Socials
        match['socials'] = live_p.get('socials', {})
        
        # Image
        if live_p.get('image_url'):
            match['image_url'] = live_p.get('image_url')
            
        # URL Fix (Important for Tatekawa case)
        match['url'] = live_p.get('url')
        match['id'] = f"lo_{pid}" # Force ID update? Maybe safe.
        
        updates += 1
    else:
        # New player? Or just no match?
        # Maybe add as new player if absolutely sure?
        # For now, skip to be safe.
        pass

print(f"Merged {updates} players.")

with open(OUTPUT_DB, 'w', encoding='utf-8') as f:
    json.dump(master_players, f, ensure_ascii=False, indent=2)

print("Done.")
