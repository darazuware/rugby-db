import requests
import re
from bs4 import BeautifulSoup
import csv
import os
import time

# JRFU Tournament IDs for Top West 2024
TOURNAMENT_IDS = {
    'top-west-b': '2811',
    'top-west-c': '2812'
}

OUTPUT_CSV = 'data_sources/top_west_players_bc.csv'

def scrape_match_ids(tournament_id):
    url = f"https://www.rugby-japan.jp/schedule/senior/2024/{tournament_id}"
    print(f"Fetching match list for tournament {tournament_id}...")
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            print(f"Failed to fetch {url}: {res.status_code}")
            return []
        # Find all match IDs linked in the page
        match_ids = re.findall(r'/match/(\d+)/', res.text)
        return list(set(match_ids))
    except Exception as e:
        print(f"Error fetching match IDs: {e}")
        return []

def scrape_players_from_match(match_id, category):
    url = f"https://www.rugby-japan.jp/match/{match_id}/print/"
    print(f"  Scraping match report {match_id} ({category})...")
    players = []
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            return []
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. チーム名の特定
        team_names = []
        for h2 in soup.find_all('h2'):
            name = h2.get_text(strip=True)
            if name: team_names.append(name)
        
        if len(team_names) < 2:
            # Fallback if h2 not found
            team_names = re.findall(r'<div class="team_name">(.*?)</div>', res.text)
            
        if not team_names:
            print(f"    Warning: No teams found in match {match_id}")
            return []

        # 2. 選手テーブルのパース
        # JRFU Print page has two main player tables
        tables = soup.find_all('table', class_='player_list')
        if not tables:
            tables = soup.find_all('table') # Fallback

        for i, table in enumerate(tables):
            if i >= 2: break # Home and Away only
            team_name = team_names[i] if i < len(team_names) else f"Unknown_{i}"
            
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 5:
                    # Column Pattern: [No, Pos, Name, Age, Height, Weight, Uni/Previous]
                    pos = cols[1].get_text(strip=True)
                    if pos in ['PR', 'HO', 'LO', 'FL', 'No.8', 'SH', 'SO', 'CTB', 'WTB', 'FB', 'No8']:
                        name = cols[2].get_text(strip=True).replace(' ', '').replace('　', '')
                        if not name or name == '氏名': continue
                        
                        players.append({
                            'name_ja': name,
                            'name_en': "",
                            'position': pos,
                            'age': cols[3].get_text(strip=True),
                            'height': cols[4].get_text(strip=True),
                            'weight': cols[5].get_text(strip=True) if len(cols) > 5 else "",
                            'university': cols[6].get_text(strip=True) if len(cols) > 6 else "",
                            'team': team_name,
                            'league': category,
                            'category': category,
                            'url': url
                        })
        return players
    except Exception as e:
        print(f"    Error scraping match {match_id}: {e}")
        return []

def main():
    all_players = []
    processed_players = set() # (name, team)

    for category, t_id in TOURNAMENT_IDS.items():
        match_ids = scrape_match_ids(t_id)
        print(f"Found {len(match_ids)} matches for {category}")
        
        for m_id in match_ids[:15]: # 各リーグの直近15試合程度から全選手を抽出
            players = scrape_players_from_match(m_id, category)
            for p in players:
                key = (p['name_ja'], p['team'])
                if key not in processed_players:
                    all_players.append(p)
                    processed_players.add(key)
            time.sleep(0.5)

    if not all_players:
        print("No players found. Aborting.")
        return

    # 保存
    fieldnames = ['name_ja', 'name_en', 'position', 'age', 'height', 'weight', 'university', 'team', 'league', 'category', 'url']
    with open(OUTPUT_CSV, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in all_players:
            writer.writerow(p)
    
    print(f"Successfully recovered {len(all_players)} players to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
