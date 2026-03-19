import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import time
import pandas as pd

def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

def scrape_standings_allrugby():
    url = "https://all.rugby/tournament/mlr-2024/table"
    print(f"Scraping standings from {url}...")
    soup = get_soup(url)
    if not soup: return []
    
    standings = []
    table = soup.find("table")
    if not table: return []
    
    rows = table.find_all("tr")[1:]
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 10: continue
        
        team_link = cols[1].find("a")
        team_name = team_link.get_text(strip=True) if team_link else cols[1].get_text(strip=True)
        
        standings.append({
            "rank": cols[0].get_text(strip=True),
            "team": team_name,
            "played": cols[2].get_text(strip=True),
            "won": cols[3].get_text(strip=True),
            "drawn": cols[4].get_text(strip=True),
            "lost": cols[5].get_text(strip=True),
            "pts_for": cols[6].get_text(strip=True),
            "pts_against": cols[7].get_text(strip=True),
            "diff": cols[8].get_text(strip=True),
            "try_bonus": cols[9].get_text(strip=True),
            "loss_bonus": cols[10].get_text(strip=True),
            "points": cols[11].get_text(strip=True)
        })
        
    json_path = "data/standings.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            all_st = json.load(f)
    else:
        all_st = {}
    
    all_st["mlr"] = standings
    all_st["last_updated"] = datetime.now().isoformat()
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_st, f, ensure_ascii=False, indent=4)
    print(f"Scraped {len(standings)} teams for standings.")
    return standings

def scrape_results_allrugby():
    url = "https://all.rugby/tournament/mlr-2024/fixtures-results"
    print(f"Scraping results from {url}...")
    soup = get_soup(url)
    if not soup: return
    
    results = []
    calendrier = soup.find("div", class_="calendrier")
    if not calendrier: return
        
    match_lists = calendrier.find_all("ul", class_="matchs")
    for ul in match_lists:
        current_date = ""
        for li in ul.children:
            if li.name == "li" and "sep_dat" in li.get("class", []):
                current_date = li.get_text(strip=True)
            elif li.name == "li" and "clearfix" in li.get("class", []):
                a_mat = li.find("a", class_="mat")
                if not a_mat: continue
                
                home_div = a_mat.find("div", class_=re.compile(r"log.*txtright"))
                away_div = a_mat.find("div", class_=re.compile(r"log.*txtleft"))
                score_div = a_mat.find("div", class_=re.compile(r"res.*txtcenter"))
                
                if home_div and away_div and score_div:
                    h_team = home_div.get_text(strip=True)
                    a_team = away_div.get_text(strip=True)
                    score_text = score_div.get_text(strip=True)
                    
                    if " - " in score_text:
                        h_score, a_score = score_text.split(" - ", 1)
                        results.append({
                            "date": current_date,
                            "home_team": h_team,
                            "away_team": a_team,
                            "home_score": h_score.strip(),
                            "away_score": a_score.strip(),
                            "league": "MLR"
                        })
            
    if results:
        df = pd.DataFrame(results)
        df.to_csv("data_sources/mlr_results_2024.csv", index=False, encoding="utf-8-sig")
        print(f"Scraped {len(results)} matches.")

def scrape_squads_allrugby():
    url = "https://all.rugby/tournament/mlr-2024/"
    soup = get_soup(url)
    if not soup: return
    
    team_links = []
    links = soup.find_all("a", href=re.compile(r"/club/"))
    for l in links:
        href = l.get("href")
        if href and "/club/" in href:
            # 修正: 正確なスラッグを抽出
            slug = href.split("/club/")[-1].split("/")[0]
            squad_url = f"/club/{slug}/squad"
            if squad_url not in team_links:
                team_links.append(squad_url)
            
    all_players = []
    # MLR以外のチームが混ざるのを防ぐためのホワイトリスト(2024参加チーム)
    mlr_2024_slugs = [
        "anthem-rc", "chicago-hounds", "dallas-jackals", "houston-sabercats",
        "miami", "new-england-free-jacks", "nola-gold", "old-glory", "rfc-los-angeles",
        "san-diego", "seattle-seawolves", "utah-warriors"
    ]
    
    for t_url in team_links:
        slug = t_url.split("/club/")[-1].split("/")[0]
        if slug not in mlr_2024_slugs: continue
        
        full_url = "https://all.rugby" + t_url
        print(f"Scraping squad from {full_url}...")
        t_soup = get_soup(full_url)
        if not t_soup: continue
        
        h1 = t_soup.find("h1")
        team_name = h1.get_text(strip=True).replace("Squad", "").strip() if h1 else slug
        
        table = t_soup.find("table")
        if not table: continue
        
        player_rows = table.find_all("tr")[1:]
        for p_row in player_rows:
            cols = p_row.find_all("td")
            if len(cols) < 5: continue
            
            name_link = cols[1].find("a")
            if not name_link: continue
            
            p_name = name_link.get_text(strip=True)
            p_url = "https://all.rugby" + name_link.get("href")
            
            all_players.append({
                "Full_Name": p_name,
                "Position": cols[2].get_text(strip=True),
                "Age": cols[3].get_text(strip=True),
                "Height": cols[4].get_text(strip=True) if len(cols) > 4 else "",
                "Weight": cols[5].get_text(strip=True) if len(cols) > 5 else "",
                "Team": team_name,
                "League": "MLR",
                "Source_URL": p_url
            })
        time.sleep(0.5)
        
    if all_players:
        df = pd.DataFrame(all_players)
        df.to_csv("data_sources/mlr_players_allrugby_2024.csv", index=False, encoding="utf-8-sig")
        print(f"Scraped {len(all_players)} players.")

if __name__ == "__main__":
    scrape_standings_allrugby()
    scrape_results_allrugby()
    scrape_squads_allrugby()
