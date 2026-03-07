import requests
from bs4 import BeautifulSoup
import json
import os
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://super.rugby/"
}

def scrape_team_details(team_id):
    # Season 2026 as per user request
    url = f"https://super.rugby/superrugby/teams/?competition=205&season=2026&team={team_id}"
    print(f"Scraping team {team_id} from {url}...")
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {
            "team_id": team_id,
            "stadium": "",
            "based": "",
            "official_website": "",
            "players": []
        }
        
        # Based on subagent investigation:
        # Stadium follows "Home:"
        # Based follows "Based:"
        # Website is in a button
        
        info_section = soup.get_text()
        
        stadium_match = re.search(r'Home:\s*(.*)', info_section)
        if stadium_match:
            details["stadium"] = stadium_match.group(1).split('\n')[0].strip()
            
        based_match = re.search(r'Based:\s*(.*)', info_section)
        if based_match:
            details["based"] = based_match.group(1).split('\n')[0].strip()
            
        # Find website button
        website_btn = soup.find('a', string=re.compile(r'Team website', re.I)) or soup.select_one('a.btn-team-website')
        if website_btn:
            details["official_website"] = website_btn['href']
            
        return details
    except Exception as e:
        print(f"Error scraping team {team_id}: {e}")
        return None

import re

def main():
    standings_path = "data/standings.json"
    if not os.path.exists(standings_path):
        print(f"Error: {standings_path} not found.")
        return
        
    with open(standings_path, "r", encoding="utf-8") as f:
        all_standings = json.load(f)
        
    sr_teams = all_standings.get("super-rugby", [])
    if not sr_teams:
        print("No Super Rugby teams found in standings.")
        return
        
    team_data = {}
    for team in sr_teams:
        team_id = team.get("team_id")
        if not team_id: continue
        
        details = scrape_team_details(team_id)
        if details:
            details["team_name"] = team.get("team_name")
            team_data[team_id] = details
            
        # Be nice to the server
        time.sleep(1)
        
    output_path = "data/super_rugby_teams_deep.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(team_data, f, ensure_ascii=False, indent=2)
        
    print(f"Deep team data saved to {output_path}")

if __name__ == "__main__":
    main()
