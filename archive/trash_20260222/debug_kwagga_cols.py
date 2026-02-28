
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
    print("Content fetched. analyzing row cells...")
    # Find match for >South Africa< link
    match = re.search(r'>(\d{2}/\d{2})<.*?href="[^"]*teams/[^"]*".*?>\s*South Africa\s*</a>', content, re.DOTALL)
    if match:
        print(f"Found row for season {match.group(1)}")
        start_index = match.end()
        # Find subsequent cells
        chunk = content[start_index:start_index+5000] # Grab enough context
        
        # Split by <td...
        cells = re.findall(r'<td[^>]*>(.*?)</td>', chunk, re.DOTALL)
        for i, cell_content in enumerate(cells):
            clean_content = re.sub(r'<[^>]+>', '', cell_content).strip()
            print(f"Cell {i+1}: '{clean_content}' (Raw: {cell_content[:20]}...)")
    else:
        print("No South Africa row found.")
else:
    print("Failed to fetch.")
