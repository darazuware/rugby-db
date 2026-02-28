
import urllib.request
import urllib.parse
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(
        url, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Referer': 'https://www.itsrugby.co.uk/'
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
    # Autocomplete endpoint found in previous research
    url = f"https://www.itsrugby.co.uk/modules/site/application/ajax/search_autocompletion.php?q={urllib.parse.quote(target)}"
    print(f"Fetching: {url}")
    
    content = fetch(url)
    print("Content:")
    print(content)

if __name__ == "__main__":
    main()
