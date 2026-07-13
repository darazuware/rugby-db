import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re

# Load Raw Data
with open('data/top14_players_raw.json', 'r') as f:
    PLAYERS = json.load(f)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

# Position Mapping (English to short JA)
POS_MAP = {
    "Prop": ("PR", "プロップ"),
    "Hooker": ("HO", "フッカー"),
    "Second row": ("LO", "セカンドロー"),
    "Lock": ("LO", "セカンドロー"),
    "Flanker": ("FL", "フランカー"),
    "Number 8": ("NO8", "ナンバーエイト"),
    "Back row": ("FL/NO8", "バックロー"),
    "Scrum-half": ("SH", "スクラムハーフ"),
    "Fly-half": ("SO", "フライハーフ"),
    "Centre": ("CTB", "センター"),
    "Wing": ("WTB", "ウィング"),
    "Winger": ("WTB", "ウィング"),
    "Fullback": ("FB", "フルバック")
}

def get_detail(player):
    url = player['all_rugby_url']
    print(f"Enriching {player['en_name']} ({url})...")
    
    try:
        # English Details Only (Verified no native JP URLs)
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Career Path
        career = []
        parcours = soup.find('div', class_='parcours')
        if parcours:
            items = parcours.find_all('li')
            for it in items:
                career.append(it.get_text(strip=True))
        
        # Stats Summary
        stats = {'matches': 0, 'tries': 0, 'points': 0}
        stats_divs = soup.find_all('div', class_='stats')
        for div in stats_divs:
            text = div.get_text().lower()
            nums = re.findall(r'\d+', text)
            if not nums: continue
            if 'match' in text or 'game' in text: stats['matches'] = int(nums[0])
            elif 'tries' in text or 'essais' in text: stats['tries'] = int(nums[0])
            elif 'points' in text: stats['points'] = int(nums[0])

        # Position Fix
        pos_raw = player.get('position_en', '')
        if pos_raw in POS_MAP:
            player['position_en'], player['position_ja'] = POS_MAP[pos_raw]
            
        player['career_history'] = career
        player['stats'] = stats
        
        return player
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return player

def main():
    output_path = 'data/top14_players_enriched.json'
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            enriched = json.load(f)
    else:
        enriched = []
        
    done_slugs = {p['slug'] for p in enriched}
    
    count = 0
    for player in PLAYERS:
        if player['slug'] in done_slugs: continue
        
        enriched_p = get_detail(player)
        enriched.append(enriched_p)
        count += 1
        
        # Save every 20
        if count % 20 == 0:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(enriched, f, ensure_ascii=False, indent=2)
            print(f"  💾 Progress saved: {len(enriched)} players")
            
        time.sleep(1.2)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)
        
    print(f"\n=== Enrichment Complete ===")
    print(f"Total Enriched: {len(enriched)}")

if __name__ == "__main__":
    main()
