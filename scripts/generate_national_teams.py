import pandas as pd
import json
import os
import re
from player_utils import PlayerDataProcessor

# 設定
CSV_PATH = 'data_sources/final_master_data_v27_normalized.csv'
CONFIG_PATH = 'data/national_teams_config.json'
OUTPUT_PATH = 'data/national_players_map.json'

def main():
    print(f"Loading config from {CONFIG_PATH}...")
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # マッピング辞書の構築
    country_to_id = {}
    for team in config:
        tid = team['id']
        name_clean = team['name'].replace('代表', '')
        country_to_id[name_clean.lower()] = tid
        country_to_id[tid.lower()] = tid
        if 'en_name' in team:
            country_to_id[team['en_name'].lower()] = tid

    # 追加の国名エイリアス
    aliases = {
        "nz": "new-zealand", "new zealand": "new-zealand", "ニュージーランド": "new-zealand",
        "sa": "south-africa", "south africa": "south-africa", "南アフリカ": "south-africa",
        "aus": "australia", "オーストラリア": "australia",
        "usa": "usa", "united states": "usa", "アメリカ": "usa",
        "ire": "ireland", "ireland": "ireland", "アイルランド": "ireland",
        "eng": "england", "england": "england", "イングランド": "england",
        "fra": "france", "french": "france", "française": "france", "français": "france", "フランス": "france",
        "jpn": "japan", "japan": "japan", "日本": "japan"
    }
    country_to_id.update(aliases)

    print(f"Loading CSV from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
    
    national_players = {team['id']: [] for team in config}
    processed_count = 0

    for i, row in df.iterrows():
        nationality = str(row.get('Nationality', '')).strip().lower()
        if not nationality or nationality == 'nan':
            # 代表キャップ数があればそこから推測 (将来的な拡張用)
            continue
            
        target_id = country_to_id.get(nationality)
        # 部分一致も試みる (例: "France代表" -> "france")
        if not target_id:
            for key, val in country_to_id.items():
                if key in nationality:
                    target_id = val
                    break
        
        if not target_id: continue
        
        name_en = str(row.get('Full_Name', ''))
        scraped_url = str(row.get('Scraped_Url', ''))
        
        # 共通スラッグ生成
        slug = PlayerDataProcessor.generate_player_slug(name_en, i + 1, scraped_url)
        
        # マップ用のデータ構造
        player_entry = {
            "name_ja": str(row.get('Name_JA', '')),
            "name_en": name_en,
            "slug": slug,
            "position": str(row.get('Position', '')),
            "team": str(row.get('Current_Team', '')),
            "league": str(row.get('League', '')),
            "caps": str(row.get('Representative_Caps', '0')),
            "age": str(row.get('Age', '')),
            "height": str(row.get('Height', '')),
            "weight": str(row.get('Weight', ''))
        }
        
        national_players[target_id].append(player_entry)
        processed_count += 1

    # 重複排除とソート (キャップ数順)
    for tid in national_players:
        # スラッグベースで重複排除
        seen_slugs = set()
        unique_list = []
        for p in national_players[tid]:
            if p['slug'] not in seen_slugs:
                unique_list.append(p)
                seen_slugs.add(p['slug'])
        
        # ソート: キャップ数順 (数値化して降順)
        unique_list.sort(key=lambda x: int(re.search(r'(\d+)', str(x['caps'])).group(1)) if re.search(r'(\d+)', str(x['caps'])) else 0, reverse=True)
        national_players[tid] = unique_list

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(national_players, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully mapped {processed_count} instances to {len(seen_slugs)} unique players in {OUTPUT_PATH}.")

if __name__ == "__main__":
    main()
