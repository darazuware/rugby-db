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

URLS = [
    ("2007", "Rugby World Cup", "https://en.wikipedia.org/wiki/2007_Rugby_World_Cup_squads"),
    ("2011", "Rugby World Cup", "https://en.wikipedia.org/wiki/2011_Rugby_World_Cup_squads"),
    ("2015", "Rugby World Cup", "https://en.wikipedia.org/wiki/2015_Rugby_World_Cup_squads"),
    ("2019", "Rugby World Cup", "https://en.wikipedia.org/wiki/2019_Rugby_World_Cup_squads"),
    ("2023", "Rugby World Cup", "https://en.wikipedia.org/wiki/2023_Rugby_World_Cup_squads"),
    ("2024", "Six Nations", "https://en.wikipedia.org/wiki/2024_Six_Nations_Championship_squads"),
    ("2025", "Six Nations", "https://en.wikipedia.org/wiki/2025_Six_Nations_Championship_squads")
]

def clean_name(name):
    name = re.sub(r'\[.*?\]', '', name)
    name = re.sub(r'\(.*?\)', '', name)
    return name.strip()

def scrape_tournament(year, tournament, url):
    print(f"Scraping {tournament} {year}...")
    players = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # すべてのテーブルを取得
        tables = soup.select('table.wikitable')
        for table in tables:
            # テーブルの直前の見出しを探して国名を特定する
            country_name = "Unknown"
            curr = table.find_previous(['h2', 'h3', 'h4'])
            while curr:
                # 'Pool', 'Group', 'Squads' などを除外して国名っぽいものを探す
                text = curr.get_text().replace('[edit]', '').strip()
                if not any(x in text.lower() for x in ['pool', 'group', 'squads', 'referees', 'coaching', 'contents', 'notes']):
                    country_name = text
                    break
                curr = curr.find_previous(['h2', 'h3', 'h4'])
            
            rows = table.find_all('tr')
            header = [th.get_text().strip().lower() for th in rows[0].find_all(['th', 'td'])]
            
            # カラム位置の特定
            name_idx = -1
            pos_idx = -1
            caps_idx = -1
            club_idx = -1
            
            for i, h in enumerate(header):
                if 'player' in h or 'name' in h: name_idx = i
                elif 'pos' in h: pos_idx = i
                elif 'caps' in h: caps_idx = i
                elif 'club' in h or 'province' in h or 'franchise' in h: club_idx = i
            
            # フォールバック
            if name_idx == -1: name_idx = 0
            if pos_idx == -1 and len(header) > 1: pos_idx = 1
            if caps_idx == -1 and len(header) > 3: caps_idx = 3
            if club_idx == -1: club_idx = len(header) - 1

            for row in rows[1:]:
                cols = row.find_all(['td', 'th'])
                if len(cols) > max(name_idx, pos_idx):
                    name_el = cols[name_idx].find('a') or cols[name_idx]
                    name = clean_name(name_el.get_text())
                    if not name or len(name) < 2: continue
                    
                    pos = clean_name(cols[pos_idx].get_text()) if pos_idx < len(cols) else ""
                    caps_txt = clean_name(cols[caps_idx].get_text()) if caps_idx < len(cols) else "0"
                    caps = re.sub(r'\D', '', caps_txt) or "0"
                    
                    club = clean_name(cols[club_idx].get_text()) if club_idx < len(cols) else ""
                    
                    players.append({
                        "name_en": name,
                        "position": pos,
                        "caps": caps,
                        "club": club,
                        "representative_team": country_name,
                        "tournament": f"{tournament} {year}"
                    })
        
        print(f"  -> Found {len(players)} players.")
        return players
    except Exception as e:
        print(f"  -> Error: {e}")
        return []

def main():
    all_players = []
    for year, tournament, url in URLS:
        all_players.extend(scrape_tournament(year, tournament, url))
        time.sleep(1)
        
    if all_players:
        df = pd.DataFrame(all_players)
        # 代表チームごとの最新キャップ数をまとめるなどの処理は後で行う
        df.to_csv("data_sources/international_representatives_raw_v2.csv", index=False, encoding='utf-8-sig')
        print(f"Saved {len(all_players)} entries to data_sources/international_representatives_raw_v2.csv")

if __name__ == "__main__":
    main()
