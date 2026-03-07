import csv
import os

def identify_missing_data(csv_path):
    missing_report = {
        "summary": {
            "total_players": 0,
            "missing_dob": 0,
            "missing_height": 0,
            "missing_weight": 0,
            "missing_multiple": 0
        },
        "leagues": {}
    }

    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return None

    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            missing_report["summary"]["total_players"] += 1
            
            league = row.get('所属チーム', 'Unknown') # Actually field '所属チーム' is team, but we can infer league from context or other fields
            # Let's use a better way to group if possible, but for now team is fine.
            # In this CSV, '所属チーム' often contains the current team.
            
            missing_fields = []
            if not row.get('身長') or row.get('身長') == "":
                missing_fields.append("height")
                missing_report["summary"]["missing_height"] += 1
            if not row.get('体重') or row.get('体重') == "":
                missing_fields.append("weight")
                missing_report["summary"]["missing_weight"] += 1
            if not row.get('生年月日') or row.get('生年月日') == "":
                missing_fields.append("dob")
                missing_report["summary"]["missing_dob"] += 1
                
            if len(missing_fields) > 1:
                missing_report["summary"]["missing_multiple"] += 1
                
            if missing_fields:
                team = row.get('所属チーム', 'Unknown')
                if team not in missing_report["leagues"]:
                    missing_report["leagues"][team] = []
                
                missing_report["leagues"][team].append({
                    "name": row.get('英語名') or row.get('選手名'),
                    "missing": missing_fields,
                    "url": row.get('URL') or row.get('Scraped_Url')
                })

    return missing_report

def main():
    csv_path = "data_sources/final_master_data_v17_consolidated.csv"
    report = identify_missing_data(csv_path)
    
    if report:
        print(f"--- Data Quality Summary ---")
        print(f"Total Players: {report['summary']['total_players']}")
        print(f"Missing DOB: {report['summary']['missing_dob']}")
        print(f"Missing Height: {report['summary']['missing_height']}")
        print(f"Missing Weight: {report['summary']['missing_weight']}")
        print(f"Players with multiple missing fields: {report['summary']['missing_multiple']}")
        print(f"----------------------------")
        
        # Output detailed report to a file
        output_file = "/Users/ktamatzmoto/.gemini/antigravity/brain/0a4cb5ef-2a47-4d0d-afe7-2dd511f55541/missing_data_report.json"
        import json
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"Detailed report saved to {output_file}")

if __name__ == "__main__":
    main()
