import json
import requests
from bs4 import BeautifulSoup
import time
import re
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_all_rugby(url):
    if not url or 'all.rugby' not in url:
        return None
    
    print(f"Scraping {url}...")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        
        info = {}
        
        # Bio text contains most info
        bio_p = soup.select_one('#bio .bio p')
        if not bio_p:
            bio_p = soup.select_one('.player-bio p')
            
        if bio_p:
            text = bio_p.get_text(separator=' ', strip=True) # Normalize whitespace
            # Height: standing at 1.77 m tall
            h_match = re.search(r'standing at\s*([0-9.]+)\s*m', text)
            if h_match:
                val = h_match.group(1).replace('.', '')
                if len(val) == 2: val += '0'
                info['height'] = val
                
            # Weight: weighing in at 91 kg
            w_match = re.search(r'weighing in at\s*(\d+)\s*kg', text)
            if w_match:
                info['weight'] = w_match.group(1)
                
            # Age
            a_match = re.search(r'is a\s*(\d+)-year-old', text)
            if a_match:
                info['age'] = a_match.group(1)
        
        # Always return something so we know we processed it
        if not info:
            info = {"not_found": True}
        return info
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def main():
    missing_list_path = "/Users/ktamatzmoto/.gemini/antigravity/brain/0a4cb5ef-2a47-4d0d-afe7-2dd511f55541/final_missing_list.json"
    output_path = "/Users/ktamatzmoto/.gemini/antigravity/brain/0a4cb5ef-2a47-4d0d-afe7-2dd511f55541/scraped_missing_details.json"
    
    if not os.path.exists(missing_list_path):
        return

    with open(missing_list_path, "r", encoding="utf-8") as f:
        missing_players = json.load(f)

    results = []
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            try: results = json.load(f)
            except: pass
            
    processed_urls = [r['url'] for r in results]

    count = 0
    for player in missing_players:
        url = player.get('url')
        if not url or url in processed_urls:
            continue
            
        if count >= 100: # Larger batch now
            break
            
        details = scrape_all_rugby(url)
        if details:
            details['name'] = player['name']
            details['url'] = url
            results.append(details)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            count += 1
        time.sleep(1)

    print(f"Processed {count} players.")

if __name__ == "__main__":
    main()
