
import re
import urllib.request
import urllib.parse
import ssl
import time

# Bypass SSL
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def normalize_university(uni_str):
    if not uni_str: return ""
    normalized = uni_str
    
    # Fix English spacing (CamelCase splitting heuristic or specific fixes)
    # Simple fix for specific known issues:
    # "UniversityofTechnology" -> "University of Technology"
    # "AucklandUniversity" -> "Auckland University"
    # "流通経済大学" -> "流通経済大学" (Keep Japanese)
    
    # Add space before capital letters if preceded by lowercase? 
    # Risk: MacAllister -> Mac Allister. 
    # Better: List of common merged words? or specific replacements.
    
    replacements = {
        "UniversityofTechnology": "University of Technology",
        "AucklandUniversity": "Auckland University",
        "流通経済": "流通経済大学",
        "帝京": "帝京大学",
        "明治": "明治大学",
        "早稲田": "早稲田大学",
        "同志社": "同志社大学",
        "慶應": "慶應義塾大学",
        "慶應義塾": "慶應義塾大学",
        "京産": "京都産業大学",
        "日体": "日本体育大学",
        "日体大": "日本体育大学",
        "東海": "東海大学",
        "天理": "天理大学",
        "近大": "近畿大学",
        "大東": "大東文化大学", # often 大東 or 大東大
        "関学": "関西学院大学",
        "関東学院": "関東学院大学",
        "法政": "法政大学",
        "中央": "中央大学",
        "立命館": "立命館大学",
        "専修": "専修大学",
        "摂南": "摂南大学",
        "拓殖": "拓殖大学",
        "山梨学院": "山梨学院大学",
        "立正": "立正大学",
        "東洋": "東洋大学",
        "青山学院": "青山学院大学",
        "福岡工業": "福岡工業大学",
    }
    
    for key, val in replacements.items():
        if key == normalized:
            normalized = val
        elif normalized.endswith(key) and not normalized.endswith("大学") and key not in ["UniversityofTechnology", "AucklandUniversity"]:
             # e.g. "明治" -> "明治大学"
             normalized = val
        elif key in normalized and "大学" not in normalized and not re.search(r'[a-zA-Z]', normalized):
             # Only replace if essentially the whole string or safe context?
             # "帝京" in "帝京可児" (High School) -> Don't change?
             # But this function is for 'University' column usually.
             normalized = normalized.replace(key, val)

    # Clean up "大学大学"
    normalized = normalized.replace("大学大学", "大学")
    if "慶応" in normalized: normalized = normalized.replace("慶応", "慶應義塾")
    if "慶應" in normalized and "大学" not in normalized: normalized += "大学"
    normalized = normalized.replace("大学大学", "大学") # Check again
    
    return normalized

def clean_rep_history(text):
    """Remove garbage from representative history."""
    if not text: return ""
    # Remove lines that look like scores "10-20", "vs Team"
    # Remove "Match Report" etc.
    # Keep lines that look like "Team Name (Caps)" or just "Team Name"
    # Or specifically remove known garbage.
    
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        l = line.strip()
        if not l: continue
        
        # Heuristics for garbage
        if re.search(r'\d+-\d+', l): continue # Score?
        if "試合" in l: continue
        if "得点" in l: continue
        if "Win" in l or "Loss" in l: continue
        
        cleaned.append(l)
        
    return ", ".join(cleaned)

def fetch_url(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error: {e}")
        return None

def search_player_itsrugby(name):
    # Reuse logic from consolidate_db.py
    # ... (Simplified for brevity in test)
    base_search_url = "https://www.itsrugby.co.uk/playersearchlist.html"
    parts = name.strip().split()
    if not parts: return None
    first = parts[0]
    last = " ".join(parts[1:]) if len(parts) > 1 else parts[0]
    
    data = urllib.parse.urlencode({'name': last, 'fname': first}).encode('utf-8')
    content = fetch_url(base_search_url) # Wait, POST?
    # consolidate_db uses fetch_url which does POST if data is provided.
    
    req = urllib.request.Request(base_search_url, data=data, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
    except: return None

    # Search logic... regex
    links = re.findall(r'href="(player_\d+\.html)"', content)
    if links:
         return urllib.parse.urljoin("https://www.itsrugby.co.uk/", links[0])
    return None

def parse_year(season_str):
    """Convert 12/13 -> 2012, 99/00 -> 1999."""
    if "/" not in season_str: return season_str
    
    start_yy = season_str.split("/")[0]
    if len(start_yy) == 2:
        if int(start_yy) < 50: # Assume 2000s
            return 2000 + int(start_yy)
        else:
            return 1900 + int(start_yy)
    return int(start_yy)

def format_career_history(raw_entries):
    """Aggregate contiguous seasons for same team."""
    if not raw_entries: return ""
    
    # Sort chronologically just in case
    # Entries: (season_str, team_name)
    # Convert to list of dicts with calculated year
    
    # Deduplicate first (ItsRugby mimics duplicate rows sometimes)
    unique_entries = []
    seen = set()
    for s, t in raw_entries:
        if (s, t) not in seen:
            unique_entries.append({'season': s, 'team': t, 'year': parse_year(s)})
            seen.add((s, t))
            
    # Sort by year
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
            # Check if contiguous? 
            # If 2012, then 2014 (skip 2013), should we split?
            # User probably just wants "2012-2015: Team" even if gap?
            # Or "2012-2013, 2014-2015".
            # Usually gaps imply another team or omission. 
            # If strictly same team, extend end_year.
            end_year = year
        else:
            # New block
            # Format previous
            if start_year == end_year:
                aggregated.append(f"{start_year}: {current_team}")
            else:
                aggregated.append(f"{start_year}-{end_year+1}: {current_team}") # End year usually +1 for season end?
                # User said "Start-End". '12/13' is 2012 start. 
                # If 12/13 only, looks like 2012. 
                # If 12/13, 13/14 -> 2012-2014? (End of 13/14 is 2014).
                
            current_team = team
            start_year = year
            end_year = year
            
    # Add last
    if start_year == end_year:
        aggregated.append(f"{start_year}: {current_team}")
    else:
        aggregated.append(f"{start_year}-{end_year+1}: {current_team}")
        
    return " -> ".join(aggregated)

def get_full_career(player_url):
    content = fetch_url(player_url)
    if not content: return ""
    
    # Extract ALL career history
    matches = re.findall(r'>(\d{2}/\d{2})<.*?href="[^"]*teams/[^"]*".*?>(.*?)</a>', content, re.DOTALL)
    
    entries = []
    for season, team in matches:
        entries.append((season, team.strip()))
            
    return format_career_history(entries)

# Test with Veterans
veterans = [
    {"name": "Kwagga Smith", "url_hint": "https://www.itsrugby.co.uk/player-international-32326.html"},
    {"name": "Michael Leitch", "url_hint": "https://www.itsrugby.co.uk/player-international-17846.html"},
    {"name": "Pieter-Steph du Toit", "url_hint": "https://www.itsrugby.co.uk/player-international-29239.html"}
]

for v in veterans:
    print(f"\nTesting {v['name']}...")
    url = search_player_itsrugby(v['name'])
    if not url:
        print(f"  Search failed.")
    else:
        print(f"  Found: {url}")
        
    # Manual override for test if search fails (to test extraction logic)
    if not url:
         # Need correct URL for PSDT. check manually or use hardcoded if known.
         # 'player-international-29239' was bad?
         pass
         
    if url:
        career = get_full_career(url)
        print(f"  Career Extracted: {career}")

