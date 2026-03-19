import json
import os

def main():
    redirects_path = 'data/redirects.json'
    teams_jp_path = 'data/team_names_jp.json'
    teams_json_path = 'data/teams.json'

    if not all(os.path.exists(p) for p in [redirects_path, teams_jp_path, teams_json_path]):
        print("Missing required data files.")
        return

    with open(redirects_path, 'r', encoding='utf-8') as f:
        redirects = json.load(f)

    with open(teams_jp_path, 'r', encoding='utf-8') as f:
        teams_jp = json.load(f)

    with open(teams_json_path, 'r', encoding='utf-8') as f:
        teams_list = json.load(f)

    # 英語スラッグの逆引き
    slug_map = { t['team_name']: t['slug'] for t in teams_list if t.get('league') == 'mlr' }
    
    # MLR のリダイレクトを追加
    count = 0
    if 'mlr' in teams_jp:
        for en_name, data in teams_jp['mlr'].items():
            jp_name = data['jp']
            target_slug = slug_map.get(jp_name)
            
            if target_slug:
                # 1. 直接の日本語名 (・あり)
                key1 = f"/teams/mlr/{jp_name}"
                if key1 not in redirects:
                    redirects[key1] = f"/teams/mlr/{target_slug}/"
                    count += 1
                
                # 2. ハイフン置換版 (ユーザー報告の形式)
                jp_name_dash = jp_name.replace('・', '-')
                if jp_name_dash != jp_name:
                    key2 = f"/teams/mlr/{jp_name_dash}"
                    if key2 not in redirects:
                        redirects[key2] = f"/teams/mlr/{target_slug}/"
                        count += 1
                
                print(f"Added redirect for {jp_name} -> {target_slug}")

    # 保存
    with open(redirects_path, 'w', encoding='utf-8') as f:
        json.dump(redirects, f, ensure_ascii=False, indent=2)

    print(f"Successfully added {count} MLR redirects to {redirects_path}.")

if __name__ == "__main__":
    main()
