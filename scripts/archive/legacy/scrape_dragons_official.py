import requests
from bs4 import BeautifulSoup
import json
import time
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

URLS = [
    "https://dragonsrfc.wales/teams/player/dragons/190938/harri-ackerman.html",
    "https://dragonsrfc.wales/teams/player/dragons/190941/huw-anderson.html",
    "https://dragonsrfc.wales/teams/player/dragons/204256/niall-armstrong.html",
    "https://dragonsrfc.wales/teams/player/dragons/150632/james-benjamin.html",
    "https://dragonsrfc.wales/teams/player/dragons/197953/burrows-burrows.html",
    "https://dragonsrfc.wales/teams/player/dragons/187444/ben-carter.html",
    "https://dragonsrfc.wales/teams/player/dragons/187394/brodie-coghlan.html",
    "https://dragonsrfc.wales/teams/player/dragons/179366/chris-coleman.html",
    "https://dragonsrfc.wales/teams/player/dragons/175641/seb-davies.html",
    "https://dragonsrfc.wales/teams/player/dragons/183324/tinus-de-beer.html",
    "https://dragonsrfc.wales/teams/player/dragons/152087/elliot-dee.html",
    "https://dragonsrfc.wales/teams/player/dragons/211354/cebo-dlamini.html",
    "https://dragonsrfc.wales/teams/player/dragons/184963/levi-douglas.html",
    "https://dragonsrfc.wales/teams/player/dragons/181171/rio-dyer.html",
    "https://dragonsrfc.wales/teams/player/dragons/181244/cai-evans.html",
    "https://dragonsrfc.wales/teams/player/dragons/188741/che-hope.html",
    "https://dragonsrfc.wales/teams/player/dragons/197886/robert-hunt.html",
    "https://dragonsrfc.wales/teams/player/dragons/197372/fine-inisi.html",
    "https://dragonsrfc.wales/teams/player/dragons/156908/wyn-jones.html",
    "https://dragonsrfc.wales/teams/player/dragons/151341/rhodri-jones.html",
    "https://dragonsrfc.wales/teams/player/dragons/158389/harrison-keddie.html",
    "https://dragonsrfc.wales/teams/player/dragons/197157/dylan-keller-griffiths.html",
    "https://dragonsrfc.wales/teams/player/dragons/190573/barny-langton-cryer.html",
    "https://dragonsrfc.wales/teams/player/dragons/155311/dillon-lewis.html",
    "https://dragonsrfc.wales/teams/player/dragons/175569/shane-lewis-hughes.html",
    "https://dragonsrfc.wales/teams/player/dragons/189066/morgan-lloyd.html",
    "https://dragonsrfc.wales/teams/player/dragons/191882/jac-lloyd.html",
    "https://dragonsrfc.wales/teams/player/dragons/192726/mackenzie-martin.html",
    "https://dragonsrfc.wales/teams/player/dragons/197862/rodrigo-martinez.html",
    "https://dragonsrfc.wales/teams/player/dragons/158416/angus-obrien.html",
    "https://dragonsrfc.wales/teams/player/dragons/187162/aneurin-owen.html",
    "https://dragonsrfc.wales/teams/player/dragons/187888/fetuli-paea.html",
    "https://dragonsrfc.wales/teams/player/dragons/189551/david-richards.html",
    "https://dragonsrfc.wales/teams/player/dragons/179244/george-roberts.html",
    "https://dragonsrfc.wales/teams/player/dragons/163238/jared-rosser.html",
    "https://dragonsrfc.wales/teams/player/dragons/185575/ewan-rosser.html",
    "https://dragonsrfc.wales/teams/player/dragons/189661/sam-scarfe.html",
    "https://dragonsrfc.wales/teams/player/dragons/145570/matthew-screech.html",
    "https://dragonsrfc.wales/teams/player/dragons/184984/aaron-wainwright.html",
    "https://dragonsrfc.wales/teams/player/dragons/189093/joe-westwood.html",
    "https://dragonsrfc.wales/teams/player/dragons/144149/rhodri-williams.html",
    "https://dragonsrfc.wales/teams/player/dragons/192331/ryan-woodman.html",
    "https://dragonsrfc.wales/teams/player/dragons/183659/luke-yendle.html",
    "https://dragonsrfc.wales/teams/player/dragons/140061/thomas-young.html"
]

def scrape_player(url):
    print(f"Scraping {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        name_elem = soup.select_one('.player__name')
        name = name_elem.get_text(strip=True) if name_elem else ""
        
        pos_elem = soup.select_one('.player__position')
        position = pos_elem.get_text(strip=True) if pos_elem else ""
        
        height_elem = soup.select_one('strong[itemprop="height"]')
        height = height_elem.get_text(strip=True) if height_elem else ""
        
        weight_elem = soup.select_one('strong[itemprop="weight"]')
        weight = weight_elem.get_text(strip=True) if weight_elem else ""
        
        dob_elem = soup.select_one('strong[itemprop="birthDate"]')
        dob = dob_elem.get_text(strip=True) if dob_elem else ""
        
        honours = ""
        info_rows = soup.select('.player__info-row')
        for row in info_rows:
            if "Honours:" in row.get_text():
                hon_elem = row.select_one('strong')
                if hon_elem:
                    honours = hon_elem.get_text(strip=True)
                break
        
        bio_elems = soup.select('.player__description p')
        bio = "\n\n".join([p.get_text(strip=True) for p in bio_elems])
        
        return {
            "name": name,
            "position": position,
            "height": height,
            "weight": weight,
            "dob": dob,
            "honours": honours,
            "career": bio,
            "url": url
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def main():
    results = []
    for url in URLS:
        data = scrape_player(url)
        if data:
            results.append(data)
        time.sleep(1) # Be nice
    
    output_path = "/Users/ktamatzmoto/.gemini/antigravity/brain/0a4cb5ef-2a47-4d0d-afe7-2dd511f55541/dragons_official_full.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(results)} players to {output_path}")

if __name__ == "__main__":
    main()
