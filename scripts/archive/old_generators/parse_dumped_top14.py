import json
from bs4 import BeautifulSoup
import os

def parse_dumped_top14():
    dump_path = "/tmp/top14_classement.html"
    if not os.path.exists(dump_path):
        return []
        
    with open(dump_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    standings = []
    table = soup.select_one('table') or soup.select_one('.stats__table')
    if not table:
        return []
        
    # チーム名日本語化マッピングの読み込み
    json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'team_names_jp.json')
    team_names_jp = {}
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            team_names_jp = json.load(f)

    rows = table.select('tbody tr')
    for row in rows:
        cols = row.select('td')
        if len(cols) < 8: continue
        
        rank_el = row.select_one('.stats__table-rank')
        rank = rank_el.text.strip().replace('=', '').replace('↑', '').replace('↓', '') if rank_el else cols[0].text.strip()
        
        team_link = row.select_one('.base-link--black') or row.select_one('a[href*="/club/"]')
        if not team_link: continue
        
        team_name = team_link.text.strip()
        team_slug = team_link['href'].split('/')[-1]
        
        team_info = team_names_jp.get('top14', {}).get(team_name, {})
        flag = team_info.get('flag', '🇫🇷')
        
        standings.append({
            "rank": rank,
            "team_name": team_name,
            "display_name": team_info.get('jp', team_name),
            "flag": flag,
            "slug": team_slug,
            "played": cols[4].text.strip(),
            "won": cols[5].text.strip(),
            "drawn": cols[6].text.strip(),
            "lost": cols[7].text.strip(),
            "diff": cols[10].text.strip() if len(cols) > 10 else "0",
            "points": row.select_one('.stats__table-points').text.strip() if row.select_one('.stats__table-points') else cols[3].text.strip()
        })
    return standings

if __name__ == "__main__":
    records = parse_dumped_top14()
    print(json.dumps(records, ensure_ascii=False, indent=2))
