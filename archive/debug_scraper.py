import requests
import re
import json

URL = "https://league-one.jp/team/100"
print(f"Fetching {URL}...")

try:
    resp = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
    print(f"Status: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('Content-Type')}")
    html = resp.text
    print(f"Length: {len(html)}")
    
    # Check for "player"
    if "player" in html:
        print("Found 'player' in HTML.")
    else:
        print("Did NOT find 'player' in HTML.")
        
    # extract hrefs
    hrefs = re.findall(r'href="(.*?)"', html)
    print(f"Total hrefs: {len(hrefs)}")
    
    player_links = [h for h in hrefs if "player" in h]
    print(f"Player links found: {len(player_links)}")
    for p in player_links[:5]:
        print(f" - {p}")

    # Check teams_enriched.json
    print("\nChecking teams_enriched.json:")
    try:
        with open('teams_enriched.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Print first key's data
            first_key = list(data.keys())[0]
            print(f"{first_key}: {data[first_key]}")
    except Exception as e:
        print(f"Error reading teams_enriched.json: {e}")

except Exception as e:
    print(f"Error: {e}")
