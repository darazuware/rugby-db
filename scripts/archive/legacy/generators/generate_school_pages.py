import json
import os
import re
import hashlib
from player_utils import (
    slugify, clean_team_name, load_unified_players, 
    get_player_score, get_team_slug, get_canonical_school_name,
    get_normalized_school_name,
    calculate_age, get_pos_rank, get_school_slug
)

# Load data via common utility
print("Loading data via player_utils...")
players = load_unified_players()

with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
    teams_detailed = json.load(f)

os.makedirs('dist/schools', exist_ok=True)

# Team Data for Filtering
TEAM_INFO = {} # slug -> {name, div, league}
L1_TEAMS = {} # div -> [team_slugs]
T14_TEAMS = [] # [team_slugs]

for t in teams_detailed:
    t_name = clean_team_name(t.get('team_name'))
    t_slug = get_team_slug(t_name)
    div_raw = t.get('division', 'Division 1')
    div = f"div{div_raw[-1]}" 
    
    TEAM_INFO[t_slug] = {"name": t_name, "div": div, "league": "l1"}
    if div not in L1_TEAMS: L1_TEAMS[div] = []
    if t_slug not in L1_TEAMS[div]: L1_TEAMS[div].append(t_slug)

# Group players by school
high_schools = {}
universities = {}

# Map to store previous names seen for each canonical name
hs_previous_names = {}
univ_previous_names = {}

for p in players:
    # Rich Check via common utility
    score = get_player_score(p)
    if score < 2: continue

    # Process Metadata for Filtering
    p_team_name = clean_team_name(p.get('team'))
    p_team_slug = get_team_slug(p_team_name)
    p_league = p.get('league') or p.get('source', '')
    
    if p_league == 'Top 14' or p_league == 'top_14':
        p['league_key'] = 't14'
        p['div_key'] = 'top-14'
        if p_team_slug not in TEAM_INFO:
            TEAM_INFO[p_team_slug] = {"name": p_team_name, "div": "top-14", "league": "top-14"}
            if p_team_slug not in T14_TEAMS: T14_TEAMS.append(p_team_slug)
    else:
        p['league_key'] = 'l1'
        p['div_key'] = TEAM_INFO.get(p_team_slug, {}).get('div', 'div1')
    
    p['team_slug'] = p_team_slug

    def collect_school(raw_name, collection, prev_map, is_hs=True):
        if not raw_name or raw_name == '-': return
        normalized = get_normalized_school_name(raw_name) or raw_name
        canonical = get_canonical_school_name(normalized) or normalized
        
        if canonical not in collection: collection[canonical] = []
        
        # Tag player with normalized name for filtering
        if is_hs: p['hs_norm'] = normalized
        else: p['univ_norm'] = normalized
        
        collection[canonical].append(p)
        
        # Track original names for the title and filter
        if canonical != normalized:
            if canonical not in prev_map: prev_map[canonical] = set()
            prev_map[canonical].add(normalized)

    collect_school(p.get('high_school'), high_schools, hs_previous_names, is_hs=True)
    collect_school(p.get('university'), universities, univ_previous_names, is_hs=False)

