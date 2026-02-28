
import re

def consolidate_career_history(career_string):
    if not career_string or career_string == '-':
        return []
        
    # 1. Parse string into list of dicts: {'team': 'Sunwolves', 'start': 2016, 'end': 2017}
    raw_entries = []
    parts = career_string.split(' -> ')
    
    # Regex to handle "Team Name (YYYY - YYYY)" or "Team Name (YYYY)"
    # Some might be "Team Name (2021 - )"
    
    for part in parts:
        part = part.strip()
        # Match "(YYYY - YYYY)" or "(YYYY - )" or "(YYYY)"
        year_match = re.search(r'\(\s*(\d{4})\s*(?:-|–)?\s*(\d{4}|)?\s*\)', part)
        
        if year_match:
            team_name = part[:year_match.start()].strip()
            start_year = int(year_match.group(1))
            end_year_str = year_match.group(2)
            
            if end_year_str:
                end_year = int(end_year_str)
            else:
                # If matches "(2021 - )", treat it as current (9999 for sorting/logic)
                if '-' in part or '–' in part:
                    end_year = 9999 
                else:
                    # "(2018)" -> start=2018, end=2018
                    end_year = start_year
            
            raw_entries.append({'team': team_name, 'start': start_year, 'end': end_year})
        else:
            # Maybe just team name?
            raw_entries.append({'team': part, 'start': 0, 'end': 0})
            
    # 2. Consolidate logic
    # We want to group by Team Name. 
    # But we need to respect distinct eras if they are far apart? 
    # User example: Sunwolves (2016-17), Coke (2017), Sunwolves (2018), Coke (2018)... 
    # User output: Sunwolves (2016-2019), Coke (2017-2021).
    # This implies we should merge ALL stints of the same team into one min-max range.
    
    merged_map = {}
    
    for entry in raw_entries:
        t = entry['team']
        if t not in merged_map:
            merged_map[t] = {'start': entry['start'], 'end': entry['end']}
        else:
            # Update min start
            if entry['start'] < merged_map[t]['start'] and entry['start'] != 0:
                merged_map[t]['start'] = entry['start']
            # Update max end
            if entry['end'] > merged_map[t]['end']:
                merged_map[t]['end'] = entry['end']
                
    # 3. Convert back to list and Sort by Start Year
    final_list = []
    for team, span in merged_map.items():
        final_list.append({'team': team, 'start': span['start'], 'end': span['end']})
        
    # Sort by start year
    final_list.sort(key=lambda x: x['start'])
    
    return final_list

# Test Data from User
# "Sunwolves (2016 - 2017) -> Coca Cola West Red Sparks (2017 - 2017) -> Sunwolves (2018 - 2018) -> Coca Cola West Red Sparks (2018 - 2018) -> Sunwolves (2018 - 2018) -> Coca Cola West Red Sparks (2018 - 2018) -> Sunwolves (2019 - 2019) -> Coca Cola West Red Sparks (2019 - 2021) -> Toyota Verblitz (2021 - )"

test_str = "Sunwolves (2016 - 2017) -> Coca Cola West Red Sparks (2017 - 2017) -> Sunwolves (2018 - 2018) -> Coca Cola West Red Sparks (2018 - 2018) -> Sunwolves (2018 - 2018) -> Coca Cola West Red Sparks (2018 - 2018) -> Sunwolves (2019 - 2019) -> Coca Cola West Red Sparks (2019 - 2021) -> Toyota Verblitz (2021 - )"

result = consolidate_career_history(test_str)
print("Original:", test_str)
print("\nConsolidated:")
for r in result:
    end_str = str(r['end'])
    if r['end'] == 9999: end_str = " "
    print(f"{r['team']} ({r['start']} - {end_str})")
