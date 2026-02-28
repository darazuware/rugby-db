import json
import requests
import time
import re
from bs4 import BeautifulSoup
import os

# Input/Output
INPUT_URLS = 'team_player_lists.json'
OUTPUT_JSON = 'live_player_data.json'

def fetch_player_data(url):
    """
    Fetches player page and extracts stats, socials, and image.
    """
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        html = response.text
        
        data = {}
        
        # 1. League One Caps
        caps = 0
        caps_el = soup.find(string=lambda t: t and "リーグワンキャップ数" in t)
        if caps_el:
            text = caps_el.strip()
            if '：' in text:
                try:
                    caps = int(text.split('：')[1].strip())
                except:
                    pass
        data['league_one_caps'] = caps
        
        # 2. Stats from Table (Matches, Tries, Points)
        matches = 0
        tries = 0
        points = 0
        
        stats_div = soup.find(class_='player-stats')
        if stats_div:
            table = stats_div.find('table')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 6: continue
                    date_text = cells[1].get_text(strip=True)
                    if not date_text or '/' not in date_text: continue
                    
                    matches += 1
                    try:
                        p_txt = cells[4].get_text(strip=True)
                        t_txt = cells[5].get_text(strip=True)
                        points += int(p_txt) if p_txt.isdigit() else 0
                        tries += int(t_txt) if t_txt.isdigit() else 0
                    except:
                        pass
                        
        data['matches'] = matches
        data['tries'] = tries
        data['points'] = points
        
        # 3. Socials
        socials = {}
        insta = re.search(r'href="(https://www\.instagram\.com/[^"/]+/?)"', html)
        if insta and "leagueone_official" not in insta.group(1):
            socials['instagram'] = insta.group(1)
        
        twit = re.search(r'href="(https://(?:twitter\.com|x\.com)/[^"/]+/?)"', html)
        if twit and "LeagueOne_JP" not in twit.group(1):
            socials['twitter'] = twit.group(1)
            
        data['socials'] = socials
        
        # 4. Image (Face)
        # Look for the main player image. Usually has a specific class or check meta tag.
        # og:image is often the face + background
        og_image = soup.find('meta', property='og:image')
        if og_image:
            data['image_url'] = og_image['content']
            
        # 5. Name (Japanese) - From Title or h1
        h1 = soup.find('h1')
        if h1:
            # Format often "Name (POS)"
            raw_name = h1.get_text(strip=True)
            data['name_ja'] = re.sub(r'\s*\(.*?\)', '', raw_name).strip()
            
        return data

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    print("Starting Fresh Player Data Scrape...")
    
    if not os.path.exists(INPUT_URLS):
        print(f"Error: {INPUT_URLS} not found. Run scrape_team_metadata.py first.")
        return

    with open(INPUT_URLS, 'r', encoding='utf-8') as f:
        urls = json.load(f)
        
    print(f"Found {len(urls)} player URLs to process.")
    
    live_data = {}
    
    # Check for existing partial data to resume
    if os.path.exists(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
                live_data = json.load(f)
            print(f"Resuming... {len(live_data)} already scraped.")
        except:
            pass
            
    try:
        for i, url in enumerate(urls):
            pid = url.split('/')[-1]
            if pid in live_data:
                continue
                
            print(f"[{i+1}/{len(urls)}] Scraping {pid}...")
            data = fetch_player_data(url)
            
            if data:
                data['url'] = url
                live_data[pid] = data
                print(f"  -> {data.get('name_ja')} (Caps: {data['league_one_caps']}, Socials: {len(data['socials'])})")
            
            time.sleep(0.5) # Be polite
            
            # Save periodically
            if i % 10 == 0:
                with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                    json.dump(live_data, f, ensure_ascii=False, indent=2)
                    
    except KeyboardInterrupt:
        print("Scraping interrupted. Saving progress...")
        
    # Final Save
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(live_data, f, ensure_ascii=False, indent=2)
        
    print("Done!")

if __name__ == "__main__":
    main()
