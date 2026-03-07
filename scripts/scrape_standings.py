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
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        standings = []
        # 固定部分 (順位のみ)
        rank_els = soup.select('.ranking-item__rank')
        ranks = [re.sub(r'\D', '', "".join(el.stripped_strings)) for el in rank_els]
        
        # スクロール部分 (チーム名とデータ)
        data_rows = soup.select('.table-line--ranking-scrollable')
        
        for i, row in enumerate(data_rows):
            # チーム名とスタラグの抽出
            link = row.select_one('a[href*="/club/"]')
            raw_name = ""
            team_slug = ""
            if link:
                raw_name = "".join(link.stripped_strings)
                team_slug = link['href'].split('/')[-1]
            
            if not raw_name: continue

            # ランク
            rank = ranks[i] if i < len(ranks) else str(i+1)
            
            # 数値データの直接抽出 (正規表現で HTML 内のタグ周辺を狙う)
            vals = row.select('.table-line__cell-wrapper--small')
            stats = []
            for val in vals:
                txt = "".join(val.stripped_strings)
                if not txt:
                    # BeautifulSoup で見えない場合、生 HTML からこの div の中身を強引に抜く
                    res = re.search(r'>\s*(-?\d+)\s*<', str(val))
                    txt = res.group(1) if res else "0"
                stats.append(txt)

            if len(stats) < 9: continue
            
            # 公式順序: Pts, M, G, N, P, Bonus, PtsM, PtsE, Diff
            points = stats[0]
            played = stats[1]
            won = stats[2]
            drawn = stats[3]
            lost = stats[4]
            diff = stats[8]

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
    params = { "feed_type": "ru2", "competition": "205", "season_id": "2025", "user": "OW2017", "psw": "dXWg5gVZ", "jsoncallback": "callback" }
    headers = HEADERS.copy(); headers.update({ "Referer": "https://super.rugby/", "Origin": "https://super.rugby/" })
    try:
        response = requests.get(url, params=params, headers=headers); text = response.text
        j = json.loads(text[text.index('(')+1 : text.rindex(')')]); teams = j.get('table', {}).get('comp', {}).get('group', {}).get('team', [])
        standings = []
        for t in teams:
            a = t.get('@attributes', {}); s = { x.get('@attributes', {}).get('type'): x.get('#text') for x in t.get('stat', []) }
            raw = a.get('name', ''); jp, f = get_team_info('super-rugby', raw)
            standings.append({ "rank": s.get('rank', '0'), "team_name": raw, "display_name": jp, "flag": f, "slug": a.get('short_name', '').lower().replace(' ', '-'), "played": s.get('played', '0'), "won": s.get('won', '0'), "drawn": s.get('drawn', '0'), "lost": s.get('lost', '0'), "diff": s.get('points_diff', '0'), "points": s.get('points', '0') })
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
    t14_s = scrape_top14_standings(); t14_r = scrape_top14_results(); lo_s = scrape_leagueone_standings(); urc_s = scrape_urc_standings(); sr_s = scrape_super_rugby_standings()
    if len(lo_s) < 12: lo_s = cur.get("league-one", cur.get("leagueone", lo_s))
    if len(t14_s) < 14:
        print(f"Warning: Top 14 incomplete ({len(t14_s)}). Keeping old."); old = cur.get("top14", {"standings": [], "results": []}); t14_s = old["standings"]; t14_r = old["results"]
    if len(urc_s) < 16: urc_s = cur.get("urc", urc_s)
    if len(sr_s) < 11: sr_s = cur.get("super-rugby", sr_s)
    all_data = { "league-one": lo_s, "top14": { "standings": t14_s, "results": t14_r }, "urc": urc_s, "super-rugby": sr_s }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Standings saved to {path}")

if __name__ == "__main__": main()
