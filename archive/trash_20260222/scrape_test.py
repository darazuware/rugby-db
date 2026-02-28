
import urllib.request
import urllib.parse
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(
        url, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
    )
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error: {e}")
        return ""

def main():
    target = "Mark Telea"
    url = f"https://www.itsrugby.co.uk/players_search.html?joueur={urllib.parse.quote(target)}"
    print(f"Fetching: {url}")
    
    html = fetch(url)
    
    # Extract Title
    title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    if title:
        print(f"Title: {title.group(1)}")
    else:
        print("No Title found")
        
    # Check if redirect happened (meta refresh or just content)
    # Check for specific player content
    if "Mark Telea" in html:
        print("Found player name in content.")
        
    # Look for "International" section
    if "International details" in html or "Test Match" in html:
        print("Found International section.")
        
    # Look for tables
    tables = re.findall(r'<table', html, re.IGNORECASE)
    print(f"Found {len(tables)} tables.")
    
    # Try to extract career rows (Year, Team)
    # These often look like: <td>2020-2021</td>
    years = re.findall(r'<td>(\d{4}-\d{4})</td>', html)
    print(f"Found years: {years[:10]}...")

    # Team extraction is harder with regex on raw HTML without structure awareness.
    # But usually it's in a specific table class.

if __name__ == "__main__":
    main()
