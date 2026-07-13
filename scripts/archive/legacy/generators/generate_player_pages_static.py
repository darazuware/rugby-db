import os
import re

# Configuration
PLAYER_MD_DIR = 'data/players'
OUTPUT_DIR = 'dist/player'
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
        .container { max-width: 900px; margin: 40px auto; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h1 { font-size: 32px; color: #333; margin-bottom: 20px; border-bottom: 3px solid #0097B2; padding-bottom: 10px; }
        h3 { font-size: 20px; color: #0097B2; margin: 30px 0 15px; border-left: 5px solid #0097B2; padding-left: 15px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { padding: 12px 15px; border-bottom: 1px solid #eee; text-align: left; }
        th { background: #f9f9f9; width: 30%; font-weight: 700; }
        a { color: #0097B2; text-decoration: none; }
        a:hover { text-decoration: underline; }
        ul { list-style: none; }
        li { margin-bottom: 10px; padding-left: 20px; position: relative; }
        li::before { content: "•"; color: #0097B2; font-weight: bold; position: absolute; left: 0; }
        footer { text-align: center; padding: 40px; color: #888; font-size: 13px; }
    </style>
"""

def get_nav():
    logo_path = "../images/logo.png"
    logo_img = f'<img src="{logo_path}" alt="RugbyPick" style="height:40px; vertical-align:middle;">'
    return f"""
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
    """

def parse_frontmatter(content):
    parts = re.split(r'^---\s*$', content, flags=re.MULTILINE)
    data = {}
    body = content
    if len(parts) >= 3:
        fm_text = parts[1].strip()
        body = parts[2].strip()
        for line in fm_text.split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                data[key.strip()] = val.strip().strip('"').strip("'")
    return data, body

def md_to_html(md_content):
    try:
        import markdown
        extensions = ['tables', 'fenced_code', 'nl2br']
        return markdown.markdown(md_content, extensions=extensions)
    except ImportError:
        # Improved fallback basic conversion
        lines = md_content.split('\n')
        html_lines = []
        in_table = False
        for line in lines:
            line = line.strip()
            # Handle Bold
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            # Handle Links
            line = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', line)

            if line.startswith('|'):
                if not in_table:
                    html_lines.append('<table>')
                    in_table = True
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if cells and not re.match(r'^[\-\s:|]+$', line):
                    # Check if it's the first row and make it <th> if needed, 
                    # but here we'll just do <tr><td> for simplicity
                    html_lines.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
            else:
                if in_table:
                    html_lines.append('</table>')
                    in_table = False
                
                if line.startswith('### '):
                    html_lines.append(f'<h3>{line[4:]}</h3>')
                elif line.startswith('- '):
                    html_lines.append(f'<li>{line[2:]}</li>')
                elif line:
                    html_lines.append(f'<p>{line}</p>')
        if in_table: html_lines.append('</table>')
        return '\n'.join(html_lines)

def generate_player_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    frontmatter, body_md = parse_frontmatter(content)
    title = frontmatter.get('title', '選手プロフィール')
    body_html = md_to_html(body_md)
    
    # Assembly
    full_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | RugbyPick</title>
    {COMMON_CSS}
</head>
<body>
    {get_nav()}
    <div class="container">
        <h1>{title}</h1>
        {body_html}
    </div>
    <footer>
        &copy; 2026 RugbyPick. All Rights Reserved.
    </footer>
</body>
</html>"""

    slug = frontmatter.get('slug', os.path.basename(file_path).replace('.md', ''))
    output_path = os.path.join(OUTPUT_DIR, f"{slug}.html")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    return output_path

def main():
    print("Starting Static Player Page Generation...")
    md_files = [f for f in os.listdir(PLAYER_MD_DIR) if f.endswith('.md')]
    
    success_count = 0
    for md_file in md_files:
        try:
            path = os.path.join(PLAYER_MD_DIR, md_file)
            generate_player_html(path)
            success_count += 1
            if success_count % 100 == 0:
                print(f"Generated {success_count} pages...")
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
            
    print(f"✓ Successfully generated {success_count} static player pages in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
