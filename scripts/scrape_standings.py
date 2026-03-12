import requests
from bs4 import BeautifulSoup
import json
import os
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# チーム名日本語化マッピングの読み込み
TEAM_NAMES_JP = {}
json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'team_names_jp.json')
if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        TEAM_NAMES_JP = json.load(f)

def get_team_info(league, name):
    name = str(name).strip()
    league_data = TEAM_NAMES_JP.get(league, {})
    
    # Specify default flag by league
    default_flag = '🇯🇵' if league == 'league-one' else '🇫🇷'
    
    if name in league_data:
        info = league_data[name]
        return info.get('jp', name), info.get('flag', default_flag)
    for main_name, data in league_data.items():
        if name == main_name or name in data.get('aliases', []) or data.get('jp') == name:
            return data.get('jp', main_name), data.get('flag', default_flag)
    return name, default_flag

def scrape_top14_standings():
    url = "https://top14.lnr.fr/classement"
    print(f"Scraping Top 14 standings from {url}...")
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        standings = []
        # 新しいサイト構造に合わせたセレクター
        table_lines = soup.select('.table-line')
        for line in table_lines:
            # 順位
            rank_el = line.select_one('.table-line__rank')
            if not rank_el: continue
            rank = re.sub(r'\D', '', "".join(rank_el.stripped_strings))
            
            # チーム名とリンク
            link = line.select_one('.table-line__cell-wrapper--club-name a')
            if not link: continue
            raw_name = "".join(link.stripped_strings)
            team_slug = link['href'].split('/')[-1]
            
            # 各種スタッツ (Played, Won, Drawn, Lost, Bonus, PtsM, PtsE, Diff, Pts)
            # 統計セルを取得
            stats_cells = line.select('.table-line__cell-wrapper--small')
            if len(stats_cells) < 8: continue
            
            # 構造: P, W, D, L, B, PM, PE, Diff, Pts (Ptsは別クラス)
            played = "".join(stats_cells[0].stripped_strings)
            won = "".join(stats_cells[1].stripped_strings)
            drawn = "".join(stats_cells[2].stripped_strings)
            lost = "".join(stats_cells[3].stripped_strings)
            diff = "".join(stats_cells[7].stripped_strings)
            
            # Pts は専用のラッパーがある場合が多い
            pts_el = line.select_one('.table-line__cell-wrapper--pts')
            points = "".join(pts_el.stripped_strings) if pts_el else "0"

            jp_name, flag = get_team_info('top14', raw_name)
            
            standings.append({
                "rank": rank, "team_name": raw_name, "display_name": jp_name, "flag": flag, "slug": team_slug,
                "played": played, "won": won, "drawn": drawn, "lost": lost, "diff": diff, "points": points
            })
            
        print(f"Scraped {len(standings)} Top 14 teams.")
        return standings
    except Exception as e:
        print(f"Error scraping Top 14: {e}")
        return []

def scrape_top14_results():
    url = "https://top14.lnr.fr/calendrier-et-resultats"
    results = []
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        match_rows = soup.select('.match-line')
        for row in match_rows:
            home_el = row.select_one('.match-line__club--home .club-line__name')
            away_el = row.select_one('.match-line__club--away .club-line__name')
            score_el = row.select_one('.match-line__score')
            if home_el and away_el and score_el:
                h = "".join(home_el.stripped_strings); a = "".join(away_el.stripped_strings)
                s = "".join(score_el.stripped_strings)
                if s and s != "VS":
                    h_jp, h_f = get_team_info('top14', h); a_jp, a_f = get_team_info('top14', a)
                    results.append({ "home": h_jp, "home_flag": h_f, "away": a_jp, "away_flag": a_f, "score": s, "date": "" })
        return results[:10]
    except: return []

def scrape_urc_standings():
    url = "https://www.unitedrugby.com/graphql"
    # seasonId 202501 (2025/26 season)
    params = { "operationName": "GetStandingData", "variables": json.dumps({"seasonId": 202501}), "extensions": json.dumps({ "persistedQuery": { "version": 1, "sha256Hash": "702a2903fbc5f7e05fb7004f6979f6c0e3a747ad1e62f8e0c0008beca15f34f3" } }) }
    headers = HEADERS.copy(); headers["Referer"] = "https://www.unitedrugby.com/"
    try:
        response = requests.get(url, params=params, headers=headers); data = response.json()
        items = data.get('data', {}).get('standings', [])
        standings = []
        for i, item in enumerate(items):
            stats = item.get('performance_stats', {}); raw = item.get('team_name', '')
            jp, f = get_team_info('urc', raw)
            rank = str(item.get('position', i + 1))
            standings.append({ "rank": rank, "team_name": raw, "display_name": jp, "flag": f, "slug": item.get('team_short_name', '').lower(), "played": str(stats.get('played', '0')), "won": str(stats.get('won', '0')), "drawn": str(stats.get('drawn', '0')), "lost": str(stats.get('lost', '0')), "diff": str(stats.get('pointsDiff', '0')), "points": str(stats.get('points', '0')) })
        return standings
    except: return []

