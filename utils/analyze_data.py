import json
import os

def analyze_quality():
    with open('data/unified_player_database_final.json', 'r', encoding='utf-8') as f:
        players = json.load(f)
    
    total = len(players)
    print(f"Total Players: {total}")
    
    # Counts
    has_height = 0
    has_weight = 0
    has_dob = 0
    has_pos = 0
    has_team = 0
    has_caps = 0
    has_image = 0
    
    # "Rich" profiles (arbitrary definition: has at least 3 distinct attributes beyond name)
    rich_count = 0
    
    # "Empty" profiles (only name/id/url)
    empty_count = 0

    for p in players:
        score = 0
        
        h = p.get('height')
        if h and str(h) != 'nan' and str(h) != '-': 
            has_height += 1
            score += 1
            
        w = p.get('weight')
        if w and str(w) != 'nan' and str(w) != '-': 
            has_weight += 1
            score += 1
            
        d = p.get('birthdate')
        if d and str(d) != 'nan' and len(d) > 4: 
            has_dob += 1
            score += 1
            
        pos = p.get('position')
        if pos and str(pos) != 'nan' and str(pos) != '-': 
            has_pos += 1
            
        # Team check (current)
        t = p.get('team')
        if t and str(t) != 'nan' and str(t) != '-': 
            has_team += 1
            
        # Caps
        c = p.get('rep_caps')
        if c and str(c) != 'nan' and str(c) != '-': 
            has_caps += 1
            score += 1

        # Image
        img = p.get('image_url')
        if img and 'placeholder' not in img and str(img) != 'nan':
            has_image += 1
            score += 1

        if score >= 3:
            rich_count += 1
        
        if score == 0 and (not pos or pos=='-'):
            empty_count += 1

    print(f"Has Height: {has_height} ({has_height/total*100:.1f}%)")
    print(f"Has Weight: {has_weight} ({has_weight/total*100:.1f}%)")
    print(f"Has DOB:    {has_dob} ({has_dob/total*100:.1f}%)")
    print(f"Has Pos:    {has_pos} ({has_pos/total*100:.1f}%)")
    print(f"Has Team:   {has_team} ({has_team/total*100:.1f}%)")
    print(f"Has Caps:   {has_caps} ({has_caps/total*100:.1f}%)")
    print(f"Has Image:  {has_image} ({has_image/total*100:.1f}%)")
    print("-" * 30)
    print(f"Rich Profiles (3+ stats): {rich_count} ({rich_count/total*100:.1f}%)")
    print(f"Empty Profiles (Name only): {empty_count} ({empty_count/total*100:.1f}%)")

if __name__ == "__main__":
    analyze_quality()
