import requests
from bs4 import BeautifulSoup
import json
import os
import time

# スーパーラグビー公式サイトのベースURL
BASE_URL = "https://super.rugby"
# 2026シーズンのコンペティションIDとシーズンID (ユーザー提供のURLより)
# https://super.rugby/superrugby/teams/?competition=205&season=2026
TEAMS_URL = f"{BASE_URL}/superrugby/teams/?competition=205&season=2026"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_team_list():
    """公式サイトからチーム一覧と各チームの公式サイトURLを取得する"""
    print(f"Fetching teams from {TEAMS_URL}...")
    try:
        response = requests.get(TEAMS_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        teams = []
        links = soup.select('a.btn.btn-primary.btn-block[href^="?competition="]')
        seen_teams = set()
        
        for link in links:
            href = link['href']
            team_id = href.split('team=')[-1].split('&')[0]
            if team_id not in seen_teams:
                # チーム個別ページへ遷移して Team Website URL を取得する
                full_team_page_url = f"{BASE_URL}/superrugby/teams/{href}" if href.startswith('?') else href
                print(f"  Getting official website for team {team_id} from {full_team_page_url}...")
                
                try:
                    t_resp = requests.get(full_team_page_url, headers=HEADERS)
                    t_soup = BeautifulSoup(t_resp.text, 'html.parser')
                    # 'TEAM WEBSITE' というテキストを持つリンクを探す
                    official_link = t_soup.find('a', string=lambda t: t and 'TEAM WEBSITE' in t.upper())
                    if not official_link:
                        # target="_blank" の btn-primary を予備で探す
                        official_link = t_soup.select_one('a.btn.btn-primary[target="_blank"]')
                    
                    if official_link:
                        official_url = official_link['href']
                        # チーム名を取得
                        team_name_el = t_soup.select_one('h1')
                        team_name = team_name_el.get_text(strip=True) if team_name_el else "Unknown Team"
                        
                        teams.append({
                            "id": team_id,
                            "name": team_name,
                            "official_url": official_url
                        })
                        seen_teams.add(team_id)
                except Exception as e:
                    print(f"  Error getting official site for {team_id}: {e}")
        
        return teams
    except Exception as e:
        print(f"Error fetching team list: {e}")
        return []

def scrape_team_players(team):
    """チーム公式サイトから選手一覧を取得する (プラットフォーム別)"""
    url = team['official_url']
    print(f"Scraping players for {team['name']} from {url}...")
    
    # 適切なスクワッドページURLを推測/構築
    squad_url = url
    if 'blues.rugby' in url: squad_url = "https://www.blues.rugby/blues-men-squad"
    elif 'brumbies.rugby' in url: squad_url = "https://brumbies.rugby/teams/super-rugby"
    elif 'chiefs.co.nz' in url: squad_url = "https://chiefs.co.nz/team/gallagher-chiefs-squad/"
    elif 'hurricanes.co.nz' in url: squad_url = "https://www.hurricanes.co.nz/squad/2024-hurricanes"
    elif 'crusaders.co.nz' in url: squad_url = "https://crusaders.co.nz/team/crusaders2025"
    elif 'drua.rugby' in url: squad_url = "https://drua.rugby/teams/men/squad-list"
    elif 'thehighlanders.co.nz' in url: squad_url = "https://thehighlanders.co.nz/our-teams/highlanders-super-rugby"
    elif 'waratahs.rugby' in url: squad_url = "https://waratahs.rugby/teams/nsw-waratahs"
    elif 'reds.rugby' in url: squad_url = "https://reds.rugby/teams/reds-mens"
    elif 'westernforce.rugby' in url: squad_url = "https://westernforce.rugby/teams/mens"
    elif 'moanapasifika.co.nz' in url: squad_url = "https://moanapasifika.co.nz/players/"
    
    try:
        response = requests.get(squad_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        players = []
        
        # Squarespace (Blues形式)
        if 'blues.rugby' in squad_url:
            cards = soup.select('div.gallery-caption-wrapper')
            for card in cards:
                p_el = card.select_one('p.gallery-caption-content')
                if p_el:
                    text = p_el.get_text(separator="\n").split('\n')
                    if len(text) >= 1:
                        players.append({"name": text[0].strip(), "position": text[1].strip() if len(text) > 1 else ""})

        # Rugby Xplorer (Brumbies形式)
        elif 'brumbies.rugby' in squad_url or 'reds.rugby' in squad_url or 'waratahs.rugby' in squad_url:
            links = soup.select('a[href^="/players/"]')
            for pl in links:
                spans = pl.select('span')
                if len(spans) >= 2:
                    players.append({"name": spans[0].get_text(strip=True), "position": spans[1].get_text(strip=True)})

        # WordPress / Custom (Chiefs/Hurricanes形式)
        else:
            # 汎用的な a タグベースの抽出 (名前が入っていそうなリンク)
            player_links = soup.select('a[href*="/player/"], a[href*="/players/"]')
            for pl in player_links:
                name = pl.get_text(strip=True)
                if name and len(name.split()) >= 2:
                    players.append({"name": name, "url": pl['href']})

        return players
    except Exception as e:
        print(f"Error scraping players from {squad_url}: {e}")
        return []

def main():
    teams = get_team_list()
    if not teams:
        print("No teams found. Check URL or selector.")
        return

    all_data = []
    for team in teams:
        players = scrape_team_players(team)
        all_data.append({
            "team_id": team['id'],
            "team_name": team['name'],
            "players": players
        })
        time.sleep(1) # 負荷軽減

    output_file = "data_sources/super_rugby_official_data.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(all_data)} teams data to {output_file}")

if __name__ == "__main__":
    main()
