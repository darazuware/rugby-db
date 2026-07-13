import json
import os

PROJECT_ROOT = '/Users/ktamatzmoto/Desktop/rugbypicks'
TEAMS_JSON_PATH = os.path.join(PROJECT_ROOT, 'data/teams.json')

# Collected Data from Browser Subagent
HOME_GROUNDS = {
    # Premiership
    "Bath Rugby": "Recreation Ground",
    "Bristol Bears": "Ashton Gate",
    "Exeter Chiefs": "Sandy Park",
    "Gloucester Rugby": "Kingsholm",
    "Harlequins": "Twickenham Stoop",
    "Leicester Tigers": "Welford Road",
    "Newcastle Falcons": "Kingston Park",
    "Northampton Saints": "Franklin's Gardens",
    "Sale Sharks": "Salford Community Stadium",
    "Saracens": "StoneX Stadium",
    
    # Top 14
    "バイヨンヌ": "Stade Jean-Dauger",
    "ボルドー・ベグル": "Stade Chaban-Delmas",
    "カストル": "Stade Pierre-Fabre",
    "クレルモン": "Stade Marcel-Michelin",
    "ラ・ロシェル": "Stade Marcel-Deflandre",
    "リヨン": "Stade de Gerland",
    "モンペリエ": "GGL Stadium",
    "ポー": "Stade du Hameau",
    "ペルピニャン": "Stade Aimé-Giral",
    "ラシン92": "Paris La Défense Arena",
    "スタッド・フランセ": "Stade Jean-Bouin",
    "トゥーロン": "Stade Mayol",
    "トゥールーズ": "Stade Ernest-Wallon",
    "ヴァンヌ": "Stade de la Rabine",
    
    # Super Rugby
    "ACTブランビーズ": "GIO Stadium",
    "オークランド・ブルーズ": "Eden Park",
    "ワイカト・チーフス": "FMG Stadium Waikato",
    "カンタベリー・クルセイダーズ": "Apollo Projects Stadium",
    "フィジアン・ドゥルア": "HFC Bank Stadium / Churchill Park",
    "オタゴ・ハイランダーズ": "Forsyth Barr Stadium",
    "ウェリントン・ハリケーンズ": "Sky Stadium",
    "モアナ・パシフィカ": "Mt Smart Stadium (Go Media Stadium)",
    "NSWワラタス（ワラターズ）": "Allianz Stadium",
    "クイーンズランド・レッズ": "Suncorp Stadium",
    "ウェスタン・フォース": "HBF Park",
    
    # URC
    "ベネットン・ラグビー・トレヴィーゾ": "Stadio Monigo",
    "ヴォーダコム・ブルズ": "Loftus Versfeld Stadium",
    "カーディフ・ラグビー": "Cardiff Arms Park",
    "コナート・ラグビー": "Dexcom Stadium (The Sportsground)",
    "ドラゴンズ・ラグビー": "Rodney Parade",
    "エディンバラ・ラグビー": "Hive Stadium",
    "グラスゴー・ウォリアーズ": "Scotstoun Stadium",
    "レンスター・ラグビー": "RDS Arena / Aviva Stadium",
    "エミレーツ・ライオンズ": "Ellis Park Stadium",
    "マンスター・ラグビー": "Thomond Park / Virgin Media Park",
    "オスプリーズ": "Swansea.com Stadium",
    "スカーレッツ": "Parc y Scarlets",
    "ハリウッドベッツ・シャークス": "Kings Park Stadium",
    "DHLストーマーズ": "DHL Stadium",
    "アルスター・ラグビー": "Ravenhill Stadium (Kingspan Stadium)",
    "ゼブレ・パルマ": "Stadio Sergio Lanfranchi"
}

def update_teams_json():
    print(f"Loading {TEAMS_JSON_PATH}...")
    with open(TEAMS_JSON_PATH, 'r', encoding='utf-8') as f:
        teams = json.load(f)
    
    updated_count = 0
    for team in teams:
        name = team.get('team_name')
        
        # Match by team_name
        if name in HOME_GROUNDS:
            team['home_ground'] = HOME_GROUNDS[name]
            updated_count += 1
        
        # Fallback to team_en_name if needed
        elif team.get('team_en_name') in HOME_GROUNDS:
            team['home_ground'] = HOME_GROUNDS[team['team_en_name']]
            updated_count += 1
            
        # Ensure the field exists even if empty
        if 'home_ground' not in team:
            team['home_ground'] = ""

    print(f"Updated {updated_count} teams with home grounds.")
    with open(TEAMS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    print("Saved teams.json.")

if __name__ == "__main__":
    update_teams_json()
