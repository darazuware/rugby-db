import csv
import json
import os
import re
import unicodedata

def normalize_name(name):
    if not name: return []
    # アクセント記号の除去 (é -> e 等)
    name = unicodedata.normalize('NFD', name)
    name = "".join([c for c in name if unicodedata.category(c) != 'Mn'])
    # 全大文字化、記号削除、スペースの正規化
    name = name.upper()
    name = re.sub(r'[^A-Z\s]', ' ', name)
    parts = name.split()
    return parts

def is_match(scraped_parts, master_parts):
    if not scraped_parts or not master_parts: return False
    # パーツの集合が一致するか (姓名の順序を問わない)
    s_set = set(scraped_parts)
    m_set = set(master_parts)
    if s_set == m_set: return True
    # 部分一致 (片方がもう片方を包含しているか、主要な2単語が一致するか)
    if len(s_set & m_set) >= 2: return True
    return False

def integrate():
    json_path = 'data/top14_scraping_results.json'
    csv_path = 'data_sources/final_master_data_v17_consolidated.csv.bak'
    output_path = 'data_sources/final_master_data_v17_consolidated_integrated.csv'
    
    if not os.path.exists(json_path):
        print("JSON data not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        scraped_data = json.load(f)

    # 検索用辞書
    club_lookup = {}
    for club, players in scraped_data.items():
        club_lookup[club] = players

    updated_count = 0
    not_found = []
    rows = []
    
    # 既存のCSVを読み込む
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = [f for f in reader.fieldnames if f] if reader.fieldnames else []
        for row in reader:
            # Noneキー (列数オーバー分) を削除
            if None in row: del row[None]
            
            team_raw = row.get("所属チーム", "")
            team_clean = re.sub(r'（.*）', '', team_raw).strip()
            
            name_en_raw = row.get("name_en", "") or row.get("英語名", "")
            master_parts = normalize_name(name_en_raw)
            
            match_found = False
            # 該当するクラブの選手リストから探す
            if team_clean in club_lookup:
                for p in club_lookup[team_clean]:
                    scraped_parts = normalize_name(p.get("name"))
                    if is_match(scraped_parts, master_parts):
                        if p.get("nationality"): row["国籍"] = p["nationality"]
                        if p.get("instagram"): row["SNS_Instagram"] = p["instagram"]
                        if p.get("twitter"): row["SNS_Twitter"] = p["twitter"]
                        if p.get("facebook"): row["SNS_Facebook"] = p["facebook"]
                        updated_count += 1
                        match_found = True
                        break
            
            if not match_found and row.get("Scraped_Url") and "top14" in row["Scraped_Url"].lower():
                not_found.append(f"{name_en_raw} ({team_clean})")
                
            rows.append(row)

    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        # extrasaction='ignore' で未知のキーを無視
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)

    print(f"Integration finished. Updated {updated_count} players.")
    if not_found:
        print(f"Match failed for {len(not_found)} Top 14 players (e.g. {not_found[:5]})")
        with open('data/mapping_failures_top14.txt', 'w', encoding='utf-8') as f:
            f.write("\n".join(not_found))
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    integrate()
