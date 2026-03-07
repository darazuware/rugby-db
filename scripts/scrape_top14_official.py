import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import re
import os
from urllib.parse import urljoin

# 設定
CLUBS_CONFIG = {
    "トゥールーズ": {
        "squad_url": "https://www.stadetoulousain.fr/equipe/equipe-pro/effectif",
        "player_link_pattern": r"/effectif/[\d]+-", 
        "parser": "toulouse"
    },
    "ボルドー": {
        "squad_url": "https://www.ubbrugby.com/equipes/equipe-premiere/effectif.html",
        "player_link_pattern": r"/effectif/j[\d]+-", 
        "parser": "ubb"
    },
    "ラ・ロシェル": {
        "squad_url": "https://www.staderochelais.com/les-equipes/equipe-premiere/effectif",
        "player_link_pattern": r"/les-equipes/[a-z\-]+/?$", 
        "parser": "larochelle"
    },
    "ラシン92": {
        "squad_url": "https://www.racing92.fr/racingmen/",
        "player_link_pattern": r"/joueurs/[a-z\-]+/?$", 
        "parser": "racing92"
    },
    "トゥーロン": {
        "squad_url": "https://rctoulon.com/effectif-joueurs/",
        "player_link_pattern": r"/joueurs/[a-z\-]+/?$",
        "parser": "toulon",
        "fixed_urls": [
            "https://rctoulon.com/joueurs/tomas-albornoz/", "https://rctoulon.com/joueurs/esteban-abadie/",
            "https://rctoulon.com/joueurs/brian-alainuuese/", "https://rctoulon.com/joueurs/teddy-baubigny/",
            "https://rctoulon.com/joueurs/daniel-brennan/", "https://rctoulon.com/joueurs/oliver-cowie/",
            "https://rctoulon.com/joueurs/juan-ignacio-brex/", "https://rctoulon.com/joueurs/jules-coulon/",
            "https://rctoulon.com/joueurs/pierre-damond/", "https://rctoulon.com/joueurs/marius-domon/",
            "https://rctoulon.com/joueurs/gael-drean/", "https://rctoulon.com/joueurs/mathis-ferte/",
            "https://rctoulon.com/joueurs/antoine-frisch/", "https://rctoulon.com/joueurs/paolo-garbisi/",
            "https://rctoulon.com/joueurs/mateo-garcia/", "https://rctoulon.com/joueurs/beka-gigashvili/",
            "https://rctoulon.com/joueurs/jean-baptiste-gros/", "https://rctoulon.com/joueurs/matthias-halagahu/",
            "https://rctoulon.com/joueurs/melvyn-jaminet/", "https://rctoulon.com/joueurs/giorgi-javakhia/",
            "https://rctoulon.com/joueurs/joe-quere-karaba/", "https://rctoulon.com/joueurs/junior-kpoku/",
            "https://rctoulon.com/joueurs/clovis-le-bail/", "https://rctoulon.com/joueurs/gianmarco-lucchesi/",
            "https://rctoulon.com/joueurs/lewis-ludlam/", "https://rctoulon.com/joueurs/corentin-mezou/",
            "https://rctoulon.com/joueurs/zach-mercer/", "https://rctoulon.com/joueurs/maa-nonu/",
            "https://rctoulon.com/joueurs/charles-ollivon/", "https://rctoulon.com/joueurs/dany-priso/",
            "https://rctoulon.com/joueurs/swan-rebbadj/", "https://rctoulon.com/joueurs/rayan-rebbadj/",
            "https://rctoulon.com/joueurs/david-ribbans/", "https://rctoulon.com/joueurs/baptiste-serin/",
            "https://rctoulon.com/joueurs/kyle-sinckler/", "https://rctoulon.com/joueurs/jeremy-sinzelle/",
            "https://rctoulon.com/joueurs/mathieu-smaili/", "https://rctoulon.com/joueurs/setariki-tuicuvu/",
            "https://rctoulon.com/joueurs/patrick-tuifua/", "https://rctoulon.com/joueurs/gabin-villiere/",
            "https://rctoulon.com/joueurs/ben-white/"
        ]
    },
    "モンペリエ": {
        "squad_url": "https://www.montpellier-rugby.com/equipes/equipe-pro/effectif",
        "player_link_pattern": r"/joueurs/[a-z\-]+/?$",
        "parser": "montpellier"
    },
    "リヨン": {
        "squad_url": "https://www.lourugby.fr/equipe-pro",
        "player_link_pattern": r"lourugby\.fr/[a-z\-]+/?$", 
        "parser": "lou",
        "fixed_urls": [
            "https://www.lourugby.fr/jermaine-ainsley", "https://www.lourugby.fr/irakli-aptsiauri",
            "https://www.lourugby.fr/cedate-gomes-sa", "https://www.lourugby.fr/hamza-kaabeche",
            "https://www.lourugby.fr/thomas-moukoro", "https://www.lourugby.fr/jerome-rey-0",
            "https://www.lourugby.fr/camille-chat", "https://www.lourugby.fr/guillaume-marchand",
            "https://www.lourugby.fr/mathis-sarragallet", "https://www.lourugby.fr/killian-geraci",
            "https://www.lourugby.fr/mickael-guillard", "https://www.lourugby.fr/felix-lambey",
            "https://www.lourugby.fr/theo-william", "https://www.lourugby.fr/liam-allen",
            "https://www.lourugby.fr/steeve-blanc-mappaz", "https://www.lourugby.fr/arno-botha",
            "https://www.lourugby.fr/dylan-cretin", "https://www.lourugby.fr/maxime-gouzou",
            "https://www.lourugby.fr/marvin-okuya", "https://www.lourugby.fr/beka-saginadze-0",
            "https://www.lourugby.fr/beka-shvangiradze", "https://www.lourugby.fr/sam-simmonds",
            "https://www.lourugby.fr/charlie-cassang", "https://www.lourugby.fr/baptiste-couilloud",
            "https://www.lourugby.fr/esteban-gonzalez-0", "https://www.lourugby.fr/leo-berdeu",
            "https://www.lourugby.fr/paddy-jackson", "https://www.lourugby.fr/martin-meliande",
            "https://www.lourugby.fr/josiah-maraku", "https://www.lourugby.fr/iosefo-masi",
            "https://www.lourugby.fr/theo-millet", "https://www.lourugby.fr/alfred-parisien",
            "https://www.lourugby.fr/thibaut-regard", "https://www.lourugby.fr/ethan-dumortier",
            "https://www.lourugby.fr/monty-ioane", "https://www.lourugby.fr/arthur-mathiron",
            "https://www.lourugby.fr/vincent-rattez", "https://www.lourugby.fr/jiuta-wainiqolo",
            "https://www.lourugby.fr/gabin-lorre", "https://www.lourugby.fr/alexandre-tchaptchet"
        ]
    },
    "カストル": {
        "squad_url": "https://castres-olympique.com/equipe-pro/effectif/",
        "player_link_pattern": r"/joueurs/[a-z\-]+/?$",
        "parser": "castres"
    },
    "アヴィロン・バイヨンヌ": {
        "squad_url": "https://www.abrugby.fr/equipe/effectif",
        "player_link_pattern": r"/effectif/[a-z\-]+_", 
        "parser": "bayonne"
    },
    "セクション・パロワーズ": {
        "squad_url": "https://www.section-paloise.com/effectif",
        "player_link_pattern": r"/joueurs-de-la-section/[a-z\-]+/?$",
        "parser": "pau"
    },
    "スタッド・フランセ": {
        "squad_url": "https://www.stade.fr/equipe-premiere/effectifs/",
        "player_link_pattern": r"/equipe-premiere/effectifs/[a-z\-]+/?$",
        "parser": "stade"
    },
    "クレルモン": {
        "squad_url": "https://www.asm-rugby.com/equipe/effectif",
        "player_link_pattern": r"/joueurs/[a-z\-]+/?$",
        "parser": "clermont"
    },
    "ペルピニャン": {
        "squad_url": "https://all.rugby/club/perpignan/squad",
        "player_link_pattern": r"/player/[a-z\-]+/?$",
        "parser": "allrugby"
    },
    "ヴァンヌ": {
        "squad_url": "https://all.rugby/club/vannes/squad",
        "player_link_pattern": r"/player/[a-z\-]+/?$",
        "parser": "allrugby"
    }
}

