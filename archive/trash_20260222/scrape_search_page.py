
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
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            print(f"  Status: {response.status}")
            content = response.read().decode('utf-8', errors='ignore')
            # Look for form action
            if "<form" in content:
                print("  Found form tag.")
            if "action=" in content:
                print("  Found action attribute.")
            return content
    except Exception as e:
        print(f"  Error: {e}")
        return ""

def main():
    base = "https://www.itsrugby.co.uk"
    content = check(base + "/playersearch.html")
    
    if content:
        with open("playersearch.html", "w") as f:
            f.write(content)
        print("Saved playersearch.html")

if __name__ == "__main__":
    main()
