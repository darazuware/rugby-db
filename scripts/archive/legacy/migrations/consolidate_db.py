
import glob
import os
import re
import csv
import time
import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError
import ssl

# --- Configuration ---
DATA_DIR = os.path.join("data", "database")
TEXT_DIR = os.path.join(DATA_DIR, "text")
OUTPUT_CSV = "final_master_data.csv"
MARKDOWN_DIR = os.path.join("data", "markdown")

# Bypass SSL context if needed
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def normalize_name(name):
    """Normalize player name for matching (remove spaces, dots, lower case)."""
    if not name:
        return ""
    return re.sub(r'[\s・\.]', '', name).lower()

def normalize_university(uni_str):
    """Normalize university names to formal 'Template University' format."""
    if not uni_str:
        return ""
    
    normalized = uni_str
    
    # Fix English spacing issues first
    replacements_en = {
        "UniversityofTechnology": "University of Technology",
        "AucklandUniversity": "Auckland University",
        # Add others if seen
    }
    for k, v in replacements_en.items():
        if k in normalized: transformed = normalized.replace(k, v)
    
    # Dictionary of Keyword -> Formal Name
    mappings = {
        "同志社": "同志社大学",
        "明治": "明治大学",
        "早稲田": "早稲田大学",
        "筑波": "筑波大学",
        "天理": "天理大学",
        "帝京": "帝京大学",
        "慶応": "慶應義塾大学",
        "慶應": "慶應義塾大学",
        "流通経済": "流通経済大学",
        "流経": "流通経済大学",
        "東海": "東海大学",
        "日大": "日本大学",
        "日体": "日本体育大学",
        "京産": "京都産業大学",
        "近大": "近畿大学",
        "大東": "大東文化大学",
        "大東文化": "大東文化大学",
        "関東学院": "関東学院大学",
        "法政": "法政大学",
        "中央": "中央大学",
        "立命館": "立命館大学",
        "関西学院": "関西学院大学",
        "関学": "関西学院大学",
        "専修": "専修大学",
        "摂南": "摂南大学",
        "拓殖": "拓殖大学",
        "山梨学院": "山梨学院大学",
        "立正": "立正大学",
        "東洋": "東洋大学",
        "青山学院": "青山学院大学",
        "福岡工業": "福岡工業大学",
        "福岡工": "福岡工業大学",
    }

    for key, formal in mappings.items():
        if key in normalized:
            if normalized == key:
                normalized = formal
            elif normalized.endswith(key + "大") and not normalized.endswith(key + "大学"):
                normalized = normalized.replace(key + "大", formal)
            elif key in normalized and formal not in normalized and "大学" not in normalized:
                 normalized = normalized.replace(key, formal)
                 
    normalized = normalized.replace("大学大学", "大学").replace("大学大", "大学")
    
    if "慶応大学" in normalized: normalized = normalized.replace("慶応大学", "慶應義塾大学")
    if "慶應大学" in normalized: normalized = normalized.replace("慶應大学", "慶應義塾大学")
    
    return normalized

def clean_rep_history(text):
    """Remove garbage from representative history."""
    if not text: return ""
    lines = text.split('\n') if '\n' in text else text.split(',')
    cleaned = []
    for line in lines:
        l = line.strip()
        if not l: continue
        # Heuristics for garbage
        if re.search(r'\d+-\d+', l): continue # Score
        if "試合" in l or "得点" in l: continue
        if "Win" in l or "Loss" in l: continue
        if "Q&A" in l: continue
        
        cleaned.append(l)
    return ", ".join(cleaned)

def parse_year(season_str):
    """Convert 12/13 -> 2012, 99/00 -> 1999."""
    if "/" not in season_str: return season_str
    parts = season_str.split("/")
    if not parts: return season_str
    
    start_yy = parts[0]
    if len(start_yy) == 2:
        if int(start_yy) < 50: # Assume 2000s
             # If 99/00 -> 1999. If 12/13 -> 2012.
            return 2000 + int(start_yy)
        else:
            return 1900 + int(start_yy)
    if start_yy.isdigit():
        return int(start_yy)
    return 0

