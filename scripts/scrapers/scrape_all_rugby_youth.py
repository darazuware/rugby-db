import json
import requests
import time
import re
from bs4 import BeautifulSoup
import random

# Input/Output
INPUT_DB = 'data/unified_player_database_final.json'
OUTPUT_FILE = 'foreign_youth_data.json'

def get_all_rugby_id(player):
    # Try to find ID or URL
    # We might need to SEARCH All.Rugby if not already linked
    # But for now, let's assume we can only enrich those we found before?
    # Actually, many foreigners might not have IDs yet.
    # Let's rely on 'all_rugby_id' if present, or search.
    return player.get('all_rugby_id')

def scrape_youth_stats(player_id):
    # https://www.all.rugby/player/{id}
    url = f"https://www.all.rugby/player/{player_id}"
    youth_vals = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200: return []
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Look for U20 in the stats table
        # Usually in "International" tab or main summary
        # Let's search for "U20" text in tables
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                text = row.get_text()
                if "U20" in text:
                    # Found a U20 row, let's extract team name
                    # e.g. "New Zealand U20", "Australia U20"
                    cols = row.find_all('td')
                    if cols and len(cols) > 0:
                        team_name = cols[0].get_text().strip()
                        if "U20" in team_name and team_name not in youth_vals:
                            youth_vals.append(team_name)
    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        
    return youth_vals

def main():
    print("Loading player database...")
    with open(INPUT_DB, 'r', encoding='utf-8') as f:
        players = json.load(f)
    
    youth_data = {}
    
    # Try load existing
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            youth_data = json.load(f)
    except:
        pass

    targets = []
    for p in players:
        # Filter for likely foreign players (Category B/C or Katakana name with no JP school)
        cat = p.get('category', '')
        name_ja = p.get('name_ja', '')
        
        is_foreign = False
        if cat in ['B', 'C']: 
            is_foreign = True
        elif name_ja and '・' in name_ja and not p.get('high_school'): 
            is_foreign = True
        
        if is_foreign and p.get('all_rugby_id'):
            targets.append(p)
            
    print(f"Found {len(targets)} target foreign players with All.Rugby IDs.")
    
    count = 0
    for p in targets:
        pid = str(p['id'])
        ar_id = p.get('all_rugby_id')
        
        if pid in youth_data: continue
        
        print(f"[{count}/{len(targets)}] Scraping Youth Stats for: {p['name_en']} (ID: {ar_id})")
        
        u20_teams = scrape_youth_stats(ar_id)
        
        if u20_teams:
            print(f"  -> Found: {u20_teams}")
            youth_data[pid] = {
                'u20_teams': u20_teams
            }
        else:
            print("  -> No U20 data found.")
            youth_data[pid] = {'no_data': True}
            
        if count % 10 == 0:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(youth_data, f, ensure_ascii=False, indent=2)
                
        count += 1
        time.sleep(random.uniform(1.0, 2.0))

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(youth_data, f, ensure_ascii=False, indent=2)
        
    print("Foreign Youth Scrape Complete.")

if __name__ == "__main__":
    main()
