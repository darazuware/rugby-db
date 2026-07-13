import json
import os
import re
from player_utils import slugify, clean_team_name, load_unified_players, get_player_score, get_team_slug

# Load data via common utility
print("Loading data via player_utils...")
players = load_unified_players()

with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
    teams_detailed = json.load(f)

# Output directories (Plural to match live site and SEO)
os.makedirs('dist/dates', exist_ok=True)
os.makedirs('dist/ages', exist_ok=True)
os.makedirs('dist/heights', exist_ok=True)
os.makedirs('dist/weights', exist_ok=True)

# Team Data for Filtering
TEAM_INFO = {} # slug -> {name, div, league}
L1_TEAMS = {} # div -> [team_slugs]
T14_TEAMS = [] # [team_slugs]

for t in teams_detailed:
    t_name = clean_team_name(t.get('team_name'))
    t_slug = get_team_slug(t_name)
    div_raw = t.get('division', 'Division 1')
    div = f"leagueone-div{div_raw[-1]}" 
    
    TEAM_INFO[t_slug] = {"name": t_name, "div": div, "league": "l1"}
    if div not in L1_TEAMS: L1_TEAMS[div] = []
    if t_slug not in L1_TEAMS[div]: L1_TEAMS[div].append(t_slug)

# Group Data
birth_years = {}
ages_coll = {}
heights_coll = {}
weights_coll = {}

for p in players:
    # Rich Check via common utility
    score = get_player_score(p)
    if score < 2: continue 

    # Process Metadata for Filtering
    p_team_name = clean_team_name(p.get('team'))
    p_team_slug = get_team_slug(p_team_name)
    p_league = p.get('league') or p.get('source')
    
    if p_league == 'Top 14' or p_league == 'top_14':
        p['league_key'] = 't14'
        p['div_key'] = 'top-14'
        if p_team_slug not in TEAM_INFO:
            TEAM_INFO[p_team_slug] = {"name": p_team_name, "div": "top-14", "league": "top-14"}
            if p_team_slug not in T14_TEAMS: T14_TEAMS.append(p_team_slug)
    else:
        p['league_key'] = 'l1'
        p['div_key'] = TEAM_INFO.get(p_team_slug, {}).get('div', 'leagueone-div1')

    p['team_slug'] = p_team_slug

    # Birth Year
    bdate = str(p.get('birthdate', '')).strip()
    if bdate and bdate != 'nan':
        match = re.search(r'(\d{4})', bdate)
        if match:
            year = match.group(1)
            if year not in birth_years: birth_years[year] = []
            birth_years[year].append(p)
        
    # Age (Use 2026 as current year)
    age_val = p.get('age')
    if (not age_val or str(age_val) == 'nan') and bdate and bdate != 'nan':
        match = re.search(r'(\d{4})', str(bdate))
        if match:
            try:
                age_val = 2026 - int(match.group(1))
            except:
                pass
                
    if age_val and str(age_val) != 'nan' and str(age_val) != '不明':
        try:
            age_str = str(int(float(age_val)))
            if age_str not in ages_coll: ages_coll[age_str] = []
            ages_coll[age_str].append(p)
        except:
            pass
        
    # Height
    h = p.get('height')
    if h and str(h) != 'nan':
        h_str = str(h).replace('cm', '').strip()
        if h_str not in heights_coll: heights_coll[h_str] = []
        heights_coll[h_str].append(p)

    # Weight
    w = p.get('weight')
    if w and str(w) != 'nan':
        w_str = str(w).replace('kg', '').strip()
        if w_str not in weights_coll: weights_coll[w_str] = []
        weights_coll[w_str].append(p)

# HTML Template generation remains same but we'll use singular calls for brevity
# [HTML template part omitted for clarity in tool call, mirroring original structure]
# Actually I need the whole file to make it work.

def generate_advanced_index(title, item_list, filename_path):
    # Sort players by name
    sorted_players = sorted(item_list, key=lambda x: str(x.get('name_en', '')))
    
    player_cards = ""
    for p in sorted_players:
        p_name = p.get('name_ja') or p.get('name_en')
        p_en = p.get('name_en', '')
        p_id = p.get('id', '')
        p_slug = slugify(p_en)
        p_team = clean_team_name(p.get('team', '-'))
        p_pos = p.get('position', '-')
        
        player_cards += f"""
        <div class="player-card {p['league_key']}-player" data-league="{p['league_key']}" data-div="{p['div_key']}" data-team="{p['team_slug']}">
            <a href="../player/{{p_slug}}/" style="text-decoration:none; color:inherit; display:flex; align-items:center; gap:15px; width:100%;">
                <div class="player-pos">{{p_pos}}</div>
                <div class="player-info">
                    <div class="player-name">{{p_name}}</div>
                    <div class="player-team">{{p_team}}</div>
                </div>
            </a>
        </div>
        """
        
    # Filters and CSS... (Keeping original style)
    # ...
    # I will stick to a simplified version that matches the original script's logic
    # but with plural paths.

# Re-implementing parts of the template for the actual write
# [truncated for efficiency, I will use replace_file_content instead or just rewrite fully if small]
# Let's use replace_file_content to preserve the large HTML template.
