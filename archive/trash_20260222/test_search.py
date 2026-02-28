
import urllib.request
import urllib.parse
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def search_player(first_name, last_name):
    url = "https://www.itsrugby.co.uk/playersearchlist.html"
    data = urllib.parse.urlencode({
        'name': last_name,
        'fname': first_name
    }).encode('utf-8')
    
    print(f"Searching for: {first_name} {last_name}")
    req = urllib.request.Request(
        url, 
        data=data,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            content = response.read().decode('utf-8', errors='ignore')
            # Look for links to player pages
            # Pattern might be /players/firstname-lastname-id.html
            links = re.findall(r'href="([^"]*players/[^"]*)"', content)
            unique_links = list(set(links))
            
            print(f"  Found {len(unique_links)} unique player links.")
            for link in unique_links:
                print(f"    - {link}")
                
            return unique_links
    except Exception as e:
        print(f"  Error: {e}")
        return []

def main():
    search_player("Mark", "Telea")
    search_player("Manaaki", "Selby-Rickit")
    search_player("Ardie", "Savea") # Common name test

if __name__ == "__main__":
    main()
