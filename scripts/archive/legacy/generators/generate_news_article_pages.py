import os
import json
from datetime import datetime
import re

# Configuration
RECOVERED_DIR = 'data/recovered_articles'
OUTPUT_BASE = 'dist'
CATEGORIES = {
    'high-school': {
        'path': 'news/domestic/high-school',
        'keywords': ['hanazono', 'high-school', '高校', '花園'],
        'title': '高校ラグビー'
    },
    'university': {
        'path': 'news/domestic/university',
        'keywords': ['university', '大学'],
        'title': '大学ラグビー'
    },
    'watch-guide': {
        'path': 'news/arekore/watch-guide',
        'keywords': ['wowow', 'dazn', '放送', 'jsports'],
        'title': '観戦ガイド'
    },
    'league-one': {
        'path': 'news/domestic/leagueone/news',
        'keywords': ['leagueone', 'リーグワン'],
        'title': 'リーグワンニュース'
    }
}

# Simple Template mimicking Cocoon
TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | RUGBY PICKS</title>
    {canonical_url}
    <link rel="stylesheet" href="{rel_path}css/style.css">
    <link rel="stylesheet" href="{rel_path}css/cocoon-style.css"> <!-- New Stylsheet -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        /* Minimal Cocoon-like override if CSS fails load */
        body {{ font-family: 'Noto Sans JP', sans-serif; background-color: #f5f7f9; color: #484848; line-height: 1.6; }}
        .header-container {{ background-color: #0097B2; padding: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header-content {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; text-align: center; }}
        .site-title {{ color: white; text-decoration: none; font-size: 24px; font-weight: 700; }}
        .nav-container {{ background-color: #007A8F; padding: 10px 0; position: sticky; top: 0; z-index: 100; }}
        .nav-menu {{ display: flex; justify-content: center; list-style: none; gap: 30px; }}
        .nav-menu a {{ color: white; text-decoration: none; font-weight: 700; font-size: 15px; }}
        .container {{ max-width: 1024px; margin: 20px auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        .entry-title {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #0097B2; padding-bottom: 10px; }}
        .post-date {{ color: #888; font-size: 14px; margin-bottom: 20px; display: block; }}
        .entry-content h2 {{ background: #f3f4f5; padding: 10px; border-left: 5px solid #0097B2; font-size: 20px; margin-top: 30px; }}
        .entry-content h3 {{ border-bottom: 2px solid #ddd; padding-bottom: 5px; font-size: 18px; margin-top: 25px; }}
        .toc {{ background: #f9f9f9; border: 1px solid #ddd; padding: 15px; margin: 20px 0; }}
        .bold {{ font-weight: bold; }}
        .marker-yellow {{ background: linear-gradient(transparent 60%, #ffff66 60%); }}
        .blog-card {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; display: flex; align-items: center; }}
        .blog-card img {{ width: 100px; height: 75px; object-fit: cover; margin-right: 15px; }}
    </style>
</head>
<body>
    <header class="header-container">
        <div class="header-content">
            <a href="{rel_path}index.html" class="site-title">RUGBY PICKS</a>
        </div>
    </header>
    <nav class="nav-container">
        <ul class="nav-menu">
            <li><a href="{rel_path}index.html">ホーム</a></li>
            <li><a href="{rel_path}pages/leagues.html">リーグ一覧</a></li>
            <li><a href="{rel_path}pages/teams.html">チーム一覧</a></li>
            <li><a href="{rel_path}pages/players.html">選手一覧</a></li>
        </ul>
    </nav>

    <div class="container">
        <article>
            <h1 class="entry-title">{title}</h1>
            <span class="post-date">{date}</span>
            <div class="entry-content">
                {content}
            </div>
        </article>
    </div>

    <footer style="text-align:center; padding: 20px; color: #666; font-size: 12px;">
        &copy; 2026 RUGBY PICKS
    </footer>
</body>
</html>
"""

def parse_frontmatter(content):
    match = re.search(r'---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        body = match.group(2)
        meta = {}
        for line in fm_text.splitlines():
            if ':' in line:
                key, val = line.split(':', 1)
                meta[key.strip()] = val.strip()
        return meta, body
    return {}, content

def generate_news_pages():
    files = [f for f in os.listdir(RECOVERED_DIR) if f.endswith('.html')]
    
    for filename in files:
        filepath = os.path.join(RECOVERED_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_content = f.read()
            
        meta, body = parse_frontmatter(raw_content)
        title = meta.get('title', 'No Title')
        date = meta.get('date', 'Unknown Date')
        original_url = meta.get('url', '')
        
        # Categorize
        category = 'category/domestic/news' # Default
        cat_title = 'News'
        
        # Heuristic Categorization
        slug = filename.replace('.html', '')
        found_cat = False
        
        # 1. Check URL path
        if 'domestic/high-school' in original_url:
            category = CATEGORIES['high-school']['path']
            cat_title = CATEGORIES['high-school']['title']
            found_cat = True
        elif 'domestic/university' in original_url:
            category = CATEGORIES['university']['path']
            cat_title = CATEGORIES['university']['title']
            found_cat = True
        elif 'overseas' in original_url or 'watch-guide' in filename or 'wowow' in filename:
             category = CATEGORIES['watch-guide']['path']
             cat_title = CATEGORIES['watch-guide']['title']
             found_cat = True
        elif 'domestic/leagueone' in original_url:
             category = CATEGORIES['league-one']['path']
             cat_title = CATEGORIES['league-one']['title']
             found_cat = True

        # 2. Check content/filename if URL check failed
        if not found_cat:
            for cat_key, cat_data in CATEGORIES.items():
                for kw in cat_data['keywords']:
                    if kw in slug or kw in title or kw in body:
                        category = cat_data['path']
                        cat_title = cat_data['title']
                        found_cat = True
                        break
                if found_cat: break

        # Output Path
        out_dir = os.path.join(OUTPUT_BASE, category)
        os.makedirs(out_dir, exist_ok=True)
        
        # Filename: Match URL structure if possible, else use slug
        out_file = os.path.join(out_dir, filename)
        
        
        # depth = news/domestic/leagueone/news -> 4 parts -> 4 levels deep from dist
        depth = len(category.split('/'))
        rel_path = "../" * depth
        
        # Build canonical tag
        if original_url:
            clean_url = original_url.replace('https://rugbypick.com/', '').strip('/')
            canonical_tag = f'<link rel="canonical" href="https://rugbypick.com/{clean_url}/">'
        else:
            canonical_tag = f'<link rel="canonical" href="https://rugbypick.com/{category}/{filename.replace(".html", "")}/">'
        
        html = TEMPLATE.format(
            title=title, 
            date=date, 
            content=body, 
            rel_path=rel_path,
            canonical_url=canonical_tag
        )
        
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(html)
            
        print(f"Generated: {out_file} ({cat_title})")

    # Generate Index Pages for Categories
    # Group files by category
    cat_files = {k: [] for k in CATEGORIES.keys()}
    
    # scan generated files? or reuse the loop? 
    # We didn't store mapping. Let's rescan output dir or refactor.
    # Easier to just scan content of OUTPUT_BASE
    
    for cat_key, cat_data in CATEGORIES.items():
        cat_path = cat_data['path']
        full_dir = os.path.join(OUTPUT_BASE, cat_path)
        if not os.path.exists(full_dir): continue
        
        articles = []
        for f in os.listdir(full_dir):
            if f.endswith('.html') and f != 'index.html':
                # Read title/date for list
                with open(os.path.join(full_dir, f), 'r', encoding='utf-8') as af:
                    acontent = af.read()
                    match = re.search(r'<title>(.*?) \|', acontent)
                    atitle = match.group(1) if match else f
                    # Date?
                    # Try to regex date? <span class="post-date">(.*?)</span>
                    dmatch = re.search(r'<span class="post-date">(.*?)</span>', acontent)
                    adate = dmatch.group(1) if dmatch else ''
                    articles.append({'file': f, 'title': atitle, 'date': adate})
        
        # Sort by date (desc) - formatting might be inconsistent but string sort is better than nothing
        articles.sort(key=lambda x: x['date'], reverse=True)
        
        # Generate Index HTML
        list_html = ""
        for a in articles:
            list_html += f'<div class="blog-card"><div class="blog-card-content"><div class="blog-card-snippet">{a["date"]}</div><a href="{a["file"]}" class="blog-card-title">{a["title"]}</a></div></div>'
            
        depth = len(cat_path.split('/'))
        rel_root = "../" * depth
        
        index_html = TEMPLATE.format(
            title=cat_data['title'],
            date=datetime.now().strftime('%Y.%m.%d'),
            content=f'<h2>記事一覧</h2>{list_html}',
            rel_path=rel_root,
            canonical_url=f'<link rel="canonical" href="https://rugbypick.com/{cat_path}/">'
        )
        
        with open(os.path.join(full_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(index_html)
        print(f"Generated Index: {full_dir}/index.html")

if __name__ == "__main__":
    generate_news_pages()
