import requests
from bs4 import BeautifulSoup
import json
import time
import re

def scrape_allrugby_player(player_id):
    """Scrape detailed player information from all.rugby using player ID"""
    
    url = f"https://all.rugby/player/{player_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        player_data = {
            'id': player_id,
            'url': url,
            'nationality_1': None,
            'nationality_2': None,
            'sporting_nationality': None,
            'origin': None,
            'name': None,
            'height': None,
            'weight': None,
            'position': None,
            'current_club': None,
            'matches_played': 0,
            'tries': 0,
            'points': 0,
            'career_path': []
        }
        
        # Extract player name from title or h1
        title = soup.find('title')
        if title:
            player_data['name'] = title.get_text().split(':')[0].strip()
        
        # Extract bio section
        bio_section = soup.find('div', class_='bio')
        if bio_section:
            # Extract nationality information
            nationality_divs = bio_section.find_all('div')
            for div in nationality_divs:
                span = div.find('span', class_='gras')
                if span:
                    label = span.get_text().strip()
                    img = div.find('img')
                    if img and 'alt' in img.attrs:
                        country = img['alt'].replace('Drapeau ', '').strip()
                        
                        if 'Nationality #1' in label:
                            player_data['nationality_1'] = country
                            if not player_data['origin']:
                                player_data['origin'] = country
                        elif 'Nationality #2' in label:
                            player_data['nationality_2'] = country
                        elif 'Sporting nationality' in label:
                            player_data['sporting_nationality'] = country
            
            # Extract origin from bio text link
            origin_link = bio_section.find('a', href=re.compile(r'/players/'))
            if origin_link and not player_data['origin']:
                origin_text = origin_link.get_text().strip()
                if 'rugby player' in origin_text.lower():
                    # Extract country (e.g., "Tongan rugby player" -> "Tonga")
                    player_data['origin'] = origin_text.replace('rugby player', '').strip()
        
        # Extract career path
        career_section = soup.find('div', class_='parcours')
        if career_section:
            career_items = career_section.find_all('li')
            for item in career_items:
                player_data['career_path'].append(item.get_text().strip())
        
        # Extract statistics (if available in a stats table)
        stats_divs = soup.find_all('div', class_='stats')
        for stats_div in stats_divs:
            text = stats_div.get_text().lower()
            # Try to extract numbers
            numbers = re.findall(r'\d+', text)
            if 'match' in text or 'game' in text:
                if numbers:
                    player_data['matches_played'] = int(numbers[0])
            if 'tries' in text or 'essais' in text:
                if numbers:
                    player_data['tries'] = int(numbers[0])
            if 'points' in text:
                if numbers:
                    player_data['points'] = int(numbers[0])
        
        return player_data
        
    except Exception as e:
        print(f"  ✗ Error scraping player {player_id}: {e}")
        return None

def main():
    print("=== All.Rugby Player Data Scraper (Corrected) ===\n")
    
    # Load existing rugby_players.json to get player IDs
    print("Loading rugby_players.json...")
    with open('data/rugby_players.json', 'r') as f:
        players = json.load(f)
    
    print(f"Found {len(players)} players to process\n")
    
    # Load existing progress if available
    output_file = 'allrugby_player_stats.json'
    try:
        with open(output_file, 'r') as f:
            scraped_data = json.load(f)
        print(f"Resuming from {len(scraped_data)} previously scraped players\n")
    except:
        scraped_data = {}
    
    # Process each player using their ID
    total = len(players)
    processed = 0
    errors = 0
    
    for idx, player in enumerate(players):
        player_id = player.get('id')
        
        # Skip if already scraped
        if str(player_id) in scraped_data:
            continue
        
        if not player_id:
            continue
        
        print(f"[{idx+1}/{total}] Scraping Player ID {player_id}...")
        
        player_stats = scrape_allrugby_player(player_id)
        
        if player_stats:
            scraped_data[str(player_id)] = player_stats
            processed += 1
            print(f"  ✓ {player_stats.get('name', 'Unknown')} (Origin: {player_stats.get('origin', 'N/A')}, Nationality: {player_stats.get('sporting_nationality', 'N/A')})")
        else:
            errors += 1
        
        # Save progress every 50 players
        if processed % 50 == 0 and processed > 0:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, ensure_ascii=False, indent=2)
            print(f"\n  💾 Progress saved: {len(scraped_data)} players\n")
        
        # Rate limiting
        time.sleep(2)
    
    # Final save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Scraping Complete ===")
    print(f"Total processed: {processed}")
    print(f"Errors: {errors}")
    print(f"Saved to: {output_file}")

if __name__ == "__main__":
    main()
