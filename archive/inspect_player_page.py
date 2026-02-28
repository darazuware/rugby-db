import requests
from bs4 import BeautifulSoup

url = "https://league-one.jp/player/484444"
print(f"Fetching {url}...")

try:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 1. League One Caps
    # Look for "リーグワンキャップ数" text and associated value
    print("\n--- Caps Section ---")
    caps_el = soup.find(string=lambda t: t and "リーグワンキャップ数" in t)
    if caps_el:
        parent = caps_el.parent
        print(f"Found Caps Label: {caps_el.strip()}")
        print(f"Parent HTML: {parent.prettify()}")
        # Traverse up/down to find value
        value_el = parent.find_next_sibling() or parent.find('span') or parent.parent.find(class_=lambda x: x and 'value' in x)
        if value_el: 
            print(f"Potential Value Element: {value_el.strip() if isinstance(value_el, str) else value_el.text.strip()}")
            
    # 8. Dump all text to file for manual inspection
    print("\n--- Dumping Text ---")
    with open('page_text_dump.txt', 'w', encoding='utf-8') as f:
        f.write(soup.get_text(separator='\n', strip=True))
    print("Dumped text to page_text_dump.txt")

except Exception as e:
    print(f"Error: {e}")
