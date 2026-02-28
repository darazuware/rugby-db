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
        # Default colors if file not found
        return {
            'primary': '#0097B2',
            'secondary': '#00b8d4',
            'accent': '#FFFFFF'
        }
    
    # Match league name (case-insensitive, partial match)
    league_lower = league_name.lower() if league_name else ''
    
    for key, colors in league_colors.items():
        if key.lower() in league_lower or league_lower in key.lower():
            return colors
    
    # League-specific overrides based on known patterns
    if 'league one' in league_lower or 'リーグワン' in league_lower:
        return league_colors.get('League One', league_colors.get('League One', {}))
    elif 'super rugby' in league_lower:
        return league_colors.get('Super Rugby', {})
    elif 'top 14' in league_lower or 'top14' in league_lower:
        return league_colors.get('Top 14', {})
    elif 'premiership' in league_lower or 'prem' in league_lower:
        return league_colors.get('Premiership Rugby', {})
    elif 'urc' in league_lower or 'united rugby' in league_lower:
        return league_colors.get('United Rugby Championship', {})
    elif 'currie' in league_lower:
        return league_colors.get('Currie Cup', {})
    elif 'mlr' in league_lower or 'major league' in league_lower:
        return league_colors.get('MLR', {})
    
    # Default
    return {
        'primary': '#0097B2',
        'secondary': '#00b8d4',
        'accent': '#FFFFFF'
    }

def generate_league_sample_page(league_data, output_dir='sample_pages'):
    """Generate a sample league page with league-specific colors"""
    
    league_name = league_data.get('name', 'Unknown League')
    slug = slugify(league_name)
    colors = get_league_colors(league_name)
    
    primary = colors.get('primary', '#0097B2')
    secondary = colors.get('secondary', '#00b8d4')
    
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{league_name} | RugbyPick</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
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
        .nav-container {{
            background-color: {primary};
            border-top: 1px solid rgba(255,255,255,0.2);
        }}
        .nav-menu {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            gap: 30px;
            list-style: none;
        }}
        .nav-menu a {{
            color: #ffffff;
            text-decoration: none;
            font-size: 14px;
            padding: 12px 0;
            display: block;
        }}
        .container {{
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
        }}
        .league-header {{
            background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
            color: #ffffff;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .league-name {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .league-info {{
            font-size: 18px;
            opacity: 0.9;
        }}
        .section-title {{
            font-size: 24px;
            font-weight: 700;
            color: {primary};
            margin: 40px 0 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid {primary};
        }}
        .team-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .team-card {{
            background: #f8f8f8;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid {primary};
            transition: transform 0.2s;
        }}
        .team-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .team-name {{
            font-size: 20px;
            font-weight: 700;
            color: {primary};
            margin-bottom: 10px;
        }}
        .team-name a {{
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
    <nav class="nav-container">
        <ul class="nav-menu">
            <li><a href="../../index.html">ホーム</a></li>
            <li><a href="../leagues.html">リーグ一覧</a></li>
            <li><a href="../teams.html">チーム一覧</a></li>
            <li><a href="../players.html">選手一覧</a></li>
        </ul>
    </nav>

    <div class="container">
        <div class="league-header">
            <div class="league-name">{league_name}</div>
            <div class="league-info">League Color Scheme: {primary} / {secondary}</div>
        </div>

        <h2 class="section-title">参加チーム</h2>
        <div class="team-grid">
            <div class="team-card">
                <div class="team-name"><a href="#">Sample Team 1</a></div>
                <p>チーム情報がここに表示されます</p>
            </div>
            <div class="team-card">
                <div class="team-name"><a href="#">Sample Team 2</a></div>
                <p>チーム情報がここに表示されます</p>
            </div>
            <div class="team-card">
                <div class="team-name"><a href="#">Sample Team 3</a></div>
                <p>チーム情報がここに表示されます</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    # Save file
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/league_{slug}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filename

def main():
    print("=== Multi-League Sample Page Generator ===\n")
    
    # Load leagues
    with open('data/rugby_leagues.json', 'r') as f:
        leagues = json.load(f)
    
    print(f"Found {len(leagues)} leagues\n")
    
    # Generate sample pages for major leagues
    major_leagues = [
        'League One',
        'Super Rugby',
        'Top 14',
        'Premiership Rugby',
        'United Rugby Championship'
    ]
    
    generated = []
    
    for league in leagues:
        league_name = league.get('name', '')
        
        # Check if it's a major league
        is_major = any(major in league_name for major in major_leagues)
        
        if is_major:
            print(f"Generating sample page for: {league_name}")
            filename = generate_league_sample_page(league)
            generated.append(filename)
            print(f"  ✓ Saved to: {filename}\n")
    
    print(f"\n✓ Generated {len(generated)} sample league pages")
    for f in generated:
        print(f"  - {f}")

if __name__ == "__main__":
    main()
