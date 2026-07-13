import requests
from bs4 import BeautifulSoup
import json
import os
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.unitedrugby.com/"
}

def scrape_urc_club_details(slug):
    url = f"https://stats.unitedrugby.com/clubs/{slug}"
    print(f"Scraping URC club {slug} from {url}...")
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {
            "slug": slug,
            "stadium": "",
            "country": "",
            "official_website": ""
        }
        
        # Based on subagent investigation:
        # Home Ground section
        # Country section
        # Clubs site button
        
        # Find labels and their following text
        labels = soup.find_all('div', class_=re.compile(r'label|title', re.I))
        for label in labels:
            text = label.get_text(strip=True).lower()
            if 'home ground' in text:
                val = label.find_next_sibling('div')
                if val: details["stadium"] = val.get_text(strip=True)
            elif 'country' in text:
                val = label.find_next_sibling('div')
                if val: details["country"] = val.get_text(strip=True)
                
        # Find website button
        website_btn = soup.find('a', string=re.compile(r'Clubs site', re.I))
        if website_btn:
            details["official_website"] = website_btn['href']
            
        return details
    except Exception as e:
        print(f"Error scraping URC club {slug}: {e}")
        return None

import re

def main():
    standings_path = "data/standings.json"
    if not os.path.exists(standings_path):
        print(f"Error: {standings_path} not found.")
        return
        
    with open(standings_path, "r", encoding="utf-8") as f:
        all_standings = json.load(f)
        
    urc_teams = all_standings.get("urc", [])
    if not urc_teams:
        print("No URC teams found in standings.")
        return
        
    team_data = {}
    for team in urc_teams:
        slug = team.get("slug")
        if not slug: continue
        
        details = scrape_urc_club_details(slug)
        if details:
            details["team_name"] = team.get("team_name")
            team_data[slug] = details
            
        # Be nice
        time.sleep(1)
        
    output_path = "data/urc_teams_deep.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(team_data, f, ensure_ascii=False, indent=2)
        
    print(f"URC deep data saved to {output_path}")

if __name__ == "__main__":
    main()
