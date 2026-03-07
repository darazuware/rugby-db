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

def scrape_top14_player_profile(player_url):
    """LNR (Top 14) 選手個別ページを解析"""
    print(f"  - Profiling from {player_url}...")
    try:
        response = requests.get(player_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 名前取得 (Head 1)
        name_el = soup.find('h1')
        name = name_el.get_text(strip=True) if name_el else "Unknown"
        
        info = {
            "name": name,
            "url": player_url,
            "age": None,
            "height": None,
            "weight": None,
            "caps": None,
            "career": []
        }
        
        # 年齢/身長/体重はメタデータやクラスから (JS実行が必要な場合があるが)
        # 以前の調査で NextData に入っている可能性がある
        # ここではフォールバックとしてテキスト解析
        meta_text = soup.get_text()
        
        # 年齢
        age_match = re.search(r'(\d+)\s*ans', meta_text)
        if age_match: info["age"] = int(age_match.group(1))
        
        # 身長
        height_match = re.search(r'(\d+)\s*cm', meta_text)
        if height_match: info["height"] = int(height_match.group(1))
        
        # 体重
        weight_match = re.search(r'(\d+)\s*kg', meta_text)
        if weight_match: info["weight"] = int(weight_match.group(1))
        
        # キャリア (履歴) - 表形式のパース
        career_section = soup.find('div', class_=re.compile(r'career|carriere', re.I))
        if career_section:
            rows = career_section.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    year = cols[0].get_text(strip=True)
                    team = cols[1].get_text(strip=True)
                    info["career"].append({"year": year, "team": team})
        
        return info
    except Exception as e:
        print(f"    Error: {e}")
        return None

def main():
    # 本来は全クラブを巡回するが、テストとして Bayonne の数人
    bayonne_url = "https://top14.lnr.fr/club/bayonne/effectif-staff"
    print(f"Fetching Bayonne squad from {bayonne_url}...")
    
    try:
        res = requests.get(bayonne_url, headers=HEADERS)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # a[href^="/joueur/"] を抽出
        player_links = soup.select('a[href*="/joueur/"]')
        from urllib.parse import urljoin
        profile_urls = list(set([urljoin("https://top14.lnr.fr", a['href']) for a in player_links]))
        
        results = []
        for url in profile_urls[:5]: # テスト
            data = scrape_top14_player_profile(url)
            if data: results.append(data)
            time.sleep(1)
            
        output_path = "data/top14_players_detailed.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"Detailed Top 14 player data saved to {output_path}")
    except Exception as e:
        print(f"Main Error: {e}")

if __name__ == "__main__":
    main()
