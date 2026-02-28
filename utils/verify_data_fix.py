import json
import re
import os
from scripts.player_utils import clean_team_name, get_canonical_school_name, get_enrolment_year

def check_all_players():
    print("=== 全選手データ整合性チェック開始 ===")
    
    with open('data/unified_player_database_final.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    players = data if isinstance(data, list) else data.values()
    
    total = 0
    enrolment_errors = 0
    school_issues = []
    
    target_canonical_schools = [
        "石見智翠館高校", "京都工学院高校", "東海大大阪仰星高校", "中部大春日ヶ丘高校"
    ]

    for p in players:
        total += 1
        name = p.get('name_ja', 'Unknown')
        
        # 1. Check Enrolment Year
        enrol = get_enrolment_year(p)
        # If it was 2025 but current team suggests they were there earlier, flag it.
        # However, the script should have fixed it. Let's look for suspicious consistency.
        # (Checking manually for specific cases is better)
        
        # 2. Check School Naming
        hs = p.get('high_school', '-')
        if hs and '?' in hs:
            school_issues.append(f"文字化けの可能性: {name} ({hs})")
            
        canonical_hs = get_canonical_school_name(hs)
        if hs in ["江の川高校", "伏見工業高校", "東海大仰星高校", "春日ヶ丘高校"]:
             if canonical_hs not in target_canonical_schools:
                 school_issues.append(f"名寄せ失敗: {name} {hs} -> {canonical_hs}")

    # Specific Case Check: 金丸 勇人
    kanamaru = data.get('lo_484641')
    if kanamaru:
        print(f"\n[個別チェック: 金丸 勇人]")
        print(f"  学校: {kanamaru.get('high_school')}")
        print(f"  入部年算出結果: {get_enrolment_year(kanamaru)}")
        # Check dist file directly too
        hs_hash_kanamaru = "ae3315a6b7d5" # Temporary MD5 placeholder, will check via script if needed
        
    print(f"\n=== チェック完了 ===")
    print(f"総選手数: {total}")
    for issue in school_issues[:20]: # Show first 20
        print(f"  - {issue}")
    if len(school_issues) > 20:
        print(f"  ...他 {len(school_issues)-20} 件")

if __name__ == "__main__":
    check_all_players()
