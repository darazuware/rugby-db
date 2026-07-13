import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://top14.lnr.fr/"
}

def scrape_top14_club_details(slug):
    url = f"https://top14.lnr.fr/club/{slug}/informations"
    print(f"Scraping Top 14 club {slug} from {url}...")
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {
            "slug": slug,
            "stadium": "",
            "region": "",
            "official_website": ""
        }
        
        # New robust logic: find all club-info-field and check labels
        fields = soup.select('.club-info-field')
        for field in fields:
            label_el = field.select_one('.club-info-field__label')
            if not label_el: continue
            
            label_text = label_el.get_text(strip=True).lower()
            content_el = field.select_one('.club-info-field__content')
            if not content_el: continue
            
            if 'nom' in label_text: # stadium name
                # Check if it's inside a block with "STADE" header
                stade_block = field.find_parent('div', class_='club-stade')
                if stade_block:
                    details["stadium"] = content_el.get_text(strip=True)
            elif 'site web' in label_text:
                link = content_el if content_el.name == 'a' else content_el.find('a')
                if link:
                    details["official_website"] = link['href']
                else:
                    details["official_website"] = content_el.get_text(strip=True)
            elif 'adresse' in label_text:
                details["region"] = content_el.get_text(separator=" ", strip=True)
                
        return details
    except Exception as e:
        print(f"Error scraping Top 14 club {slug}: {e}")
        return None

def main():
    # List of slugs identified from read_url_content
    top14_slugs = [
        "clermont", "bayonne", "castres", "lyon", "montpellier", 
        "toulon", "racing-92", "pau", "paris", "la-rochelle", 
        "toulouse", "perpignan", "bordeaux-begles", "vannes" # Vannes is likely the 14th
    ]
    
    team_data = {}
    for slug in top14_slugs:
        details = scrape_top14_club_details(slug)
        if details:
            team_data[slug] = details
            
        # Be nice
        time.sleep(1)
        
    output_path = "data/top14_teams_deep.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(team_data, f, ensure_ascii=False, indent=2)
        
    print(f"Top 14 deep data saved to {output_path}")

if __name__ == "__main__":
    main()
