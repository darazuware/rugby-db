import json
import pandas as pd

print("=== Merging Nationality Data ===\n")

# Load unified player database
print("Loading unified_player_database.json...")
with open('unified_player_database.json', 'r') as f:
    unified_players = json.load(f)
print(f"  ✓ Loaded {len(unified_players)} players\n")

# Load rugby_players.json (4072 players with nationality data)
print("Loading rugby_players.json...")
with open('data/rugby_players.json', 'r') as f:
    rugby_players = json.load(f)
print(f"  ✓ Loaded {len(rugby_players)} players with nationality data\n")

# Create name-based lookup for rugby_players
def normalize_name(name):
    """Normalize name for matching"""
    if pd.isna(name) or not name:
        return ""
    return str(name).lower().strip().replace(' ', '').replace('-', '').replace('.', '')

print("Creating name lookup index...")
rugby_players_by_name = {}
for player in rugby_players:
    name_ja = normalize_name(player.get('name_ja', ''))
    name_en = normalize_name(player.get('name', ''))
    
    if name_ja:
        rugby_players_by_name[name_ja] = player
    if name_en:
        rugby_players_by_name[name_en] = player

print(f"  ✓ Indexed {len(rugby_players_by_name)} unique names\n")

# Merge nationality data
print("Merging nationality data...")
merged_count = 0
for player in unified_players:
    name_ja_norm = normalize_name(player.get('name_ja', ''))
    name_en_norm = normalize_name(player.get('name_en', ''))
    
    # Try to find match
    rugby_player = None
    if name_ja_norm in rugby_players_by_name:
        rugby_player = rugby_players_by_name[name_ja_norm]
    elif name_en_norm in rugby_players_by_name:
        rugby_player = rugby_players_by_name[name_en_norm]
    
    if rugby_player:
        # Merge nationality data
        if rugby_player.get('nationality'):
            player['nationality'] = rugby_player['nationality']
            merged_count += 1
        
        # Add other useful fields if available
        if rugby_player.get('caps'):
            player['international_caps'] = rugby_player['caps']
        
        if rugby_player.get('url') and 'player-' not in rugby_player.get('url', ''):
            player['allrugby_url'] = rugby_player['url']

print(f"  ✓ Merged nationality for {merged_count} players\n")

# Save updated database
print("Saving updated unified_player_database.json...")
with open('unified_player_database.json', 'w', encoding='utf-8') as f:
    json.dump(unified_players, f, ensure_ascii=False, indent=2)
print("  ✓ Saved\n")

# Statistics
with_nationality = sum(1 for p in unified_players if p.get('nationality'))
print(f"=== Statistics ===")
print(f"Total players: {len(unified_players)}")
print(f"Players with nationality: {with_nationality} ({with_nationality/len(unified_players)*100:.1f}%)")
print(f"Newly merged: {merged_count}")
