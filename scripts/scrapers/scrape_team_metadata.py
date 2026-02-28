import json
import re
import time
import urllib.request
from team_data_config import TEAM_METADATA

def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_logo(html, team_name):
    # Try multiple patterns for logo
    # Pattern 1: og:image
    og_match = re.search(r'<meta property="og:image" content="(.*?)"', html)
    if og_match:
        return og_match.group(1)
    
    # Pattern 2: img inside header or specific div
    # This is harder with regex, but let's try to find an image with the team name or "logo" in filename
    # League One images often are on S3
    logo_match = re.search(r'<img src="(https://league-one.s3.*?)"', html)
    if logo_match:
        return logo_match.group(1)
        
    return None

def extract_socials(html):
    socials = {}
    # Instagram
    insta = re.search(r'href="(https://www\.instagram\.com/[^"/]+/?)"', html)
    if insta and "leagueone_official" not in insta.group(1):
        socials['instagram'] = insta.group(1)
    
    # Twitter/X
    twit = re.search(r'href="(https://(?:twitter\.com|x\.com)/[^"/]+/?)"', html)
    if twit and "LeagueOne_JP" not in twit.group(1):
        socials['twitter'] = twit.group(1)
        
    return socials

def extract_players(html):
    # Extract player URLs from the team page
    # Pattern: <a href="/player/484030"> (Relative) or absolute
    # We want unique URLs
    player_urls = set()
    # Match both relative and absolute w/ or w/o quotes
    matches = re.finditer(r'href=["\']?((?:https://league-one\.jp)?/player/\d+)["\']?', html)
    for m in matches:
        raw = m.group(1)
        if not raw.startswith('http'):
            full_url = f"https://league-one.jp{raw}"
        else:
            full_url = raw
        player_urls.add(full_url)
    return list(player_urls)

print("Scraping team details and player lists...")
enriched_data = {}
all_player_urls = []

for name, data in TEAM_METADATA.items():
    tid = data['id']
    url = f"https://league-one.jp/team/{tid}"
    print(f"Processing {name} ({url})...")
    
    html = fetch_html(url)
    if html:
        logo = extract_logo(html, name)
        socials = extract_socials(html)
        players = extract_players(html)
        
        data['logo'] = logo
        data['socials'] = socials
        data['player_count'] = len(players)
        
        all_player_urls.extend(players)
        
        print(f"  Found Logo: {bool(logo)}")
        print(f"  Found Socials: {list(socials.keys())}")
        print(f"  Found Players: {len(players)}")
    else:
        print("  Failed to fetch.")
    
    enriched_data[name] = data
    time.sleep(1) # Be nice

# Save Team Data
with open('teams_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(enriched_data, f, ensure_ascii=False, indent=2)

# Save Player URLs list
with open('team_player_lists.json', 'w', encoding='utf-8') as f:
    json.dump(list(set(all_player_urls)), f, ensure_ascii=False, indent=2)

print(f"Done! Saved metadata and {len(set(all_player_urls))} unique player URLs.")
