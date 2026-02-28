
import urllib.request
import re
import ssl

def fetch_url(url):
    try:
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

url = "https://www.itsrugby.co.uk/player_28888.html"
content = fetch_url(url)

if content:
    print("Testing regex extraction...")
    # Regex to capture Season, Team, Matches (P)
    # Assuming P is the next cell after Team
    regex = r'>(\d{2}/\d{2})<.*?href="[^"]*teams/[^"]*".*?>(.*?)</a>\s*</td>\s*<td[^>]*>(.*?)</td>'
    
    matches = re.findall(regex, content, re.DOTALL)
    print(f"Found {len(matches)} entries.")
    for m in matches:
        season, team, played = m
        print(f"  {season}: {team} (Games: {played})")
else:
    print("Failed to fetch.")
