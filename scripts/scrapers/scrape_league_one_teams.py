import requests
from bs4 import BeautifulSoup
import json
import time
import re

# League One team IDs (from league-one.jp)
# Division 1: 98-109, Division 2: 110-115, Division 3: 116-121
TEAM_IDS = list(range(98, 122))  # All League One teams

BASE_URL = "https://league-one.jp/team/{}?t1=2"

def scrape_team_details(team_id):
    """Scrape detailed team information from league-one.jp"""
    url = BASE_URL.format(team_id)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        team_data = {
            'team_id': team_id,
            'url': url,
            'team_name': None,
            'legal_entity': None,
            'entity_address': None,
            'official_name': None,
            'nickname': None,
            'host_area': None,
            'practice_ground': None,
            'official_site': None,
            'division': None
        }
        
        # Extract team name from page title or header
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            team_data['team_name'] = title_tag.get_text(strip=True).split('|')[0].strip()
        
        # Find all definition lists (dl tags) which contain team info
        dl_elements = soup.find_all('dl')
        
        for dl in dl_elements:
            dt_elements = dl.find_all('dt')
            dd_elements = dl.find_all('dd')
            
            for dt, dd in zip(dt_elements, dd_elements):
                label = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                
                if '法人名' in label or '組織名' in label:
                    team_data['legal_entity'] = value
                elif '法人・組織所在地' in label:
                    team_data['entity_address'] = value
                elif '公式チーム名称' in label:
                    team_data['official_name'] = value
                elif '呼称' in label:
                    team_data['nickname'] = value
                elif 'ホストエリア' in label:
                    team_data['host_area'] = value
                elif '練習グラウンド' in label:
                    team_data['practice_ground'] = value
                elif '公式サイト' in label:
                    # Extract URL from link
                    link = dd.find('a')
                    if link and link.get('href'):
                        team_data['official_site'] = link.get('href')
                    else:
                        team_data['official_site'] = value
        
        # Determine division from team_id
        if 98 <= team_id <= 109:
            team_data['division'] = 'Division 1'
        elif 110 <= team_id <= 115:
            team_data['division'] = 'Division 2'
        elif 116 <= team_id <= 121:
            team_data['division'] = 'Division 3'
        
        print(f"✓ Scraped: {team_data['team_name']} (ID: {team_id})")
        return team_data
        
    except Exception as e:
        print(f"✗ Error scraping team {team_id}: {e}")
        return None

def main():
    print("Starting League One team scraper...")
    print(f"Target: {len(TEAM_IDS)} teams\n")
    
    teams = []
    
    for team_id in TEAM_IDS:
        team_data = scrape_team_details(team_id)
        if team_data:
            teams.append(team_data)
        
        # Rate limiting
        time.sleep(1.5)
    
    # Save to JSON
    output_file = 'league_one_teams_detailed.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Scraping complete!")
    print(f"✓ Saved {len(teams)} teams to {output_file}")
    
    # Print summary
    div1 = sum(1 for t in teams if t.get('division') == 'Division 1')
    div2 = sum(1 for t in teams if t.get('division') == 'Division 2')
    div3 = sum(1 for t in teams if t.get('division') == 'Division 3')
    
    print(f"\nSummary:")
    print(f"  Division 1: {div1} teams")
    print(f"  Division 2: {div2} teams")
    print(f"  Division 3: {div3} teams")

if __name__ == "__main__":
    main()
