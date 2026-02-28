import json
import re

DB_PATH = 'data/unified_player_database_final.json'

def is_suspicious_name(name_ja, name_en):
    if not name_ja: return True, "Missing JA Name"
    
    # 1. Length Check (Too short)
    if len(name_ja) <= 1:
        return True, f"Too Short: {name_ja}"
    
    # 2. Kanji + Katakana Mixed (often OCR error or bad scrape like "野ザキ")
    # But exclude valid foreign names with dots e.g. "ジョーンズ・..."
    # And valid mixed names? Usually names are all Kanji or all Katakana (for foreign).
    # "野ザキ" is Kanji + Katakana.
    has_kanji = bool(re.search(r'[\u4e00-\u9faf]', name_ja))
    has_katakana = bool(re.search(r'[\u30a0-\u30ff]', name_ja))
    has_hiragana = bool(re.search(r'[\u3040-\u309f]', name_ja))
    
    if has_kanji and has_katakana:
         return True, f"Mixed Script (Kanji+Kata): {name_ja}"
         
    # 3. Check against EN name
    # e.g. if JA is "青柳" but EN is "Ryunosuke Aoyagi" -> JA is missing first name
    if name_en:
        parts_en = name_en.split()
        if len(parts_en) >= 2:
            # If JA name has no space and is short (2-3 chars), it MIGHT be just family name
            # But "高田" (2 chars) is family name. "高田賢臣" (4 chars).
            # Hard to automate perfectly, but let's flag short names < 4 chars if EN has 2 parts?
            # actually many short full names exists "Li Qi" etc.
            # But "青柳" (2 chars) vs "Ryunosuke Aoyagi" (long).
            pass

    return False, ""

def main():
    print("--- Starting Data Diagnosis ---")
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("DB not found.")
        return

    print("\n[Suspicious Entries]")
    if isinstance(data, dict):
        players = data.values()
    elif isinstance(data, list):
        players = data
    else:
        players = []

    print("\n[Yakult Levins Check]")
    yakult_list = []
    suspicious_others = []
    
    for p in players:
        pid = p.get('id')
        name_ja = p.get('name_ja') or ""
        name_en = p.get('name_en') or ""
        team = p.get('team', '') or ""
        
        # 1. Yakult Check
        if 'ヤクルト' in team or 'Yakult' in team or 'Levins' in team:
            yakult_list.append(f"ID:{pid} | JA:{name_ja} | EN:{name_en}")

        # 2. Length Check
        # Length 1 is definitely bad (unless "Li"?) but usually bad.
        if len(name_ja) == 1:
            suspicious_others.append(f"[Len 1] ID:{pid} | JA:{name_ja} | EN:{name_en} | Team:{team}")
        
        # Length 2 but EN has > 1 part (e.g. "青柳" vs "Ryunosuke Aoyagi")
        # Exclude known 2-char full names? Hard. But manual review is feasible if list is small.
        elif len(name_ja) == 2 and len(name_en.split()) > 1:
             suspicious_others.append(f"[Len 2 vs EN] ID:{pid} | JA:{name_ja} | EN:{name_en} | Team:{team}")

        # 3. Mixed Script (Kanji + Katakana)
        # Exclude valid ones with "・"
        # "野ザキ" matched.
        has_kanji = bool(re.search(r'[\u4e00-\u9faf]', name_ja))
        has_katakana = bool(re.search(r'[\u30a0-\u30ff]', name_ja))
        if has_kanji and has_katakana and '・' not in name_ja and ' ' not in name_ja:
             suspicious_others.append(f"[Mixed] ID:{pid} | JA:{name_ja} | EN:{name_en} | Team:{team}")

    print(f"--- Yakult Levins Players ({len(yakult_list)}) ---")
    for row in yakult_list:
        print(row)
        
    print(f"\n--- Other Suspicious Candidates ({len(suspicious_others)}) ---")
    # Limit output to avoid scroll buffer issues if too many
    count = 0
    for row in suspicious_others:
        print(row)
        count += 1
        if count > 200:
            print("... (truncated)")
            break

if __name__ == "__main__":
    main()
