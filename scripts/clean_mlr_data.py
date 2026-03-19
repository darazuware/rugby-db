import pandas as pd
import json
import os
import re

def clean_mlr_data():
    csv_path = 'data_sources/final_master_data_v27_normalized.csv'
    teams_json_path = 'data/teams.json'
    team_names_jp_path = 'data/team_names_jp.json'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return

    # Load teams data for MLR
    with open(teams_json_path, 'r', encoding='utf-8') as f:
        teams_data = json.load(f)
    
    mlr_teams = [t['team_name'] for t in teams_data if t.get('league') == 'mlr']
    print(f"Loaded {len(mlr_teams)} MLR teams from teams.json")

    # Load team names JP for mapping
    with open(team_names_jp_path, 'r', encoding='utf-8') as f:
        team_names_jp = json.load(f).get('mlr', {})

    # Read CSV
    df = pd.read_csv(csv_path).fillna('')
    print(f"Original CSV rows: {len(df)}")
    
    mlr_mask = df['League'] == 'mlr'
    mlr_df = df[mlr_mask].copy()
    other_df = df[~mlr_mask].copy()
    
    print(f"MLR players before cleaning: {len(mlr_df)}")

    cleaned_mlr_rows = []
    
    for _, row in mlr_df.iterrows():
        team_raw = str(row['Current_Team'])
        
        # 1. Extract actual team name from "The ... rugby team for ..."
        match = re.search(r'(?:The\s+)?(.*?)\s+rugby team for', team_raw, re.IGNORECASE)
        if match:
            clean_team = match.group(1).strip()
            # Special case mapping
            if "RFC Los Angeles" in clean_team: clean_team = "RFCLA"
            if "Houston Sabercats" in clean_team: clean_team = "Houston SaberCats"
            if "Old Glory DC RFC" in clean_team: clean_team = "Old Glory DC"
            if "Anthem Rugby Carolina" in clean_team: clean_team = "Anthem RC"
            
            row['Current_Team'] = clean_team
        else:
            clean_team = team_raw
            
        # 2. Filter: Is this an actual MLR team?
        if clean_team not in mlr_teams:
            # If it's a famous non-MLR team like Toulouse, Leinster, etc., skip this player (likely an error)
            if any(x in clean_team for x in ["Toulousain", "Leinster", "Bath Rugby", "Northampton Saints", "Blues", "Crusaders"]):
                continue
            
            # If it's not in our list, but labeled as mlr, keep it but maybe it's low quality
            # (Wait! Zurabi Zhvania was in Chicago Hounds, which IS in mlr_teams)
        
        # 3. Fix Height/Weight
        try:
            h = float(row['Height'])
            if h < 140: # Too short
                row['Height'] = ""
        except:
            row['Height'] = ""
            
        try:
            w = float(row['Weight'])
            if w < 50: # Too light
                row['Weight'] = ""
        except:
            row['Weight'] = ""

        # 4. Fill Name_JA if missing and we have a mapping? (Hard for names, but let's keep it as is)
        
        cleaned_mlr_rows.append(row)

    new_mlr_df = pd.DataFrame(cleaned_mlr_rows)
    print(f"MLR players after cleaning: {len(new_mlr_df)}")

    # Combine back
    final_df = pd.concat([other_df, new_mlr_df], ignore_index=True)
    
    # Save back
    final_df.to_csv(csv_path, index=False)
    print(f"Saved cleaned data to {csv_path}")

if __name__ == "__main__":
    clean_mlr_data()
