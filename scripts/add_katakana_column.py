import csv
import json
import os
import shutil

CSV_PATH = 'data_sources/final_master_data_v25.csv'
INTEGRATED_CSV_PATH = 'data_sources/final_master_data_v17_consolidated_integrated.csv'
if os.path.exists(INTEGRATED_CSV_PATH):
    CSV_PATH = INTEGRATED_CSV_PATH

MAPPING_PATH = 'scripts/katakana_mapping.json'
BACKUP_PATH = CSV_PATH + '.bak'

def main():
    if not os.path.exists(MAPPING_PATH):
        print(f"Error: {MAPPING_PATH} not found.")
        return

    with open(MAPPING_PATH, 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found.")
        return

    # Backup
    shutil.copy2(CSV_PATH, BACKUP_PATH)
    print(f"Backup created at {BACKUP_PATH}")

    rows = []
    fieldnames = []
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        if '選手名_カタカナ' not in fieldnames:
            fieldnames.append('選手名_カタカナ')
        
        for row in reader:
            eng_name = row.get('英語名', '')
            if eng_name in mapping:
                row['選手名_カタカナ'] = mapping[eng_name]
            elif '選手名_カタカナ' not in row:
                row['選手名_カタカナ'] = ""
            rows.append(row)

    with open(CSV_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully updated CSV with {len(mapping)} Katakana names.")

if __name__ == "__main__":
    main()
