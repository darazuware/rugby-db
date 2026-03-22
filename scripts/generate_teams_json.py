import csv
import json
import os
import re
import unicodedata
from team_utils import get_team_info

def slugify(text):
    if not text: return ""
    # 日本語（ひらがな、カタカナ、漢字）が含まれているかチェック
    try:
        for char in text:
            name = unicodedata.name(char)
            if any(x in name for x in ['HIRAGANA', 'KATAKANA', 'CJK UNIFIED']):
                return "" # 日本語が含まれる場合は空を返す
    except:
        pass

    # アクセント除去 (NFD分解して結合文字を除く)
    text = unicodedata.normalize('NFD', text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    # 記号置換
    text = text.lower().replace(' ', '-').replace("'", '').replace('&', 'and')
    # アルファベット、数字、ハイフン以外を除去
    text = re.sub(r'[^a-z0-9-]', '', text)
    return text.strip('-')

def main():
    all_teams = []
    
    # 手動スラッグマッピング (アクセント記号や特殊な命名規則用)
    top14_slug_map = {
        "トゥールーズ": "toulouse",
        "ボルドー・ベグル": "bordeaux",
        "スタッド・フランセ": "paris",
        "トゥーロン": "toulon",
        "ラ・ロシェル": "la-rochelle",
        "ラシン92": "racing-92",
        "リヨン": "lyon",
        "カストル": "castres",
        "ポー": "pau",
        "ペルピニャン": "perpignan",
        "バイヨンヌ": "bayonne",
        "クレルモン": "clermont",
        "モンペリエ": "montpellier",
        "ヴァンヌ": "vannes"
    }
    
    prem_slug_map = {
        "ノーサンプトン・セインツ": "northampton-saints",
        "バース・ラグビー": "bath-rugby",
        "ブリストル・ベアーズ": "bristol-bears",
        "レスター・タイガーズ": "leicester-tigers",
        "エクセター・チーフス": "exeter-chiefs",
        "サラセンズ": "saracens",
        "セール・シャークス": "sale-sharks",
        "グロスター・ラグビー": "gloucester-rugby",
        "ハーレクインズ": "harlequins",
        "ニューカッスル・ファルコンズ": "newcastle-falcons"
    }

    # V27 Master CSV から全リーグのチームを抽出
    MASTER_CSV = 'data_sources/final_master_data_v27_normalized.csv'
    print(f"Extracting all teams from {MASTER_CSV}...")
    
    # リーグごとのチーム辞書
    leagues_teams = {
        'league-one': {},
        'super-rugby': {},
        'urc': {},
        'top14': {},
        'premiership': {}
    }

    # 外国チームのスタジアム情報
    FOREIGN_STADIUMS = {
        "Bath Rugby": ("Recreation Ground", "Spring Gardens, Bath BA2 4DS, UK"),
        "Bristol Bears": ("Ashton Gate", "Ashton Gate Rd, Bristol BS3 2EJ, UK"),
        "Exeter Chiefs": ("Sandy Park", "Sandy Park Way, Exeter EX2 7NN, UK"),
        "Gloucester Rugby": ("Kingsholm", "Kingsholm Rd, Kingsholm, Gloucester GL1 3AX, UK"),
        "Harlequins": ("Twickenham Stoop", "Langhorn Dr, Twickenham TW2 7SX, UK"),
        "Leicester Tigers": ("Welford Road", "Aylestone Rd, Leicester LE2 7TR, UK"),
        "Newcastle Falcons": ("Kingston Park", "Brunton Rd, Kenton Bank Foot, Newcastle upon Tyne NE13 8AF, UK"),
        "Northampton Saints": ("Franklin's Gardens", "Weedon Road, St James, Northampton NN5 5BG, UK"),
        "Sale Sharks": ("Salford Community Stadium", "1 Stadium Way, Eccles, Manchester M30 7EY, UK"),
        "Saracens": ("StoneX Stadium", "Greenlands Lane, Hendon, London NW4 1RL, UK"),
        "トゥールーズ": ("Stade Ernest-Wallon", "114 Rue des Troènes, 31200 Toulouse, France"),
        "ボルドー・ベグル": ("Stade Chaban-Delmas", "Place Johnston, 33000 Bordeaux, France"),
        "バイヨンヌ": ("Stade Jean-Dauger", "Stade Jean-Dauger, Bayonne, France"),
        "カストル": ("Stade Pierre-Fabre", "Stade Pierre-Fabre, Castres, France"),
        "クレルモン": ("Stade Marcel-Michelin", "35 Rue du Clos Four, 63100 Clermont-Ferrand, France"),
        "ラ・ロシェル": ("Stade Marcel-Deflandre", "27 avenue du Maréchal Juin, 17000 La Rochelle, France"),
        "リヨン": ("Stade de Gerland", "Stade de Gerland, Lyon, France"),
        "モンペリエ": ("GGL Stadium", "GGL Stadium, Montpellier, France"),
        "ポー": ("Stade du Hameau", "Stade du Hameau, Pau, France"),
        "ペルピニャン": ("Stade Aimé-Giral", "Stade Aimé-Giral, Perpignan, France"),
        "ラシン92": ("Paris La Défense Arena", "99 Jardins de l'Arche, 92000 Nanterre, France"),
        "スタッド・フランセ": ("Stade Jean-Bouin", "20-40 Avenue du Général Sarrail, 75016 Paris, France"),
        "トゥーロン": ("Stade Mayol", "Quai Joseph Lafontan, 83000 Toulon, France"),
        "ヴァンヌ": ("Stade de la Rabine", "Stade de la Rabine, Vannes, France"),
        "ACTブランビーズ": ("GIO Stadium", "Battye St, Bruce ACT 2617, Australia"),
        "オークランド・ブルーズ": ("Eden Park", "42 Reimers Ave, Kingsland, Auckland 1024, New Zealand"),
        "ワイカト・チーフス": ("FMG Stadium Waikato", "128 Seddon Road, Frankton, Hamilton 3204, New Zealand"),
        "カンタベリー・クルセイダーズ": ("Apollo Projects Stadium", "95 Jack Hinton Drive, Addington, Christchurch 8024, New Zealand"),
        "フィジアン・ドゥルア": ("HFC Bank Stadium", "Nanuku St, Suva, Fiji"),
        "オタゴ・ハイランダーズ": ("Forsyth Barr Stadium", "130 Anzac Avenue, Dunedin North, Dunedin 9016, New Zealand"),
        "ウェリントン・ハリケーンズ": ("Sky Stadium", "105 Waterloo Quay, Pipitea, Wellington 6140, New Zealand"),
        "モアナ・パシフィカ": ("Mt Smart Stadium", "2 Beasley Ave, Penrose, Auckland 1061, New Zealand"),
        "NSWワラタス（ワラターズ）": ("Allianz Stadium", "Driver Ave, Moore Park NSW 2021, Australia"),
        "クイーンズランド・レッズ": ("Suncorp Stadium", "40 Castlemaine St, Milton QLD 4064, Australia"),
        "ウェスタン・フォース": ("HBF Park", "310 Pier St, Perth WA 6000, Australia"),
        "ベネットン・ラグビー・トレVIーゾ": ("Stadio Monigo", "Stadio Monigo, 31100 Treviso, Italy"),
        "ヴォーダコム・ブルズ": ("Loftus Versfeld Stadium", "416 Kirkness St, Arcadia, Pretoria, 0007, South Africa"),
        "カーディフ・ラグビー": ("Cardiff Arms Park", "Westgate St, Cardiff CF10 1JA, UK"),
        "コナート・ラグビー": ("Dexcom Stadium", "College Rd, Galway, Ireland"),
        "ドラゴンズ・ラグビー": ("Rodney Parade", "Rodney Rd, Newport NP19 0UU, UK"),
        "エディンバラ・ラグビー": ("Hive Stadium", "Roseburn St, Edinburgh EH12 5PJ, UK"),
        "グラスゴー・ウォリアーズ": ("Scotstoun Stadium", "72-112 Danes Drive, Glasgow G14 9HD, UK"),
        "レンスター・ラグビー": ("RDS Arena", "Merrion Road, Ballsbridge, Dublin 4, Ireland"),
        "エミレーツ・ライオンズ": ("Ellis Park Stadium", "47 Siemert Road, Doornfontein, Johannesburg, 2028, South Africa"),
        "マンスター・ラグビー": ("Thomond Park", "Cratloe Rd, Ballynanty Beg, Limerick, Ireland"),
        "オスプリーズ": ("Swansea.com Stadium", "Landore, Swansea SA1 2FA, UK"),
        "スカーレッツ": ("Parc y Scarlets", "Pemberton, Llanelli SA14 9UZ, UK"),
        "ハリウッドベッツ・シャークス": ("Kings Park Stadium", "1 Jacko Jackson Dr, Stamford Hill, Durban, 4025, South Africa"),
        "DHLストーマーズ": ("DHL Stadium", "Fritz Sonnenberg Rd, Green Point, Cape Town, 8051, South Africa"),
        "アルスター・ラグビー": ("Ravenhill Stadium", "134 Ravenhill Rd, Belfast BT6 0DG, UK"),
        "ゼブレ・パルマ": ("Stadio Sergio Lanfranchi", "Viale Sergio Lanfranchi, 1, 43122 Parma, Italy")
    }

    if os.path.exists(MASTER_CSV):
        with open(MASTER_CSV, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                league = str(row.get('League', '')).strip().lower()
                if league == 'leagueone': league = 'league-one'
                if league not in leagues_teams: continue
                
                t_name = row.get('Current_Team')
                if not t_name or t_name.lower() == 'nan': continue
                
                if t_name not in leagues_teams[league]:
                    info = get_team_info(t_name)
                    jp_name = info.get('jp', t_name) if info else t_name
                    en_name = info.get('name_en', t_name) if info else t_name
                    
                    # スラッグ決定
                    slug = info['slug'] if info else slugify(en_name)
                    # 手動マッピング優先
                    if league == 'top14' and jp_name in top14_slug_map:
                        slug = top14_slug_map[jp_name]
                    elif league == 'premiership' and jp_name in prem_slug_map:
                        slug = prem_slug_map[jp_name]
                    
                    # 万が一スラッグが空の場合は名前から生成
                    if not slug:
                        slug = re.sub(r'[^a-z0-9-]+', '-', t_name.lower()).strip('-')

                    # 外国チームのグラウンド情報を補完
                    ground_name = ""
                    ground_address = ""
                    if jp_name in FOREIGN_STADIUMS:
                        ground_name, ground_address = FOREIGN_STADIUMS[jp_name]
                    elif en_name in FOREIGN_STADIUMS:
                        ground_name, ground_address = FOREIGN_STADIUMS[en_name]

                    leagues_teams[league][t_name] = {
                        "team_name": jp_name,
                        "team_en_name": en_name,
                        "slug": slug,
                        "league": league,
                        "home_ground": ground_name,
                        "home_ground_address": ground_address
                    }

    # League One の詳細情報をマージ
    if os.path.exists('data/league_one_teams_detailed.json'):
        with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
            l1_details = json.load(f)
            for d in l1_details:
                for t_name, t_data in leagues_teams['league-one'].items():
                    if t_name == d['team_name'] or t_data['team_name'] == d['team_name']:
                        t_data.update({
                            "division": d.get('division'),
                            "host_area": d.get('host_area'),
                            "legal_entity": d.get('legal_entity'),
                            "official_site": d.get('official_site'),
                            "home_ground": d.get('home_ground'),
                            "home_ground_address": d.get('home_ground_address')
                        })
                        break
    
    # 全チームをリスト化
    for league in leagues_teams:
        all_teams.extend(leagues_teams[league].values())

    # 重複排除 (名前 + リーグ + スラッグベース)
    unique_teams = []
    seen = set()
    for t in all_teams:
        key = f"{t['league']}-{t['team_name']}-{t['slug']}"
        if key not in seen:
            unique_teams.append(t)
            seen.add(key)

    with open('data/teams.json', 'w', encoding='utf-8') as f:
        json.dump(unique_teams, f, ensure_ascii=False, indent=2)
    
    print(f"Generated data/teams.json with {len(unique_teams)} teams.")

if __name__ == "__main__":
    main()
