import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

CLUBS = {
    "Bath Rugby": "https://www.premiershiprugby.com/clubs/bath-rugby/squad",
    "Bristol Bears": "https://www.premiershiprugby.com/clubs/bristol-bears/squad",
    "Exeter Chiefs": "https://www.premiershiprugby.com/clubs/exeter-chiefs/squad",
    "Gloucester Rugby": "https://www.premiershiprugby.com/clubs/gloucester-rugby/squad",
    "Harlequins": "https://www.premiershiprugby.com/clubs/harlequins/squad",
    "Leicester Tigers": "https://www.premiershiprugby.com/clubs/leicester-tigers/squad",
    "Newcastle Falcons": "https://www.premiershiprugby.com/clubs/newcastle-redbulls/squad",
    "Northampton Saints": "https://www.premiershiprugby.com/clubs/northampton-saints/squad",
    "Sale Sharks": "https://www.premiershiprugby.com/clubs/sale-sharks/squad",
    "Saracens": "https://www.premiershiprugby.com/clubs/saracens/squad"
}

def clean_text(text):
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()

def scrape_squad(club_name, url):
    print(f"Scraping {club_name} from {url}...")
    players = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # サブエージェントの調査に基づくセレクタ
        # a.flex.flex-col.justify-end の中に div.text-mono-50 (名) と div.text-primary-200 (ポジション) がある
        cards = soup.select('a.flex.flex-col.justify-end')
        if not cards:
            # 代替セレクタの試行 (構造が微妙に違う場合)
            cards = soup.select('.flex.flex-col.justify-end')

        for card in cards:
            name_el = card.select_one('div.text-mono-50')
            pos_el = card.select_one('div.text-primary-200')
            
            if name_el:
                name = clean_text(name_el.get_text())
                pos = clean_text(pos_el.get_text()) if pos_el else ""
                
                # 姓名の分割（簡易的）
                name_parts = name.split(' ')
                first_name = name_parts[0] if len(name_parts) > 0 else ""
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                
                players.append({
                    "name_en": name,
                    "first_name": first_name,
                    "last_name": last_name,
                    "position": pos,
                    "team": club_name,
                    "league": "premiership"
                })
        
        print(f"Found {len(players)} players for {club_name}.")
        return players
    except Exception as e:
        print(f"Error scraping {club_name}: {e}")
        return []

def main():
    all_players = []
    for club, url in CLUBS.items():
        all_players.extend(scrape_squad(club, url))
        time.sleep(1) # 負荷軽減
    
    if all_players:
        df = pd.DataFrame(all_players)
        output_path = "data_sources/gallagher_premiership_players_raw.csv"
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Saved {len(all_players)} players to {output_path}")
    else:
        print("No players found.")

if __name__ == "__main__":
    main()
