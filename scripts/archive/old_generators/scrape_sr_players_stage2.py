import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re
from player_utils import PlayerDataProcessor

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_crusaders_profiles(squad_url):
    """Crusaders 独自の構造を解析"""
    print(f"Deep scraping Crusaders from {squad_url}...")
    try:
        response = requests.get(squad_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Squad ページから個別リンクを再抽出 (Stage 1 or 2)
        links = soup.find_all('a', string=re.compile(r'Find out more', re.I))
        player_data = []
        
        for link in links[:5]: # テストのため5人
            raw_url = link['href']
            from urllib.parse import urljoin
            url = urljoin(squad_url, raw_url)
            
            # 名前取得のロジックを強化
            parent = link.find_parent()
            name = "Unknown"
            if parent:
                prev_h3 = parent.find_previous_sibling('h3')
                if prev_h3:
                    name = prev_h3.get_text(strip=True)
                else:
                    # 別の構造：親の親にh3がある場合など
                    grandparent = parent.parent
                    if grandparent:
                        h3 = grandparent.find('h3')
                        if h3: name = h3.get_text(strip=True)
            
            print(f"  - Profiling {name}...")
            try:
                p_res = requests.get(url, headers=HEADERS)
                p_res.raise_for_status()
                p_soup = BeautifulSoup(p_res.text, 'html.parser')
                
                p_info = {
                    "name": name,
                    "url": url,
                    "caps": None,
                    "school": None,
                    "birth_date": None,
                    "age": None
                }
                
                # About セクションのテキスト解析
                about_text = p_soup.get_text()
                p_info["caps"] = PlayerDataProcessor.extract_caps(about_text)
                
                # 出身校
                school_match = re.search(r'(?:played|schoolboy rugby for|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4}\s+(?:College|School|University))', about_text)
                if school_match:
                    p_info["school"] = school_match.group(1)
                
                player_data.append(p_info)
            except Exception as pe:
                print(f"    Error profiling {name}: {pe}")
            
            time.sleep(1)
            
        return player_data
    except Exception as e:
        print(f"Error scraping Crusaders: {e}")
        return []

def main():
    # Stage 1 で得た URL を読み込み
    with open("data/super_rugby_teams_deep.json", "r") as f:
        teams = json.load(f)
        
    crusaders_url = teams.get("96", {}).get("official_website")
    if crusaders_url:
        results = scrape_crusaders_profiles(crusaders_url)
        
        output_path = "data/super_rugby_players_detailed.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Detailed player data saved to {output_path}")

if __name__ == "__main__":
    main()
