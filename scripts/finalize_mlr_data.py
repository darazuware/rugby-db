import json
import os
import pandas as pd
from datetime import datetime

MLR_NAME_MAP = {
    # Full names in rugby_teams.json
    "Anthem RC": {"ja": "アンセムRC", "id": 2000, "slug": "anthem-rc"},
    "Chicago Hounds": {"ja": "シカゴ・ハウンズ", "id": 2001, "slug": "chicago-hounds"},
    "Dallas Jackals": {"ja": "ダラス・ジャッカルズ", "id": 2002, "slug": "dallas-jackals"},
    "Houston SaberCats": {"ja": "ヒューストン・セイバーキャッツ", "id": 2003, "slug": "houston-sabercats"},
    "Miami Sharks": {"ja": "マイアミ・シャークス", "id": 2004, "slug": "miami-sharks"},
    "New England Free Jacks": {"ja": "ニューイングランド・フリージャックス", "id": 2005, "slug": "new-england-free-jacks"},
    "Nola Gold": {"ja": "NOLAゴールド", "id": 2006, "slug": "nola-gold"},
    "Old Glory DC": {"ja": "オールドグローリーDC", "id": 2007, "slug": "old-glory-dc"},
    "RFC Los Angeles": {"ja": "RFCLA", "id": 2008, "slug": "rfcla"},
    "San Diego Legion": {"ja": "サンディエゴ・レギオン", "id": 2009, "slug": "san-diego-legion"},
    "Seattle Seawolves": {"ja": "シアトル・シーウルブズ", "id": 2010, "slug": "seattle-seawolves"},
    "Utah Warriors": {"ja": "ユタ・ウォリアーズ", "id": 2011, "slug": "utah-warriors"},
    
    # all.rugby での略称・表記揺れ対応
    "Nola": {"ja": "NOLAゴールド", "id": 2006, "slug": "nola-gold"},
    "Old Glory": {"ja": "オールドグローリーDC", "id": 2007, "slug": "old-glory-dc"},
    "Houston": {"ja": "ヒューストン・セイバーキャッツ", "id": 2003, "slug": "houston-sabercats"},
    "Utah": {"ja": "ユタ・ウォリアーズ", "id": 2011, "slug": "utah-warriors"},
    "Seattle": {"ja": "シアトル・シーウルブズ", "id": 2010, "slug": "seattle-seawolves"},
    "San Diego": {"ja": "サンディエゴ・レギオン", "id": 2009, "slug": "san-diego-legion"},
    "Miami": {"ja": "マイアミ・シャークス", "id": 2004, "slug": "miami-sharks"},
    "Chicago": {"ja": "シカゴ・ハウンズ", "id": 2001, "slug": "chicago-hounds"},
    "New England": {"ja": "ニューイングランド・フリージャックス", "id": 2005, "slug": "new-england-free-jacks"},
    "Dallas": {"ja": "ダラス・ジャッカルズ", "id": 2002, "slug": "dallas-jackals"},
}

def update_rugby_teams():
    path = "data/rugby_teams.json"
    with open(path, "r", encoding="utf-8") as f:
        teams = json.load(f)
    
    added = 0
    # ユニークなIDで登録
    for info in [v for k, v in MLR_NAME_MAP.items() if "id" in v]:
        if info["id"] >= 2000 and not any(t.get("id") == info["id"] for t in teams):
            # チーム名を逆引き (Infoから元のキーを取得するのは面倒なのでハードコード)
            team_full_name = next(k for k, v in MLR_NAME_MAP.items() if v["id"] == info["id"] and len(k) > 10) 
            # もっと単純に
            teams.append({
                "id": info["id"],
                "name": team_full_name,
                "name_ja": info["ja"],
                "league_id": 13,
                "url": f"https://all.rugby/club/{info['slug']}"
            })
            added += 1
            
    if added > 0:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(teams, f, ensure_ascii=False, indent=2)
        print(f"Added {added} teams to rugby_teams.json.")

def process_results():
    input_path = "data_sources/mlr_results_2024.csv"
    if not os.path.exists(input_path): return
    
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} matches from {input_path}")
    
    # rugby_matches.json ロード
    matches_path = "data/rugby_matches.json"
    with open(matches_path, "r", encoding="utf-8") as f:
        all_matches = json.load(f)
        
    next_id = max([m.get("id", 0) for m in all_matches]) + 1
    
    # 重複排除のためのセット
    existing_mlr = set([(m["date"], m["home_team_id"], m["away_team_id"]) for m in all_matches if m.get("league_id") == 13])
    
    added = 0
    for _, row in df.iterrows():
        h_team = row["home_team"]
        a_team = row["away_team"]
        
        h_info = MLR_NAME_MAP.get(h_team)
        a_info = MLR_NAME_MAP.get(a_team)
        
        if h_info and a_info:
            # 日付パース (Saturday, March 2, 2024)
            # all.rugby Format: Sunday, March 3, 2024
            try:
                dt = datetime.strptime(row["date"], "%A, %B %d, %Y")
                date_iso = dt.strftime("%Y-%m-%d")
            except:
                date_iso = str(row["date"])
            
            match_key = (date_iso, h_info["id"], a_info["id"])
            if match_key not in existing_mlr:
                all_matches.append({
                    "id": next_id,
                    "date": date_iso,
                    "home_team_id": h_info["id"],
                    "away_team_id": a_info["id"],
                    "home_score": int(row["home_score"]) if str(row["home_score"]).isdigit() else 0,
                    "away_score": int(row["away_score"]) if str(row["away_score"]).isdigit() else 0,
                    "venue": "",
                    "league_id": 13
                })
                next_id += 1
                added += 1
                existing_mlr.add(match_key)
            
    if added > 0:
        with open(matches_path, "w", encoding="utf-8") as f:
            json.dump(all_matches, f, ensure_ascii=False, indent=2)
        print(f"Added {added} MLR matches to rugby_matches.json.")

if __name__ == "__main__":
    update_rugby_teams()
    process_results()
