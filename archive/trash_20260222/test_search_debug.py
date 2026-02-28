
import urllib.request
import urllib.parse
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def search_player_debug(first_name, last_name):
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
            filename = f"search_debug_{last_name}.html"
            with open(filename, "w") as f:
                f.write(content)
            print(f"Saved response to {filename}")

    except Exception as e:
        print(f"  Error: {e}")

def main():
    search_player_debug("Mark", "Telea")

if __name__ == "__main__":
    main()
