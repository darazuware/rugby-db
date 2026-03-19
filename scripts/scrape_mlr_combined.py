import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import time

def get_next_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        if script:
            return json.loads(script.string)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

def scrape_standings():
    url = "https://www.majorleague.rugby/standings/"
    print(f"Scraping standings from {url}...")
    data = get_next_data(url)
    if not data:
        return
    
    standings = []
    # NEXT_DATA の構造から順位表を探す
    # 構造の例: props -> pageProps -> data -> standings
    try:
        raw_standings = data["props"]["pageProps"]["data"]["standings"]
        for entry in raw_standings:
            # entry は各チームのデータ
            team_info = entry.get("team", {})
            stats = entry.get("stats", [{}])[0] if entry.get("stats") else {}
            
            standings.append({
                "rank": str(entry.get("pos", "")),
                "team": team_info.get("name", ""),
                "played": str(stats.get("played", "0")),
                "won": str(stats.get("won", "0")),
                "lost": str(stats.get("lost", "0")),
                "drawn": str(stats.get("drawn", "0")),
                "pts_for": str(stats.get("ptsFor", "0")),
                "pts_against": str(stats.get("ptsAgainst", "0")),
                "diff": str(stats.get("ptsDiff", "0")),
                "try_bonus": str(stats.get("bonusTry", "0")),
                "loss_bonus": str(stats.get("bonusLoss", "0")),
                "points": str(stats.get("pts", "0"))
            })
            
        json_path = "data/standings.json"
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                all_standings = json.load(f)
        else:
            all_standings = {}
            
        all_standings["mlr"] = standings
        all_standings["last_updated"] = datetime.now().isoformat()
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_standings, f, ensure_ascii=False, indent=4)
            
        print(f"Successfully scraped {len(standings)} teams for MLR standings.")
    except KeyError as e:
        print(f"Could not find standings data in JSON: {e}")

def scrape_players():
    # チームリスト (スラグ)
    team_slugs = [
        "anthem-rc-6675", "chicago-hounds-6631", "dallas-jackals-6629",
        "houston-sabercats-1502", "miami-sharks-6632", "new-england-free-jacks-2625",
        "nola-gold-311", "old-glory-dc", "rfcl-a-6674", "san-diego-legion-313",
        "seattle-seawolves", "utah-warriors-314"
    ]
    
    all_players = []
    
    for slug in team_slugs:
        url = f"https://www.majorleague.rugby/teams/{slug}/squad/"
        print(f"Scraping squad for {slug}...")
        data = get_next_data(url)
        if not data:
            continue
            
        try:
            # ページ内のリンクから選手リストを取得する場合もあれば、JSON内に含まれている場合もある
            # squad ページの場合は pageProps.data.squad にあるはず
            squad_data = data["props"]["pageProps"]["data"].get("squad", [])
            if not squad_data:
                # 構造が違う場合は playerLinks などを探す
                continue
                
            for p in squad_data:
                # 選手個別ページのデータを取得するために URL を生成
                p_slug = p.get("slug")
                if not p_slug: continue
                
                player_url = f"https://www.majorleague.rugby/players/{p_slug}"
                print(f"  Fetching player: {p.get('firstName')} {p.get('lastName')}...")
                p_data = get_next_data(player_url)
                if not p_data: continue
                
                details = p_data["props"]["pageProps"]["data"].get("player", {})
                
                all_players.append({
                    "First_Name": details.get("firstName", ""),
                    "Last_Name": details.get("lastName", ""),
                    "Full_Name": f"{details.get('firstName', '')} {details.get('lastName', '')}",
                    "Position": details.get("position", ""),
                    "Height": details.get("height", ""), # cm
                    "Weight": details.get("weight", ""), # kg
                    "Birth_Date": details.get("birthDate", ""), # YYYY-MM-DD
                    "Age": details.get("age", ""),
                    "Country": details.get("nationality", ""),
                    "Team": slug,
                    "League": "MLR",
                    "URL": player_url
                })
                time.sleep(0.5) # 負荷軽減
        except Exception as e:
            print(f"  Error processing squad {slug}: {e}")
            
    # CSV 保存
    import pandas as pd
    df = pd.DataFrame(all_players)
    output_path = "data_sources/mlr_players_raw.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Saved {len(all_players)} players to {output_path}")

if __name__ == "__main__":
    scrape_standings()
    scrape_players()
