import json
import os
import re
from player_utils import (
    slugify, clean_team_name, load_unified_players, 
    get_player_score, get_team_slug, get_league_slug_for_team,
    calculate_age, get_canonical_school_name, get_pos_rank
)

# Load data
players = load_unified_players()
with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
    league_one_teams = json.load(f)
with open('data/rugby_leagues.json', 'r', encoding='utf-8') as f:
    leagues = json.load(f)

CONTENT_BASE = 'content/teams'
os.makedirs(CONTENT_BASE, exist_ok=True)

def generate_team_md(team_data):
    team_name = team_data['team_name']
    slug = get_team_slug(team_name)
    league_slug = team_data.get('league_slug', 'leagueone')
    
    team_dir = os.path.join(CONTENT_BASE, league_slug, slug)
    os.makedirs(team_dir, exist_ok=True)
    
    # Filter players
    team_players = []
    for p in players:
        if get_player_score(p) < 2: continue
        
        p_team = clean_team_name(p.get('team', ''))
        matched = (p_team == team_name)
        if not matched and p.get('career_history'):
            h = p.get('career_history')
            if isinstance(h, list) and len(h) > 0:
                last_item = h[-1]
                last_team = clean_team_name(last_item.get('team', '')) if isinstance(last_item, dict) else clean_team_name(str(last_item))
                if last_team == team_name: matched = True
                
        if matched:
            team_players.append(p)
            
    team_players.sort(key=lambda x: get_pos_rank(x.get('position', '')))
    
    # Roster MD
    roster_md = "## 選手名簿 (Roster)\n\n"
    if team_players:
        roster_md += "| 選手名 | ポジション | 年齢 | 出身高校 | 大学/出身校 | 代表暦 |\n"
        roster_md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for p in team_players:
            p_name = p.get('name_ja', '不明')
            p_en = p.get('name_en', 'Unknown')
            p_id = p.get('id', '')
            p_slug = f"{slugify(p_en)}_{p_id}"
            p_pos = p.get('position', '-')
            p_age = calculate_age(p.get('birthdate'))
            
            p_hs = get_canonical_school_name(p.get('high_school')) or p.get('high_school') or '-'
            p_univ = get_canonical_school_name(p.get('university')) or p.get('university') or '-'
            p_caps = p.get('representative_caps') or '-'
            
            # Simple link to player page
            p_name_disp = f"[{p_name} ({p_en})](../../../player/{p_slug}.html)" if get_player_score(p) >= 2 else p_name
            roster_md += f"| {p_name_disp} | {p_pos} | {p_age}歳 | {p_hs} | {p_univ} | {p_caps} |\n"
    else:
        roster_md += "所属選手のデータが準備中です。\n"

    # Frontmatter
    frontmatter = {
        'title': team_name,
        'layout': 'team',
        'slug': slug,
        'league': league_slug,
        'division': team_data.get('division', '-'),
        'official_site': team_data.get('official_site', '-'),
        'host_area': team_data.get('host_area', '-'),
        'practice_ground': team_data.get('practice_ground', '-')
    }
    
    md_content = f"---\n{json.dumps(frontmatter, ensure_ascii=False, indent=2)}\n---\n\n"
    md_content += f"# {team_name}\n\n"
    md_content += f"**リーグ**: {league_slug.upper()} / {team_data.get('division', '-')}\n\n"
    md_content += roster_md

    output_path = os.path.join(team_dir, 'index.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

if __name__ == "__main__":
    print(f"Generating {len(league_one_teams)} League One team MDs...")
    for team in league_one_teams:
        team['league_slug'] = 'leagueone'
        generate_team_md(team)
    print("✓ Team MDs Complete!")
