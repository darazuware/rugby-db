import requests
import json
import os
import re
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.unitedrugby.com/",
    "Origin": "https://www.unitedrugby.com/"
}

# データの保存先
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TEAM_NAMES_JP_PATH = os.path.join(DATA_DIR, 'team_names_jp.json')
RESULTS_JSON_PATH = os.path.join(DATA_DIR, 'results_2026.json')

# チーム名日本語化マッピングの読み込み
with open(TEAM_NAMES_JP_PATH, 'r', encoding='utf-8') as f:
    TEAM_NAMES_DATA = json.load(f)
    URC_NAMES = TEAM_NAMES_DATA.get('urc', {})

def normalize_team(name):
    name = name.strip()
    # 既に日本語名ならそのまま
    for team_data in URC_NAMES.values():
        if team_data['jp'] == name:
            return team_data['jp'], team_data['flag']
    
    # マッピングから検索
    for main_name, data in URC_NAMES.items():
        if name == main_name or name in data.get('aliases', []):
            return data['jp'], data['flag']
    
    # 部分一致
    for main_name, data in URC_NAMES.items():
        if name in main_name or any(name in alias for alias in data.get('aliases', [])):
            return data['jp'], data['flag']
            
    return name, "🏴" # デフォルト

def scrape_urc_results():
    url = "https://www.unitedrugby.com/graphql"
    # operationName: GetRoundsData
    # sha256Hash: 4735fb2d10bd7bcd64b519813bf87de70abc5e6fe5f93b3aab2e6f68e3ee4e5b
    params = {
        "operationName": "GetRoundsData",
        "variables": json.dumps({"seasonId": 202501}),
        "extensions": json.dumps({
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "4735fb2d10bd7bcd64b519813bf87de70abc5e6fe5f93b3aab2e6f68e3ee4e5b"
            }
        })
    }
    
    print(f"Fetching URC rounds and match stats from GraphQL API...")
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        matchstats = data.get('data', {}).get('matchstats', [])
        if not matchstats:
            print("No matchstats found in response.")
            # Debug: dump data if empty
            with open('data/urc_rounds_error_debug.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return []
            
        all_results = []
        for ms in matchstats:
            try:
                sd = ms.get('stats_data', {})
                if not sd: continue
                
                home_obj = sd.get('homeTeam', {})
                away_obj = sd.get('awayTeam', {})
                
                home_team_name = home_obj.get('team', {}).get('name', '')
                away_team_name = away_obj.get('team', {}).get('name', '')
                
                if not home_team_name or not away_team_name:
                    continue
                    
                h_score = home_obj.get('score', {}).get('finalScore')
                a_score = away_obj.get('score', {}).get('finalScore')
                
                score = "VS"
                if h_score is not None and a_score is not None:
                    score = f"{h_score}-{a_score}"
                
                date_raw = sd.get('dateTime', '') or ms.get('match_datetime', '')
                date_iso = date_raw[:10] if date_raw else ""
                
                round_info = sd.get('round', {})
                if isinstance(round_info, dict):
                    round_num = round_info.get('name', '')
                else:
                    round_num = str(round_info)

                # "Round 1" から数字だけ抽出
                if isinstance(round_num, str) and 'Round' in round_num:
                    round_match = re.search(r'(\d+)', round_num)
                    if round_match:
                        round_num = int(round_match.group(1))
                else:
                    try:
                        round_num = int(round_num) if round_num else 0
                    except:
                        round_num = 0

                match_id = sd.get('id', '') or ms.get('match_id', '')

                home_jp, home_flag = normalize_team(home_team_name)
                away_jp, away_flag = normalize_team(away_team_name)
                
                detail_url = ""
                if match_id:
                    detail_url = f"https://www.unitedrugby.com/match-centre/202501/{match_id}"
                
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
            except Exception as e:
                print(f"Error processing matchstat: {e}")
                print(f"Data: {json.dumps(ms, indent=2)}")
                continue
        
        return all_results
    except Exception as e:
        print(f"Error fetching URC results: {e}")
        return []

def main():
    if os.path.exists(RESULTS_JSON_PATH):
        with open(RESULTS_JSON_PATH, 'r', encoding='utf-8') as f:
            all_results = json.load(f)
    else:
        all_results = {"league-one": [], "super-rugby": [], "top14": [], "urc": []}

    new_urc_results = scrape_urc_results()
    
    if new_urc_results:
        # 重複排除をしつつマージするのが理想だが、今回は洗い替え
        all_results["urc"] = new_urc_results
        
        with open(RESULTS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"Successfully updated {len(new_urc_results)} matches for URC.")
    else:
        print("No URC results found.")

if __name__ == "__main__":
    main()
