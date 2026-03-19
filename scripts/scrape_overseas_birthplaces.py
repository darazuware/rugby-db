import subprocess
import pandas as pd
from bs4 import BeautifulSoup
import time
import os
import re

def scrape_player_details(url):
    try:
        # User curl to bypass requests identification and set language to French/English
        cmd = [
            'curl', '-s', '-L',
            '-A', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '-H', 'Accept-Language: fr-FR,fr;q=0.9,en-US;q=0.8',
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            return None
        
        html = result.stdout
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. Nationality
        nationalities = []
        for b in soup.find_all(['b', 'span'], class_='gras'):
            label = b.get_text()
            if 'Nationality' in label or 'Nationalité' in label:
                parent = b.parent
                val = parent.get_text().replace(label, '').strip()
                val = re.sub(r'Sporting nationality.*', '', val, flags=re.S).strip()
                if val:
                    nationalities.append(val)
        
        # 2. Born (Detailed) - Search in raw HTML
        place_of_birth = ""
        # Patterns: 
        # "born on 19 January 1996 in Perth (Scotland)."
        # "born in Perth (Scotland)."
        # "born le ... à ..." (French if fallback happens)
        patterns = [
            r'born (?:on [^,.]+ )?in ([^,.]+)',
            r'n[ée] (?:le [^,.]+ )?[àa] ([^,.]+)'
        ]
        for p in patterns:
            born_match = re.search(p, html, re.I | re.S)
            if born_match:
                place_of_birth = born_match.group(1).strip()
                # Clean up if matched a whole paragraph
                if '\n' in place_of_birth:
                    place_of_birth = place_of_birth.split('\n')[0].strip()
                if place_of_birth:
                    # Final cleanup of periods
                    place_of_birth = place_of_birth.split('.')[0].strip()
                    break
        
        # Fallback to soup if raw matched weirdly
        if not place_of_birth or len(place_of_birth) > 150:
            bio_elem = soup.select_one('#rgybody') or soup.select_one('.bio')
            if bio_elem:
                bio_text = bio_elem.get_text()
                born_match = re.search(r'born (?:on [^,.]+ )?in ([^,.]+)', bio_text, re.I)
                if born_match:
                    place_of_birth = born_match.group(1).strip()
        
        # 3. Birth Date
        birth_date = ""
        import json
        ld_json = soup.find('script', type='application/ld+json')
        if ld_json:
            try:
                data = json.loads(ld_json.string)
                if isinstance(data, list): data = data[0]
                if isinstance(data, dict):
                    birth_date = data.get('birthDate', '')
            except:
                pass

        return {
            "nationality": ", ".join(list(set(nationalities))) if nationalities else "",
            "place_of_birth": place_of_birth,
            "birth_date": birth_date
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def main():
    csv_path = 'data_sources/final_master_data_v27_normalized.csv'
    df = pd.read_csv(csv_path)
    
    # Filter overseas leagues
    overseas_leagues = ['top14', 'super-rugby', 'urc', 'mlr', 'premiership']
    mask = df['League'].isin(overseas_leagues) & df['Scraped_Url'].notna()
    targets = df[mask]
    
    print(f"Total targets: {len(targets)}")
    
    results = []
    output_path = 'data_sources/overseas_birthplaces_scraped.csv'
    
    # Resume check
    if os.path.exists(output_path):
        processed_df = pd.read_csv(output_path)
        processed_urls = set(processed_df['scraped_url'].tolist())
    else:
        processed_urls = set()

    count = 0
    for idx, row in targets.iterrows():
        url = str(row['Scraped_Url'])
        if 'all.rugby' not in url:
            continue
            
        if url in processed_urls:
            continue
            
        print(f"Scraping [{count}/{len(targets)}]: {row['Full_Name']} ({url})")
        details = scrape_player_details(url)
        if details:
            details['scraped_url'] = url
            details['player_name'] = row['Full_Name']
            results.append(details)
            
            # Periodically save
            if len(results) >= 10:
                pd.DataFrame(results).to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)
                results = []
        
        count += 1
        time.sleep(1) # Be nice

    if results:
        pd.DataFrame(results).to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)

if __name__ == "__main__":
    main()
