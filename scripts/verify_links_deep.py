import os
import glob
import json
import re
import requests

# サーバーURL (npm run dev が起動している前提)
BASE_URL = "http://localhost:4322"

def verify_links():
    # 1. チームデータの読み込み
    teams_json_path = "data/teams.json"
    if not os.path.exists(teams_json_path):
        print(f"❌ Error: {teams_json_path} not found.")
        return

    with open(teams_json_path, "r", encoding="utf-8") as f:
        teams_data = json.load(f)

    # 有効なチームパスのセットを作成
    valid_team_paths = set()
    for t in teams_data:
        path = f"/teams/{t['league']}/{t['slug']}/"
        valid_team_paths.add(path)
        # スラッシュなしも許容する場合
        valid_team_paths.add(f"/teams/{t['league']}/{t['slug']}")

    print(f"Loaded {len(valid_team_paths)//2} valid team paths from {teams_json_path}.")

    # 2. 選手Markdownの検証
    player_files = glob.glob("src/content/players/*.md")
    print(f"Verifying {len(player_files)} player files...")

    errors = []
    slug_to_files = {}

    for pf in player_files:
        slug = os.path.basename(pf).replace(".md", "")
        if slug not in slug_to_files:
            slug_to_files[slug] = []
        slug_to_files[slug].append(pf)
        
        with open(pf, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Frontmatter抽出
            fm_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if fm_match:
                fm_text = fm_match.group(1)
                team_match = re.search(r'team: "(.*?)"', fm_text)
                league_match = re.search(r'league: "(.*?)"', fm_text)
                
                if team_match and league_match:
                    team_name = team_match.group(1)
                    league = league_match.group(1)
                    
                    if league == 'urc':
                        errors.append(f"Exclusion Error: URC player still generated: {slug}")
                    
                    found = False
                    for t in teams_data:
                        if t['team_name'] == team_name and t['league'] == league:
                            found = True
                            break
                    if not found and league != "":
                        errors.append(f"Header Link Error: Team '{team_name}' in league '{league}' not found in teams.json (Player: {slug})")
            
            # Bodyリンク抽出
            links = re.findall(r'\[.*?\]\((/teams/.*?)\)', content)
            for link in links:
                if "/teams/urc/" in link:
                    errors.append(f"Legacy Link Error: URC link found: {link} (Player: {slug})")
                if link not in valid_team_paths:
                    errors.append(f"Invalid Team Link: {link} (Player: {slug})")

    # 重複スラッグのチェック
    for slug, files in slug_to_files.items():
        if len(files) > 1:
            errors.append(f"Duplicate Slug: {slug} is used in {files}")

    print(f"Verified {len(player_files)} players.")

    # 4. HTTP 200 チェック (サンプリング)
    print("Performing HTTP 200 checks on sample pages...")
    # トップ、名鑑、リーグ、チーム
    test_urls = ["/", "/players/", "/leagues/league-one/", "/leagues/super-rugby/", "/leagues/top14/"]
    
    # 各リーグから3チームずつ
    for league in ["league-one", "super-rugby", "top14"]:
        count = 0
        for t in teams_data:
            if t['league'] == league:
                test_urls.append(f"/teams/{league}/{t['slug']}/")
                count += 1
                if count >= 3: break
    
    # 選手ページも数名
    sample_players = list(slug_to_files.keys())[:10]
    for p_slug in sample_players:
        test_urls.append(f"/players/{p_slug}/")

    for url in test_urls:
        full_url = BASE_URL + url
        try:
            resp = requests.get(full_url, timeout=10)
            if resp.status_code != 200:
                # 404の場合、末尾スラッシュの有無を試す
                if resp.status_code == 404 and not url.endswith('/'):
                    resp = requests.get(full_url + '/', timeout=10)
                    if resp.status_code == 200: continue
                errors.append(f"HTTP {resp.status_code} Error: {full_url}")
            else:
                print(f"OK: {full_url}")
        except Exception as e:
            errors.append(f"Connection Error: {full_url} - {e}")

    # 5. サイト全体の「URC」漏れチェック
    print("Checking for any URC leftovers in the final teams list...")
    for t in teams_data:
        if t['league'] == 'urc':
            errors.append(f"Exclusion Error: URC team still in teams.json: {t['team_name']}")
    if not errors:
        print("\n✅ All links verified successfully!")
    else:
        print(f"\n❌ Found {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")

if __name__ == "__main__":
    verify_links()
