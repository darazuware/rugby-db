import json
import os
import re
from player_utils import (
    slugify, clean_team_name, load_unified_players, 
    get_player_score, get_team_slug, get_league_slug_for_team,
    calculate_age, get_canonical_school_name, get_pos_rank
)

# normalize_position function is in generate_player_pages, we'll keep the import or copy if needed.
# For now, let's copy a simple version or keep it.
def normalize_position(pos):
    if not pos: return '-'
    pos = str(pos).strip().upper()
    if pos in ['PR', 'HO', 'LO', 'FL', 'NO8', 'No8']: return pos
    if pos in ['SH', 'SO', 'CTB', 'WTB', 'FB']: return pos
    return pos



# Load de-duplicated data via utility
print("Loading data via player_utils...")
players = load_unified_players()

with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
    league_one_teams = json.load(f)

COMMON_CSS = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Noto Sans JP', sans-serif; background-color: #f5f7f9; color: #484848; line-height: 1.6; }
        .header-container { background-color: #0097B2; padding: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; text-align: center; }
        .site-title { color: white; text-decoration: none; font-size: 24px; font-weight: 700; }
        .nav-container { background-color: #007A8F; padding: 10px 0; position: sticky; top: 0; z-index: 100; }
        .nav-menu { display: flex; justify-content: center; list-style: none; gap: 30px; }
        .nav-menu a { color: white; text-decoration: none; font-weight: 700; font-size: 15px; }
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
    </style>
"""

with open('data/rugby_leagues.json', 'r', encoding='utf-8') as f:
    leagues = json.load(f)

with open('data/league_colors.json', 'r', encoding='utf-8') as f:
    league_colors = json.load(f)

# Create output base directory
TEAMS_OUT_BASE = 'dist/teams'
os.makedirs(TEAMS_OUT_BASE, exist_ok=True)

def generate_team_page(team):
    """Generate HTML page for a single team"""
    
    team_name = team['team_name']
    slug = get_team_slug(team_name)
    
    # Determine League and path
    # Default to leagueone if not specified
    league_slug = team.get('league_slug', 'leagueone')
    
    # ROOT: ../../../
    # dist/teams/leagueone/team-slug/index.html
    relative_root = "../../../" 
    logo_img = f'<img src="{relative_root}images/logo.png" alt="RugbyPick" style="height:40px; vertical-align:middle;">'
    division = team.get('division', '不明')
    
    # Create directory: dist/teams/leagueone/team/
    team_dir = os.path.join(TEAMS_OUT_BASE, league_slug, slug)
    os.makedirs(team_dir, exist_ok=True)
    
    # Get league info
    league_name = "League One" if league_slug == 'leagueone' else "Top 14"
    if "Top 14" in team.get('league_name', ''): league_name = "Top 14" # Double check
    
    l_color = league_colors.get(league_name, {}).get('primary', '#0097B2')
    
    # Find players belonging to this team
    team_players = []
    for p in players:
        # Match using common utility score
        if get_player_score(p) < 2: continue
        
        p_team = clean_team_name(p.get('team', ''))
        matched = (p_team == team_name)
        if not matched and p.get('career_history'):
             h = p.get('career_history')
             if isinstance(h, list) and len(h) > 0:
                  last_item = h[-1]
                  if isinstance(last_item, dict):
                      last_team = clean_team_name(last_item.get('team', ''))
                  else:
                      # If it's a string like "Team (Year)"
                      last_team = clean_team_name(str(last_item))
                  if last_team == team_name: matched = True
             elif isinstance(h, str) and team_name in h:
                  # Simple fallback for string career history
                  if h.strip().split('->')[-1].strip().startswith(team_name):
                      matched = True

        if matched:
            team_players.append(p)
    
    # Sort players by position
    position_order = {
        'PR': 1, 'HO': 2, 'LO': 3, 'FL': 4, 'No.8': 5, 
        'SH': 6, 'SO': 7, 'CTB': 8, 'WTB': 9, 'FB': 10
    }
    
    team_players.sort(key=lambda x: get_pos_rank(x.get('position')))

    # Group players by position groups for the roster table
    roster_html = ""
    if team_players:
        roster_html = """
        <table class="roster-table" id="rosterTable">
            <thead>
                <tr>
                    <th data-sort="string">選手名</th>
                    <th data-sort="pos-rank">ポジション</th>
                    <th data-sort="number">年齢</th>
                    <th data-sort="string">出身高校</th>
                    <th data-sort="string">出身校</th>
                    <th data-sort="string">代表歴</th>
                </tr>
            </thead>
            <tbody>
        """
        for p in team_players:
            p_name = p.get('name_ja', '不明')
            p_en = p.get('name_en', 'Unknown')
            p_id = p.get('id', '')
            p_slug = f"{slugify(p_en)}_{p_id}"
            p_pos = p.get('position', '-')
            p_age = calculate_age(p.get('birthdate'))
            
            # School Info
            univ_raw = p.get('university')
            hs_raw = p.get('high_school')
            
            univ_name = get_canonical_school_name(univ_raw) or univ_raw or '-'
            hs_name = get_canonical_school_name(hs_raw) or hs_raw or '-'
            
            p_univ = '-' if str(univ_name).lower() == 'nan' else univ_name
            p_hs = '-' if str(hs_name).lower() == 'nan' else hs_name
            
            p_caps_val = p.get('representative_caps') or '-'
            p_caps = '-' if str(p_caps_val).lower() == 'nan' else p_caps_val
            
            # Match common threshold >= 2
            p_name_disp = f"{p_name} ({p_en})" if p_en and p_en != 'Unknown' else p_name
            p_link = f'<a href="{relative_root}player/{p_slug}.html">{p_name_disp}</a>' if get_player_score(p) >= 2 else p_name_disp
            
            p_pos_norm = normalize_position(p_pos)
            # Smarter check to avoid No.8No8
            clean_p_pos = str(p_pos).replace('.', '').replace(' ', '').upper()
            clean_norm = str(p_pos_norm).replace('.', '').replace(' ', '').upper()
            if p_pos_norm == '-' or clean_norm in clean_p_pos:
                p_pos_disp = p_pos
            else:
                p_pos_disp = f"{p_pos}{p_pos_norm}"
            p_pos_rank = get_pos_rank(p_pos)

            # LINK UPDATE: Permanent Flat Path
            roster_html += f"""
                <tr>
                    <td data-sort-value="{p_en}">{p_link}</td>
                    <td data-sort-value="{p_pos_rank}" data-rank="{p_pos_rank}"><span class="pos-tag">{p_pos_disp}</span></td>
                    <td data-sort-value="{p_age}">{p_age}歳</td>
                    <td data-sort-value="{p_hs}">{p_hs}</td>
                    <td data-sort-value="{p_univ}">{p_univ}</td>
                    <td>{p_caps}</td>
                </tr>
            """
        roster_html += "</tbody></table>"
    else:
        roster_html = "<p>所属選手のデータがありません。</p>"

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{team_name} | RugbyPick</title>
    <link rel="canonical" href="https://rugbypick.com/teams/{league_slug}/{slug}/">
    {COMMON_CSS}
    <style>
        .team-header {{
            background: linear-gradient(135deg, {l_color} 0%, #333 100%);
            color: #ffffff;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .profile-card {{
            background: #ffffff;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .profile-label {{
            font-size: 13px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        .profile-value {{
            font-size: 18px;
            font-weight: 700;
            color: #333;
        }}
        .section-title {{
            font-size: 24px;
            font-weight: 700;
            color: #333;
            margin: 40px 0 20px;
            padding-left: 15px;
            border-left: 5px solid {l_color};
        }}
        .roster-table {{
            width: 100%;
            background: #ffffff;
            border-collapse: collapse;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .roster-table th {{
            background-color: #f8f9fa;
            text-align: left;
            padding: 15px;
            font-size: 14px;
            color: #888;
            border-bottom: 2px solid #eee;
        }}
        .roster-table td {{
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}
        .roster-table tr:hover {{
            background-color: #fdfdfd;
        }}
        .roster-table a {{
            color: #0097B2;
            text-decoration: none;
            font-weight: 700;
        }}
        .pos-tag {{
            display: inline-block;
            background-color: #e9ecef;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 700;
            color: #495057;
        }}
        .official-link {{
            color: {l_color};
            text-decoration: none;
            font-weight: 700;
        }}
        /* Sort Icons */
        th[data-sort]::after {{ content: " ↕"; opacity: 0.3; font-size: 0.8em; }}
        th.sort-asc::after {{ content: " ↑"; opacity: 1; color: #0097B2; }}
        th.sort-desc::after {{ content: " ↓"; opacity: 1; color: #0097B2; }}
    </style>
    <script src="{relative_root}js/table-sorter.js" defer></script>
</head>
<body>
    <header class="header-container">
        <div class="header-content">
            <a href="{relative_root}index.html" class="site-title">{logo_img}</a>
        </div>
    </header>
    <nav class="nav-container">
        <ul class="nav-menu">
            <li><a href="{relative_root}index.html">ホーム</a></li>
            <li><a href="{relative_root}pages/leagues.html">リーグ一覧</a></li>
            <li><a href="{relative_root}pages/teams.html">チーム一覧</a></li>
            <li><a href="{relative_root}pages/players.html">選手一覧</a></li>
        </ul>
    </nav>

    <div class="container">
        <div class="team-header">
            <div class="division-tag">{division}</div>
            <div class="team-name">{team_name}</div>
        </div>

        <div class="profile-grid">
            <div class="profile-card">
                <div class="profile-label">運営母体 / 法人名</div>
                <div class="profile-value">{team.get('legal_entity', '-') or '-'}</div>
            </div>
            <div class="profile-card">
                <div class="profile-label">ホストエリア</div>
                <div class="profile-value">{team.get('host_area', '-') or '-'}</div>
            </div>
            <div class="profile-card">
                <div class="profile-label">練習グラウンド</div>
                <div class="profile-value">{team.get('practice_ground', '-') or '-'}</div>
            </div>
            <div class="profile-card">
                <div class="profile-label">公式サイト</div>
                <div class="profile-value">
                    <a href="{team.get('official_site', '#')}" class="official-link" target="_blank">
                        {team_name} 公式サイト ↗
                    </a>
                </div>
            </div>
        </div>

        <h2 class="section-title">選手名簿 (Roster)</h2>
        {roster_html}
    </div>
</body>
</html>"""
    
    # Final path: pages/category/domestic/leagueone/{div}/{team}/index.html
    filename = os.path.join(team_dir, 'index.html')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    return filename

# Generate all team pages
# 1. League One Teams (Detailed)
print(f"Generating {len(league_one_teams)} League One team pages...")
for team in league_one_teams:
    team['league_slug'] = 'leagueone'
    fname = generate_team_page(team)
    print(f"  ✓ {fname}")

# 2. Dynamic generation for all other leagues
print("Detecting teams for overseas leagues...")
league_to_teams = {}
for p in players:
    t_raw = p.get('team')
    if p.get('source') == 'all_rugby' and not t_raw:
        from generate_player_pages import consolidate_career_history
        career = consolidate_career_history(p.get('career_history'))
        if career:
            t_raw = career[-1].get('team')
            
    if get_player_score(p) < 2: continue
    
    # Collect all teams (current and history) for score >= 2 players
    teams_to_process = []
    t_name = clean_team_name(t_raw)
    if t_name and str(t_name).lower() != 'nan': 
        teams_to_process.append((t_name, p.get('team_en', '')))
    
    # Also collect from career history
    career = p.get('career_history', [])
    if isinstance(career, list):
        for c in career:
            if isinstance(c, dict):
                ct_name = clean_team_name(c.get('team'))
                if ct_name: teams_to_process.append((ct_name, ''))
            elif isinstance(c, str):
                ct_name = clean_team_name(c)
                if ct_name: teams_to_process.append((ct_name, ''))
    elif isinstance(career, str) and career != '-':
        # Handle string like "Team A (2020) -> Team B (2021)"
        parts = career.split(' -> ')
        for part in parts:
            # Simple clean (year-re-check similar to consolidate_career_history)
            ct_name = re.sub(r'\(\s*\d{4}.*?\)', '', part).strip()
            if ct_name: teams_to_process.append((ct_name, ''))
    
    for tn, te in teams_to_process:
        l_s = get_league_slug_for_team(tn, te)
        if not l_s:
            l_name_raw = p.get('league') or p.get('source', '')
            l_s = slugify(l_name_raw)
        
        if l_s and tn:
            if l_s not in league_to_teams:
                league_to_teams[l_s] = set()
            league_to_teams[l_s].add(tn)

for l in leagues:
    l_name_ja = l['name_ja']
    l_name_en = l['name']
    l_slug = l['url'].split('/')[-1]
    
    if l_slug == 'leagueone': continue
    
    keys_to_try = [
        slugify(l_name_en), 
        slugify(l_name_ja), 
        slugify(l_slug),
        slugify(l_slug.replace('-', '_')),
        "top_14" if "top" in l_slug.lower() and "14" in l_slug else "",
        "urc" if "united" in l_slug.lower() else ""
    ]
    
    t_names = set()
    for k in keys_to_try:
        if k and k in league_to_teams:
            t_names.update(league_to_teams[k])
            
    if t_names:
        print(f"Generating {len(t_names)} team pages for {l_name_ja} ({l_slug})...")
        for t_name in t_names:
            t_data = {
                'team_name': t_name,
                'league_slug': l_slug,
                'league_name': l_name_ja,
                'division': l_name_ja
            }
            fname = generate_team_page(t_data)
            print(f"  ✓ {fname}")

print("\n✓ Done!")
