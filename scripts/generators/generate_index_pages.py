import json
import os
import re
from player_utils import slugify, clean_team_name, load_unified_players, get_player_score, get_team_slug, get_league_slug_for_team, calculate_age, get_pos_rank

# Load data via common utility
print("Loading data via player_utils...")
players = load_unified_players()



# Load metadata
with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
    teams_detailed = json.load(f)
with open('data/rugby_leagues.json', 'r', encoding='utf-8') as f:
    leagues = json.load(f)
with open('data/league_colors.json', 'r', encoding='utf-8') as f:
    league_colors = json.load(f)

# --- Bilingual Team Mapping ---
try:
    with open('data/top14_teams.json', 'r', encoding='utf-8') as f:
        TOP14_DATA = json.load(f)
    TEAM_EN_MAP = {t['name_ja']: t['name'] for t in TOP14_DATA}
except:
    TEAM_EN_MAP = {}

def get_team_en_name(ja_name, current_raw=''):
    if current_raw and re.search(r'[a-zA-Z]', str(current_raw)):
        clean_raw = re.sub(r'[（(]\s*\d{4}.*?[）)]', '', str(current_raw)).strip()
        if re.search(r'[a-zA-Z]', clean_raw):
            return clean_raw
    return TEAM_EN_MAP.get(ja_name, '')

# Players already loaded from player_utils

# Path settings: Moving Indices to dist/pages/
OUTPUT_DIR = 'dist/pages'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Navigation Template (Now from dist/pages/ depth)
def get_nav():
    root_prefix = "../" # Home (index.html) is at dist/
    prefix = "./"       # Indices are at dist/pages/
    logo_path = "../images/logo.png"

    logo_img = f'<img src="{logo_path}" alt="RugbyPick" style="height:40px; vertical-align:middle;">'

    return f"""
    <header class="header-container">
        <div class="header-content">
            <a href="{root_prefix}index.html" class="site-title">{logo_img}</a>
        </div>
    </header>
    <nav class="nav-container">
        <ul class="nav-menu">
            <li><a href="{root_prefix}index.html">ホーム</a></li>
            <li><a href="{prefix}leagues.html">リーグ一覧</a></li>
            <li><a href="{prefix}teams.html">チーム一覧</a></li>
            <li><a href="{prefix}players.html">選手一覧</a></li>
        </ul>
    </nav>
    """

