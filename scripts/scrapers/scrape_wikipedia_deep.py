import json
import requests
import time
import re
import urllib.parse
from bs4 import BeautifulSoup

# Input/Output
INPUT_DB = 'data/unified_player_database_final.json'
OUTPUT_FILE = 'player_history_deep.json'

def normalize_name(name):
    return str(name).replace(' ', '').replace('　', '').strip()

def get_wikipedia_url(name_ja):
    # Search Wikipedia API
    base_url = "https://ja.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "search": name_ja,
        "limit": 1,
        "namespace": 0,
        "format": "json"
    }
    try:
        resp = requests.get(base_url, params=params, timeout=10)
        data = resp.json()
        if data[1]:
            # Check if title matches reasonably well (or contains Rugby)
            title = data[1][0]
            url = data[3][0]
            return title, url
    except Exception as e:
        print(f"Error searching {name_ja}: {e}")
    return None, None

def scrape_wikipedia_page(url):
    history_data = {
        'junior_high': None,
        'rugby_school': None,
        'high_school': None, # Redundant but good for verification
        'university': None, # Redundant
        'minor_rep': [] # U17, U18, regional selections
    }
    
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # 1. InfoBox check
        infobox = soup.find('table', {'class': 'infobox'})
        if infobox:
            # Try to parse rows
            rows = infobox.find_all('tr')
            for row in rows:
                th = row.find('th')
                td = row.find('td')
                if th and td:
                    header = th.get_text().strip()
                    val = td.get_text().strip()
                    
                    if "中学" in header:
                        history_data['junior_high'] = val
                    elif "スクール" in header:
                        history_data['rugby_school'] = val
        
        # 2. Main Text / Career Section
        # Look for "経歴" (Career) or "来歴" (History) section
        content = soup.find('div', {'id': 'mw-content-text'})
        if content:
            text = content.get_text()
            
            # Simple Regex heuristics for schools if not in infobox
            if not history_data['junior_high']:
                # Pattern: XX中学校卒 or XX中学卒業
                m = re.search(r'([^\s「」、。]+中学校)', text)
                if m:
                    history_data['junior_high'] = m.group(1)
            
            if not history_data['rugby_school']:
                # Pattern: XXラグビースクール
                m = re.search(r'([^\s「」、。]+ラグビースクール)', text)
                if m:
                    history_data['rugby_school'] = m.group(1)
            
            # Minor Reps (U17, Kansai, etc.)
            # This is hard to structured parse, but we can look for keywords
            keywords = ['U17', 'U18', 'U19', '高校日本代表', '中学日本代表', '関西代表', '関東代表', '九州代表']
            for k in keywords:
                if k in text:
                    history_data['minor_rep'].append(k)

    except Exception as e:
        print(f"  Error scraping {url}: {e}")
        
    return history_data

def main():
    print("Loading player database...")
    with open(INPUT_DB, 'r', encoding='utf-8') as f:
        players = json.load(f)
    
    deep_history = {}
    
    # Try to load existing progress
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            deep_history = json.load(f)
    except:
        pass

    count = 0
    total = len(players)
    
    print(f"Starting Wikipedia Scrape for {total} players...")
    
    for i, p in enumerate(players):
        # Only target Japanese players or those with Kanji names likely to have JP Wiki
        name_ja = p.get('name_ja')
        if not name_ja or name_ja == '不明': continue
        
        # Skip if already done
        if p['id'] in deep_history:
            continue
            
        print(f"[{i}/{total}] Searching: {name_ja} ...")
        
        # Search Wiki
        title, url = get_wikipedia_url(name_ja)
        if url:
            print(f"  Found: {title} ({url})")
            # Scrape
            data = scrape_wikipedia_page(url)
            
            # Clean data
            if data['junior_high'] or data['rugby_school'] or data['minor_rep']:
                print(f"  Captured: {data}")
                deep_history[p['id']] = {
                    'name': name_ja,
                    'wiki_url': url,
                    'data': data
                }
            else:
                print("  No deep data found.")
                deep_history[p['id']] = {'no_data': True} # Mark as checked
        else:
            print("  No Wikipedia page found.")
            deep_history[p['id']] = {'no_data': True}
            
        # Save periodically
        if count % 10 == 0:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(deep_history, f, ensure_ascii=False, indent=2)
        
        count += 1
        time.sleep(1.0) # Be nice to Wikipedia API

    # Final Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(deep_history, f, ensure_ascii=False, indent=2)
        
    print("Wikipedia scrape complete.")

if __name__ == "__main__":
    main()
