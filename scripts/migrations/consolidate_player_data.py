import pandas as pd
import json
from datetime import datetime
import re

def calculate_age(birthdate_str):
    """Calculate age from birthdate string (format: YYYY.MM.DD)"""
    if pd.isna(birthdate_str) or not birthdate_str:
        return None
    try:
        parts = str(birthdate_str).split('.')
        if len(parts) == 3:
            birth_year, birth_month, birth_day = map(int, parts)
            today = datetime.now()
            age = today.year - birth_year
            if (today.month, today.day) < (birth_month, birth_day):
                age -= 1
            return age
    except:
        return None
    return None

def normalize_name(name):
    """Normalize name for matching"""
    if pd.isna(name) or not name:
        return ""
    return str(name).lower().strip().replace(' ', '').replace('-', '')

def main():
    print("=== Rugby Player Data Consolidation ===\n")
    
    # 1. Load League One players (main dataset)
    print("Loading League One players...")
    df_league_one = pd.read_csv('final_master_data_v16_nz_caps.csv')
    print(f"  ✓ Loaded {len(df_league_one)} League One players")
    
    # 2. Load Wallabies data
    print("Loading Wallabies data...")
    df_wallabies = pd.read_csv('wallabies.csv', encoding='shift_jis')
    print(f"  ✓ Loaded {len(df_wallabies)} Wallabies")
    
    # 3. Load All.Rugby players
    print("Loading All.Rugby players...")
    with open('data/rugby_players.json', 'r') as f:
        all_rugby_players = json.load(f)
    print(f"  ✓ Loaded {len(all_rugby_players)} All.Rugby players")
    
    # 4. Load teams and leagues
    print("Loading teams and leagues...")
    with open('data/rugby_teams.json', 'r') as f:
        teams = json.load(f)
    with open('data/rugby_leagues.json', 'r') as f:
        leagues = json.load(f)
    print(f"  ✓ Loaded {len(teams)} teams, {len(leagues)} leagues")
    
    # Create team and league lookups
    team_lookup = {t['id']: t for t in teams}
    league_lookup = {l['id']: l for l in leagues}
    
    # 5. Merge Wallabies caps into League One data
    print("\nMerging Wallabies caps...")
    wallabies_dict = {}
    for _, row in df_wallabies.iterrows():
        name = row['選手名']
        caps_col9 = row.get('Unnamed: 9', '')
        caps_col10 = row.get('Unnamed: 10', '')
        caps_col11 = row.get('Unnamed: 11', '')
        caps_col12 = row.get('Unnamed: 12', '')
        
        wallabies_dict[normalize_name(name)] = {
            'team1': caps_col9,
            'caps1': caps_col10,
            'team2': caps_col11,
            'caps2': caps_col12
        }
    
    merged_count = 0
    for idx, row in df_league_one.iterrows():
        name_norm = normalize_name(row['選手名'])
        if name_norm in wallabies_dict:
            wb_data = wallabies_dict[name_norm]
            # Update representative caps
            existing_caps = str(row.get('代表キャップ数', ''))
            if pd.notna(wb_data['team1']) and wb_data['team1']:
                new_cap = f"{wb_data['team1']}({int(wb_data['caps1'])})"
                if existing_caps and existing_caps != 'nan':
                    df_league_one.at[idx, '代表キャップ数'] = f"{existing_caps}, {new_cap}"
                else:
                    df_league_one.at[idx, '代表キャップ数'] = new_cap
            merged_count += 1
    
    print(f"  ✓ Merged {merged_count} Wallabies players")
    
    # 6. Update ages
    print("\nUpdating ages...")
    for idx, row in df_league_one.iterrows():
        new_age = calculate_age(row['生年月日'])
        if new_age:
            df_league_one.at[idx, '年齢'] = new_age
    print("  ✓ Ages updated")
    
    # 7. Create unified player database
    print("\nCreating unified player database...")
    
    unified_players = []
    
    for idx, row in df_league_one.iterrows():
        player = {
            'id': f"lo_{idx}",
            'source': 'league_one',
            'name_ja': row['選手名'],
            'name_en': row['英語名'],
            'position': row['ポジション'],
            'team': row['所属チーム'],
            'height': row['身長'],
            'weight': row['体重'],
            'birthdate': row['生年月日'],
            'age': row['年齢'],
            'high_school': row['高校'],
            'university': row['大学'],
            'league_one_caps': row['リーグワンキャップ数'],
            'representative_caps': row['代表キャップ数'],
            'career_history': row.get('Full_Career', ''),
            'url': row['URL']
        }
        unified_players.append(player)
    
    print(f"  ✓ Created {len(unified_players)} unified player records")
    
    # 8. Save consolidated data
    output_file = 'unified_player_database.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unified_players, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved to {output_file}")
    
    # Also save updated CSV
    csv_output = 'final_master_data_v17_consolidated.csv'
    df_league_one.to_csv(csv_output, index=False, encoding='utf-8-sig')
    print(f"✓ Saved to {csv_output}")
    
    # Summary
    print("\n=== Summary ===")
    print(f"Total players: {len(unified_players)}")
    print(f"With career history: {sum(1 for p in unified_players if p['career_history'])}")
    print(f"With representative caps: {sum(1 for p in unified_players if pd.notna(p['representative_caps']))}")

if __name__ == "__main__":
    main()
