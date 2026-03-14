import csv
import json
import requests
import time
import random
from bs4 import BeautifulSoup

# Input/Output
INPUT_CSV = 'final_master_data_v25.csv'
OUTPUT_JSON = 'league_one_stats_live.json'

def fetch_player_stats(url):
    """
    Fetches player page and calculates stats from the table.
    Returns: {'caps': int, 'matches': int, 'tries': int, 'points': int}
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. League One Caps
        caps = 0
        caps_el = soup.find(string=lambda t: t and "リーグワンキャップ数" in t)
        if caps_el:
            parent = caps_el.parent
            # Text is likely "リーグワンキャップ数：7"
            text = caps_el.strip()
            if '：' in text:
                try:
                    caps = int(text.split('：')[1].strip())
                except:
                    pass
        
        # 2. Stats from Table
        matches = 0
        tries = 0
        points = 0
        
        # Find the stats table (usually the first one in player-stats div)
        stats_div = soup.find(class_='player-stats')
        if stats_div:
            table = stats_div.find('table')
            if table:
                # Headers: No., 開催日, 対戦チーム, スコア, P, T, G, PG, DG, 成功率
                # Indices: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
                
                rows = table.find_all('tr')
                # Skip header
                for row in rows:
                    cells = row.find_all(['td', 'th']) # sometimes th used in body?
                    if len(cells) < 6: continue
                    
                    # Check if it's a valid match row (has date like YYYY/MM/DD)
                    date_text = cells[1].get_text(strip=True)
                    if not date_text or '/' not in date_text: continue

                    # Count match
                    matches += 1
                    
                    # Points (Index 4), Tries (Index 5)
                    try:
                        p_txt = cells[4].get_text(strip=True)
                        t_txt = cells[5].get_text(strip=True)
                        
                        points += int(p_txt) if p_txt.isdigit() else 0
                        tries += int(t_txt) if t_txt.isdigit() else 0
                    except Exception as e:
                        # print(f"  Error parsing row: {e}")
                        pass
                        
        return {
            'league_one_caps': caps,
            'matches': matches,
            'tries': tries,
            'points': points
        }

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    print("Starting League One Stats Scrape...")
    
    # Read CSV
    players = []
    with open(INPUT_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)
        # URL is column 13 (index 13) based on previous checks
        # Let's find URL index dynamically
        try:
            url_idx = header.index('URL')
        except:
            url_idx = 13
            
        for row in reader:
            if len(row) > url_idx and 'league-one.jp/player' in row[url_idx]:
                 players.append({'name': row[0], 'url': row[url_idx]})

    print(f"Found {len(players)} players with League One URLs.")
    
    # Scrape (Limit for testing? Or full batch?)
    # User said "Go inspect", but implied "Scrape them".
    # I'll do a batch.
    
    stats_db = {}
    
    count = 0
    for p in players:
        url = p['url']
        p_id = url.split('/')[-1] # Player ID
        
        print(f"[{count+1}/{len(players)}] Scraping {p['name']} ({p_id})...")
        data = fetch_player_stats(url)
        
        if data:
            stats_db[p_id] = data
            print(f"  -> Caps: {data['league_one_caps']}, Tries: {data['tries']}")
        
        count += 1
        time.sleep(1.0) # Be polite
        
        # Test Limit
        # if count >= 5: break 

    # Save
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(stats_db, f, indent=2)
        
    print("Done.")

if __name__ == "__main__":
    main()
