import json
import os
import re
from player_utils import slugify, clean_team_name, load_unified_players, get_player_score, get_team_slug, get_league_slug_for_team

# Load data
players = load_unified_players()
with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
    teams_detailed = json.load(f)
with open('data/rugby_leagues.json', 'r', encoding='utf-8') as f:
    leagues = json.load(f)

# --- Global Team Data for Indices ---
GLOBAL_TEAM_DATA = {}
for t in teams_detailed:
    t_name = clean_team_name(t['team_name'])
    t_slug = get_team_slug(t_name)
    div_raw = t.get('division', 'Division 1')
    div = f"div{div_raw[-1]}"
    GLOBAL_TEAM_DATA[t_slug] = {"name": t_name, "div": div, "league": "leagueone", "league_ja": "League One"}

# Populate other teams from players
for p in players:
    if get_player_score(p) < 2: continue
    t_name = clean_team_name(p.get('team'))
    if not t_name: continue
    t_slug = get_team_slug(t_name)
    if t_slug not in GLOBAL_TEAM_DATA:
        l_slug = get_league_slug_for_team(t_name, p.get('team_en', '')) or 'unknown'
        l_ja = '不明'
        for l in leagues:
            if l['url'].split('/')[-1] == l_slug:
                l_ja = l['name_ja']
                break
        GLOBAL_TEAM_DATA[t_slug] = {"name": t_name, "div": l_slug, "league": l_slug, "league_ja": l_ja}

def generate_leagues_md():
    content = "# リーグ一覧\n\n## 国内リーグ\n\n"
    for l in leagues:
        if l.get('country') == "日本":
            name = l['name']
            slug = slugify(name)
            link = f"../leagues/leagueone/index.html" if "League One" in name else f"../leagues/{slug}/index.html"
            content += f"- [{l['name_ja']} ({l['name']})]({link})\n"
    
    content += "\n## 海外リーグ\n\n"
    for l in leagues:
        if l.get('country') != "日本":
            name = l['name']
            slug = slugify(name)
            link = f"../leagues/top-14/index.html" if "top 14" in name.lower() else f"../leagues/{slug}/index.html"
            content += f"- [{l['name_ja']} ({l['name']})]({link})\n"

    frontmatter = {'title': 'リーグ一覧', 'layout': 'page'}
    with open('content/pages/leagues.md', 'w', encoding='utf-8') as f:
        f.write(f"---\n{json.dumps(frontmatter, ensure_ascii=False, indent=2)}\n---\n\n{content}")

def generate_teams_md():
    # JavaScript and HTML for filtering is kept in MD for simplicity
    team_list_html = '<div class="card-grid" id="teams-grid">'
    for t_slug, data in GLOBAL_TEAM_DATA.items():
        if data['league'] == 'unknown': continue
        link = f"../teams/{data['league']}/{t_slug}/index.html"
        team_list_html += f'<a href="{link}" class="item-card team-card" data-league="{data["league"]}" data-div="{data["div"]}"><div class="item-name">{data["name"]}</div><div class="item-meta">{data["league_ja"]}</div></a>'
    team_list_html += '</div>'

    # Filter section
    filter_html = """
<div class="filter-section">
    <div class="filter-group">
        <div class="filter-label">リーグで絞り込む</div>
        <div class="filter-tabs">
            <div class="filter-tab active" data-league="all" onclick="switchLeague('all')">すべて</div>
            <div class="filter-tab" data-league="leagueone" onclick="switchLeague('leagueone')">League One</div>
        </div>
    </div>
</div>
<script>
function switchLeague(l) {
    document.querySelectorAll('.team-card').forEach(c => {
        c.style.display = (l === 'all' || c.getAttribute('data-league') === l) ? 'block' : 'none';
    });
    document.querySelectorAll('.filter-tab').forEach(t => t.classList.toggle('active', t.getAttribute('data-league') === l));
}
</script>
"""

    frontmatter = {'title': 'チーム一覧', 'layout': 'page'}
    with open('content/pages/teams.md', 'w', encoding='utf-8') as f:
        f.write(f"---\n{json.dumps(frontmatter, ensure_ascii=False, indent=2)}\n---\n\n# チーム一覧\n\n{filter_html}\n\n{team_list_html}")

def generate_index_md():
    content = """
# RugbyPick へようこそ

ラグビーの国内・海外選手、チーム、リーグ情報を網羅したデータベースサイトです。

- [🏆 リーグから探す](pages/leagues.html)
- [🛡️ チームから探す](pages/teams.html)
- [🏃 選手から探す](pages/players.html)
"""
    frontmatter = {'title': 'ホーム', 'layout': 'home'}
    with open('content/index.md', 'w', encoding='utf-8') as f:
        f.write(f"---\n{json.dumps(frontmatter, ensure_ascii=False, indent=2)}\n---\n\n{content}")

if __name__ == "__main__":
    os.makedirs('content/pages', exist_ok=True)
    generate_leagues_md()
    generate_teams_md()
    generate_index_md()
    print("✓ Index MDs Complete!")
