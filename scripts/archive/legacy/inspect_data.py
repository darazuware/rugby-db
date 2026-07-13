import json

def inspect():
    try:
        with open('data/unified_player_database_final.json', 'r', encoding='utf-8') as f:
            players = json.load(f)
    except FileNotFoundError:
        print("Final DB not found, trying full...")
        with open('unified_player_database_full.json', 'r', encoding='utf-8') as f:
            players = json.load(f)

    targets = [
        "Atsuro Nakamura", "atsuro_nakamura",
        "Taro Uesugi", "taro_uesugi",
        "Soki Watanabe", "soki_watanabe",
        "Iori Nozaki", "iori_nozaki"
    ]

    found_count = 0
    for p in players.values():
        name_en = p.get('name_en', '')
        name_ja = p.get('name_ja', '')
        
        # Check against targets
        is_target = False
        for t in targets:
            if t.lower() in name_en.lower() or t in name_ja:
                is_target = True
                break
        
        if is_target:
            print(f"\n--- Found: {name_en} ({name_ja}) ---")
            print(f"ID: {p.get('id')}")
            print(f"Team: {p.get('team')}")
            print(f"Career: {p.get('career_history')}")
            print(f"Name JA Raw: {p.get('name_ja')}")
            found_count += 1

    print(f"\nTotal fouund: {found_count}")
    if found_count == 0:
        print("No targets found. Sample names from DB:")
        for i, p in enumerate(players):
            if i < 10: print(f"- {p.get('name_en')} | {p.get('name_ja')}")

if __name__ == "__main__":
    inspect()
