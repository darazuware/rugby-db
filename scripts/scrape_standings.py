import requests
from bs4 import BeautifulSoup
import json
import os
import unicodedata
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

from team_utils import get_team_info as get_canonical_info

def get_team_info(league, name):
    info = get_canonical_info(name)
    default_flag = '🇯🇵' if league == 'league-one' else '🇫🇷'
    
    if info:
        return info['jp'], info['flag'], info['slug']
    
    # フォールバック
    slug = str(name).lower()
    slug = unicodedata.normalize('NFD', slug).encode('ascii', 'ignore').decode('utf-8')
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    return name, default_flag, slug

import subprocess

def scrape_top14_standings():
    url = "https://top14.lnr.fr/classement"
    print(f"Scraping Top 14 standings from {url} (using curl for robustness)...")
    
    # SSR版を確実に取得するため Google Bot UA を使用
    ua = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    
    try:
        # requests だと文字コードや動的コンテンツの扱いでデータが空になるケースがあるため、curlを使用
        cmd = ['curl', '-s', '-L', '-A', ua, url]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        if result.returncode != 0:
            print(f"Curl error: {result.stderr}")
            return []
            
        content = result.stdout
        soup = BeautifulSoup(content, 'html.parser')
        
        standings = []
        # 固定ブロック（順位・ロゴ）とスクロールブロック（統計）を取得
        fixed_rows = soup.select('.ranking__fixed-block .table-line--ranking-fixed')
        scroll_rows = soup.select('.ranking__scrollable-cells .table-line--ranking-scrollable')
        
        if not fixed_rows:
            # フォールバック
            fixed_rows = soup.find_all('div', class_=re.compile(r'table-line--ranking-fixed'))
            scroll_rows = soup.find_all('div', class_=re.compile(r'table-line--ranking-scrollable'))

        print(f"Found {len(fixed_rows)} fixed rows and {len(scroll_rows)} scroll rows.")

        for i in range(min(len(fixed_rows), len(scroll_rows))):
            fixed_row = fixed_rows[i]
            scroll_row = scroll_rows[i]

            # 順位: 数字のみを抽出
            rank_el = fixed_row.find(class_=re.compile(r'rank'))
            if rank_el:
                # 非常に頑健な方法でテキストを抽出（タグを除去して空白を詰める）
                rank_text = re.sub(r'<[^>]+>', '', str(rank_el))
                rank = re.sub(r'\D', '', rank_text)
            else:
                rank = str(i+1)
            if not rank: rank = str(i+1)

            # チーム名: 画像の alt 属性を最優先（最も正確）
            img_el = fixed_row.find('img', alt=True)
            raw_name = img_el['alt'].strip() if img_el else ""
            
            if not raw_name:
                name_link = scroll_row.find('a', class_=re.compile(r'base-link'))
                if name_link:
                    name_text = re.sub(r'<[^>]+>', '', str(name_link))
                    raw_name = name_text.strip()
            
            if not raw_name:
                raw_name = f"Team {rank}"

            # 統計データ: 数値のみを抽出
            stat_wrappers = scroll_row.find_all('div', class_=re.compile(r'table-line__cell-wrapper--small'))
            
            if len(stat_wrappers) >= 9:
                stats = []
                for sw in stat_wrappers:
                    # タグを除去して空白を詰める（TemplateString対策）
                    clean_val = re.sub(r'<[^>]+>', '', str(sw))
                    val = re.sub(r'\s+', '', clean_val).strip()
                    stats.append(val)
                
                # インデックス: 0: Pts, 1: J, 2: V, 3: N, 4: D, 8: Diff
                points = stats[0]
                played = stats[1]
                won = stats[2]
                drawn = stats[3]
                lost = stats[4]
                diff = stats[8]
            else:
                points = played = won = drawn = lost = diff = ""

            jp_name, flag, slug = get_team_info('top14', raw_name)
            
            standings.append({
                "rank": rank, "team_name": raw_name, "display_name": jp_name, "flag": flag, "slug": slug,
                "played": played, "won": won, "drawn": drawn, "lost": lost, "diff": diff, "points": points
            })
            
        print(f"Scraped {len(standings)} Top 14 teams.")
        if standings:
            s = standings[0]
            print(f"Top 14 Sample: Rank {s['rank']} {s['team_name']} ({s['points']} pts, Diff:{s['diff']})")
        
        return standings
    except Exception as e:
        print(f"Error scraping Top 14: {e}")
        import traceback
        traceback.print_exc()
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
                    h_jp, h_f, h_s = get_team_info('top14', h); a_jp, a_f, a_s = get_team_info('top14', a)
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
            jp, f, slug = get_team_info('urc', raw)
            rank = str(item.get('position', i + 1))
            standings.append({ "rank": rank, "team_name": raw, "display_name": jp, "flag": f, "slug": slug, "played": str(stats.get('played', '0')), "won": str(stats.get('won', '0')), "drawn": str(stats.get('drawn', '0')), "lost": str(stats.get('lost', '0')), "diff": str(stats.get('pointsDiff', '0')), "points": str(stats.get('points', '0')) })
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
            jp, f, slug = get_team_info('super-rugby', raw)
            
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
                "slug": slug,
                "played": p,
                "won": w,
                "drawn": d,
                "lost": l,
                "diff": diff,
                "points": pts
            })
        return standings
    except: return []