EXCLUDE_KEYWORDS = [
    "/staff/", "/coachs/", "/actualites/", "/news/", "/espoirs/", "/feminines/",
    "billetterie", "business", "boutique", "calendrier", "matchs", "partenaires",
    "boutique", "mentions-legales", "politique-confidentialite", "un-projet-feminin",
    "lyon-rouge-e-noir", "lou-attitude", "accroitre-votre-notoriete", "vos-evenements",
    "nos-espaces", "lou-rugby-parc", "notre-expertise", "vos-interlocuteurs"
]

def get_soup(url, retries=3):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            if i == retries - 1:
                print(f"Error fetching {url} after {retries} retries: {e}")
                return None
            print(f"Retry {i+1} for {url} due to {e}")
            time.sleep(2)
    return None

def extract_sns(soup):
    sns = {"instagram": "", "twitter": "", "facebook": ""}
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if "instagram.com" in href and not sns["instagram"]: sns["instagram"] = a["href"]
        elif ("twitter.com" in href or "x.com" in href) and not sns["twitter"]: sns["twitter"] = a["href"]
        elif "facebook.com" in href and not sns["facebook"]: sns["facebook"] = a["href"]
    return sns

def parse_allrugby(soup):
    data = {"nationality": "", "caps": "", "career": ""}
    bio_sec = soup.find(id="bio") or soup.find("h2", string="Bio")
    if bio_sec:
        p = bio_sec.find_next("p")
        if p:
            text = p.get_text()
            match = re.search(r'([A-Z][a-z]+)\s+rugby player', text)
            if match: data["nationality"] = match.group(1)
            
    career_sec = soup.find(id="career") or soup.find("h2", string="Career")
    if career_sec:
        ul = career_sec.find_next(["ul", "ol"])
        if ul:
            items = []
            for li in ul.find_all("li"):
                txt = li.get_text(strip=True)
                if "(" in txt: items.append(txt)
            if items: data["career"] = " -> ".join(items)
            
    return data