# Common CSS
COMMON_CSS = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Noto Sans JP', sans-serif; background-color: #f5f7f9; color: #484848; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .header-container { background-color: #0097B2; padding: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; text-align: center; }
        .site-title { color: white; text-decoration: none; font-size: 24px; font-weight: 700; }
        .nav-container { background-color: #007A8F; padding: 10px 0; position: sticky; top: 0; z-index: 100; }
        .nav-menu { display: flex; justify-content: center; list-style: none; gap: 30px; }
        .nav-menu a { color: white; text-decoration: none; font-weight: 700; font-size: 15px; }
        .section-title { font-size: 28px; color: #333; margin-bottom: 20px; font-weight: 700; }
        .card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
        .item-card { background: white; border-radius: 12px; padding: 25px; text-decoration: none; color: inherit; box-shadow: 0 4px 15px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s; display: block; }
        .item-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
        .item-name { font-size: 18px; font-weight: 700; margin-bottom: 8px; color: #0097B2; }
        .item-meta { font-size: 14px; color: #666; display: flex; align-items: center; gap: 10px; }
        .league-tag { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
        
        /* Filters */
        .filter-section { background: white; border-radius: 12px; padding: 20px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .filter-group { margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #eee; }
        .filter-group:last-child { border-bottom: none; }
        .filter-label { font-size: 14px; font-weight: 700; color: #666; margin-bottom: 10px; }
        .filter-tabs { display: flex; flex-wrap: wrap; gap: 8px; }
        .filter-tab { padding: 6px 15px; background: #f0f2f5; border-radius: 20px; cursor: pointer; font-size: 14px; transition: all 0.2s; white-space: nowrap; }
        .filter-tab.active { background: #0097B2; color: white; }

        /* Roster Table */
        .roster-table-container { background: white; border-radius: 12px; overflow-x: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        .roster-table { width: 100%; border-collapse: collapse; font-size: 14px; min-width: 800px; }
        .roster-table th { background: #f8f9fa; padding: 12px 15px; text-align: left; font-weight: 700; color: #666; border-bottom: 2px solid #eee; cursor: pointer; position: relative; }
        .roster-table th:hover { background: #edf2f7; }
        .roster-table th::after { content: '↕'; position: absolute; right: 5px; opacity: 0.3; }
        .roster-table td { padding: 12px 15px; border-bottom: 1px solid #efefef; vertical-align: middle; }
        .roster-table tr:hover { background: #fcfdfe; }
        .pos-tag { display: inline-block; padding: 2px 6px; border-radius: 4px; background: #e2e8f0; color: #4a5568; font-size: 11px; font-weight: 700; min-width: 35px; text-align: center; }
        .player-link { color: #0097B2; text-decoration: none; font-weight: 700; }
        .player-link:hover { text-decoration: underline; }

        .search-box { width: 100%; padding: 12px 20px; border: 2px solid #eee; border-radius: 30px; font-size: 16px; outline: none; transition: border-color 0.2s; margin-bottom: 15px; }
        .search-box:focus { border-color: #0097B2; }
    </style>
"""

# 1. leagues.html
def generate_leagues_index():
    domestic_cards = ""
    overseas_cards = ""
    
    for l in leagues:
        name = l['name']
        slug = slugify(name)
        color = league_colors.get(name, {}).get('primary', '#0097B2')
        country = l.get('country', '')
        
        # New Master Structure: /leagues/{slug}/index.html
        if "League One" in name:
            if "Division 1" in name: link = "../leagues/leagueone/div1/index.html"
            elif "Division 2" in name: link = "../leagues/leagueone/div2/index.html"
            elif "Division 3" in name: link = "../leagues/leagueone/div3/index.html"
            else: link = "../leagues/leagueone/index.html"
        elif "top 14" in name.lower():
            link = "../leagues/top-14/index.html"
        else:
            link = f"../leagues/{slug}/index.html"
            
        card_html = f"""
        <a href="{link}" class="item-card" style="border-top: 5px solid {color}">
            <div class="item-name">{l['name_ja']} <span style="font-size: 0.85em; opacity: 0.7;">({l['name']})</span></div>
            <div class="item-meta">{country}</div>
        </a>
        """
        
        if country == "日本": domestic_cards += card_html
        else: overseas_cards += card_html
    
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>リーグ一覧 | RugbyPick</title>
    <link rel="canonical" href="https://rugbypick.com/pages/leagues.html">
    {COMMON_CSS}
</head>
<body>
    {get_nav()}
    <div class="container">
        <h1 class="section-title" style="margin-bottom:30px;">国内リーグ</h1>
        <div class="card-grid" style="margin-bottom: 50px;">
            {domestic_cards}
        </div>
        <h1 class="section-title" style="margin-bottom:30px;">海外リーグ</h1>
        <div class="card-grid">
            {overseas_cards}
        </div>
    </div>
</body>
</html>"""
    with open(f'{OUTPUT_DIR}/leagues.html', 'w', encoding='utf-8') as f:
        f.write(html)

# 2. teams.html (ADVANCED FILTERING)

from generate_player_pages import consolidate_career_history, normalize_position

# Determine all teams and their leagues
league_dict = {slugify(l['name']): l for l in leagues}
for l in leagues:
    league_dict[l['url'].split('/')[-1]] = l
    league_dict[l['name_ja']] = l

# Overseas team to league_slug mapping

# Find which team belongs to which league and division
GLOBAL_TEAM_DATA = {}
for t in teams_detailed:
    t_name = clean_team_name(t['team_name'])
    t_slug = get_team_slug(t_name)
    div_raw = t.get('division', 'Division 1')
    div = f"div{div_raw[-1]}"
    GLOBAL_TEAM_DATA[t_slug] = {"name": t_name, "en_name": get_team_en_name(t_name), "div": div, "league": "leagueone", "league_ja": "League One", "area": t.get('host_area', '')}

for p in players:
    t_raw = p.get('team')
    if p.get('source') == 'all_rugby' and not t_raw:
        career = consolidate_career_history(p.get('career_history'))
        if career:
            t_raw = career[-1].get('team')
            
    t_name = clean_team_name(t_raw)
    if not t_name: continue
    t_slug = get_team_slug(t_name)
    
    if t_slug not in GLOBAL_TEAM_DATA:
        en_name = get_team_en_name(t_name)
        if not en_name:
             en_name = p.get('team_en', '')
             
        l_slug = 'unknown'
        l_ja = '不明'
        
        l_name_raw = p.get('league') or p.get('source', '')
        l_slug = get_league_slug_for_team(t_name, en_name)
        if not l_slug:
            l_slug = 'top-14' if 'top-14' in l_name_raw.lower() or 'top_14' in l_name_raw.lower() else 'unknown'
                     
        if l_slug != 'unknown':
             # Find l_ja from league dict
             for l in leagues:
                 if l['url'].split('/')[-1] == l_slug:
                     l_ja = l['name_ja']
                     break
                     
             div_slug = "top-14" if l_slug == "top-14" else l_slug
             GLOBAL_TEAM_DATA[t_slug] = {"name": t_name, "en_name": en_name, "div": div_slug, "league": l_slug, "league_ja": l_ja, "area": ""}

def generate_teams_index():

    team_cards = ""
    league_tabs = '<div class="filter-tab active" data-league="all" onclick="switchLeague(\'all\')">全リーグ</div>'
    
    seen_leagues = set()
    
    # Priority sort
    def lprio(slug):
        if slug.startswith('japan'): return 0
        if slug == 'top-14': return 1
        return 2

    l_list = sorted(list(set(d['league'] for d in GLOBAL_TEAM_DATA.values() if d['league'] != 'unknown')), key=lambda x: (lprio(x), x))
    
    for l_slug in l_list:
        l_ja = next((d['league_ja'] for d in GLOBAL_TEAM_DATA.values() if d['league'] == l_slug), l_slug)
        league_tabs += f'<div class="filter-tab" data-league="{l_slug}" onclick="switchLeague(\'{l_slug}\')">{l_ja}</div>'
    
    for t_slug, data in GLOBAL_TEAM_DATA.items():
        if data['league'] == 'unknown': continue
        
        name = data['name']
        en_name = data['en_name']
        disp_name = name
        if en_name and en_name != name:
            disp_name += f' <span style="font-size: 0.8em; opacity: 0.7;">({en_name})</span>'
            
        link = f"../teams/{data['league']}/{t_slug}/index.html"
        
        div_disp = data.get('div', '').replace('leagueone-', '').replace('div', 'Division ')
        if not data['league'].startswith('japan'): div_disp = data['league_ja']
        
        lid = "leagueone" if data['league'] == 'leagueone' or data['league'].startswith('japan') else data['league']
        team_cards += f"""
        <a href="{link}" class="item-card team-card" data-league="{lid}" data-div="{data['div']}">
            <div class="item-meta">{div_disp}</div>
            <div class="item-name">{disp_name}</div>
            <div class="item-meta">{data.get('area', '')}</div>
        </a>
        """

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>チーム一覧 | RugbyPick</title>
    <link rel="canonical" href="https://rugbypick.com/pages/teams.html">
    {COMMON_CSS}
</head>
<body>
    {get_nav()}
    <div class="container">
        <div class="section-header">
            <h1 class="section-title">チーム一覧</h1>
        </div>

        <div class="filter-section">
            <div class="filter-group">
                <div class="filter-label">1. リーグを選択</div>
                <div class="filter-tabs">
                    {league_tabs.replace('japan-rugby-league-one-division-1', 'leagueone')}
                </div>
            </div>

            <div id="div-group" class="filter-group" style="display:none;">
                <div class="filter-label">2. ディビジョンを選択</div>
                <div class="filter-tabs">
                    <div class="filter-tab active" data-div="all" onclick="filterDiv('all')">全ディビジョン</div>
                    <div class="filter-tab" data-div="div1" onclick="filterDiv('div1')">Division 1</div>
                    <div class="filter-tab" data-div="div2" onclick="filterDiv('div2')">Division 2</div>
                    <div class="filter-tab" data-div="div3" onclick="filterDiv('div3')">Division 3</div>
                </div>
            </div>
        </div>

        <div class="card-grid" id="teams-grid">
            {team_cards}
        </div>
    </div>

    <script>
        let currentLeague = 'all';
        let currentDiv = 'all';

        function switchLeague(league) {{
            currentLeague = league;
            currentDiv = 'all';
            
            document.querySelectorAll('.filter-group:nth-child(1) .filter-tab').forEach(t => t.classList.toggle('active', t.getAttribute('data-league') === league));
            document.getElementById('div-group').style.display = (league === 'leagueone') ? 'block' : 'none';
            document.querySelectorAll('#div-group .filter-tab').forEach(t => t.classList.toggle('active', t.getAttribute('data-div') === 'all'));
            
            applyFilters();
        }}

        function filterDiv(div) {{
            currentDiv = div;
            document.querySelectorAll('#div-group .filter-tab').forEach(t => t.classList.toggle('active', t.getAttribute('data-div') === div));
            applyFilters();
        }}

        function applyFilters() {{
            const cards = document.querySelectorAll('.team-card');
            cards.forEach(card => {{
                const cLeague = card.getAttribute('data-league');
                const cDiv = card.getAttribute('data-div');
                
                let show = true;
                if (currentLeague !== 'all' && cLeague !== currentLeague) show = false;
                if (currentLeague === 'leagueone' && currentDiv !== 'all' && cDiv !== currentDiv) show = false;
                
                card.style.display = show ? 'block' : 'none';
            }});
        }}
    </script>
</body>
</html>"""
    with open(f'{OUTPUT_DIR}/teams.html', 'w', encoding='utf-8') as f:
        f.write(html)

# 3. players.html (ADVANCED FILTERING)
def generate_players_index():
    all_player_rows = []
    sorted_players = sorted(players, key=lambda x: str(x.get('name_en', '')))
    
    TEAM_SLUGS_BY_LEAGUE = {}
    for ts, td in GLOBAL_TEAM_DATA.items():
        if td['league'] == 'unknown': continue
        lid = "leagueone" if td['league'].startswith('japan') else td['league']
        if lid not in TEAM_SLUGS_BY_LEAGUE: TEAM_SLUGS_BY_LEAGUE[lid] = []
        TEAM_SLUGS_BY_LEAGUE[lid].append(ts)

    for p in sorted_players:
        # Rich Check via utility
        score = get_player_score(p)
        if score < 2: continue

        name_ja = p.get('name_ja')
        p_en = p.get('name_en', '')
        
        name_disp = name_ja if name_ja else p_en
        # Store birth year and age
        bdate = str(p.get('birthdate', '')).strip()
        birth_year = ""
        age = ""
        if bdate and bdate not in ['-', '不明', 'nan']:
            age = calculate_age(bdate)
            # Extract year from YYYY/MM/DD or similar
            match = re.search(r'(\d{4})', bdate)
            if match: birth_year = match.group(1)

        p_id = p.get('id', '')
        p_slug = f"{slugify(p_en)}_{p_id}"
        pos = normalize_position(p.get('position', '-'))
        pos_rank = get_pos_rank(pos)

        t_raw = p.get('team')
        if p.get('source') == 'all_rugby' and not t_raw:
            career = consolidate_career_history(p.get('career_history'))
            if career:
                t_raw = career[-1].get('team')
                
        team_clean = clean_team_name(t_raw)
        team_slug = get_team_slug(team_clean)
        
        if team_slug not in GLOBAL_TEAM_DATA or GLOBAL_TEAM_DATA[team_slug]['league'] == 'unknown':
            continue
            
        td = GLOBAL_TEAM_DATA[team_slug]
        
        link = f"../player/{p_slug}.html"
        
        # Bilingual team name for player list
        team_disp = team_clean
        if td['en_name'] and td['en_name'] != team_clean:
             team_disp += f' ({td["en_name"]})'
             
        lid = "leagueone" if td['league'].startswith('japan') else td['league']
        
        hs = p.get('high_school', '-')
        if not hs or str(hs).lower() == 'nan': hs = '-'
        univ = p.get('university', '-')
        if not univ or str(univ).lower() == 'nan': univ = '-'

        row = f"""
        <tr class="player-row" data-name="{name_disp} {p_en}" data-league="{lid}" data-div="{td["div"]}" data-team="{team_slug}" data-pos="{pos}" data-year="{birth_year}">
            <td><a href="{link}" class="player-link">{name_disp}</a><br><small style="color:#999">{p_en}</small></td>
            <td data-sort="{birth_year or '9999'}">{birth_year or '-'} ({age or '-'})</td>
            <td data-sort="{pos_rank}"><span class="pos-tag">{pos}</span></td>
            <td>{team_disp}</td>
            <td>{univ}</td>
            <td>{hs}</td>
        </tr>"""
        all_player_rows.append(row)

    all_rows = "".join(all_player_rows)
    
    def make_team_filters():
        filters = ""
        for l_slug, ts_list in TEAM_SLUGS_BY_LEAGUE.items():
            for ts in sorted(ts_list):
                td = GLOBAL_TEAM_DATA[ts]
                filters += f'<div class="team-filter" data-team="{ts}" data-div="{td["div"]}" data-league="{l_slug}" onclick="toggleTeam(\u0027{ts}\u0027)">{td["name"]}</div>'
        return filters

    def lprio(slug):
        if slug == 'leagueone': return 0
        if slug == 'top-14': return 1
        return 2

    l_list = sorted(list(TEAM_SLUGS_BY_LEAGUE.keys()), key=lambda x: (lprio(x), x))
    league_tabs = '<div class="filter-tab active" data-league="all" onclick="switchLeague(\'all\')">全リーグ</div>'
    for l_slug in l_list:
        if l_slug == 'leagueone':
             l_ja = "League One"
        else:
             l_ja = next((d['league_ja'] for d in GLOBAL_TEAM_DATA.values() if d['league'] == l_slug), l_slug)
        league_tabs += f'<div class="filter-tab" data-league="{l_slug}" onclick="switchLeague(\'{l_slug}\')">{l_ja}</div>'

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>選手一覧 | RugbyPick</title>
    <link rel="canonical" href="https://rugbypick.com/pages/players.html">
    {COMMON_CSS}
    <style>
        .filter-section {{ background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .team-filters {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; }}
        .team-filter {{ padding: 6px 10px; background: #f0f2f5; border-radius: 4px; cursor: pointer; font-size: 12px; text-align: center; }}
        .team-filter.active {{ background: #0097B2; color: white; }}
        #player-count {{ font-size:16px; color:#999; }}
    </style>
</head>
<body>
    {get_nav()}
    <div class="container">
        <div class="section-header">
            <h1 class="section-title">選手一覧</h1>
            <span id="player-count"></span>
        </div>
        
        <div class="filter-section">
            <div class="filter-group">
                <div class="filter-label">🔍 選手名・生年で絞り込む</div>
                <input type="text" id="name-search" class="search-box" placeholder="選手名または生年(例: 1998)を入力..." oninput="applyFilters()">
            </div>

            <div class="filter-group">
                <div class="filter-label">1. リーグを選択</div>
                <div class="filter-tabs">
                    {league_tabs}
                </div>
            </div>
            <div id="div-group" class="filter-group" style="display:none;">
                <div class="filter-label">2. ディビジョンを選択</div>
                <div class="filter-tabs">
                    <div class="filter-tab active" data-div="all" onclick="filterDiv('all')">全ディビジョン</div>
                    <div class="filter-tab" data-div="div1" onclick="filterDiv('div1')">Division 1</div>
                    <div class="filter-tab" data-div="div2" onclick="filterDiv('div2')">Division 2</div>
                    <div class="filter-tab" data-div="div3" onclick="filterDiv('div3')">Division 3</div>
                </div>
            </div>
            <div class="filter-group">
                <div class="filter-label">3. チームで絞り込む (複数選択可)</div>
                <div class="team-filters">
                    <div class="team-filter active" id="all-teams-btn" onclick="resetTeams()">全チーム</div>
                    {make_team_filters()}
                </div>
            </div>
            <div class="filter-group">
                <div class="filter-label">4. ポジションで絞り込む</div>
                <div class="filter-tabs">
                    <div class="filter-tab active" data-pos="all" onclick="filterPos('all')">全ポジション</div>
                    <div class="filter-tab" data-pos="FW" onclick="filterPos('FW')">FW全般</div>
                    <div class="filter-tab" data-pos="BK" onclick="filterPos('BK')">BK全般</div>
                    <div class="filter-tab" data-pos="PR" onclick="filterPos('PR')">PR</div>
                    <div class="filter-tab" data-pos="HO" onclick="filterPos('HO')">HO</div>
                    <div class="filter-tab" data-pos="LO" onclick="filterPos('LO')">LO</div>
                    <div class="filter-tab" data-pos="FL" onclick="filterPos('FL')">FL</div>
                    <div class="filter-tab" data-pos="No8" onclick="filterPos('No8')">No8</div>
                    <div class="filter-tab" data-pos="SH" onclick="filterPos('SH')">SH</div>
                    <div class="filter-tab" data-pos="SO" onclick="filterPos('SO')">SO</div>
                    <div class="filter-tab" data-pos="CTB" onclick="filterPos('CTB')">CTB</div>
                    <div class="filter-tab" data-pos="WTB" onclick="filterPos('WTB')">WTB</div>
                    <div class="filter-tab" data-pos="FB" onclick="filterPos('FB')">FB</div>
                </div>
            </div>
        </div>

        <div class="roster-table-container">
            <table class="roster-table" id="player-table">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)">選手名</th>
                        <th onclick="sortTable(1)">生年 (年齢)</th>
                        <th onclick="sortTable(2)">Pos</th>
                        <th onclick="sortTable(3)">所属チーム</th>
                        <th onclick="sortTable(4)">出身大学</th>
                        <th onclick="sortTable(5)">出身高校</th>
                    </tr>
                </thead>
                <tbody id="players-body">
                    {all_rows}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        let currentLeague = 'all';
        let currentDiv = 'all';
        let currentPos = 'all';
        let selectedTeams = new Set();
        
        window.addEventListener('DOMContentLoaded', () => {{
            const params = new URLSearchParams(window.location.search);
            const p = params.get('pos');
            if (p) {{
                filterPos(p);
            }}
        }});

        function switchLeague(league) {{
            currentLeague = league;
            currentDiv = 'all';
            selectedTeams.clear();
            document.querySelectorAll('.filter-group:nth-child(1) .filter-tab').forEach(t => t.classList.toggle('active', t.getAttribute('data-league') === league));
            document.getElementById('div-group').style.display = (league === 'leagueone') ? 'block' : 'none';
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

        function toggleTeam(slug) {{
            if (selectedTeams.has(slug)) selectedTeams.delete(slug);
            else selectedTeams.add(slug);
            document.getElementById('all-teams-btn').classList.toggle('active', selectedTeams.size === 0);
            updateTeamSelectionUI();
            applyFilters();
        }}

        function resetTeams() {{
            selectedTeams.clear();
            document.getElementById('all-teams-btn').classList.add('active');
            updateTeamSelectionUI();
            applyFilters();
        }}

        function updateTeamSelectionUI() {{
            document.querySelectorAll('.team-filter').forEach(t => {{
                const s = t.getAttribute('data-team');
                if (s) t.classList.toggle('active', selectedTeams.has(s));
            }});
        }}

        function updateTeamFilterVisibility() {{
            document.querySelectorAll('.team-filter').forEach(t => {{
                if (t.id === 'all-teams-btn') return;
                const td = t.getAttribute('data-div');
                const tl = t.getAttribute('data-league');
                let vis = false;
                if (currentLeague === 'all') vis = true;
                else if (currentLeague === tl) {{
                    if (currentLeague !== 'leagueone') vis = true;
                    else if (currentDiv === 'all' || td === currentDiv) vis = true;
                }}
                t.style.display = vis ? 'block' : 'none';
            }});
            resetTeams();
        }}

        function filterPos(pos) {{
            currentPos = pos;
            document.querySelectorAll('[data-pos].filter-tab').forEach(t => t.classList.toggle('active', t.getAttribute('data-pos') === pos));
            applyFilters();
        }}

        function applyFilters() {{
            const rows = document.querySelectorAll('.player-row');
            const searchText = document.getElementById('name-search').value.toLowerCase();
            let count = 0;
            
            rows.forEach(r => {{
                const cl = r.getAttribute('data-league');
                const cd = r.getAttribute('data-div');
                const ct = r.getAttribute('data-team');
                const cp = r.getAttribute('data-pos');
                const cy = r.getAttribute('data-year');
                const cn = r.getAttribute('data-name').toLowerCase();
                
                let show = true;
                
                // Search Text (Name or Year)
                if (searchText && !cn.includes(searchText) && !cy.includes(searchText)) show = false;
                
                // League/Div
                if (show && currentLeague !== 'all' && cl !== currentLeague) show = false;
                if (show && currentLeague === 'leagueone' && currentDiv !== 'all' && cd !== currentDiv) show = false;
                
                // Team
                if (show && selectedTeams.size > 0 && !selectedTeams.has(ct)) show = false;
                
                // Position
                if (show && currentPos !== 'all') {{
                    if (currentPos === 'FW' && !['PR', 'HO', 'LO', 'FL', 'No8'].includes(cp)) show = false;
                    else if (currentPos === 'BK' && !['SH', 'SO', 'CTB', 'WTB', 'FB'].includes(cp)) show = false;
                    else if (cp !== currentPos) show = false;
                }}
                
                r.style.display = show ? '' : 'none';
                if (show) count++;
            }});
            document.getElementById('player-count').innerText = count + "名";
        }}

        function sortTable(n) {{
            const table = document.getElementById("player-table");
            let rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
            switching = true;
            dir = "asc";
            while (switching) {{
                switching = false;
                rows = table.rows;
                for (i = 1; i < (rows.length - 1); i++) {{
                    shouldSwitch = false;
                    x = rows[i].getElementsByTagName("TD")[n];
                    y = rows[i+1].getElementsByTagName("TD")[n];
                    
                    let xVal = x.getAttribute('data-sort') || x.innerText.toLowerCase();
                    let yVal = y.getAttribute('data-sort') || y.innerText.toLowerCase();
                    
                    if (!isNaN(xVal) && !isNaN(yVal)) {{
                        xVal = parseFloat(xVal);
                        yVal = parseFloat(yVal);
                    }}

                    if (dir == "asc") {{
                        if (xVal > yVal) {{ shouldSwitch = true; break; }}
                    }} else if (dir == "desc") {{
                        if (xVal < yVal) {{ shouldSwitch = true; break; }}
                    }}
                }}
                if (shouldSwitch) {{
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchcount++;
                }} else {{
                    if (switchcount == 0 && dir == "asc") {{
                        dir = "desc";
                        switching = true;
                    }}
                }}
            }}
        }}
        
        updateTeamFilterVisibility();
    </script>
</body>
</html>"""
    with open(f'{OUTPUT_DIR}/players.html', 'w', encoding='utf-8') as f:
        f.write(html)

def generate_main_index():
    print("Generating Root index.html...")
    logo_img = '<img src="images/logo.png" alt="RugbyPick" style="height:60px; margin-bottom:10px;">'
    
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RugbyPick | ラグビーデータベース & 最新ニュース</title>
    <link rel="canonical" href="https://rugbypick.com/">
    {COMMON_CSS}
    <style>
        .hero {{ background: linear-gradient(135deg, #0097B2 0%, #007A8F 100%); color: white; padding: 60px 20px; text-align: center; border-radius: 0 0 50px 50px; margin-bottom: 40px; }}
        .hero h1 {{ font-size: 36px; margin-bottom: 20px; }}
        .search-container {{ max-width: 600px; margin: 0 auto; background: white; padding: 10px; border-radius: 30px; display: flex; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .search-input {{ flex: 1; border: none; padding: 10px 20px; font-size: 16px; border-radius: 30px; outline: none; }}
        .search-btn {{ background: #0097B2; color: white; border: none; padding: 10px 25px; border-radius: 30px; cursor: pointer; font-weight: bold; }}
        .main-menu {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 40px; }}
        .menu-card {{ background: white; padding: 30px; border-radius: 15px; text-align: center; text-decoration: none; color: inherit; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: transform 0.2s; border: 1px solid #efefef; }}
        .menu-card:hover {{ transform: translateY(-5px); border-color: #0097B2; }}
        .menu-icon {{ font-size: 40px; margin-bottom: 15px; display: block; }}
        .menu-title {{ font-size: 20px; font-weight: bold; color: #0097B2; margin-bottom: 10px; }}
        .menu-desc {{ font-size: 14px; color: #777; }}
    </style>
</head>
<body>
    <header style="background:#0097B2; padding:10px; text-align:center;">
        <a href="index.html" style="text-decoration:none; color:white; font-weight:bold; font-size:20px;">RugbyPick</a>
    </header>
    
    <div class="hero">
        <h1>{logo_img}<br>ラグビーをもっと身近に</h1>
        <p>国内・海外の選手・チームデータを網羅したデータベース</p>
    </div>

    <div class="container">
        <div class="main-menu">
            <a href="pages/leagues.html" class="menu-card">
                <span class="menu-icon">🏆</span>
                <div class="menu-title">リーグから探す</div>
                <div class="menu-desc">リーグワン、Top 14などの主要リーグを網羅</div>
            </a>
            <a href="pages/teams.html" class="menu-card">
                <span class="menu-icon">🛡️</span>
                <div class="menu-title">チームから探す</div>
                <div class="menu-desc">国内外の全チーム情報と所属選手リスト</div>
            </a>
            <a href="pages/players.html" class="menu-card">
                <span class="menu-icon">🏃</span>
                <div class="menu-title">選手から探す</div>
                <div class="menu-desc">3,000名以上の選手詳細プロフィール</div>
            </a>
        </div>

        <h2 class="section-title" style="margin-top:50px;">ニュース・記事</h2>
        <div class="main-menu" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
            <a href="news/domestic/leagueone/news/index.html" class="menu-card" style="padding:15px;">
                <div class="menu-title" style="font-size:16px;">リーグワン</div>
            </a>
            <a href="news/domestic/high-school/index.html" class="menu-card" style="padding:15px;">
                <div class="menu-title" style="font-size:16px;">高校ラグビー</div>
            </a>
            <a href="news/domestic/university/index.html" class="menu-card" style="padding:15px;">
                <div class="menu-title" style="font-size:16px;">大学ラグビー</div>
            </a>
            <a href="news/arekore/watch-guide/index.html" class="menu-card" style="padding:15px;">
                <div class="menu-title" style="font-size:16px;">観戦ガイド</div>
            </a>
        </div>
    </div>

    <footer style="text-align:center; padding:40px; color:#aaa; font-size:12px;">
        &copy; 2026 RugbyPick. All Rights Reserved.
    </footer>
</body>
</html>"""
    with open('dist/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

print("Generating Index Pages in dist/pages/...")
generate_leagues_index()
generate_teams_index()
generate_players_index()
generate_main_index()
print("✓ Done!")
