import json
import os
import re
from player_utils import slugify, clean_team_name, load_unified_players, get_player_score, get_team_slug


# --- Bilingual Team Mapping ---
TEAM_EN_MAP = {}
try:
    with open('data/top14_teams.json', 'r', encoding='utf-8') as f:
        TOP14_DATA = json.load(f)
    for t in TOP14_DATA:
        TEAM_EN_MAP[t['name_ja']] = t['name']
except:
    pass

# Players loaded via utility
print("Loading data via player_utils...")
players = load_unified_players()

def get_team_en_name(ja_name, current_raw=''):
    if current_raw and re.search(r'[a-zA-Z]', str(current_raw)):
        clean_raw = re.sub(r'[（(]\s*\d{4}.*?[）)]', '', str(current_raw)).strip()
        if re.search(r'[a-zA-Z]', clean_raw):
            return clean_raw
    return TEAM_EN_MAP.get(ja_name, '')

def clean_team_name(name):
    if not name: return ""
    return re.sub(r'[（(]\d{4}.*?[）)]', '', name).strip()

OVERSEAS_TEAM_MAP = {
    'Crusaders': 'super-rugby-pacific', 'Blues': 'super-rugby-pacific', 'Hurricanes': 'super-rugby-pacific', 
    'Chiefs': 'super-rugby-pacific', 'Highlanders': 'super-rugby-pacific', 'Brumbies': 'super-rugby-pacific',
    'Reds': 'super-rugby-pacific', 'Waratahs': 'super-rugby-pacific', 'Western Force': 'super-rugby-pacific',
    'Northampton Saints': 'premiership-rugby', 'Saracens': 'premiership-rugby', 'Bath Rugby': 'premiership-rugby',
    'Leinster': 'united-rugby-championship', 'Munster': 'united-rugby-championship', 'Stormers': 'united-rugby-championship',
    'Bulls': 'united-rugby-championship', 'Glasgow Warriors': 'united-rugby-championship', 'Sharks': 'united-rugby-championship',
    'Vannes': 'top-14', 'Provence': 'pro-d2', 'Béziers': 'pro-d2'
}

def get_league_slug_for_team(t_name_ja, t_name_en=''):
    if not isinstance(t_name_ja, str): t_name_ja = ''
    if not isinstance(t_name_en, str): t_name_en = ''
    
    # Priority: League One Check
    # Priority: League One Check
    if any(x in t_name_ja for x in ['浦安', '豊田自動', 'NEC', '九州電力', '日本製鉄', 'レッドハリケーンズ', '日野', '清水', 'クリタ', '中国電力', 'マツダ', 'ヤクルト', 'ルリーロ', 'ブルーレヴズ', 'サンゴリアス', 'D-Rocks', 'スティーラーズ', 'ワイルドナイツ', 'ブレイブルーパス', 'ヴェルブリッツ', 'ヒート', 'ダイナボアーズ', 'イーグルス', 'ブラックラムズ', 'スピアーズ', 'ライナーズ', '花園', '近鉄']):
        return 'leagueone'
    
    # Check Top 14 mapping
    if t_name_ja in ['トゥールーズ', 'ボルドー・ベグル', 'スタッド・フランセ', 'トゥーロン', 'ラ・ロシェル', 'ラシン92', 'リヨン', 'カストル', 'ポー', 'ペルピニャン', 'バイヨンヌ', 'クレルモン', 'モンペリエ', 'ヴァンヌ']:
        return 'top-14'
        
    # Check Overseas Map using specific word matching to avoid 'Sharks' matching 'Blue Sharks'
    for k, v in OVERSEAS_TEAM_MAP.items():
        if k in t_name_ja:
            return v
        if t_name_en and (k == t_name_en or f" {k}" in t_name_en or f"{k} " in t_name_en):
            return v
    return None


# Load data
print("Loading data...")
with open('data/rugby_leagues.json', 'r', encoding='utf-8') as f:
    leagues = json.load(f)

with open('data/league_colors.json', 'r', encoding='utf-8') as f:
    league_colors = json.load(f)

with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
    league_one_teams = json.load(f)

# Create output directory
LEAGUES_OUT_BASE = 'dist/leagues'
os.makedirs(LEAGUES_OUT_BASE, exist_ok=True)

