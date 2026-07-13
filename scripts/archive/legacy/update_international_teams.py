import json
import pandas as pd
import os
import re

def main():
    # 1. データの読み込み
    rankings_path = "data/world_rankings.json"
    teams_path = "data/teams.json"
    csv_path = "data_sources/final_master_data_v25_integrated.csv"
    
    with open(rankings_path, "r", encoding="utf-8") as f:
        rankings = json.load(f)
        
    with open(teams_path, "r", encoding="utf-8") as f:
        teams = json.load(f)
        
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    
    # 既存の国際チームのセット（重複チェック用）
    existing_international_slugs = {t["slug"] for t in teams if t["league"] == "international"}
    
    # 全てのランキング対象国（男子・女子統合）
    target_countries = []
    for entry in (rankings.get("mens", []) + rankings.get("womens", [])):
        target_countries.append({
            "name_en": entry["team_en"],
            "name_jp": entry["team_jp"],
            "slug": entry["team_en"].lower().replace(" ", "-"),
            "abbreviation": entry["abbreviation"]
        })
        
    # 重複排除しながら追加
    added_count = 0
    new_slugs_added = []
    
    for country in target_countries:
        slug = country["slug"]
        if slug in existing_international_slugs:
            continue
            
        # 選手データに存在するかチェック
        # 1. Caps カラムに "(国名)" が含まれるか
        # 2. Name_EN または Name_JP に国名が含まれる（これは微妙だが一応）
        # 3. Country カラムが一致するか
        
        name_en = country["name_en"]
        name_jp = country["name_jp"]
        
        # Caps 内のカッコ内一致を検索
        has_players = False
        
        # パターン1: (Country)
        pattern = rf"\({re.escape(name_en)}\)"
        pattern_jp = rf"\({re.escape(name_jp)}\)"
        
        if df["Caps"].str.contains(pattern, case=False, regex=True).any() or \
           df["Caps"].str.contains(pattern_jp, case=False, regex=True).any() or \
           df["Country"].str.contains(name_en, case=False).any() or \
           df["Country"].str.contains(name_jp, case=False).any():
            has_players = True
            
        if has_players:
            # teams.json に追加
            new_id = max([t["id"] for t in teams]) + 1
            new_team = {
                "id": new_id,
                "team_name": name_jp,
                "team_en_name": name_en.upper(),
                "league": "international",
                "slug": slug,
                "division": name_jp,
                "host_area": name_jp,
                "official_site": ""
            }
            teams.append(new_team)
            existing_international_slugs.add(slug)
            new_slugs_added.append(slug)
            added_count += 1
            
    if added_count > 0:
        with open(teams_path, "w", encoding="utf-8") as f:
            json.dump(teams, f, ensure_ascii=False, indent=4)
        print(f"Successfully added {added_count} new international teams to teams.json: {', '.join(new_slugs_added)}")
    else:
        print("No new international teams need to be added.")

if __name__ == "__main__":
    main()
