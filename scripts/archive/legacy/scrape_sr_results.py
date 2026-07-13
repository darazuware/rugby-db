import requests
import json
import os
import re
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://super.rugby/",
    "Origin": "https://super.rugby/"
}

# データの保存先
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TEAM_NAMES_JP_PATH = os.path.join(DATA_DIR, 'team_names_jp.json')
RESULTS_JSON_PATH = os.path.join(DATA_DIR, 'results_2026.json')

# チーム名日本語化マッピングの読み込み
with open(TEAM_NAMES_JP_PATH, 'r', encoding='utf-8') as f:
    TEAM_NAMES_DATA = json.load(f)
    SR_NAMES = TEAM_NAMES_DATA.get('super-rugby', {})

def normalize_team(name):
    name = name.strip()
    # 既に日本語名ならそのまま
    for team_data in SR_NAMES.values():
        if team_data['jp'] == name:
            return team_data['jp'], team_data['flag']
    
    # マッピングから検索
    for main_name, data in SR_NAMES.items():
        if name == main_name or name in data.get('aliases', []):
            return data['jp'], data['flag']
    
    # 部分一致
    for main_name, data in SR_NAMES.items():
        if name in main_name or any(name in alias for alias in data.get('aliases', [])):
            return data['jp'], data['flag']
            
    return name, "🇳🇿" # デフォルト

def scrape_sr_results():
    url = "https://omo.akamai.opta.net/auth/competition.php"
    params = {
        "feed_type": "ru1",
        "competition": "205",
        "season_id": "2026",
        "user": "OW2017",
        "psw": "dXWg5gVZ",
        "jsoncallback": "callback"
    }
    
    print(f"Fetching Super Rugby results from API...")
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()
        text = response.text
        
        json_str = text[text.find('(')+1 : text.rindex(')')]
        with open('/tmp/sr_api_debug.json', 'w', encoding='utf-8') as f_debug:
            f_debug.write(json_str)
        data = json.loads(json_str)
        
        # デバッグログ
        # print(f"DEBUG API DATA: {json.dumps(data.get('fixtures', {}).get('fixture', [])[:1], indent=2)}")
        
        fixtures_data = data.get('fixtures', {}).get('fixture', [])
        if not isinstance(fixtures_data, list):
            fixtures_data = [fixtures_data]
            
        # デバッグログ：最初の1件を詳細表示
        if fixtures_data:
             print("DEBUG Fixture JSON:", json.dumps(fixtures_data[0], indent=2))
            
        all_results = []
        for f in fixtures_data:
            attr = f.get('@attributes', {})
            match_id = attr.get('id')
            
            # 日付
            dt_raw = attr.get('datetime', '')
            date_iso = dt_raw.split('T')[0] if 'T' in dt_raw else ""
            
            # 節
            round_num = 0
            try:
                round_num = int(attr.get('round', '0'))
            except:
                pass
            
            # チームとスコア
            teams = f.get('team', [])
            home_team_name = ""
            away_team_name = ""
            score = "VS"
            
            if isinstance(teams, list) and len(teams) >= 2:
                # API構造に基づき @attributes.teamname, @attributes.home_or_away, @attributes.score を参照
                t0_attr = teams[0].get('@attributes', {})
                t1_attr = teams[1].get('@attributes', {})
                
                # home_or_away で分離
                if t0_attr.get('home_or_away', '').lower() == 'home':
                    h_obj, a_obj = t0_attr, t1_attr
                else:
                    h_obj, a_obj = t1_attr, t0_attr
                
                home_team_name = h_obj.get('teamname', '')
                away_team_name = a_obj.get('teamname', '')
                h_score = h_obj.get('score', '')
                a_score = a_obj.get('score', '')
                
                if h_score and a_score and str(h_score) != "0" and str(a_score) != "0": # 未来の試合は 0 になる可能性があるため VS に
                    score = f"{h_score}-{a_score}"
                elif f.get('@attributes', {}).get('status', '').lower() == 'result':
                    score = f"{h_score}-{a_score}" # 結果確定なら 0-0 もあり得る
            
            if not home_team_name or not away_team_name or home_team_name == away_team_name:
                continue

            home_jp, home_flag = normalize_team(home_team_name)
            away_jp, away_flag = normalize_team(away_team_name)
            
            detail_url = ""
            if match_id:
                detail_url = f"https://super.rugby/superrugby/match-centre/?competition=205&season=2026&match={match_id}"
            
            all_results.append({
                "round": round_num,
                "date": date_iso,
                "home": home_jp,
                "away": away_jp,
                "score": score,
                "home_flag": home_flag,
                "away_flag": away_flag,
                "detail_url": detail_url
            })
        
        return all_results
    except Exception as e:
        print(f"Error fetching SR results: {e}")
        return []

def main():
    if os.path.exists(RESULTS_JSON_PATH):
        with open(RESULTS_JSON_PATH, 'r', encoding='utf-8') as f:
            all_results = json.load(f)
    else:
        all_results = {"league-one": [], "super-rugby": [], "top14": [], "urc": []}

    new_sr_results = scrape_sr_results()
    
    if new_sr_results:
        all_results["super-rugby"] = new_sr_results
        
        with open(RESULTS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"Successfully updated {len(new_sr_results)} matches for Super Rugby.")
    else:
        print("No Super Rugby results found.")

if __name__ == "__main__":
    main()
