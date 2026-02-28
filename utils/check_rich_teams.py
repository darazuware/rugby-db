import json
import os
import re

def check_rich_teams():
    with open('data/unified_player_database_final.json', 'r', encoding='utf-8') as f:
        players = json.load(f)
    
    with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
        l1_teams = json.load(f)
        
    # Create valid team map
    # Normalize names to match player data if possible
    valid_teams = {} # name -> division
    for t in l1_teams:
        valid_teams[t['team_name']] = t.get('division')
        
    # Additional mapping if needed (known variations)
    # The player data 'team' field might differ from 'team_name'
    
    rich_players = []
    
    for p in players:
        score = 0
        if p.get('height') and str(p.get('height')) not in ['nan', '-']: score += 1
        if p.get('weight') and str(p.get('weight')) not in ['nan', '-']: score += 1
        if p.get('birthdate') and len(str(p.get('birthdate'))) > 4: score += 1
        img = p.get('image_url')
        if img and 'placeholder' not in img and str(img) != 'nan': score += 1
        if p.get('rep_caps') and str(p.get('rep_caps')) not in ['nan', '-']: score += 1
        
        # User defined "Rich" as having data. I used score>=3 before.
        # Let's stick to the 1375 number logic.
        if score >= 3:
            rich_players.append(p)
            
    print(f"Rich Players Found: {len(rich_players)}")
    
    # Check teams
    matched = 0
    unmatched = 0
    unmatched_teams = set()
    
    for p in rich_players:
        p_team = p.get('team')
        # Clean team name (remove year etc)
        # e.g. "Suntory (2024)" -> "Suntory"
        if not p_team:
            unmatched +=1
            continue
            
        clean_team = re.sub(r'[（(]\d{4}.*?[）)]', '', str(p_team)).strip()
        
        # Try finding in valid_teams
        # We need a robust check (fuzzy or direct)
        # For now, simplistic check
        
        found = False
        for vt in valid_teams:
            if vt in clean_team or clean_team in vt:
                found = True
                break
        
        if found:
            matched += 1
        else:
            unmatched += 1
            unmatched_teams.add(clean_team)
            
    print(f"Matched to League One: {matched}")
    print(f"Unmatched: {unmatched}")
    
    if unmatched > 0:
        print("Unmatched Teams Sample:")
        for t in list(unmatched_teams)[:10]:
            print(f" - {t}")

if __name__ == "__main__":
    check_rich_teams()
