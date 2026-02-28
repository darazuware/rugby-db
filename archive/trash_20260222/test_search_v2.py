
import urllib.request
import urllib.parse
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def search_player_v2(first_name, last_name):
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
            # New regex for relative links like player_38490.html
            links = re.findall(r'href="(player_\d+\.html)"', content)
            unique_links = list(set(links))
            
            print(f"  Found {len(unique_links)} unique player links.")
            for link in unique_links:
                full_link = urllib.parse.urljoin(url, link)
                print(f"    - {link} -> {full_link}")
                check_player_page(full_link)
                
            return unique_links
    except Exception as e:
        print(f"  Error: {e}")
        return []

def check_player_page(url):
    print(f"  Checking player page: {url}")
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, context=ctx) as response:
             print(f"    Status: {response.status}")
             print(f"    Final URL: {response.geturl()}")
    except Exception as e:
        print(f"    Error: {e}")

def main():
    search_player_v2("Mark", "Telea")
    search_player_v2("Manaaki", "Selby-Rickit")

if __name__ == "__main__":
    main()
