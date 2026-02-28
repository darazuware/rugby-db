
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
    print("Content fetched. Analyzing Summary Table Row...")
    # Find a row that starts with Season 23/24 and contains South Africa
    # Look for >23/24<
    match = re.search(r'>23/24<.*?South Africa', content, re.DOTALL)
    if match:
        print(f"Found row for 23/24 South Africa at {match.start()}")
        # Grab context starting from Season >23/24<
        start_index = match.start()
        chunk = content[start_index:start_index+2000]
        
        # Split by <td
        cells = re.findall(r'<td[^>]*>(.*?)</td>', chunk, re.DOTALL)
        for i, cell_content in enumerate(cells):
            clean = re.sub(r'<[^>]+>', '', cell_content).strip()
            print(f"Cell {i+1}: '{clean}'")
    else:
        print("Row not found.")
