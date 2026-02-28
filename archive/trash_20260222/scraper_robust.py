import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
import re

# --- 設定 ---
INPUT_FILE = "final_master_data_v9_complete.csv"
OUTPUT_FILE = "final_master_data_v10_parcours.csv"
BASE_URL = "https://all.rugby"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

LEAGUE_KEYWORDS = [
    "League One", "Top League", "Super Rugby", "Test Match", "World Cup",
    "Championship", "Cup", "Challenge", "Pro D2", "Premiership", "Top 14",
    "United Rugby", "Major League", "Division", "Series", "Trophy",
    "Autumn Nations", "Pacific Nations"
]

def get_html(url):
    try:
        time.sleep(2.0)
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return BeautifulSoup(resp.content, "html.parser")
    except:
        pass
    return None

def name_to_slug(name):
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9\s\-]", "", name)
    name = re.sub(r"\s+", "-", name)
    return name

def generate_url_candidates(eng_name):
    slug = name_to_slug(eng_name)
    candidates = [f"{BASE_URL}/player/{slug}"]
    parts = eng_name.strip().split()
    if len(parts) >= 2:
        swapped = f"{parts[-1]} {' '.join(parts[:-1])}"
        candidates.append(f"{BASE_URL}/player/{name_to_slug(swapped)}")
    return candidates

def is_league_name(text):
    for keyword in LEAGUE_KEYWORDS:
        if keyword.lower() in text.lower(): return True
    return False

def scrape_smart_career(soup):
    # === 1. PRIMARY: div.parcours list ===
    target_div = soup.select_one("div.parcours")
    if target_div:
        items = target_div.select("li")
        career_list = []
        for item in items:
            text = item.get_text(strip=True)
            if text:
                career_list.append(text)
        if career_list:
            return " -> ".join(career_list[::-1]), "PARCOURS"

    # === 2. FALLBACK: Table with blacklist filter ===
    career_res = []
    for table in soup.find_all("table"):
        header_row = table.find("tr")
        if not header_row: continue
        headers = [th.get_text(strip=True).lower() for th in header_row.find_all(["th","td"])]
        header_text = " ".join(headers)
        if "season" in header_text and "team" in header_text:
            for row in table.find_all("tr")[1:]:
                cols = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cols) < 3: continue
                year = cols[0]
                team_name = ""
                for col in cols[1:]:
                    if not col: continue
                    if col[0].isdigit(): continue
                    if is_league_name(col): continue
                    if len(col) > 2:
                        team_name = col
                        break
                stats = [c for c in cols[-6:] if c.isdigit()]
                stat_str = ""
                if stats:
                    stat_str = f"({stats[0]}G"
                    if len(stats) > 2: stat_str += f"/{stats[2]}T"
                    stat_str += ")"
                if ("20" in year or "19" in year) and team_name:
                    career_res.append(f"{year} {team_name} {stat_str}")
    if career_res:
        return " -> ".join(career_res), "TABLE"
    return None, None

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    # Resume logic
    if os.path.exists(OUTPUT_FILE):
        df = pd.read_csv(OUTPUT_FILE)
        print(f"Resuming from {OUTPUT_FILE}...")
    else:
        df = pd.read_csv(INPUT_FILE)
        df["Full_Career"] = ""
    
    total = len(df)
    print(f"Processing ALL {total} players...")

    found = 0
    not_found = 0
    skipped = 0
    parcours_ct = 0
    table_ct = 0

    for idx, row in df.iterrows():
        fc = row.get("Full_Career")
        if pd.notna(fc) and str(fc) not in ("", "nan"):
            skipped += 1
            continue

        eng_name = str(row.get("英語名", ""))
        if not eng_name or eng_name == "nan": continue

        urls = generate_url_candidates(eng_name)
        soup = None
        for url in urls:
            soup = get_html(url)
            if soup: break

        if soup:
            career, source = scrape_smart_career(soup)
            if career:
                df.at[idx, "Full_Career"] = career
                found += 1
                if source == "PARCOURS": parcours_ct += 1
                else: table_ct += 1
                print(f"[{idx+1}/{total}] ✓ [{source}] {eng_name}: {career[:60]}...")
            else:
                df.at[idx, "Full_Career"] = "No Data"
                print(f"[{idx+1}/{total}] △ {eng_name}")
        else:
            df.at[idx, "Full_Career"] = "Not Found"
            not_found += 1
            if not_found <= 20 or not_found % 50 == 0:
                print(f"[{idx+1}/{total}] ✗ {eng_name}")

        if idx % 10 == 0:
            df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"\n=== ALL DONE ===")
    print(f"Found: {found} (Parcours: {parcours_ct}, Table: {table_ct})")
    print(f"Not Found: {not_found}, Skipped: {skipped}")

if __name__ == "__main__":
    main()
