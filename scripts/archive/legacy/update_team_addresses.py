import json
import os
import re

PROJECT_ROOT = '/Users/ktamatzmoto/Desktop/rugbypicks'
TEAMS_JSON_PATH = os.path.join(PROJECT_ROOT, 'data/teams.json')

# Collected Addresses from Browser Subagent
STADIUM_INFO = {
    "Recreation Ground": "Spring Gardens, Bath BA2 4DS, UK",
    "Ashton Gate": "Ashton Gate Rd, Bristol BS3 2EJ, UK",
    "Sandy Park": "Sandy Park Way, Exeter EX2 7NN, UK",
    "Kingsholm": "Kingsholm Rd, Kingsholm, Gloucester GL1 3AX, UK",
    "Twickenham Stoop": "Langhorn Dr, Twickenham TW2 7SX, UK",
    "Welford Road": "Aylestone Rd, Leicester LE2 7TR, UK",
    "Kingston Park": "Brunton Rd, Kenton Bank Foot, Newcastle upon Tyne NE13 8AF, UK",
    "Franklin's Gardens": "Weedon Road, St James, Northampton NN5 5BG, UK",
    "Salford Community Stadium": "1 Stadium Way, Eccles, Manchester M30 7EY, UK",
    "StoneX Stadium": "Greenlands Lane, Hendon, London NW4 1RL, UK",
    "Stade Ernest-Wallon": "114 Rue des Troènes, 31200 Toulouse, France",
    "Stade Chaban-Delmas": "Place Johnston, 33000 Bordeaux, France",
    "Stade Mayol": "Quai Joseph Lafontan, 83000 Toulon, France",
    "Stade Marcel-Deflandre": "27 avenue du Maréchal Juin, 17000 La Rochelle, France",
    "Stade Marcel-Michelin": "35 Rue du Clos Four, 63100 Clermont-Ferrand, France",
    "Paris La Défense Arena": "99 Jardins de l'Arche, 92000 Nanterre, France",
    "Stade Jean-Bouin": "20-40 Avenue du Général Sarrail, 75016 Paris, France",
    "Eden Park": "42 Reimers Ave, Kingsland, Auckland 1024, New Zealand",
    "Sky Stadium": "105 Waterloo Quay, Pipitea, Wellington 6140, New Zealand",
    "RDS Arena": "Merrion Road, Ballsbridge, Dublin 4, Ireland",
    "Scotstoun Stadium": "72-112 Danes Drive, Glasgow G14 9HD, UK",
    "Thomond Park": "Cratloe Rd, Ballynanty Beg, Limerick, V94 XWK5, Ireland",
    "Stadio Monigo": "Stadio Monigo, 31100 Treviso, Italy",
    "Loftus Versfeld Stadium": "416 Kirkness St, Arcadia, Pretoria, 0007, South Africa",
    "Loftus Versfeld": "416 Kirkness St, Arcadia, Pretoria, 0007, South Africa",
    "Cardiff Arms Park": "Westgate St, Cardiff CF10 1JA, UK",
    "Dexcom Stadium (The Sportsground)": "Merrion Road, Ballsbridge, Dublin 4, Ireland", # Note: Sportsground is Galway
    "Dexcom Stadium": "College Rd, Galway, Ireland",
    "Rodney Parade": "Rodney Rd, Newport NP19 0UU, UK",
    "Hive Stadium": "Roseburn St, Edinburgh EH12 5PJ, UK",
    "Ellis Park Stadium": "47 Siemert Road, Doornfontein, Johannesburg, 2028, South Africa",
    "Virgin Media Park": "Tramore Rd, Cork, Ireland",
    "Swansea.com Stadium": "Landore, Swansea SA1 2FA, UK",
    "Parc y Scarlets": "Pemberton, Llanelli SA14 9UZ, UK",
    "Kings Park Stadium": "1 Jacko Jackson Dr, Stamford Hill, Durban, 4025, South Africa",
    "DHL Stadium": "Fritz Sonnenberg Rd, Green Point, Cape Town, 8051, South Africa",
    "Ravenhill Stadium": "134 Ravenhill Rd, Belfast BT6 0DG, UK",
    "Stadio Sergio Lanfranchi": "Viale Sergio Lanfranchi, 1, 43122 Parma, Italy",
    "GIO Stadium": "Battye St, Bruce ACT 2617, Australia",
    "FMG Stadium Waikato": "128 Seddon Road, Frankton, Hamilton 3204, New Zealand",
    "Apollo Projects Stadium": "95 Jack Hinton Drive, Addington, Christchurch 8024, New Zealand",
    "HFC Bank Stadium": "Nanuku St, Suva, Fiji",
    "Forsyth Barr Stadium": "130 Anzac Avenue, Dunedin North, Dunedin 9016, New Zealand",
    "Mt Smart Stadium (Go Media Stadium)": "2 Beasley Ave, Penrose, Auckland 1061, New Zealand",
    "Allianz Stadium": "Driver Ave, Moore Park NSW 2021, Australia",
    "Suncorp Stadium": "40 Castlemaine St, Milton QLD 4064, Australia",
    "HBF Park": "310 Pier St, Perth WA 6000, Australia"
}

def update_teams_json():
    print(f"Loading {TEAMS_JSON_PATH}...")
    with open(TEAMS_JSON_PATH, 'r', encoding='utf-8') as f:
        teams = json.load(f)
    
    updated_count = 0
    for team in teams:
        current_ground = team.get('home_ground', "")
        
        # 1. Foreign Teams - Match by Stadium Name and Add Address
        if current_ground in STADIUM_INFO:
            team['home_ground_address'] = STADIUM_INFO[current_ground]
            updated_count += 1
        
        # 2. League One Teams - Split Address and Name
        elif team.get('league') == 'league-one' and current_ground:
            # Try to split if it looks like [Address][Name]
            # Many end with "センター", "グラウンド", "スタジアム", "パーク"
            match = re.search(r'(.*)(サントリー.*センター|ワイルドナイツ.*|スピアーズ.*|ヴォルテクス.*|シャトルズ.*|イーグルス.*|ライナーズ.*|ヴェルブリッツ.*|ブラックラムズ.*|ラガッツ.*|レッドハリケーンズ.*|レッドレグリオンズ.*|グリーンロケッツ.*|ブレイブルーパス.*|スティーラーズ.*|ダイナボアーズ.*|ヒート.*|福岡.*|ブルーレヴズ.*|Dパーク|シーウェイブス.*|レッドドルフィンズ.*|ブルーシャークス.*|レビンズ.*|ウォーターガッシュ.*|スカイアクティブズ.*|ラグビー場)', current_ground)
            if match:
                address = match.group(1).strip()
                name = match.group(2).strip()
                team['home_ground'] = name
                team['home_ground_address'] = address
                updated_count += 1
            else:
                # If no clear name split, keep as is but ensure field exists
                team['home_ground_address'] = ""

        else:
            if 'home_ground_address' not in team:
                team['home_ground_address'] = ""

    # Specific fixes
    for team in teams:
        if team.get('team_name') == "レンスター・ラグビー":
             team['home_ground'] = "RDS Arena"
             team['home_ground_address'] = STADIUM_INFO["RDS Arena"]

    print(f"Updated {updated_count} teams.")
    with open(TEAMS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    print("Saved teams.json.")

if __name__ == "__main__":
    update_teams_json()
