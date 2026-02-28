import json
import pandas as pd
import os
import re

def slugify(text):
    """Convert text to URL-friendly slug"""
    if not text or pd.isna(text):
        return "unknown"
    text = str(text).lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '_', text)
    return text.strip('_')

def get_league_colors(league_name):
    """Get colors for a specific league"""
    
    # Load league colors
    try:
        with open('league_colors.json', 'r') as f:
            league_colors = json.load(f)
    except:
        return {
            'primary': '#0097B2',
            'secondary': '#00b8d4',
            'accent': '#FFFFFF',
            'text_light': '#FFFFFF'
        }
    
    # Direct match first
    if league_name in league_colors:
        return league_colors[league_name]
    
    # Fuzzy match
    league_lower = league_name.lower() if league_name else ''
    
    for key, colors in league_colors.items():
        key_lower = key.lower()
        if key_lower in league_lower or league_lower in key_lower:
            return colors
    
    # Pattern matching
    if 'league one' in league_lower or 'リーグワン' in league_lower:
        return league_colors.get('League One', {})
    elif 'super rugby pacific' in league_lower:
        return league_colors.get('Super Rugby Pacific', {})
    elif 'super rugby americas' in league_lower:
        return league_colors.get('Super Rugby Americas', {})
    elif 'top 14' in league_lower or 'top14' in league_lower:
        return league_colors.get('Top 14', {})
    elif 'premiership' in league_lower:
        return league_colors.get('Premiership Rugby', {})
    elif 'urc' in league_lower or 'united rugby' in league_lower:
        return league_colors.get('United Rugby Championship', {})
    elif 'currie' in league_lower:
        return league_colors.get('Currie Cup', {})
    elif 'mlr' in league_lower or 'major league' in league_lower:
        return league_colors.get('Major League Rugby', {})
    elif 'npc' in league_lower or 'bunnings' in league_lower:
        return league_colors.get('Bunnings NPC', {})
    elif 'shute' in league_lower:
        return league_colors.get('Shute Shield', {})
    elif 'hospital' in league_lower:
        return league_colors.get('Hospital Cup', {})
    elif 'pro d2' in league_lower or 'prod2' in league_lower:
        return league_colors.get('Pro D2', {})
    
    # Default
    return {
        'primary': '#0097B2',
        'secondary': '#00b8d4',
        'accent': '#FFFFFF',
        'text_light': '#FFFFFF'
    }

