import json
import os

def update_leagues():
    path = "data/rugby_leagues.json"
    if not os.path.exists(path): return
    
    with open(path, "r", encoding="utf-8") as f:
        leagues = json.load(f)
        
    # すでにないかチェック
    if not any(l.get("id") == 13 for l in leagues):
        leagues.append({
            "id": 13,
            "name": "Major League Rugby",
            "name_ja": "MLR",
            "country": "アメリカ・カナダ",
            "level": 1,
            "season": "2024",
            "url": "https://all.rugby/league/major-league-rugby"
        })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(leagues, f, ensure_ascii=False, indent=2)
        print("Updated rugby_leagues.json with MLR.")

def update_teams():
    path = "data/teams.json"
    if not os.path.exists(path): return
    
    with open(path, "r", encoding="utf-8") as f:
        teams = json.load(f)
        
    mlr_teams = [
        {"team_name": "Anthem RC", "slug": "anthem-rc", "league": "mlr"},
        {"team_name": "Chicago Hounds", "slug": "chicago-hounds", "league": "mlr"},
        {"team_name": "Dallas Jackals", "slug": "dallas-jackals", "league": "mlr"},
        {"team_name": "Houston SaberCats", "slug": "houston-sabercats", "league": "mlr"},
        {"team_name": "Miami Sharks", "slug": "miami-sharks", "league": "mlr"},
        {"team_name": "New England Free Jacks", "slug": "new-england-free-jacks", "league": "mlr"},
        {"team_name": "NOLA Gold", "slug": "nola-gold", "league": "mlr"},
        {"team_name": "Old Glory DC", "slug": "old-glory-dc", "league": "mlr"},
        {"team_name": "RFCLA", "slug": "rfcla", "league": "mlr"},
        {"team_name": "San Diego Legion", "slug": "san-diego-legion", "league": "mlr"},
        {"team_name": "Seattle Seawolves", "slug": "seattle-seawolves", "league": "mlr"},
        {"team_name": "Utah Warriors", "slug": "utah-warriors", "league": "mlr"}
    ]
    
    added_count = 0
    for mt in mlr_teams:
        if not any(t.get("slug") == mt["slug"] for t in teams):
            teams.append(mt)
            added_count += 1
            
    if added_count > 0:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(teams, f, ensure_ascii=False, indent=2)
        print(f"Added {added_count} MLR teams to teams.json.")

if __name__ == "__main__":
    update_leagues()
    update_teams()
