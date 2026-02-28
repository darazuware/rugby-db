import requests
from bs4 import BeautifulSoup
import json
import re

class TeamColorScraper:
    """Scrape team colors from official websites"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # League One teams
        self.leagues_to_scrape = {
            'League One': [
                {'name': 'クボタスピアーズ船橋・東京ベイ', 'url': 'https://www.kubota-spears.com/'},
                {'name': '東京サントリーサンゴリアス', 'url': 'https://www.suntory.co.jp/culture-sports/sungoliath/'},
                {'name': '埼玉パナソニックワイルドナイツ', 'url': 'https://panasonic.co.jp/sports/rugby/'},
                {'name': '東芝ブレイブルーパス東京', 'url': 'https://www.bravelupus.com/'},
                {'name': '横浜キヤノンイーグルス', 'url': 'https://www.canon-eagles.jp/'},
                {'name': 'トヨタヴェルブリッツ', 'url': 'https://sports.gazoo.com/verblitz/'},
                {'name': '静岡ブルーレヴズ', 'url': 'https://www.shizuoka-bluerevs.com/'},
                {'name': 'コベルコ神戸スティーラーズ', 'url': 'https://www.kobelcosteelers.com/'},
                {'name': '花園近鉄ライナーズ', 'url': 'https://www.kintetsu-liners.com/'},
                {'name': '三重ホンダヒート', 'url': 'https://www.honda-heat.jp/'},
                {'name': '日野レッドドルフィンズ', 'url': 'https://hino-reddolphins.com/'},
                {'name': '九州電力キューデンヴォルテクス', 'url': 'https://www.kyuden.co.jp/kyuden-vortex/'}
            ],
            'Top 14': [
                {'name': 'Stade Toulousain', 'url': 'https://www.stadetoulousain.fr/'},
                {'name': 'Stade Rochelais', 'url': 'https://www.staderochelais.com/'},
                {'name': 'Union Bordeaux Bègles', 'url': 'https://www.ubbrugby.com/'},
                {'name': 'ASM Clermont Auvergne', 'url': 'https://www.asm-rugby.com/'}
            ],
            'Super Rugby': [
                {'name': 'Blues', 'url': 'https://www.blues.rugby/'},
                {'name': 'Crusaders', 'url': 'https://crusaders.co.nz/'},
                {'name': 'Chiefs', 'url': 'https://www.chiefs.co.nz/'}
            ]
        }
    
    def extract_colors_from_css(self, url):
        """Extract colors from website CSS"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            colors = set()
            
            # Extract from inline styles
            for element in soup.find_all(style=True):
                style = element['style']
                hex_colors = re.findall(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})', style)
                colors.update([f'#{c.lower()}' for c in hex_colors])
            
            # Extract from CSS links
            for link in soup.find_all('link', rel='stylesheet'):
                css_url = link.get('href')
                if css_url:
                    if not css_url.startswith('http'):
                        from urllib.parse import urljoin
                        css_url = urljoin(url, css_url)
                    
                    try:
                        css_response = requests.get(css_url, headers=self.headers, timeout=5)
                        hex_colors = re.findall(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})', css_response.text)
                        colors.update([f'#{c.lower()}' for c in hex_colors])
                    except:
                        pass
            
            # Filter out common colors
            filtered = []
            exclude = ['#fff', '#ffffff', '#000', '#000000', '#ccc', '#cccccc', '#ddd', '#dddddd', 
                      '#eee', '#eeeeee', '#f0f0f0', '#f5f5f5', '#fafafa']
            
            for color in colors:
                if color not in exclude and len(color) == 7:  # Only 6-digit hex
                    filtered.append(color)
            
            return list(set(filtered))[:10]  # Top 10 unique colors
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []
    
    def scrape_all_teams(self):
        """Scrape colors for all teams in specified leagues"""
        results = []
        
        for league, teams in self.leagues_to_scrape.items():
            print(f"=== Scraping {league} Team Colors ===\n")
            for team in teams:
                print(f"Scraping {team['name']}...")
                colors = self.extract_colors_from_css(team['url'])
                
                result = {
                    'league': league,
                    'name': team['name'],
                    'url': team['url'],
                    'colors': colors,
                    'primary': colors[0] if colors else None,
                    'secondary': colors[1] if len(colors) > 1 else None
                }
                
                results.append(result)
                print(f"  Found {len(colors)} colors: {colors[:3]}")
        
        return results
    
    def generate_html_preview(self, results, output_file='team_colors_preview.html'):
        """Generate HTML preview for visual verification"""
        
        html = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>チームカラー確認</title>
    <style>
        body {
            font-family: 'Hiragino Sans', 'Noto Sans JP', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .team-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .team-name {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .team-url {
            font-size: 12px;
            color: #666;
            margin-bottom: 15px;
        }
        .color-palette {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .color-box {
            width: 80px;
            height: 80px;
            border-radius: 4px;
            border: 1px solid #ddd;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            padding: 5px;
            font-size: 11px;
            color: white;
            text-shadow: 0 0 3px rgba(0,0,0,0.5);
        }
        .primary-label, .secondary-label {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 10px;
            margin-left: 10px;
        }
        .primary-label {
            background: #e60012;
            color: white;
        }
        .secondary-label {
            background: #0066cc;
            color: white;
        }
        .edit-section {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
        .edit-input {
            width: 100px;
            padding: 5px;
            border: 1px solid #ddd;
            border-radius: 3px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <h1>🎨 チームカラー確認ページ</h1>
    <p style="text-align: center; color: #666;">
        各チームのカラーを確認し、必要に応じて修正してください。<br>
        Primary（メイン）とSecondary（サブ）を選択してください。
    </p>
"""
        
        for team in results:
            html += f"""
    <div class="team-card">
        <div class="team-name">{team['name']}</div>
        <div class="team-url">{team['url']}</div>
        <div class="color-palette">
"""
            
            for i, color in enumerate(team['colors']):
                label = ''
                if i == 0:
                    label = '<span class="primary-label">Primary</span>'
                elif i == 1:
                    label = '<span class="secondary-label">Secondary</span>'
                
                html += f"""
            <div class="color-box" style="background-color: {color};">
                {color}{label}
            </div>
"""
            
            html += """
        </div>
        <div class="edit-section">
            <label>Primary: <input type="text" class="edit-input" value="{}" placeholder="#e95506"></label>
            <label style="margin-left: 20px;">Secondary: <input type="text" class="edit-input" value="{}" placeholder="#12aaab"></label>
        </div>
    </div>
""".format(team['primary'] or '', team['secondary'] or '')
        
        html += """
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_file

def main():
    scraper = TeamColorScraper()
    
    # Scrape all teams
    results = scraper.scrape_all_teams()
    
    # Save raw data
    with open('team_colors_raw.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Generate HTML preview
    html_file = scraper.generate_html_preview(results)
    
    print(f"\n=== Complete ===")
    print(f"Raw data: team_colors_raw.json")
    print(f"HTML preview: {html_file}")
    print(f"\nPlease open {html_file} in your browser to verify colors.")

if __name__ == "__main__":
    main()
