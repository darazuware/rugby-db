import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

url = "https://all.rugby/player/bundee-aki"
r = requests.get(url, headers=HEADERS)
soup = BeautifulSoup(r.text, 'html.parser')

print(f"URL: {url}")
print(f"Status Code: {r.status_code}")

# Print potential containers
for selector in ['#bio .bio p', '.player-bio p', '.bio p', '.bio-info', 'section#bio']:
    elem = soup.select_one(selector)
    print(f"Selector '{selector}': {'Found' if elem else 'Not Found'}")
    if elem:
        print(f"Content: {elem.get_text()[:100]}...")

# If nothing found, print first 500 chars of body
if not soup.select_one('#bio'):
    print("Body snippet:")
    print(r.text[:500])
