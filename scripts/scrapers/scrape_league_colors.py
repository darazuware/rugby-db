import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin

def extract_colors_from_css(css_text):
    """Extract color codes from CSS text"""
    colors = set()
    
    # Find hex colors
    hex_colors = re.findall(r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b', css_text)
    for color in hex_colors:
        if len(color) == 3:
            # Convert 3-digit to 6-digit
            color = ''.join([c*2 for c in color])
        colors.add(f'#{color.upper()}')
    
    # Find rgb/rgba colors
    rgb_colors = re.findall(r'rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', css_text)
    for r, g, b in rgb_colors:
        # Convert to hex
        hex_color = f'#{int(r):02X}{int(g):02X}{int(b):02X}'
        colors.add(hex_color)
    
    return list(colors)

def scrape_league_colors(league_name, league_url):
    """Scrape brand colors from a league's official website"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        print(f"\nScraping {league_name}...")
        print(f"  URL: {league_url}")
        
        response = requests.get(league_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        colors = set()
        
        # Extract colors from inline styles
        elements_with_style = soup.find_all(style=True)
        for elem in elements_with_style[:50]:  # Limit to first 50
            style = elem.get('style', '')
            extracted = extract_colors_from_css(style)
            colors.update(extracted)
        
        # Extract colors from linked CSS files
        css_links = soup.find_all('link', rel='stylesheet')
        for link in css_links[:3]:  # Check first 3 CSS files
            css_url = link.get('href')
            if css_url:
                if not css_url.startswith('http'):
                    css_url = urljoin(league_url, css_url)
                
                try:
                    css_response = requests.get(css_url, headers=headers, timeout=5)
                    extracted = extract_colors_from_css(css_response.text[:50000])  # First 50KB
                    colors.update(extracted)
                except:
                    pass
        
        # Filter out common colors (white, black, gray)
        filtered_colors = []
        for color in colors:
            # Skip very light colors (near white)
            if color.upper() in ['#FFFFFF', '#FFF', '#FEFEFE', '#FDFDFD']:
                continue
            # Skip very dark colors (near black) unless it's pure black
            if color.upper() not in ['#000000', '#000'] and all(int(color[i:i+2], 16) < 20 for i in (1, 3, 5)):
                continue
            filtered_colors.append(color)
        
        print(f"  ✓ Found {len(filtered_colors)} colors")
        return list(set(filtered_colors))[:5]  # Return top 5 unique colors
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []

def main():
    print("=== League Color Scraper ===\n")
    
    # Define leagues with their official websites
    leagues = {
        'League One': {
            'url': 'https://league-one.jp/',
            'known_colors': ['#E60012', '#000000']  # Red, Black
        },
        'Super Rugby': {
            'url': 'https://www.superrugby.co.nz/',
            'known_colors': ['#0066CC', '#00BFFF', '#FFFFFF']  # Blue, Light Blue, White
        },
        'Top 14': {
            'url': 'https://www.lnr.fr/top-14',
            'known_colors': ['#000000', '#FFD700']  # Black, Gold
        },
        'Premiership Rugby': {
            'url': 'https://www.premiershiprugby.com/',
            'known_colors': ['#FF6600', '#000000']  # Orange, Black
        },
        'United Rugby Championship': {
            'url': 'https://www.unitedrugby.com/',
            'known_colors': []
        },
        'Currie Cup': {
            'url': 'https://www.sarugby.co.za/currie-cup/',
            'known_colors': []
        },
        'MLR': {
            'url': 'https://www.majorleague.rugby/',
            'known_colors': []
        }
    }
    
    league_colors = {}
    
    for league_name, league_info in leagues.items():
        scraped_colors = scrape_league_colors(league_name, league_info['url'])
        
        # Use known colors if scraping failed or found too few
        if len(scraped_colors) < 2 and league_info['known_colors']:
            colors = league_info['known_colors']
            print(f"  → Using known colors: {colors}")
        else:
            colors = scraped_colors if scraped_colors else league_info['known_colors']
        
        league_colors[league_name] = {
            'primary': colors[0] if len(colors) > 0 else '#0097B2',
            'secondary': colors[1] if len(colors) > 1 else '#00b8d4',
            'accent': colors[2] if len(colors) > 2 else '#FFFFFF',
            'all_colors': colors
        }
    
    # Save to JSON
    output_file = 'league_colors.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(league_colors, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved league colors to {output_file}")
    
    # Print summary
    print("\n=== Color Summary ===")
    for league, colors in league_colors.items():
        print(f"\n{league}:")
        print(f"  Primary: {colors['primary']}")
        print(f"  Secondary: {colors['secondary']}")
        print(f"  Accent: {colors['accent']}")

if __name__ == "__main__":
    main()