def main():
    all_results = {}
    json_path = 'data/top14_scraping_results.json'
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            all_results = json.load(f)

    for club_name, config in CLUBS_CONFIG.items():
        # レジューム機能
        if club_name in all_results and len(all_results[club_name]) >= 20:
            print(f"Skipping {club_name} (already has {len(all_results[club_name])} players).")
            continue
            
        print(f"--- Scraping {club_name} ---")
        player_links = set()
        
        if "fixed_urls" in config:
            print(f"  Using {len(config['fixed_urls'])} fixed URLs for {club_name}.")
            player_links.update(config["fixed_urls"])
        else:
            soup = get_soup(config["squad_url"])
            if not soup: continue
            
            pattern = config["player_link_pattern"]
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if re.search(pattern, href):
                    full_url = urljoin(config["squad_url"], href)
                    if any(x in full_url.lower() for x in EXCLUDE_KEYWORDS): continue
                    player_links.add(full_url)
        
        if club_name == "ラ・ロシェル":
            player_links.add("https://www.staderochelais.com/les-equipes/uini-atonio")

        print(f"Found {len(player_links)} potential players for {club_name}. Extracting details...")
        
        club_data = []
        for link in list(player_links):
            print(f"  [{club_name}] Processing {link}...")
            p_soup = get_soup(link)
            if not p_soup: continue
            
            p_data = {"url": link, "club": club_name}
            p_data.update(extract_sns(p_soup))
            
            if config["parser"] == "allrugby":
                p_data.update(parse_allrugby(p_soup))
            
            name = ""
            if p_soup.title: name = p_soup.title.string.split("|")[0].split("-")[0].strip()
            if not name or len(name) < 3:
                name = link.split("/")[-1].replace("-", " ").strip("/").replace("-", " ").title()
                if ".html" in name: name = name.split(".")[0]
            
            p_data["name"] = name
            
            text = p_soup.get_text()
            if not p_data.get("nationality"):
                nat_match = re.search(r'Nationalité\s*[:\s]*([A-Za-zÀ-ÿ]+)', text, re.IGNORECASE)
                if not nat_match:
                    if "French" in text: p_data["nationality"] = "France"
                    elif "Argentine" in text or "Argentin" in text: p_data["nationality"] = "Argentina"
                    elif "Géorgie" in text or "Georgian" in text: p_data["nationality"] = "Georgia"
                else:
                    p_data["nationality"] = nat_match.group(1).strip()
            
            if not p_data.get("caps"):
                caps_match = re.search(r'International\s*[:\s]*(.+)', text, re.IGNORECASE)
                if caps_match: p_data["caps"] = caps_match.group(1).strip()[:100]
            
            club_data.append(p_data)
            time.sleep(1.0)
            
        all_results[club_name] = club_data
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

    print("Scraping completed.")

if __name__ == "__main__":
    main()
