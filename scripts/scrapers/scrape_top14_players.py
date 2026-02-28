import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re

# Load Top 14 Teams
with open('data/top14_teams.json', 'r') as f:
    TEAMS = json.load(f)

# Force English to avoid translation artifacts
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

# Translation Map for English Positions
POS_MAP = {
    "Prop": "PR",
    "Hooker": "HO",
    "Second row": "LO",
    "Flanker": "FL",
    "Number 8": "NO8",
    "Scrum-half": "SH",
    "Fly-half": "SO",
    "Centre": "CTB",
    "Wing": "WTB",
    "Fullback": "FB"
}

# Mapping for Japanese Position names for the bio table display
POS_JA_MAP = {
    "PR": "プロップ",
    "HO": "フッカー",
    "LO": "セカンドロー",
    "FL": "フランカー",
    "NO8": "ナンバーエイト",
    "SH": "スクラムハーフ",
    "SO": "フライハーフ",
    "CTB": "センター",
    "WTB": "ウィング",
    "FB": "フルバック"
}

def scrape_squad(team_info):
    url = team_info['url']
    print(f"Scraping {team_info['name']} ({url})...")
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        table = soup.select_one('table.rtable')
        if not table:
            print(f"  ✗ Table not found for {team_info['name']}")
            return []
            
        players = []
        rows = table.select('tbody tr') or table.select('tr')[1:]
        
        for row in rows:
            tds = row.find_all('td')
            if len(tds) < 7: continue
            
            name_a = tds[1].find('a')
            if not name_a: continue
            
            en_name = name_a.get_text(strip=True)
            profile_url = "https://all.rugby" + name_a.get('href')
            slug = profile_url.split('/')[-1]
            
            # Position (In English since headers were set)
            pos_en_raw = tds[2].get_text(strip=True)
            pos_en = POS_MAP.get(pos_en_raw, pos_en_raw) 
            pos_ja = POS_JA_MAP.get(pos_en, pos_en_raw)
            
            dob_en = tds[4].get_text(strip=True) # e.g. "Jul 25, 2003" or similar
            height_en = tds[5].get_text(strip=True) # e.g. "1.80 m"
            weight_en = tds[6].get_text(strip=True) # e.g. "128 kg"
            
            # Normalize Physical Stats
            height = re.sub(r'[^\d.]', '', height_en)
            if height:
                try: 
                    h_val = float(height)
                    if h_val < 3: h_val *= 100
                    height = str(int(h_val))
                except: pass
                
            weight = re.sub(r'[^\d]', '', weight_en)
            
            # Birthday localization if needed (DD/MM/YYYY to YYYY年MM月DD日)
            # all.rugby English format is often "Jul 25, 2003"
            birthday_ja = dob_en 
            try:
                # Try common formats
                for fmt in ('%b %d, %Y', '%d/%m/%Y', '%Y-%m-%d'):
                    try:
                        from datetime import datetime
                        dt = datetime.strptime(dob_en, fmt)
                        birthday_ja = dt.strftime('%Y年%m月%d日')
                        break
                    except: continue
            except: pass

            players.append({
                'en_name': en_name,
                'name_ja': en_name, # Initially same, user might want to translate later
                'all_rugby_url': profile_url,
                'slug': slug,
                'team_ja': team_info['name_ja'],
                'team_en': team_info['name'],
                'position_ja': pos_ja,
                'position_en': pos_en,
                'birthday': birthday_ja,
                'height': height,
                'weight': weight,
                'league': 'TOP 14'
            })
            
        print(f"  ✓ Found {len(players)} players")
        return players
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []

def main():
    all_players = []
    for team in TEAMS:
        all_players.extend(scrape_squad(team))
        time.sleep(1.5) # Polite delay
        
    output_path = 'data/top14_players_raw.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_players, f, ensure_ascii=False, indent=2)
        
    print(f"\n=== Scrape Complete ===")
    print(f"Total Top 14 Players: {len(all_players)}")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    main()