def generate_school_page(school_name, alumni_list, school_type="High School", prev_names=None):
    slug = get_school_slug(school_name)
    if not slug: return None
    
    # Display name with previous names if applicable
    display_title = str(school_name)
    if prev_names:
        display_title += f'（旧：{", ".join(sorted(str(name) for name in prev_names))}）'
    # Sort alumni by name
    sorted_players = sorted(alumni_list, key=lambda x: str(x.get('name_en', '')))

    player_rows = ""
    for p in sorted_players:
        p_name = p.get('name_ja') or p.get('name_en')
        p_en = p.get('name_en', '')
        p_id = p.get('id', '')
        p_slug = f"{slugify(p_en)}_{p_id}"
        p_team = clean_team_name(p.get('team', '-'))
        p_pos = p.get('position', '-')
        p_age = calculate_age(p.get('birthdate'))
        p_pos_rank = get_pos_rank(p_pos)
        
        # Cross-reference school
        p_univ_raw = p.get('university', '-')
        p_univ_norm = get_normalized_school_name(p_univ_raw) or p_univ_raw
        p_univ_can = get_canonical_school_name(p_univ_raw) or p_univ_raw
        
        p_hs_raw = p.get('high_school', '-')
        p_hs_norm = get_normalized_school_name(p_hs_raw) or p_hs_raw
        p_hs_can = get_canonical_school_name(p_hs_raw) or p_hs_raw
        
        # The filter value depends on which school type we are currently viewing
        filter_school_norm = p['hs_norm'] if school_type == "高校" else p.get('univ_norm', p_univ_norm)
        
        # Link only if score >= 2
        score = get_player_score(p)
        p_name_disp = f"{p_name} ({p_en})" if p_en and p_en != 'Unknown' else p_name
        p_link = f'<a href="../player/{p_slug}.html">{p_name_disp}</a>' if score >= 2 else p_name_disp

        player_rows += f"""
        <tr class="player-row {p['league_key']}-player" data-league="{p['league_key']}" data-div="{p['div_key']}" data-team="{p['team_slug']}" data-school-norm="{filter_school_norm}">
            <td data-sort-value="{p_en}">{p_link}</td>
            <td data-sort-value="{p_pos_rank}" data-rank="{p_pos_rank}"><span class="pos-tag">{p_pos}</span></td>
            <td data-sort-value="{p_age}">{p_age}歳</td>
            <td data-sort-value="{p_team}">{p_team}</td>
            <td data-sort-value="{p_hs_norm}">{p_hs_norm}</td>
            <td data-sort-value="{p_univ_norm}">{p_univ_norm}</td>
        </tr>
        """
        
    def make_team_filters(team_slugs):
        filters = ""
        for ts in sorted(team_slugs):
            if ts not in TEAM_INFO: continue
            t_info = TEAM_INFO[ts]
            filters += f'<div class="team-filter" data-team="{ts}" data-div="{t_info["div"]}" onclick="toggleTeam(\'{ts}\')">{t_info["name"]}</div>'
        return filters

    def make_school_name_filters(current_name, older_names):
        if not older_names: return ""
        all_names = sorted([current_name] + list(older_names))
        filters = f"""
            <div id="school-name-group" class="filter-group">
                <div class="filter-label">0. 校名を選択</div>
                <div class="filter-tabs">
                    <div class="filter-tab active" data-school="all" onclick="filterSchool('all')">すべて</div>
        """
        for name in all_names:
            filters += f'<div class="filter-tab" data-school="{name}" onclick="filterSchool(\'{name}\')">{name}</div>'
        filters += "</div></div>"
        return filters

    logo_img = f'<img src="../images/logo.png" alt="RugbyPick" style="height:40px; vertical-align:middle;">'

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{display_title} | RugbyPick School</title>
    <link rel="canonical" href="https://rugbypick.com/schools/{slug}.html">
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
        
        .school-header-card {{ background: #fff; padding: 30px; border-radius: 12px; margin-bottom: 30px; border-top: 8px solid #0097B2; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        .school-name {{ font-size: 32px; font-weight: 700; color: #333; }}
        .school-type {{ font-size: 14px; color: #666; background: #eee; padding: 4px 12px; border-radius: 20px; display: inline-block; margin-top: 10px; }}
        
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
        
        .players-table-container {{ background: #fff; border-radius: 8px; overflow-x: auto; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .roster-table {{ width: 100%; border-collapse: collapse; min-width: 800px; }}
        .roster-table th {{ background-color: #f8f9fa; text-align: left; padding: 15px; font-size: 14px; color: #888; border-bottom: 2px solid #eee; }}
        .roster-table td {{ padding: 15px; border-bottom: 1px solid #eee; }}
        .roster-table tr:hover {{ background-color: #fdfdfd; }}
        .roster-table a {{ color: #0097B2; text-decoration: none; font-weight: 700; }}
        
        .pos-tag {{ display: inline-block; background-color: #e9ecef; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 700; color: #495057; }}
        
        .section-header {{ margin-bottom: 20px; border-bottom: 2px solid #0097B2; padding-bottom: 10px; display: flex; align-items: center; justify-content: space-between; }}
        .section-title {{ font-size: 24px; font-weight: 700; }}
        .player-count {{ color: #999; font-size: 16px; }}

        .reset-filter-btn {{
            display: inline-block;
            margin-top: 15px;
            padding: 10px 20px;
            background-color: #f8f9fa;
            color: #666;
            text-decoration: none;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 700;
            border: 1px solid #ddd;
            transition: all 0.2s;
        }}
        .reset-filter-btn:hover {{ background-color: #e9ecef; color: #333; }}

        /* Sort Icons */
        th[data-sort]::after {{ content: " ↕"; opacity: 0.3; font-size: 0.8em; }}
        th.sort-asc::after {{ content: " ↑"; opacity: 1; color: #0097B2; }}
        th.sort-desc::after {{ content: " ↓"; opacity: 1; color: #0097B2; }}
    </style>
    <script src="../js/table-sorter.js" defer></script>
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
        <div class="school-header-card">
            <h1 class="school-name">{display_title}</h1>
            <span class="school-type">{school_type}</span>
            <div style="margin-top: 15px; font-weight: 700; color: #0097B2;">登録OB選手: {len(sorted_players)}名</div>
            <a href="../pages/players.html" class="reset-filter-btn" onclick="resetPageContext('../pages/players.html'); return false;">← 全選手一覧へ戻る（絞り込み解除）</a>
        </div>

        <div class="filter-section">
            {make_school_name_filters(school_name, prev_names)}
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
                    <div class="filter-tab" data-div="div1" onclick="filterDiv('div1')">Division 1</div>
                    <div class="filter-tab" data-div="div2" onclick="filterDiv('div2')">Division 2</div>
                    <div class="filter-tab" data-div="div3" onclick="filterDiv('div3')">Division 3</div>
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

        <div class="section-header">
            <h2 class="section-title">出身選手一覧</h2>
            <span id="player-count" class="player-count">{len(sorted_players)}名</span>
        </div>
        <div class="players-table-container">
            <table class="roster-table" id="rosterTable">
                <thead>
                    <tr>
                        <th data-sort="string">選手名</th>
                        <th data-sort="pos-rank">ポジション</th>
                        <th data-sort="number">年齢</th>
                        <th data-sort="string">チーム</th>
                        <th data-sort="string">高校</th>
                        <th data-sort="string">大学</th>
                    </tr>
                </thead>
                <tbody id="players-grid">
                    {player_rows}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        let currentLeague = 'all';
        let currentDiv = 'all';
        let currentSchool = 'all';
        let selectedTeams = new Set();

        function filterSchool(schoolName) {{
            currentSchool = schoolName;
            document.querySelectorAll('#school-name-group .filter-tab').forEach(t => {{
                t.classList.toggle('active', t.getAttribute('data-school') === schoolName);
            }});
            applyFilters();
        }}

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
                const isL1 = tDiv.startsWith('div');
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
            const rows = document.querySelectorAll('.player-row');
            let visibleCount = 0;
            
            rows.forEach(row => {{
                const cLeague = row.getAttribute('data-league');
                const cDiv = row.getAttribute('data-div');
                const cTeam = row.getAttribute('data-team');
                const cSchool = row.getAttribute('data-school-norm');
                
                let show = true;
                if (currentSchool !== 'all' && cSchool !== currentSchool) show = false;
                if (currentLeague !== 'all' && cLeague !== currentLeague) show = false;
                if (currentLeague === 'l1' && currentDiv !== 'all' && cDiv !== currentDiv) show = false;
                if (selectedTeams.size > 0 && !selectedTeams.has(cTeam)) show = false;
                
                row.style.display = show ? 'table-row' : 'none';
                if (show) visibleCount++;
            }});
            
            document.getElementById('player-count').textContent = visibleCount + '名';
        }}
        
        // Initial setup
        updateTeamFilterVisibility();
    </script>
</body>
</html>"""
    
    filename = f"dist/schools/{slug}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    return filename

print(f"Generating {len(high_schools)} High School pages...")
for hs, alumni in high_schools.items():
    generate_school_page(hs, alumni, "高校", hs_previous_names.get(hs))

print(f"Generating {len(universities)} University pages...")
for univ, alumni in universities.items():
    generate_school_page(univ, alumni, "大学", univ_previous_names.get(univ))

print("✓ School pages generated!")
