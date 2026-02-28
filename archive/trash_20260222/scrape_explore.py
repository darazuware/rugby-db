
import urllib.request
import urllib.parse
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def check(url):
    print(f"Checking: {url}")
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    )
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            print(f"  Status: {response.status}")
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"  Error: {e}")
        return ""

def main():
    base = "https://www.itsrugby.co.uk"
    
    # Check Homepage
    home = check(base + "/")
    with open("homepage.txt", "w") as f:
        f.write(home)
    print("Saved homepage.txt")
    
    # Potential search endpoints
    endpoints = [
        "/players_search.html?joueur=Mark+Telea",
        "/player-search.html?q=Mark+Telea",
        "/search.html?q=Mark+Telea",
        "/recherche.html?recherche=Mark+Telea",
        "/players/mark-telea.html", # Guess
    ]
    
    for ep in endpoints:
        check(base + ep)

if __name__ == "__main__":
    main()