def format_career_history(raw_entries):
    """Aggregate contiguous seasons for same team."""
    if not raw_entries: return ""
    
    unique_entries = []
    seen = set()
    for s, t in raw_entries:
        if (s, t) not in seen:
            unique_entries.append({'season': s, 'team': t, 'year': parse_year(s)})
            seen.add((s, t))
            
    # Sort chronologically (Old -> New)
    unique_entries.sort(key=lambda x: x['year'])
    
    aggregated = []
    if not unique_entries: return ""
    
    current_team = unique_entries[0]['team']
    start_year = unique_entries[0]['year']
    end_year = unique_entries[0]['year']
    
    for i in range(1, len(unique_entries)):
        entry = unique_entries[i]
        year = entry['year']
        team = entry['team']
        
        if team == current_team:
            end_year = year
        else:
            if start_year == end_year:
                aggregated.append(f"{start_year}: {current_team}")
            else:
                aggregated.append(f"{start_year}-{end_year+1}: {current_team}")
                
            current_team = team
            start_year = year
            end_year = year
            
    if start_year == end_year:
        aggregated.append(f"{start_year}: {current_team}")
    else:
        aggregated.append(f"{start_year}-{end_year+1}: {current_team}")
        
    return " -> ".join(aggregated)

def extract_details_from_text(text_content):
    """Extract Career History and Representative History."""
    career_history = ""
    rep_history = ""
    
    lines = text_content.split('\n')
    arrow_lines = [line.strip() for line in lines if '→' in line]
    
    if arrow_lines:
        career_history = max(arrow_lines, key=len)
    
    match_rep = re.search(r'代表歴\s*[:：\n]?\s*(.*?)(?=\nQ&A|\n\n|$)', text_content, re.DOTALL | re.IGNORECASE)
    if match_rep:
        raw_rep = match_rep.group(1).strip()
        rep_history = clean_rep_history(raw_rep)
        
    return career_history, rep_history

# --- Scraping Logic ---