def scrape_super_rugby_standings():
    url = "https://omo.akamai.opta.net/auth/competition.php"
    # season_id: 2026
    params = { "feed_type": "ru2", "competition": "205", "season_id": "2026", "user": "OW2017", "psw": "dXWg5gVZ", "jsoncallback": "callback" }
    headers = HEADERS.copy(); headers.update({ "Referer": "https://super.rugby/", "Origin": "https://super.rugby/" })
    try:
        response = requests.get(url, params=params, headers=headers); text = response.text
        j = json.loads(text[text.index('(')+1 : text.rindex(')')]); 
        
        # 階層構造に応じて取得
        table_data = j.get('table', {})
        comp_data = table_data.get('comp', {})
        group_data = comp_data.get('group', {})
        teams = group_data.get('team', [])
        
        if not isinstance(teams, list):
            teams = [teams] if teams else []

        standings = []
        for t in teams:
            a = t.get('@attributes', {})
            
            raw = a.get('name', '')
            jp, f = get_team_info('super-rugby', raw)
            
            # API構造：属性直下にデータがある
            p = a.get('played', '0')
            w = a.get('won', '0')
            d = a.get('drawn', '0')
            l = a.get('lost', '0')
            diff = a.get('pointsdiff', '0')
            pts = a.get('points', '0')
            rk = a.get('rank', '0')

            standings.append({
                "rank": rk,
                "team_name": raw,
                "display_name": jp,
                "flag": f,
                "slug": a.get('short_name', rk).lower().replace(' ', '-'),
                "played": p,
                "won": w,
                "drawn": d,
                "lost": l,
                "diff": diff,
                "points": pts
            })
        return standings
    except: return []

def scrape_leagueone_standings():
    url = "https://league-one.jp/standings/"
    try:
        response = requests.get(url, headers=HEADERS); soup = BeautifulSoup(response.text, 'html.parser'); tables = soup.select('table.standings-table'); standings = []
        for i, table in enumerate(tables):
            rows = table.select('tbody tr')
            for row in rows:
                cols = row.select('td, th'); link = cols[2].select_one('a')
                if link:
                    name = link.text.strip(); slug = link['href'].split('/')[-1]; jp, f = get_team_info('league-one', name)
                    standings.append({ "rank": cols[0].text.strip(), "team_name": name, "display_name": jp, "flag": f, "slug": slug, "played": cols[3].text.strip(), "points": cols[4].text.strip(), "won": cols[5].text.strip(), "drawn": cols[6].text.strip(), "lost": cols[7].text.strip(), "diff": cols[10].text.strip() if len(cols) > 10 else "0", "division": f"D{i+1}" })
        return standings
    except: return []

def main():
    path = "data/standings.json"; cur = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: cur = json.load(f)
    
    lo_s = scrape_leagueone_standings()
    t14_s = scrape_top14_standings(); t14_r = scrape_top14_results()
    urc_s = scrape_urc_standings()
    sr_s = scrape_super_rugby_standings()
    
    # 既存データのバックアップ (不完全な場合のフォールバック)
    def get_old(league, key):
        old = cur.get(league, {})
        if isinstance(old, list): return old if key == "standings" else []
        return old.get(key, [])

    if len(lo_s) < 12: lo_s = get_old("league-one", "standings")
    if len(t14_s) < 14:
        print(f"Warning: Top 14 incomplete ({len(t14_s)}). Keeping old.")
        t14_s = get_old("top14", "standings")
        t14_r = get_old("top14", "results")
    if len(urc_s) < 16: urc_s = get_old("urc", "standings")
    if len(sr_s) < 11: sr_s = get_old("super-rugby", "standings")
    
    # 全てのリーグの構造を統一 {"standings": [], "results": []}
    # resultsData (results_2026.json) もあるが、StandingsTable の Props 互換性のためにこちらにも入れる
    # URC / SR の最近の試合結果は results_2026.json から取得されるが、構造だけ定義しておく
    all_data = {
        "league-one": { "standings": lo_s, "results": get_old("league-one", "results") },
        "top14": { "standings": t14_s, "results": t14_r },
        "urc": { "standings": urc_s, "results": get_old("urc", "results") },
        "super-rugby": { "standings": sr_s, "results": get_old("super-rugby", "results") }
    }
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Standings saved to {path}")

if __name__ == "__main__": main()
