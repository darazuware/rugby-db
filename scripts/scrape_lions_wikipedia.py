import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

PLAYERS = [
    "JC Pretorius", "Siba Qoma", "Darrien Landsberg", "Franco Marais", "PJ Botha",
    "Francke Horn", "Jaco Visagie", "Reinhard Nothnagel", "Etienne Oosthuizen",
    "Leon Lyons", "Morgan Naude", "Ruben Schoeman", "Morne Brandon", "Juan Schoeman",
    "Asenathi Ntlabakanye", "Conrad van Vuuren", "WJ Steenkamp", "Raynard Roets",
    "Janco Uys", "Izan Esterhuizen", "Jarod Cairns", "Heiko Pohlmann", "Ruan Venter",
    "Eddie Davids", "Sebastian Lombard", "Ruan Delport", "Sivu Mabece", "Renzo du Plessis",
    "JR Stopforth", "Dylan Sjoblom", "SJ Kotze", "Tiaan Wessels", "Batho Hlekani",
    "Sibabalwe Mahashe", "RF Schoeman", "Luca Ribbens", "Marno Grobbelaar", 
    "Stian de Bruyn", "Marco Ferreira", "Siya Dube", "Manuel Rass", "Rabz Maxwane",
    "Eduan Keyter", "Angelo Davids", "Lubabalo Dobela", "Gianni Lombard", "Richard Kriel",
    "Chris Smith", "Morne van den Berg", "Rynhardt Jonker", "Tapiwa Mafura",
    "Erich Cronje", "Henco van Wyk", "Quan Horn", "Nico Steyn", "Kelly Mpeku",
    "Bronson Mills", "Sam Francis", "Hasseim Pead", "Layton Horn", "Keagan Smith"
]

def search_wikipedia(name):
    print(f"Searching Wikipedia for {name}...")
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={name} rugby&format=json"
    try:
        r = requests.get(search_url, headers=HEADERS)
        data = r.json()
        if not data['query']['search']:
            return None
            
        page_title = data['query']['search'][0]['title']
        page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
        
        r = requests.get(page_url, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        info = {"name": name, "url": page_url}
        infobox = soup.select_one('.infobox.vcard')
        if not infobox:
            return info
            
        rows = infobox.select('tr')
        for row in rows:
            label = row.select_one('th')
            value = row.select_one('td')
            if label and value:
                l_text = label.get_text(strip=True).lower()
                v_text = value.get_text(strip=True)
                
                if 'born' in l_text:
                    info['dob'] = v_text
                elif 'height' in l_text:
                    info['height'] = v_text
                elif 'weight' in l_text:
                    info['weight'] = v_text
                elif 'position' in l_text:
                    info['position'] = v_text
                elif 'club' in l_text or 'team' in l_text:
                    # Career history is often in a table, skip for now or extract if simple
                    pass
        
        return info
    except Exception as e:
        print(f"Error for {name}: {e}")
        return None

def main():
    output_path = "/Users/ktamatzmoto/.gemini/antigravity/brain/0a4cb5ef-2a47-4d0d-afe7-2dd511f55541/lions_wikipedia_details.json"
    results = []
    
    # Check if we have partial results
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            try:
                results = json.load(f)
            except:
                pass
                
    processed_names = [r['name'] for r in results]
    
    for name in PLAYERS:
        if name in processed_names:
            print(f"Skipping {name} (already processed)")
            continue
            
        data = search_wikipedia(name)
        if data:
            results.append(data)
            # Save every time
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        time.sleep(1)
        
    print(f"Total {len(results)} Lions players details recorded to {output_path}")

if __name__ == "__main__":
    main()
