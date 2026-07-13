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

RWC_URLS = {
    "2007": "https://en.wikipedia.org/wiki/2007_Rugby_World_Cup_squads",
    "2011": "https://en.wikipedia.org/wiki/2011_Rugby_World_Cup_squads",
    "2015": "https://en.wikipedia.org/wiki/2015_Rugby_World_Cup_squads",
    "2019": "https://en.wikipedia.org/wiki/2019_Rugby_World_Cup_squads",
    "2023": "https://en.wikipedia.org/wiki/2023_Rugby_World_Cup_squads"
}

OTHER_URLS = {
    "2024_6N": "https://en.wikipedia.org/wiki/2024_Six_Nations_Championship_squads",
    "2025_6N": "https://en.wikipedia.org/wiki/2025_Six_Nations_Championship_squads"
}

def clean_name(name):
    # Remove citations like [1]
    name = re.sub(r'\[.*?\]', '', name)
    # Remove notes or tags sometimes in brackets
    name = re.sub(r'\(.*?\)', '', name)
    return name.strip()

def scrape_wikipedia_squads(year, url, tournament_name):
    print(f"Scraping {tournament_name} ({year}) from {url}...")
    players = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Wikipediaの構造: チーム名は H3+span.mw-headline、その後に table.wikitable が来る
        headlines = soup.select('span.mw-headline')
        for headline in headlines:
            country_name = headline.get_text().strip()
            # 無関係なセクションを除外
            if any(x in country_name.lower() for x in ['contents', 'see also', 'references', 'external links', 'notes', 'coaching', 'referees']):
                continue
            
            # 親のH3等を取得
            h_tag = headline.parent
            if h_tag.name not in ['h2', 'h3']:
                continue
                
            # 次のテーブルを探す
            table = None
            curr = h_tag.find_next_sibling()
            while curr:
                if curr.name in ['h2', 'h3']: # 次のセクションに来たら中断
                    break
                if curr.name == 'table' and 'wikitable' in curr.get('class', []):
                    table = curr
                    break
                curr = curr.find_next_sibling()
            
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 4:
                        # ヘッダー行をスキップ (通常最初のセルが 'Pos' や 'Player')
                        first_col_text = cols[0].get_text().strip()
                        if first_col_text in ['Pos', 'Player', 'No.', '#']:
                            continue
                            
                        # Wikipedia RWC/6N テーブル標準: Player, Pos, Date of birth, Caps, Club
                        # インデックスは大会によって微妙に違う場合があるが、subagentの調査に基づき 0:Name, 1:Pos, 3:Caps, 4:Club を基本とする
                        name_el = cols[0].find('a') or cols[0]
                        name = clean_name(name_el.get_text())
                        if not name: continue
                        
                        pos = clean_name(cols[1].get_text()) if len(cols) > 1 else ""
                        caps_text = clean_name(cols[3].get_text()) if len(cols) > 3 else "0"
                        club_el = cols[4].find('a') or cols[4] if len(cols) > 4 else None
                        club = clean_name(club_el.get_text()) if club_el else ""
                        
                        caps = re.sub(r'\D', '', caps_text)
                        if not caps: caps = "0"
                        
                        players.append({
                            "name_en": name,
                            "position": pos,
                            "caps": caps,
                            "club": club,
                            "representative_team": country_name,
                            "tournament": f"{tournament_name} {year}"
                        })
        
        print(f"Found {len(players)} players for {tournament_name} {year}.")
        return players
    except Exception as e:
        print(f"Error scraping {year}: {e}")
        return []

def main():
    all_data = []
    
    for year, url in RWC_URLS.items():
        all_data.extend(scrape_wikipedia_squads(year, url, "Rugby World Cup"))
        time.sleep(1)
        
    for key, url in OTHER_URLS.items():
        year = key.split('_')[0]
        name = "Six Nations"
        all_data.extend(scrape_wikipedia_squads(year, url, name))
        time.sleep(1)
    
    if all_data:
        df = pd.DataFrame(all_data)
        output_path = "data_sources/international_representatives_raw.csv"
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Saved {len(all_data)} entries to {output_path}")
    else:
        print("No players found.")

if __name__ == "__main__":
    main()