def fetch_url(url, data=None):
    """Helper to fetch URL with error handling."""
    req = urllib.request.Request(url, data=data, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore'), response.geturl()
    except Exception as e:
        print(f"    Error fetching {url}: {e}")
        return None, None

def search_player_itsrugby(name_str):
    """
    Search for a player on ItsRugby.
    Returns: (player_url) or None
    """
    base_search_url = "https://www.itsrugby.co.uk/playersearchlist.html"
    
    parts = name_str.strip().split()
    if not parts:
        return None
        
    first = parts[0]
    last = " ".join(parts[1:]) if len(parts) > 1 else parts[0]
    
    # Updated strategies for handling hyphens e.g. Pieter-Steph -> Pieter Steph
    strategies = [
        (first, last),                
        ("", last),                   
        ("", parts[-1]),             
        (first, parts[-1]),
        (first.replace("-", " "), last), # Try space instead of hyphen
        (first, last.replace("-", " "))
    ]
    
    if len(parts) == 1:
        strategies = [("", parts[0])]

    for fname, lname in strategies:
        # print(f"  Searching ItsRugby for: First='{fname}', Last='{lname}'")
        data = urllib.parse.urlencode({'name': lname, 'fname': fname}).encode('utf-8')
        
        content, _ = fetch_url(base_search_url, data)
        if not content:
            continue
            
        links = re.findall(r'href="(player_\d+\.html)"', content)
        unique_links = list(set(links))
        
        if unique_links:
            target_link = unique_links[0] 
            full_url = urllib.parse.urljoin("https://www.itsrugby.co.uk/", target_link)
            print(f"    Found match: {full_url}")
            return full_url
            
        time.sleep(1) 
        
    return None

def get_player_details(player_url):
    """Scrape details from player page."""
    print(f"  Scraping details from {player_url}...")
    content, _ = fetch_url(player_url)
    if not content:
        return {}
        
    details = {}
    
    # 1. International Caps (Header Method - Primary)
    intl_caps_found = None
    intl_row_match = re.search(r'(International Tests\s*<.*?</tr>)', content, re.DOTALL | re.IGNORECASE)
    if intl_row_match:
        row_html = intl_row_match.group(1)
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
        clean_cells = []
        for c in cells:
            text = re.sub(r'<[^>]+>', '', c).strip()
            clean_cells.append(text)
        
        if len(clean_cells) > 4:
            played = clean_cells[4]
            if played.isdigit() or played == "-":
                intl_caps_found = played if played != "-" else "0"
            elif clean_cells[2].isdigit(): 
                intl_caps_found = clean_cells[2]
    
    if intl_caps_found:
        details['International_Caps'] = intl_caps_found

    # 2. Full Career History & Calculated Caps (Fallback)
    # Iterate over rows to get Season, Team, and Matches
    entries = []
    career_caps_sum = 0
    
    # Known International Teams for summation fallback
    INTL_TEAMS = ["South Africa", "Japan", "New Zealand", "Australia", 
                  "England", "France", "Ireland", "Scotland", "Wales", 
                  "Argentina", "Fiji", "Samoa", "Tonga", "Italy", 
                  "USA", "Canada", "Uruguay", "Namibia", "Georgia", "Romania"]

    # Use finditer to locate rows and parse subsequent cells
    # Pattern matches: Season ... Team Link
    row_pattern = r'>(\d{2}/\d{2})<.*?href="[^"]*teams/[^"]*".*?>(.*?)</a>'
    
    for match in re.finditer(row_pattern, content, re.DOTALL):
        season = match.group(1)
        team = match.group(2).strip()
        
        # Capture Matches (P) from subsequent cells
        # We look ahead from the end of the Team link
        start_search = match.end()
        chunk = content[start_search:start_search+1000] # 1000 chars context
        
        # Parse next few TDs
        tds = re.findall(r'<td[^>]*>(.*?)</td>', chunk, re.DOTALL)
        
        # Clean TDs
        vals = []
        for td in tds[:15]: # check first 15 cells
            v = re.sub(r'<[^>]+>', '', td).strip()
            if v: vals.append(v)
            
        # Heuristic to find 'Matches' value in vals
        # vals usually: [Competition?, Matches(digit)]
        matches_played = 0
        for v in vals:
            if v.isdigit():
                matches_played = int(v)
                break
            elif v == "-":
                matches_played = 0 # Explicit 0
                break
                
        # Append to entries
        entries.append((season, team))
        
        # Sum caps if International Team
        if team in INTL_TEAMS:
            career_caps_sum += matches_played

    details['Career_History_Scraped'] = format_career_history(entries)
    
    # Use calculated caps if Primary method failed
    if 'International_Caps' not in details and career_caps_sum > 0:
        details['International_Caps'] = str(career_caps_sum)
        print(f"    Calculated International Caps from career table: {career_caps_sum}")

    return details


def main():
    print("Step 1: Loading CSV files...")
    csv_pattern = os.path.join(DATA_DIR, "LEAGUEONE_DATA_BATCH_*.csv")
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print("No CSV files found.")
        return

    all_rows = []
    headers = []

    for f in csv_files:
        try:
            with open(f, 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                if not headers:
                    headers = reader.fieldnames
                for row in reader:
                    all_rows.append(row)
        except Exception as e:
            print(f"Error read {f}: {e}")
            
    if not all_rows:
        return

    # Deduplicate
    unique_rows = {}
    for row in all_rows:
        key = (row.get('選手名', ''), row.get('所属チーム', ''))
        unique_rows[key] = row
    
    final_rows = list(unique_rows.values())
    
    # New Columns
    cols_to_remove = ['Team_History_2016_2024'] 
    new_cols = ['Text_Detail', 'キャリア遍歴', '代表キャップ数', 'International_Caps', 'Scraped_Url'] 
    
    print("Step 2: Processing Text Files...")
    text_files = glob.glob(os.path.join(TEXT_DIR, "**", "*.txt"), recursive=True)
    text_lookup = {}
    
    for tf in text_files:
        filename = os.path.basename(tf).replace(".txt", "")
        norm_key = normalize_name(filename)
        try:
            with open(tf, 'r', encoding='utf-8') as f:
                content = f.read()
            text_lookup[norm_key] = content
        except: pass

    print("Step 3: Consolidating and Scraping details...")
    
    count = 0
    scrape_count = 0
    
    # DEBUG MODE: Process ONLY specific veterans for testing (Set to False for production)
    DEBUG_MODE = False
    TARGET_VETERANS = ["クワッガ・スミス", "リーチマイケル", "ピーターステフ・デュトイ"]

    for row in final_rows:
        name = row.get('選手名', '')

        if DEBUG_MODE:
            n_name = normalize_name(name)
            is_target = False
            for t in TARGET_VETERANS:
                if normalize_name(t) in n_name:
                    is_target = True
                    break
            if not is_target:
                continue
        
        count += 1
        
        # 3.1 Normalize University
        if '大学' in row:
            row['大学'] = normalize_university(row['大学'])
            
        # 3.2 Initialize fields
        row['キャリア遍歴'] = ""
        row['代表キャップ数'] = ""
        row['Text_Detail'] = ""
        # Keep existing if present, else empty
        if 'International_Caps' not in row: row['International_Caps'] = ""
        row['Scraped_Url'] = ""

        # 3.3 Text File Extraction
        norm_name = normalize_name(name)
        if norm_name in text_lookup:
            content = text_lookup[norm_name]
            row['Text_Detail'] = content
            career, rep = extract_details_from_text(content)
            row['キャリア遍歴'] = career
            row['代表キャップ数'] = rep
        
        # 3.4 Scraping (Optional/Augment)
        # Only scrape if Text Detail is missing OR we are specifically looking for International Caps
        # AND we have an English name
        
        should_scrape = False
        if not row.get('Text_Detail') and not row.get('URL', ''):
             should_scrape = True
        
        # Also scrape if we have english name but no caps info?
        # Let's prioritize rows with English names for scraping.
        en_name = row.get('英語名', '')
        
        # Simple Logic: Scrape if we have En name and no rep history?
        # Or just scrape everyone with English Name to be thorough?
        # Given potential volume, maybe restrict?
        # But 'final_master_data' implies completeness.
        # I'll enable scraping if we have English Name.
        
        if en_name:
             # Check if we already have data to avoid unnecessary requests?
             # If we have '代表キャップ数' from text, do we need ItsRugby?
             # Yes, for 'International Caps' column.
             
             # Don't scrape if we already have URL and International Caps?
             # Assuming we don't have it yet.
             
             # Rate Limit protection: only scrape first 5 for now to test?
             # User says "Consolidating...".
             # I should probably just run it. 
             # But I'll print progress.
             pass

        # 3.4 Scraping (Optional/Augment)
        should_scrape = False
        if en_name:
             should_scrape = True
             
        if should_scrape:
             # Limit removed for production
             print(f"[{count}/{len(final_rows)}] Scraping for {en_name}...")
             scraped_url = search_player_itsrugby(en_name)
             
             if scraped_url:
                 row['Scraped_Url'] = scraped_url
                 details = get_player_details(scraped_url)
                 
                 if 'International_Caps' in details:
                     row['International_Caps'] = details['International_Caps']
                 
                 if 'Career_History_Scraped' in details:
                     if not row['キャリア遍歴']:
                         row['キャリア遍歴'] = details['Career_History_Scraped']
                     else:
                         row['キャリア遍歴'] = row['キャリア遍歴'] + " | " + details['Career_History_Scraped']
                 
                 time.sleep(2)

    # Step 4: Output CSV
    output_headers = [h for h in headers if h not in cols_to_remove]
    for n in new_cols:
        if n not in output_headers:
            output_headers.append(n)
            
    print(f"Step 4: Saving {OUTPUT_CSV}...")
    try:
        with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=output_headers)
            writer.writeheader()
            writer.writerows(final_rows)
    except Exception as e:
        print(f"Error writing CSV: {e}")

    # Step 5: Markdown
    print(f"Step 5: Generating Markdown in {MARKDOWN_DIR}/...")
    if not os.path.exists(MARKDOWN_DIR):
        os.makedirs(MARKDOWN_DIR)
        
    for row in final_rows:
        p_name = row.get('選手名', 'Unknown')
        safe_name = re.sub(r'[\\/*?:"<>|]', "", p_name).replace(" ", "_")
        if not safe_name: continue
        
        md_path = os.path.join(MARKDOWN_DIR, f"{safe_name}.md")
        
        md = f"""# {p_name}
        
## Profile
- **Position**: {row.get('ポジション', '')}
- **Team**: {row.get('所属チーム', '')}
- **DOB**: {row.get('生年月日', '')}
- **Height**: {row.get('身長', '')} cm
- **Weight**: {row.get('体重', '')} kg
- **Category**: {row.get('カテゴリ', '')}

## Career
- **High School**: {row.get('高校', '')}
- **University**: {row.get('大学', '')}
- **Career Path**: {row.get('キャリア遍歴', '')}
- **League One Caps**: {row.get('リーグワンキャップ数', '')}

## Representative History
- **Caps**: {row.get('代表キャップ数', '')}
- **International Caps (ItsRugby)**: {row.get('International_Caps', '')}

## Details
{row.get('Text_Detail', '')}

## Links
- [ItsRugby Profile]({row.get('Scraped_Url', '')})
- [League One Profile]({row.get('URL', '')})
"""
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md)

    print("Processing Complete.")
    
    # Quick Check for user report
    # Use normalized name to find Yasuda
    yasuda = next((r for r in final_rows if "安田卓平" in normalize_name(r.get('選手名', ''))), None)
    if yasuda:
        print(f"REPORT_CHECK: Yasuda Rep: {yasuda.get('代表キャップ数')}")

if __name__ == "__main__":
    main()