def scrape_premiership_standings():
    url = "https://www.premiershiprugby.com/competitions/gallagher-prem/standings"
    print(f"Scraping Premiership standings from {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        standings = []
        # Official site table rows are within a tbody
        rows = soup.select('tbody tr')
        for i, row in enumerate(rows):
            cells = row.select('td')
            if len(cells) < 7: continue
            
            rank = cells[0].get_text(strip=True)
            team_cell = cells[1]
            name_el = team_cell.select_one('span.font-condensed')
            raw_name = name_el.get_text(strip=True) if name_el else team_cell.get_text(strip=True)
            
            played = cells[2].get_text(strip=True)
            won = cells[3].get_text(strip=True)
            drawn = cells[4].get_text(strip=True)
            lost = cells[5].get_text(strip=True)
            diff = cells[6].get_text(strip=True)
            points = cells[11].get_text(strip=True)
            
            jp_name, flag, slug = get_team_info('premiership', raw_name)
            
            standings.append({
                "rank": rank, "team_name": raw_name, "display_name": jp_name, "flag": flag, "slug": slug,
                "played": played, "won": won, "drawn": drawn, "lost": lost, "diff": diff, "points": points
            })
            
        print(f"Scraped {len(standings)} Premiership teams.")
        return standings
    except Exception as e:
        print(f"Error scraping Premiership: {e}")
        return []

def scrape_leagueone_standings():
    url = "https://league-one.jp/standings/"
    try:
        response = requests.get(url, headers=HEADERS); soup = BeautifulSoup(response.text, 'html.parser'); tables = soup.select('table.standings-table'); standings = []
        for i, table in enumerate(tables):
            rows = table.select('tbody tr')
            for row in rows:
                cols = row.select('td, th'); link = cols[2].select_one('a')
                if link:
                    name = link.text.strip(); jp, f, slug = get_team_info('league-one', name)
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
    prem_s = scrape_premiership_standings()
    
    # 既存データのバックアップ (不完全な場合のフォールバック)
    def get_old(league, key):
        old = cur.get(league, {})
        # TOP 14 の JS レンダリング問題への暫定対応
        if league == "top14" and key == "standings" and (not t14_s or t14_s[0].get('rank') == ''):
             return old.get(key, [])
        if isinstance(old, list): return old if key == "standings" else []
        return old.get(key, [])

    if len(lo_s) < 12: lo_s = get_old("league-one", "standings")
    if len(t14_s) < 14:
        print(f"Warning: Top 14 incomplete ({len(t14_s)}). Keeping old.")
        t14_s = get_old("top14", "standings")
        t14_r = get_old("top14", "results")
    if len(urc_s) < 16: urc_s = get_old("urc", "standings")
    if len(sr_s) < 11: sr_s = get_old("super-rugby", "standings")
    if len(prem_s) < 10: prem_s = get_old("premiership", "standings")
    
    # 全てのリーグの構造を統一 {"standings": [], "results": []}
    all_data = {
        "league-one": { "standings": lo_s, "results": get_old("league-one", "results") },
        "top14": { "standings": t14_s, "results": t14_r },
        "urc": { "standings": urc_s, "results": get_old("urc", "results") },
        "super-rugby": { "standings": sr_s, "results": get_old("super-rugby", "results") },
        "premiership": { "standings": prem_s, "results": get_old("premiership", "results") }
    }
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Standings saved to {path}")

if __name__ == "__main__": main()
