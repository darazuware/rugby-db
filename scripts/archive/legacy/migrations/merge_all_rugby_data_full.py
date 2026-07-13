import json
import os
import re

def normalize_name(name):
    """Normalize name for matching"""
    if not name:
        return ""
    return str(name).lower().strip().replace(' ', '').replace('-', '')

def clean_team_name(name):
    """Remove year notation from team name"""
    if not name:
        return ""
    name = re.sub(r'[（(]\d{4}.*?[）)]', '', name)
    return name.strip()

# Load data
print("Loading master database...")
with open('unified_player_database.json', 'r', encoding='utf-8') as f:
    master_players = json.load(f)

print("Loading All.Rugby data...")
with open('allrugby_player_stats.json', 'r', encoding='utf-8') as f:
    all_rugby_data = json.load(f)

print(f"Master players: {len(master_players)}")
print(f"All.Rugby players: {len(all_rugby_data)}")

# Create lookup for master players by normalized English name
master_lookup = {normalize_name(p.get('name_en')): p for p in master_players}

merged_count = 0
new_count = 0

# Track matching
matched_all_rugby_ids = set()

# Process All.Rugby data
final_players = []

# Load CSV for Category and latest Caps
import csv
csv_lookup = {}
try:
    with open('final_master_data_v25.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader) # Skip header
        for row in reader:
            if len(row) > 11:
                # Key: English Name or Normalized? 
                # Master DB uses name_en.
                csv_lookup[normalize_name(row[0])] = {
                    'category': row[11],
                    'caps': row[12] if len(row) > 12 else 0
                }
except Exception as e:
    print(f"Warning: Could not read CSV: {e}")

# First, process existing master players and enrich them
for p in master_players:
    name_en_norm = normalize_name(p.get('name_en'))
    
    # Inject CSV data (Category)
    csv_info = csv_lookup.get(name_en_norm)
    if csv_info:
        p['category'] = csv_info['category']
        # Optionally update caps from CSV if 0 in master? 
        # Master DB 'league_one_caps' might be old.
        if p.get('league_one_caps', 0) == 0 and csv_info['caps']:
             try:
                 p['league_one_caps'] = int(csv_info['caps'])
             except:
                 pass
    else:
        p['category'] = '-'

    # Manual Fix: Zack Gallagher Caps
    if p.get('name_ja') == 'ザック ・ギャラハー' or 'Zach Gallagher' in str(p.get('name_en')):
         p['league_one_caps'] = 3
         p['category'] = 'B' # Force B just in case

    # Try to find in All.Rugby (existing logic)
    matched_id = None
    for ar_id, ar_p in all_rugby_data.items():
        if normalize_name(ar_p.get('name')) == name_en_norm:
            matched_id = ar_id
            break
    
    if matched_id:
        ar_p = all_rugby_data[matched_id]
        # Enrich
        p['all_rugby_id'] = ar_p.get('id')
        p['nationality_1'] = ar_p.get('nationality_1')
        p['nationality_2'] = ar_p.get('nationality_2')
        p['sporting_nationality'] = ar_p.get('sporting_nationality')
        p['origin'] = ar_p.get('origin')
        p['all_rugby_stats'] = {
            'matches_played': ar_p.get('matches_played'),
            'tries': ar_p.get('tries'),
            'points': ar_p.get('points')
        }
        # Update career if missing
        if not p.get('career_history') and ar_p.get('career_path'):
            p['career_history'] = ' -> '.join(ar_p['career_path'])
            
        matched_all_rugby_ids.add(matched_id)
        merged_count += 1
    
    final_players.append(p)

# Manual overrides for specific missing players (e.g. Tetta Shigematsu)
# User reported: Nationality missing, career history needs fix (handled in generator but data helps)
for p in final_players:
    if p.get('name_ja') == '繁松 哲大':
        p['nationality_1'] = 'Japan'
        p['origin'] = 'Japan'
        # Add basic stats if we can find them, otherwise 0
        p['all_rugby_stats'] = {'matches_played': 0, 'tries': 0, 'points': 0}

# Second, add players from All.Rugby that are not in master
print("\nAdding new players from All.Rugby...")
for ar_id, ar_p in all_rugby_data.items():
    if ar_id not in matched_all_rugby_ids:
        # Create new player record
        new_p = {
            'id': f"ar_{ar_id}",
            'source': 'all_rugby',
            'name_ja': None, # To be translated or keep as is
            'name_en': ar_p.get('name'),
            'position': ar_p.get('position'),
            'team': ar_p.get('current_club'),
            'height': ar_p.get('height'),
            'weight': ar_p.get('weight'),
            'birthdate': None,
            'age': None,
            'high_school': None,
            'university': None,
            'category': None, # All.Rugby data doesn't have this field directly
            'league_one_caps': 0,
            'representative_caps': None,
            'career_history': ' -> '.join(ar_p.get('career_path', [])),
            'all_rugby_id': ar_p.get('id'),
            'nationality_1': ar_p.get('nationality_1'),
            'nationality_2': ar_p.get('nationality_2'),
            'sporting_nationality': ar_p.get('sporting_nationality'),
            'origin': ar_p.get('origin'),
            'all_rugby_stats': {
                'matches_played': ar_p.get('matches_played'),
                'tries': ar_p.get('tries'),
                'points': ar_p.get('points')
            }
        }
        final_players.append(new_p)
        new_count += 1

# Third, integrate Live League One Stats
print("\nIntegrating Live League One Data...")
try:
    with open('league_one_stats_live.json', 'r', encoding='utf-8') as f:
        live_stats = json.load(f)
    
    live_update_count = 0
    for p in final_players:
        # Extract ID from URL (e.g. https://league-one.jp/player/483678)
        url = p.get('url', '')
        if not url or 'league-one.jp/player/' not in url:
            continue
            
        try:
            l1_id = url.split('/')[-1]
            if l1_id in live_stats:
                stat = live_stats[l1_id]
                
                # Update League One Caps (priority over CSV/Master)
                if 'league_one_caps' in stat:
                    p['league_one_caps'] = stat['league_one_caps']
                
                # Update detailed stats (Matches, Tries, Points)
                # These overwrite All.Rugby stats if available, as L1 is more specific/current for these players
                current_stats = p.get('all_rugby_stats', {})
                current_stats['matches_played'] = stat.get('matches', current_stats.get('matches_played', 0))
                current_stats['tries'] = stat.get('tries', current_stats.get('tries', 0))
                current_stats['points'] = stat.get('points', current_stats.get('points', 0))
                p['all_rugby_stats'] = current_stats
                
                live_update_count += 1
        except Exception as e:
            continue
            
    print(f"Live stats updated for {live_update_count} players.")

except FileNotFoundError:
    print("Warning: league_one_stats_live.json not found. Skipping live stats integration.")

# Save merged database
with open('unified_player_database_full.json', 'w', encoding='utf-8') as f:
    json.dump(final_players, f, ensure_ascii=False, indent=2)

print(f"\n=== Merge Complete ===")
print(f"Master players enriched: {merged_count}")
print(f"New players added: {new_count}")
print(f"Total unified players: {len(final_players)}")