def generate_league_page_deep(league_name, teams=None, sub_title=None, is_top=False, league_slug='leagueone'):
    """Generate HTML page for a league"""
    
    # Path calculation (NEW MASTER MAP)
    # dist/leagues/leagueone/index.html
    # dist/leagues/leagueone/div1/index.html
    
    league_dir = os.path.join(LEAGUES_OUT_BASE, league_slug)
    os.makedirs(league_dir, exist_ok=True)

    if is_top:
        output_path = os.path.join(league_dir, 'index.html')
        relative_root = "../../" 
        display_title = league_name
        current_dir_slug = ""
    else:
        # Map "Division 1" -> div1
        div_num = sub_title.split(" ")[-1]
        dir_slug = f"div{div_num}"
        os.makedirs(os.path.join(league_dir, dir_slug), exist_ok=True)
        output_path = os.path.join(league_dir, dir_slug, 'index.html')
        relative_root = "../../../" 
        display_title = f"{league_name} - {sub_title}"
        current_dir_slug = dir_slug
    
    colors = league_colors.get(league_name, {})
    l_color = colors.get('primary', '#0097B2')
    
    # Teams list HTML
    teams_html = ""
    if teams:
        teams_html = '<div class="teams-grid">'
        for t in teams:
            t_name = t.get('team_name') or t.get('name')
            division = t.get('division', '')
            div_tag = f'<div class="team-div">{division}</div>' if division else ''
            
            # Master Link: /teams/{league}/{team}/index.html
            t_slug = get_team_slug(t_name)
            
            # Map JRLO divisions to unified 'leagueone' team directory
            link_league_slug = league_slug
            if 'league-one' in league_slug or 'leagueone' in league_slug:
                link_league_slug = 'leagueone'
                
            link_href = f"{relative_root}teams/{link_league_slug}/{t_slug}/index.html"

            # Bilingual display
            t_en = get_team_en_name(t_name)
            t_disp = t_name
            if t_en and t_en != t_name:
                t_disp += f' <span style="font-size: 0.8em; opacity: 0.7;">({t_en})</span>'

            teams_html += f"""
            <a href="{link_href}" class="team-card">
                {div_tag}
                <div class="team-name">{t_disp}</div>
                <div class="view-link">チーム詳細を見る ↗</div>
            </a>
            """
        teams_html += '</div>'
    else:
        teams_html = '<p>所属チームのデータが準備中です。</p>'

    logo_img = f'<img src="{relative_root}images/logo.png" alt="RugbyPick" style="height:40px; vertical-align:middle;">'
    nav_prefix = f"{relative_root}pages/"

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{display_title} | RugbyPick</title>
    {f'<link rel="canonical" href="https://rugbypick.com/leagues/{league_slug}/{current_dir_slug}/">' if current_dir_slug else f'<link rel="canonical" href="https://rugbypick.com/leagues/{league_slug}/">'}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Noto Sans JP', sans-serif; background-color: #f5f7f9; color: #484848; line-height: 1.6; }}
        .header-container {{ background-color: #0097B2; padding: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header-content {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; text-align: center; }}
        .site-title {{ color: white; text-decoration: none; font-size: 24px; font-weight: 700; }}
        .nav-container {{ background-color: #007A8F; padding: 10px 0; position: sticky; top: 0; z-index: 100; }}
        .nav-menu {{ display: flex; justify-content: center; list-style: none; gap: 30px; }}
        .nav-menu a {{ color: white; text-decoration: none; font-weight: 700; font-size: 15px; }}
        .container {{ max-width: 1200px; margin: 40px auto; padding: 0 20px; }}
        .league-header {{
            background: linear-gradient(135deg, {l_color} 0%, #333 100%);
            color: #ffffff; padding: 50px 40px; border-radius: 12px; margin-bottom: 40px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .league-title {{ font-size: 38px; font-weight: 700; margin-bottom: 15px; }}
        .league-desc {{ font-size: 18px; opacity: 0.9; max-width: 800px; margin: 0 auto; }}
        .section-title {{ font-size: 24px; font-weight: 700; color: #333; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 3px solid {l_color}; }}
        .teams-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        .team-card {{
            background: #ffffff; padding: 25px; border-radius: 10px; text-decoration: none; color: inherit;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s; position: relative; border: 1px solid #eee;
        }}
        .team-card:hover {{ transform: translateY(-5px); box-shadow: 0 6px 15px rgba(0,0,0,0.1); }}
        .team-div {{ position: absolute; top: 15px; right: 15px; background: #f0f0f0; padding: 2px 10px; border-radius: 4px; font-size: 11px; font-weight: 700; color: #666; }}
        .team-name {{ font-size: 19px; font-weight: 700; color: #333; margin-top: 10px; margin-bottom: 15px; }}
        .view-link {{ font-size: 13px; color: #0097B2; font-weight: 700; }}
        .division-nav {{ display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; }}
        .div-link {{
            padding: 8px 20px; background: #fff; border: 2px solid #ddd; border-radius: 25px;
            text-decoration: none; color: #666; font-weight: 700; font-size: 14px; transition: all 0.2s;
        }}
        .div-link:hover, .div-link.active {{ background: {l_color}; border-color: {l_color}; color: #fff; }}
    </style>
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
            <li><a href="{nav_prefix}leagues.html">リーグ一覧</a></li>
            <li><a href="{nav_prefix}teams.html">チーム一覧</a></li>
            <li><a href="{nav_prefix}players.html">選手一覧</a></li>
        </ul>
    </nav>

    <div class="container">
        <div class="league-header">
            <div class="league-title">{display_title}</div>
            <div class="league-desc">{colors.get('description', 'ラグビー界最高峰のリーグ戦。')}</div>
        </div>

        {"<div class='division-nav'>" + generate_deep_nav(is_top, current_dir_slug) + "</div>" if league_slug == 'leagueone' else ""}

        <h2 class="section-title">所属チーム一覧</h2>
        {teams_html}
    </div>
</body>
</html>"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated {output_path}")

def generate_deep_nav(is_top, current_slug):
    # Base structure:
    # Top: .
    # Div1: leagueone-div1
    # Div2: leagueone-div2
    # Div3: leagueone-div3
    
    nav_html = ""
    
    # ALL
    if is_top:
        nav_html += '<a href="index.html" class="div-link active">ALL</a>'
    else:
        nav_html += '<a href="../index.html" class="div-link">ALL</a>'
        
    divs = [
        ("Division 1", "div1"),
        ("Division 2", "div2"),
        ("Division 3", "div3")
    ]
    
    for label, slug in divs:
        is_active = (slug == current_slug)
        active_class = " active" if is_active else ""
        
        if is_top:
            # Link to ./slug/index.html
            link = f"{slug}/index.html"
        else:
            # Link to ../slug/index.html
            # But if self?
            if is_active:
                link = "index.html"
            else:
                link = f"../{slug}/index.html"
                
        nav_html += f'<a href="{link}" class="div-link{active_class}">{label}</a>'
        
    return nav_html


if __name__ == "__main__":
    # 1. League One (Main + Divisions)
    div1_teams = [t for t in league_one_teams if t.get('division') == 'Division 1']
    div2_teams = [t for t in league_one_teams if t.get('division') == 'Division 2']
    div3_teams = [t for t in league_one_teams if t.get('division') == 'Division 3']

    print("Generating League One Deep pages...")
    generate_league_page_deep("League One", teams=league_one_teams, is_top=True, league_slug='leagueone')
    generate_league_page_deep("League One", teams=div1_teams, sub_title="Division 1", is_top=False, league_slug='leagueone')
    generate_league_page_deep("League One", teams=div2_teams, sub_title="Division 2", is_top=False, league_slug='leagueone')
    generate_league_page_deep("League One", teams=div3_teams, sub_title="Division 3", is_top=False, league_slug='leagueone')

    # 2. Top 14 (Mixed from player source & top14_teams.json)
    print("Generating Top 14 page...")
    # Convert TOP14_DATA (list of {name, name_ja, slug}) to format expected by generator
    t14_teams_formatted = []
    for t in TOP14_DATA:
        t14_teams_formatted.append({
            'team_name': t['name_ja'],
            'division': 'TOP14'
        })
    generate_league_page_deep("TOP14", teams=t14_teams_formatted, is_top=True, league_slug='top-14')

    # Load data from all sources to ensure completeness (Libbok, Biziwu, etc.)
    print("Loading data...")
    all_players_combined = {}

    # 1. Load League One / Master Unified High Quality Data
    sources = [
        'data/unified_player_database_full.json',
        'data/unified_player_database_final.json',
        'data/top14_players_enrich.json',
        'data/top14_players_enriched.json'
    ]

    for s_path in sources:
        try:
            if os.path.exists(s_path):
                with open(s_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    p_list = data if isinstance(data, list) else data.values()
                    for p in p_list:
                        # Create a robust matching key: Normalized Name
                        name_en = str(p.get('name_en') or p.get('en_name', '')).lower().replace(' ', '').replace('-', '')
                        if not name_en: continue
                        
                        if name_en not in all_players_combined:
                            all_players_combined[name_en] = p
                        else:
                            existing = all_players_combined[name_en]
                            # Merge fields
                            for key, val in p.items():
                                if val and (not existing.get(key) or existing.get(key) == '-' or existing.get(key) == []):
                                    existing[key] = val
                            if p.get('career_history') and (not existing.get('career_history') or existing.get('career_history') == [] or existing.get('career_history') == '-'):
                                existing['career_history'] = p.get('career_history')
        except Exception as e:
            print(f"Warning: Failed to load {s_path}: {e}")

    players = list(all_players_combined.values())

    # Build league -> teams map once
    league_to_teams = {}
    for p in players:
        t_raw = p.get('team')
        if p.get('source') == 'all_rugby' and not t_raw:
            from generate_player_pages import consolidate_career_history
            career = consolidate_career_history(p.get('career_history'))
            if career:
                t_raw = career[-1].get('team')
                
        t_name = clean_team_name(t_raw)
        if not t_name or str(t_name).lower() == 'nan': continue
        
        t_en = p.get('team_en', '')
        l_slug = get_league_slug_for_team(t_name, t_en)
        
        if not l_slug:
            l_name_raw = p.get('league') or p.get('source', '')
            l_slug = slugify(l_name_raw)
            
        if l_slug not in league_to_teams:
            league_to_teams[l_slug] = set()
        league_to_teams[l_slug].add(t_name)

    # Load All Rugby Teams to fill missing league members
    try:
        with open('data/rugby_teams.json', 'r', encoding='utf-8') as f:
            all_teams_data = json.load(f)
        with open('data/rugby_leagues.json', 'r', encoding='utf-8') as f:
            all_leagues_data = json.load(f)
        
        league_id_to_slug = {}
        for l in all_leagues_data:
            league_id_to_slug[l['id']] = l['url'].split('/')[-1]
            
        for t in all_teams_data:
            l_id = t.get('league_id')
            if l_id and l_id in league_id_to_slug:
                l_s = league_id_to_slug[l_id]
                l_k = slugify(l_s)
                
                t_n_raw = t.get('name_ja') or t.get('name')
                t_n_en = t.get('name', '')
                # Skip dummy data (e.g. "Team 1 League 8" and "チーム1")
                if t_n_en and str(t_n_en).startswith('Team ') and ' League ' in str(t_n_en):
                    continue
                if t_n_raw and str(t_n_raw).startswith('チーム') and str(t_n_raw).replace('チーム', '').isdigit():
                    continue
                    
                t_n = clean_team_name(t_n_raw)
                if t_n and l_k:
                    if l_k not in league_to_teams:
                        league_to_teams[l_k] = set()
                    league_to_teams[l_k].add(t_n)
    except Exception as e:
        print(f"Warning: Failed to load auxiliary team data: {e}")

    for l in leagues:
        l_name_ja = l['name_ja']
        l_name_en = l['name']
        l_slug = l['url'].split('/')[-1]
        
        # Unify JRLO slugs to leagueone and skip because they are generated at the top
        if 'leagueone' in l_slug or 'japan-rugby-league-one' in l_slug:
            continue
            
        # Top 14 is also explicitly generated at the top
        if 'top' in l_slug.lower() and '14' in l_slug:
            continue
            
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
        teams_list = [{'team_name': tn, 'division': l_name_ja} for tn in t_names]
        
        print(f"  Generating {l_name_ja} ({len(teams_list)} teams)...")
        generate_league_page_deep(l_name_ja, teams=teams_list, is_top=True, league_slug=l_slug)

    print("\n✓ Done!")
