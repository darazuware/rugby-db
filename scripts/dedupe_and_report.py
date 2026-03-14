import csv
import os
import unicodedata
import re

def normalize_name(name):
    if not name: return ""
    normalized = unicodedata.normalize('NFD', name)
    normalized = "".join([c for c in normalized if not unicodedata.combining(c)])
    normalized = normalized.replace('　', ' ')
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized.strip().lower()

def deduplicate_and_analyze(csv_path):
    if not os.path.exists(csv_path):
        return
    
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
        
    seen = {} # key: (norm_name, team)
    unique_rows = []
    duplicates_removed = 0
    
    for row in rows:
        name = row.get('英語名') or row.get('選手名')
        team = row.get('所属チーム')
        key = (normalize_name(name), team)
        
        if key in seen:
            duplicates_removed += 1
            # Merge logic: if existing has empty fields, try to take from duplicate
            existing = seen[key]
            for field in ['身長', '体重', '生年月日', '高校', '大学', 'URL', 'Scraped_Url']:
                if (not existing[field] or existing[field] == "") and row[field]:
                    existing[field] = row[field]
        else:
            seen[key] = row
            unique_rows.append(row)
            
    print(f"Original rows: {len(rows)}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Unique rows: {len(unique_rows)}")
    
    # Save deduplicated CSV
    temp_path = csv_path + ".tmp"
    with open(temp_path, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_rows)
    os.replace(temp_path, csv_path)
    
    # Re-analyze missing
    missing_players = []
    for row in unique_rows:
        missing = []
        if not row['身長']: missing.append('height')
        if not row['体重']: missing.append('weight')
        if not row['生年月日']: missing.append('dob')
        
        if missing:
            missing_players.append({
                "name": row['英語名'],
                "team": row['所属チーム'],
                "missing": missing,
                "url": row.get('URL') or row.get('Scraped_Url')
            })
            
    return missing_players

if __name__ == "__main__":
    csv_path = "data_sources/final_master_data_v25.csv"
    missing = deduplicate_and_analyze(csv_path)
    
    output_report = "/Users/ktamatzmoto/.gemini/antigravity/brain/0a4cb5ef-2a47-4d0d-afe7-2dd511f55541/final_missing_list.json"
    import json
    with open(output_report, "w", encoding="utf-8") as f:
        json.dump(missing, f, ensure_ascii=False, indent=2)
    print(f"Final missing list (deduplicated) saved to {output_report}")
