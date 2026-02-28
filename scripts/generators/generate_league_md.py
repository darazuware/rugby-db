import json
import os
import re
from player_utils import slugify, clean_team_name, get_team_slug

# Load data
with open('data/rugby_leagues.json', 'r', encoding='utf-8') as f:
    leagues = json.load(f)

with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
    league_one_teams = json.load(f)

CONTENT_BASE = 'content/leagues'
os.makedirs(CONTENT_BASE, exist_ok=True)

def generate_league_md(league_name, teams=None, sub_title=None, is_top=False, league_slug='leagueone'):
    """Generate Markdown page for a league"""
    
    league_dir = os.path.join(CONTENT_BASE, league_slug)
    os.makedirs(league_dir, exist_ok=True)

    if is_top:
        output_path = os.path.join(league_dir, 'index.md')
        display_title = league_name
        rel_root = "../../../" # Relative to content root for links in MD if needed
    else:
        # Map "Division 1" -> div1
        div_num = sub_title.split(" ")[-1]
        dir_slug = f"div{div_num}"
        os.makedirs(os.path.join(league_dir, dir_slug), exist_ok=True)
        output_path = os.path.join(league_dir, dir_slug, 'index.md')
        display_title = f"{league_name} - {sub_title}"

    # Teams list MD
    teams_md = ""
    if teams:
        teams_md = "### 所属チーム一覧\n\n"
        for t in teams:
            t_name = t.get('team_name') or t.get('name')
            t_slug = get_team_slug(t_name)
            division = t.get('division', '')
            
            # Master Link: /teams/leagueone/{team}/index.html
            # Note: MD links should be relative or absolute from site root. 
            # In our SSG, we use rel_root for images/CSS but links can be relative to current.
            # From leagues/leagueone/index.html to teams/leagueone/slug/index.html: ../../teams/leagueone/slug/index.html
            # From leagues/leagueone/div1/index.html to teams/leagueone/slug/index.html: ../../../teams/leagueone/slug/index.html
            depth = 2 if is_top else 3
            link_prefix = "../" * depth
            link_href = f"{link_prefix}teams/{league_slug}/{t_slug}/index.html"
            
            div_tag = f" [{division}]" if division else ""
            teams_md += f"- [{t_name}]({link_href}){div_tag}\n"
    else:
        teams_md = "\n所属チームのデータが準備中です。\n"

    # Frontmatter
    frontmatter = {
        'title': display_title,
        'layout': 'league',
        'league_slug': league_slug,
        'is_top': is_top
    }
    
    md_content = f"---\n{json.dumps(frontmatter, ensure_ascii=False, indent=2)}\n---\n\n"
    md_content += f"# {display_title}\n\n"
    md_content += teams_md

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Generated MD: {output_path}")

if __name__ == "__main__":
    # League One
    div1_teams = [t for t in league_one_teams if t.get('division') == 'Division 1']
    div2_teams = [t for t in league_one_teams if t.get('division') == 'Division 2']
    div3_teams = [t for t in league_one_teams if t.get('division') == 'Division 3']

    print("Generating League One MDs...")
    generate_league_md("League One", teams=league_one_teams, is_top=True, league_slug='leagueone')
    generate_league_md("League One", teams=div1_teams, sub_title="Division 1", is_top=False, league_slug='leagueone')
    generate_league_md("League One", teams=div2_teams, sub_title="Division 2", is_top=False, league_slug='leagueone')
    generate_league_md("League One", teams=div3_teams, sub_title="Division 3", is_top=False, league_slug='leagueone')

    print("\n✓ Done!")