def generate_player_sample(league_name, output_dir='sample_pages'):
    """Generate a sample player page with league-specific colors"""
    
    colors = get_league_colors(league_name)
    primary = colors.get('primary', '#0097B2')
    secondary = colors.get('secondary', '#00b8d4')
    
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample Player | {league_name} | RugbyPick</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Noto Sans JP', sans-serif;
            background-color: #ffffff;
            color: #484848;
            font-size: 18px;
            line-height: 1.6;
        }}
        .header-container {{
            background-color: {primary};
            padding: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        .site-title {{
            color: #ffffff;
            font-size: 24px;
            font-weight: 700;
            text-decoration: none;
        }}
        .container {{
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
        }}
        .player-header {{
            background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
            color: #ffffff;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .player-name {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .player-name-en {{
            font-size: 24px;
            opacity: 0.95;
            margin-bottom: 20px;
            font-weight: 500;
        }}
        .section-title {{
            font-size: 24px;
            font-weight: 700;
            color: {primary};
            margin: 40px 0 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid {primary};
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .info-card {{
            background: #f8f8f8;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid {primary};
        }}
        .info-label {{
            font-size: 14px;
            color: #000000;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        .info-value {{
            font-size: 20px;
            font-weight: 700;
            color: #484848;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        .info-value a {{
            color: {primary};
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <header class="header-container">
        <div class="header-content">
            <a href="../../index.html" class="site-title">RugbyPick</a>
        </div>
    </header>

    <div class="container">
        <div class="player-header">
            <div class="player-name">サンプル選手</div>
            <div class="player-name-en">Sample Player</div>
        </div>

        <h2 class="section-title">基本情報</h2>
        <div class="info-grid">
            <div class="info-card">
                <div class="info-label">生年月日</div>
                <div class="info-value">1995.01.15</div>
            </div>
            <div class="info-card">
                <div class="info-label">年齢</div>
                <div class="info-value">31歳</div>
            </div>
            <div class="info-card">
                <div class="info-label">国籍</div>
                <div class="info-value">日本</div>
            </div>
            <div class="info-card">
                <div class="info-label">出身</div>
                <div class="info-value">ニュージーランド</div>
            </div>
        </div>

        <div class="info-grid">
            <div class="info-card">
                <div class="info-label">高校</div>
                <div class="info-value"><a href="#">サンプル高校</a></div>
            </div>
            <div class="info-card">
                <div class="info-label">大学</div>
                <div class="info-value"><a href="#">サンプル大学</a></div>
            </div>
            <div class="info-card">
                <div class="info-label">リーグキャップ数</div>
                <div class="info-value">45</div>
            </div>
            <div class="info-card">
                <div class="info-label">代表歴</div>
                <div class="info-value">日本代表 15cap</div>
            </div>
        </div>

        <h2 class="section-title">所属チーム</h2>
        <div class="info-card">
            <div class="info-value"><a href="#">サンプルチーム</a></div>
        </div>

        <p style="margin-top: 40px; text-align: center; color: #888;">
            League: {league_name}<br>
            Colors: {primary} / {secondary}
        </p>
    </div>
</body>
</html>"""
    
    os.makedirs(output_dir, exist_ok=True)
    slug = slugify(league_name)
    filename = f"{output_dir}/player_{slug}_sample.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filename

def generate_team_sample(league_name, output_dir='sample_pages'):
    """Generate a sample team page with league-specific colors"""
    
    colors = get_league_colors(league_name)
    primary = colors.get('primary', '#0097B2')
    secondary = colors.get('secondary', '#00b8d4')
    
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample Team | {league_name} | RugbyPick</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Noto Sans JP', sans-serif;
            background-color: #ffffff;
            color: #484848;
            font-size: 18px;
            line-height: 1.6;
        }}
        .header-container {{
            background-color: {primary};
            padding: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        .site-title {{
            color: #ffffff;
            font-size: 24px;
            font-weight: 700;
            text-decoration: none;
        }}
        .container {{
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
        }}
        .team-header {{
            background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
            color: #ffffff;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .team-name {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .section-title {{
            font-size: 24px;
            font-weight: 700;
            color: {primary};
            margin: 40px 0 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid {primary};
        }}
        .player-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }}
        .player-card {{
            background: #f8f8f8;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid {primary};
        }}
        .player-card a {{
            color: {primary};
            text-decoration: none;
            font-weight: 700;
        }}
    </style>
</head>
<body>
    <header class="header-container">
        <div class="header-content">
            <a href="../../index.html" class="site-title">RugbyPick</a>
        </div>
    </header>

    <div class="container">
        <div class="team-header">
            <div class="team-name">サンプルチーム</div>
            <div>League: {league_name}</div>
        </div>

        <h2 class="section-title">所属選手</h2>
        <div class="player-grid">
            <div class="player-card">
                <a href="#">選手A (FW)</a>
            </div>
            <div class="player-card">
                <a href="#">選手B (BK)</a>
            </div>
            <div class="player-card">
                <a href="#">選手C (FW)</a>
            </div>
        </div>

        <p style="margin-top: 40px; text-align: center; color: #888;">
            League: {league_name}<br>
            Colors: {primary} / {secondary}
        </p>
    </div>
</body>
</html>"""
    
    os.makedirs(output_dir, exist_ok=True)
    slug = slugify(league_name)
    filename = f"{output_dir}/team_{slug}_sample.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filename

def main():
    print("=== Multi-League Sample Generator (All 12 Leagues) ===\n")
    
    # Load all leagues
    with open('data/rugby_leagues.json', 'r') as f:
        leagues = json.load(f)
    
    # Load league colors
    with open('league_colors.json', 'r') as f:
        league_colors = json.load(f)
    
    print(f"Total leagues: {len(leagues)}")
    print(f"Color schemes defined: {len(league_colors)}\n")
    
    generated_players = []
    generated_teams = []
    
    # Generate samples for each league
    for league in leagues:
        league_name = league.get('name', 'Unknown')
        print(f"Generating samples for: {league_name}")
        
        # Generate player sample
        player_file = generate_player_sample(league_name)
        generated_players.append(player_file)
        print(f"  ✓ Player: {player_file}")
        
        # Generate team sample
        team_file = generate_team_sample(league_name)
        generated_teams.append(team_file)
        print(f"  ✓ Team: {team_file}\n")
    
    print(f"\n=== Generation Complete ===")
    print(f"Player samples: {len(generated_players)}")
    print(f"Team samples: {len(generated_teams)}")
    print(f"Total: {len(generated_players) + len(generated_teams)} files")

if __name__ == "__main__":
    main()
