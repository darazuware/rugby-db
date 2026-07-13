import json
import os
import re

PROJECT_ROOT = '/Users/ktamatzmoto/Desktop/rugbypicks'
L1_DETAILED_JSON = os.path.join(PROJECT_ROOT, 'data/league_one_teams_detailed.json')

def update_l1_detailed():
    print(f"Loading {L1_DETAILED_JSON}...")
    with open(L1_DETAILED_JSON, 'r', encoding='utf-8') as f:
        teams = json.load(f)
    
    updated_count = 0
    for team in teams:
        current_ground = team.pop('practice_ground', "")
        
        # Split Address and Name for League One
        # Many end with "センター", "グラウンド", "スタジアム", "パーク", "ラグビー場"
        match = re.search(r'(.*)(サントリー.*センター|ワイルドナイツ.*|スピアーズ.*|ヴォルテクス.*|シャトルズ.*|イーグルス.*|ライナーズ.*|ヴェルブリッツ.*|ブラックラムズ.*|ラガッツ.*|レッドハリケーンズ.*|レッドレグリオンズ.*|グリーンロケッツ.*|ブレイブルーパス.*|スティーラーズ.*|ダイナボアーズ.*|ヒート.*|福岡.*|ブルーレヴズ.*|Dパーク|シーウェイブス.*|レッドドルフィンズ.*|ブルーシャークス.*|レビンズ.*|ウォーターガッシュ.*|スカイアクティブズ.*|ラグビー場|スタジアム)', current_ground)
        if match:
            address = match.group(1).strip()
            name = match.group(2).strip()
            team['home_ground'] = name
            team['home_ground_address'] = address
            updated_count += 1
        else:
            team['home_ground'] = current_ground
            team['home_ground_address'] = ""

    print(f"Updated {updated_count} League One teams.")
    with open(L1_DETAILED_JSON, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    print("Saved detailed JSON.")

if __name__ == "__main__":
    update_l1_detailed()
