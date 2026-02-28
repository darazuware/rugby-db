
import json
import requests
from bs4 import BeautifulSoup
import time
import os
import random
import re

DATABASE_PATH = 'data/unified_player_database_final.json'
OUTPUT_PATH = 'data/unified_player_database_final.json'  # Overwrite directly or merge later
LOG_FILE = 'logs/scrape_global.log'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
}

def load_database():
    with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_database(data):
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def log(message):
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def scrape_player_details(url):
    try:
        if not url.startswith('http'):
            return None
        
        # Use existing logic from similar scrapers (e.g. merge_all_rugby_data.py but with page fetching)
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            log(f"Request failed for {url}: {e}")
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        data = {}
        
        # 1. Image (Common class in all.rugby)
        # Often: <div class="player-header-img"><img src="..."></div>
        img_tag = soup.select_one('.player-header-img img')
        if img_tag:
            src = img_tag.get('src')
            if src and not src.endswith('svg'): # Avoid default placeholders
                if src.startswith('/'):
                    src = 'https://all.rugby' + src
                data['image_url'] = src
        
        # 2. Stats (Matches, Points, Tries, Caps)
        # Look for the "Career" block or "Stats" block
        # Often structured as: <div class="stat-value">123</div> <div class="stat-label">Matches</div>
        # Or look for specific tables
        
        # Simplified: Just grab the text of stats if easy, or skip if complex.
        # Main goal is IMAGE to make the profile "Rich".
        
        # 3. Position / Height / Weight
        # Often in .player-infos or similar
        info_block = soup.select_one('.player-infos')
        if info_block:
            text = info_block.get_text()
            # Parse logic could be added here if needed, but risky without seeing live HTML.
            # Stick to Image as primary target for "Rich Status".
            
        return data

    except Exception as e:
        log(f"Error scraping {url}: {e}")
        return None

def main():
    log("Starting Global Player Scrape...")
    players = load_database()
    
    count = 0
    updated_count = 0
    
    # Shuffle to avoid hitting same team/pattern consistently
    player_list = list(players.items())
    random.shuffle(player_list)
    
    for player_id, player in player_list:
        # Filter condition: Missing Image AND has a valid All.Rugby URL
        if not player.get('image_url') and 'all.rugby' in player.get('url', ''):
             
            url = player['url']
            log(f"Scraping {player['en_name']} ({url})...")
            
            details = scrape_player_details(url)
            
            if details:
                if details.get('image_url'):
                    players[player_id]['image_url'] = details['image_url']
                    updated_count += 1
                
                # Add slight delay
                time.sleep(random.uniform(1.0, 3.0))
            
            count += 1
            
            # Incremental Save every 50
            if count % 50 == 0:
                save_database(players)
                log(f"Saved progress after {count} players. Updated: {updated_count}")
                
            # Cap at 4 hours worth? or just run all
            # 4000 players * 2s = 8000s = ~2.2 hours. Doable.
            
    save_database(players)
    log(f"Finished. Total scanned: {count}. Total updated: {updated_count}")
    
if __name__ == "__main__":
    main()
