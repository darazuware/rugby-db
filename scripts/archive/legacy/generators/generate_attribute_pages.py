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

# slugify and clean_team_name imported from player_utils


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
ages = {}
heights = {}
weights = {}

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
        
    # Age
    age_val = p.get('age')
    if (not age_val or str(age_val) == 'nan') and bdate and bdate != 'nan':
        match = re.search(r'(\d{4})', str(bdate))
        if match:
            try:
                age_val = 2025 - int(match.group(1))
            except:
                pass
                
    if age_val and str(age_val) != 'nan' and str(age_val) != '不明':
        try:
            age_str = str(int(float(age_val)))
            if age_str not in ages: ages[age_str] = []
            ages[age_str].append(p)
        except:
            pass
        
    # Height
    h = p.get('height')
    if h and str(h) != 'nan':
        h_str = str(h).replace('cm', '').strip()
        if h_str not in heights: heights[h_str] = []
        heights[h_str].append(p)

    # Weight
    w = p.get('weight')
    if w and str(w) != 'nan':
        w_str = str(w).replace('kg', '').strip()
        if w_str not in weights: weights[w_str] = []
        weights[w_str].append(p)

def generate_advanced_index(title, item_list, filename_path):
    # Sort players by name
    sorted_players = sorted(item_list, key=lambda x: str(x.get('name_en', '')))
    
    player_cards = ""
    for p in sorted_players:
        p_name = p.get('name_ja') or p.get('name_en')
        p_en = p.get('name_en', '')
        p_slug = f"{slugify(p_en)}_{p.get('id')}"
        p_team = clean_team_name(p.get('team', '-'))
        p_pos = p.get('position', '-')
        
        # Rich Player Check via utility
        score = get_player_score(p)

        card_content = f"""
                <div class="player-pos">{p_pos}</div>
                <div class="player-info">
                    <div class="player-name">{p_name}</div>
                    <div class="player-team">{p_team}</div>
                </div>
        """
        
        if score >= 2:
            link_html = f'<a href="../player/{p_slug}.html" style="text-decoration:none; color:inherit; display:flex; align-items:center; gap:15px; width:100%;">{card_content}</a>'
        else:
            link_html = f'<div style="display:flex; align-items:center; gap:15px; width:100%;">{card_content}</div>'

        player_cards += f"""
        <div class="player-card {p['league_key']}-player" data-league="{p['league_key']}" data-div="{p['div_key']}" data-team="{p['team_slug']}">
            {link_html}
        </div>
        """

    def make_team_filters(team_slugs):
        filters = ""
        for ts in sorted(team_slugs):
            if ts not in TEAM_INFO: continue
            t_info = TEAM_INFO[ts]
            filters += f'<div class="team-filter" data-team="{ts}" data-div="{t_info["div"]}" onclick="toggleTeam(\'{ts}\')">{t_info["name"]}</div>'
        return filters

    logo_img = f'<img src="../images/logo.png" alt="RugbyPick" style="height:40px; vertical-align:middle;">'

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | RugbyPick Filter</title>
    <link rel="canonical" href="https://rugbypick.com/pages/{os.path.basename(filename_path)}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Noto Sans JP', sans-serif; background-color: #f5f7f9; color: #484848; line-height: 1.6; padding-bottom: 40px; }}
        .header-container {{ background-color: #0097B2; padding: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header-content {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; text-align: center; }}
        .site-title {{ color: white; text-decoration: none; font-size: 24px; font-weight: 700; }}
        .nav-container {{ background-color: #007A8F; padding: 10px 0; position: sticky; top: 0; z-index: 100; }}
        .nav-menu {{ display: flex; justify-content: center; list-style: none; gap: 30px; }}
        .nav-menu a {{ color: white; text-decoration: none; font-weight: 700; font-size: 15px; }}
        .container {{ max-width: 1200px; margin: 40px auto; padding: 0 20px; }}
        .filter-section {{ background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .filter-group {{ margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 15px; }}
        .filter-group:last-child {{ border-bottom: none; }}
        .filter-label {{ font-size: 14px; font-weight: 700; color: #666; margin-bottom: 10px; }}
        .filter-tabs {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .filter-tab {{ padding: 6px 15px; background: #f0f2f5; border-radius: 20px; cursor: pointer; font-size: 14px; transition: all 0.2s; }}
        .filter-tab.active {{ background: #0097B2; color: white; }}
        
        .team-filters {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; }}
        .team-filter {{ padding: 6px 10px; background: #f0f2f5; border-radius: 4px; cursor: pointer; font-size: 12px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .team-filter.active {{ background: #0097B2; color: white; }}
        
        .players-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }}
        .player-card {{ background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #efefef; transition: all 0.2s; }}
        .player-card:hover {{ transform: translateY(-2px); border-color: #0097B2; box-shadow: 0 5px 12px rgba(0,0,0,0.1); }}
        .player-pos {{ background: #f0f4f8; color: #0097B2; font-weight: 700; padding: 8px 12px; border-radius: 6px; font-size: 14px; min-width: 50px; text-align: center; }}
        .player-name {{ font-weight: 700; font-size: 16px; color: #333; }}
        .player-team {{ font-size: 13px; color: #888; }}
        
        .section-header {{ margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; }}
        .section-title {{ font-size: 24px; font-weight: 700; }}
        .player-count {{ color: #999; font-size: 16px; }}
    </style>
</head>
<body>
    <header class="header-container">
        <div class="header-content">
            <a href="../index.html" class="site-title">{logo_img}</a>
        </div>
    </header>
    <nav class="nav-container">
        <ul class="nav-menu">
            <li><a href="../index.html">ホーム</a></li>
            <li><a href="../pages/leagues.html">リーグ一覧</a></li>
            <li><a href="../pages/teams.html">チーム一覧</a></li>
            <li><a href="../pages/players.html">選手一覧</a></li>
        </ul>
    </nav>

    <div class="container">
        <div class="section-header">
            <h1 class="section-title">{title}</h1>
            <span id="player-count" class="player-count">{len(sorted_players)}名</span>
        </div>

        <div class="filter-section">
            <div class="filter-group">
                <div class="filter-label">1. リーグを選択</div>
                <div class="filter-tabs">
                    <div class="filter-tab active" data-league="all" onclick="switchLeague('all')">全リーグ</div>
                    <div class="filter-tab" data-league="l1" onclick="switchLeague('l1')">League One</div>
                    <div class="filter-tab" data-league="t14" onclick="switchLeague('t14')">Top 14</div>
                </div>
            </div>

            <div id="div-group" class="filter-group" style="display:none;">
                <div class="filter-label">2. ディビジョンを選択</div>
                <div class="filter-tabs">
                    <div class="filter-tab active" data-div="all" onclick="filterDiv('all')">全ディビジョン</div>
                    <div class="filter-tab" data-div="leagueone-div1" onclick="filterDiv('leagueone-div1')">Division 1</div>
                    <div class="filter-tab" data-div="leagueone-div2" onclick="filterDiv('leagueone-div2')">Division 2</div>
                    <div class="filter-tab" data-div="leagueone-div3" onclick="filterDiv('leagueone-div3')">Division 3</div>
                </div>
            </div>

            <div class="filter-group">
                <div class="filter-label">3. チームで絞り込む (複数選択可能)</div>
                <div id="team-filters-container" class="team-filters">
                    <div class="team-filter active" id="all-teams-btn" onclick="resetTeams()">全チーム</div>
                    {make_team_filters(sum(L1_TEAMS.values(), []) + T14_TEAMS)}
                </div>
            </div>
        </div>

        <div class="players-grid" id="players-grid">
            {player_cards}
        </div>
    </div>

    <script>
        let currentLeague = 'all';
        let currentDiv = 'all';
        let selectedTeams = new Set();

        function switchLeague(league) {{
            currentLeague = league;
            currentDiv = 'all';
            selectedTeams.clear();
            
            document.querySelectorAll('.filter-group:nth-child(1) .filter-tab').forEach(t => t.classList.toggle('active', t.getAttribute('data-league') === league));
            document.getElementById('div-group').style.display = (league === 'l1') ? 'block' : 'none';
            
            // Reset Div tabs
            document.querySelectorAll('#div-group .filter-tab').forEach(t => t.classList.toggle('active', t.getAttribute('data-div') === 'all'));
            
            updateTeamFilterVisibility();
            applyFilters();
        }}

        function filterDiv(div) {{
            currentDiv = div;
            selectedTeams.clear();
            document.querySelectorAll('#div-group .filter-tab').forEach(t => t.classList.toggle('active', t.getAttribute('data-div') === div));
            
            updateTeamFilterVisibility();
            applyFilters();
        }}

        function toggleTeam(teamSlug) {{
            if (selectedTeams.has(teamSlug)) {{
                selectedTeams.delete(teamSlug);
            }} else {{
                selectedTeams.add(teamSlug);
            }}
            
            document.getElementById('all-teams-btn').classList.toggle('active', selectedTeams.size === 0);
            document.querySelectorAll('.team-filter').forEach(t => {{
                const slug = t.getAttribute('data-team');
                if (slug) {{
                    t.classList.toggle('active', selectedTeams.has(slug));
                }}
            }});
            
            applyFilters();
        }}

        function resetTeams() {{
            selectedTeams.clear();
            document.getElementById('all-teams-btn').classList.add('active');
            document.querySelectorAll('.team-filter').forEach(t => {{
                if (t.getAttribute('data-team')) t.classList.remove('active');
            }});
            applyFilters();
        }}

        function updateTeamFilterVisibility() {{
            document.querySelectorAll('.team-filter').forEach(t => {{
                if (t.id === 'all-teams-btn') return;
                
                const tDiv = t.getAttribute('data-div');
                const tTeam = t.getAttribute('data-team');
                // Finding league from TEAM_INFO would be better but we can infer from div
                const isL1 = tDiv.startsWith('leagueone');
                const isT14 = tDiv === 'top-14';
                
                let visible = false;
                if (currentLeague === 'all') {{
                    visible = true;
                }} else if (currentLeague === 'l1' && isL1) {{
                    if (currentDiv === 'all' || tDiv === currentDiv) visible = true;
                }} else if (currentLeague === 't14' && isT14) {{
                    visible = true;
                }}
                
                t.style.display = visible ? 'block' : 'none';
            }});
            resetTeams();
        }}

        function applyFilters() {{
            const cards = document.querySelectorAll('.player-card');
            let visibleCount = 0;
            
            cards.forEach(card => {{
                const cLeague = card.getAttribute('data-league');
                const cDiv = card.getAttribute('data-div');
                const cTeam = card.getAttribute('data-team');
                
                let show = true;
                if (currentLeague !== 'all' && cLeague !== currentLeague) show = false;
                if (currentLeague === 'l1' && currentDiv !== 'all' && cDiv !== currentDiv) show = false;
                if (selectedTeams.size > 0 && !selectedTeams.has(cTeam)) show = false;
                
                card.style.display = show ? 'block' : 'none';
                if (show) visibleCount++;
            }});
            
            document.getElementById('player-count').textContent = visibleCount + '名';
        }}
        
        // Initial setup
        updateTeamFilterVisibility();
    </script>
</body>
</html>"""
    
    with open(filename_path, 'w', encoding='utf-8') as f:
        f.write(html)

print("Generating Year pages...")
for year, p_list in birth_years.items():
    generate_advanced_index(f"{year}年生まれ", p_list, f"dist/dates/{year}.html")

print("Generating Age pages...")
for age, p_list in ages.items():
    generate_advanced_index(f"{age}歳", p_list, f"dist/ages/{age}.html")

print("Generating Height pages...")
for h, p_list in heights.items():
    generate_advanced_index(f"{h}cm", p_list, f"dist/heights/{h}.html")

print("Generating Weight pages...")
for w, p_list in weights.items():
    generate_advanced_index(f"{w}kg", p_list, f"dist/weights/{w}.html")

print("✓ Attribute pages generated!")
