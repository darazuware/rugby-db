import requests
from bs4 import BeautifulSoup

url = "https://league-one.jp/team/98?t1=2"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

print(f"Status Code: {response.status_code}")
print(f"Title: {soup.title.string if soup.title else 'No Title'}")

# Check for #team-profile
profile = soup.find(id='team-profile')
if profile:
    print("Found #team-profile")
    dls = profile.find_all('dl')
    print(f"Found {len(dls)} dl elements under #team-profile")
    for dl in dls:
        dts = dl.find_all('dt')
        dds = dl.find_all('dd')
        for dt, dd in zip(dts, dds):
            print(f"{dt.text.strip()}: {dd.text.strip()}")
else:
    print("Could NOT find #team-profile")
    # Search for any dl
    dls = soup.find_all('dl')
    print(f"Found {len(dls)} dl elements in the whole page")
