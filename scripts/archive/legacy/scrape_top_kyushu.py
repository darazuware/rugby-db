import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import time
import os

def scrape_top_kyushu():
    base_url = "https://www.rugby-kyushu.jp/kyushuleague/2025-2026/topkyushu/"
    list_url = base_url + "topteam.html"
    
    print(f"Fetching team list from {list_url}...")
    res = requests.get(list_url)
    if res.status_code != 200:
        print(f"Failed to fetch list page: {res.status_code}")
        return
    
    soup = BeautifulSoup(res.content, 'html.parser')
    # 2025-2026のチームリンクを抽出
    team_links = []
    # 記事内のリンクを探す
    for a in soup.find_all('a', href=True):
        if 'topteam/' in a['href'] and a['href'].endswith('.html') and 'topteam.html' not in a['href']:
            href = a['href']
            # "/kyushuleague/..." -> "https://www.rugby-kyushu.jp/kyushuleague/..."
            if href.startswith('/'):
                href = "https://www.rugby-kyushu.jp" + href
            
            name = a.get_text(strip=True)
            if not name:
                # span inside a (e.g. icon--arrow)
                span = a.find('span')
                if span:
                    name = span.get_text(strip=True)
                else:
                    name = os.path.basename(href).replace('.html', '')
            
            if name:
                team_links.append((name, href))
    
    # 重複排除
    team_links = list(dict.fromkeys(team_links))
    print(f"Found {len(team_links)} teams: {[t[0] for t in team_links]}")
    
    all_players = []
    
    for team_name, href in team_links:
        print(f"Scraping team: {team_name} ({href})...")
        t_res = requests.get(href)
        if t_res.status_code != 200:
            print(f"Failed to fetch team page: {href}")
            continue
        
        t_soup = BeautifulSoup(t_res.content, 'html.parser')
        # テーブルを探す
        tables = t_soup.find_all('table')
        if not tables:
            print(f"No tables found for {team_name}")
            continue
            
        found_players_in_team = 0
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    pos = cols[1].get_text(strip=True)
                    # ポジション名が含まれているか確認
                    if pos in ['PR', 'HO', 'LO', 'FL', 'No.8', 'SH', 'SO', 'CTB', 'WTB', 'FB', 'No8']:
                        try:
                            name = cols[2].get_text(strip=True).replace(' ', '').replace('　', '')
                            if not name or name == '氏名': continue
                            
                            p_data = {
                                'Full_Name': name,
                                'Position': pos,
                                'Age': cols[3].get_text(strip=True),
                                'Height': cols[4].get_text(strip=True),
                                'Weight': cols[5].get_text(strip=True) if len(cols) > 5 else "---",
                                'University': cols[6].get_text(strip=True) if len(cols) > 6 else "---",
                                'Team': team_name,
                                'League': 'top-kyushu',
                                'Category': 'top-kyushu',
                                'Scraped_Url': href
                            }
                            all_players.append(p_data)
                            found_players_in_team += 1
                        except Exception as e:
                            print(f"Error parsing row: {e}")
            if found_players_in_team > 0:
                print(f"  Extracted {found_players_in_team} players from table.")
                break
        
        if found_players_in_team == 0:
            print(f"  Warning: No players found for {team_name}")
        
        time.sleep(1) # マナー
        
    # 保存
    output_path = "data_sources/top_kyushu_players.csv"
    os.makedirs("data_sources", exist_ok=True)
    df = pd.DataFrame(all_players)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Saved {len(all_players)} players to {output_path}")

if __name__ == "__main__":
    scrape_top_kyushu()
