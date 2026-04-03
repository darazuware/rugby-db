#!/usr/bin/env python3
"""
JRFUの試合メンバー表から選手の身長・体重・ポジションを取得する。

rugby-japan.jp の試合印刷ページ (/match/{id}/print/) には
メンバー表（番号・ポジション・氏名・身長・体重・年齢）が含まれている。

使い方:
  pip install requests beautifulsoup4

  # Top West A のリーグページからマッチIDを自動取得して全選手を抽出
  python3 scripts/scrape_jrfu_matches.py --league top-west-a

  # Top West B/C
  python3 scripts/scrape_jrfu_matches.py --league top-west-b
  python3 scripts/scrape_jrfu_matches.py --league top-west-c

  # Top East
  python3 scripts/scrape_jrfu_matches.py --league top-east-a

  # 結果をCSVに保存（デフォルト: data_sources/jrfu_{league}.csv）
  python3 scripts/scrape_jrfu_matches.py --league top-west-a --out data_sources/top_west_jrfu.csv

  # CSVを保存後、mdファイルに反映するには apply_csv_to_md.py を使う:
  python3 scripts/apply_csv_to_md.py --csv data_sources/jrfu_top-west-a.csv --div top-west-a

注意:
  - 試合結果ページのIDは毎シーズン変わる場合がある
  - リーグURLが変わった場合は LEAGUE_URLS を更新してください
"""

import argparse
import csv
import os
import re
import time

import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; rugby-db-scraper/1.0)'}
DELAY = 0.5  # seconds between requests

# JRFUシニアリーグの結果ページURL（シーズンごとに番号が変わる）
# https://www.rugby.or.jp/senior/result/{ID}/ の形式
LEAGUE_URLS = {
    'top-west-a':  'https://www.rugby.or.jp/senior/result/2812/',
    'top-west-b':  'https://www.rugby.or.jp/senior/result/2813/',
    'top-west-c':  'https://www.rugby.or.jp/senior/result/2814/',
    'top-east-a':  'https://www.rugby.or.jp/senior/result/2800/',
    'top-east-b':  'https://www.rugby.or.jp/senior/result/2801/',
    'top-east-c':  'https://www.rugby.or.jp/senior/result/2802/',
    'top-kyushu':  'https://www.rugby.or.jp/senior/result/2820/',
}

# ポジション正規化
POSITION_NORM = {
    'No.8': 'No8', 'NO8': 'No8', 'no8': 'No8',
    'PR': 'PR', 'HO': 'HO', 'LO': 'LO', 'FL': 'FL',
    'SH': 'SH', 'SO': 'SO', 'CTB': 'CTB', 'WTB': 'WTB', 'FB': 'FB',
}


def fetch(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return BeautifulSoup(resp.text, 'html.parser')
    except requests.RequestException as e:
        print(f'  FETCH ERROR {url}: {e}')
        return None


def get_match_ids(league_url: str) -> list[str]:
    """リーグ結果ページからmatch IDのリストを取得"""
    print(f'Fetching match IDs from {league_url} ...')
    soup = fetch(league_url)
    if not soup:
        return []
    ids = re.findall(r'/match/(\d+)/', soup.decode() if hasattr(soup, 'decode') else str(soup))
    unique_ids = list(dict.fromkeys(ids))  # 順序を保持して重複除去
    print(f'  Found {len(unique_ids)} match IDs')
    return unique_ids


def parse_match_page(match_id: str) -> list[dict]:
    """試合印刷ページを解析して選手リストを返す"""
    url = f'https://www.rugby-japan.jp/match/{match_id}/print/'
    soup = fetch(url)
    if not soup:
        return []

    players = []
    current_team = ''

    # チーム名の取得（テーブルの直前のテキストや見出しから）
    for element in soup.find_all(['h2', 'h3', 'h4', 'p', 'table']):
        if element.name == 'table':
            rows = element.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4:
                    continue
                text_cols = [c.get_text(strip=True) for c in cols]

                # ヘッダ行をスキップ
                if text_cols[0] in ('番号', 'No', '#', ''):
                    continue

                # 列構造の推測: 番号,ポジション,氏名,身長,体重,年齢 or 氏名,ポジション,身長,体重
                name, pos, height, weight = '', '', '', ''

                # パターン1: [番号, ポジション, 氏名, 身長, 体重, ...]
                if len(cols) >= 5 and re.match(r'^\d+$', text_cols[0]):
                    pos = text_cols[1]
                    name = text_cols[2]
                    height_raw = text_cols[3]
                    weight_raw = text_cols[4] if len(cols) > 4 else ''
                    height = re.sub(r'[^\d]', '', height_raw)
                    weight = re.sub(r'[^\d]', '', weight_raw)

                # パターン2: [氏名, ポジション, 身長cm, 体重kg]
                elif len(cols) >= 3 and not re.match(r'^\d+$', text_cols[0]):
                    name = text_cols[0]
                    if len(cols) >= 4:
                        # 身長・体重は数字のみ
                        for col_text in text_cols[1:]:
                            if re.match(r'^1[5-9]\d$', col_text) or re.match(r'^2[0-1]\d$', col_text):
                                height = col_text
                            elif re.match(r'^\d{2,3}$', col_text) and not height:
                                pass  # skip small numbers
                            elif re.match(r'^\d{2,3}$', col_text) and height and not weight:
                                weight = col_text
                        pos_candidates = [t for t in text_cols[1:] if t in POSITION_NORM or t in ('PR','HO','LO','FL','SH','SO','CTB','WTB','FB','No.8','No8')]
                        if pos_candidates:
                            pos = pos_candidates[0]

                # 名前の簡易バリデーション
                name = name.replace(' ', '').replace('　', '').strip()
                if not name or len(name) < 2 or re.match(r'^\d+$', name):
                    continue
                # スタッフ・ヘッダ除外
                skip_words = ['監督', 'コーチ', 'スタッフ', '主務', '氏名', '選手名', 'マネージャー']
                if any(w in name for w in skip_words):
                    continue

                pos = POSITION_NORM.get(pos, pos)

                player = {
                    'name_ja': name,
                    'position': pos,
                    'height': height if height and len(height) == 3 else '',
                    'weight': weight if weight and 50 <= int(weight or 0) <= 200 else '',
                    'team': current_team,
                    'match_id': match_id,
                }
                players.append(player)
        else:
            # テーブル外のテキストからチーム名を推測
            text = element.get_text(strip=True)
            if 'チーム' in text or len(text) < 30:
                if any(c in text for c in ['大学', '電力', '製鉄', '銀行', '自動車', 'Japan', 'FC', 'RC']):
                    current_team = text.split('（')[0].split('(')[0].strip()

    return players


def merge_players(all_records: list[dict]) -> list[dict]:
    """同一選手の複数試合データをマージ（最初に見つかった値を優先）"""
    merged: dict[str, dict] = {}
    for p in all_records:
        key = p['name_ja']
        if key not in merged:
            merged[key] = {k: v for k, v in p.items() if k != 'match_id'}
        else:
            # 空フィールドを補完
            for field in ('position', 'height', 'weight', 'team'):
                if not merged[key].get(field) and p.get(field):
                    merged[key][field] = p[field]
    return list(merged.values())


def save_csv(players: list[dict], out_path: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fieldnames = ['name_ja', 'position', 'height', 'weight', 'team']
    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(players)
    print(f'Saved {len(players)} players to {out_path}')


def main():
    parser = argparse.ArgumentParser(description='Scrape JRFU match pages for player data')
    parser.add_argument('--league', required=True,
                        choices=list(LEAGUE_URLS.keys()),
                        help='League to scrape')
    parser.add_argument('--out', default='',
                        help='Output CSV path (default: data_sources/jrfu_{league}.csv)')
    parser.add_argument('--limit', type=int, default=0,
                        help='Limit number of matches (0=all, useful for testing)')
    args = parser.parse_args()

    league_url = LEAGUE_URLS[args.league]
    match_ids = get_match_ids(league_url)

    if args.limit:
        match_ids = match_ids[:args.limit]
        print(f'Limiting to {args.limit} matches')

    if not match_ids:
        print('No match IDs found. Check LEAGUE_URLS in the script.')
        return

    all_records = []
    for i, mid in enumerate(match_ids):
        print(f'[{i+1}/{len(match_ids)}] Match {mid}')
        records = parse_match_page(mid)
        all_records.extend(records)
        print(f'  → {len(records)} players found')
        time.sleep(DELAY)

    merged = merge_players(all_records)
    print(f'\nTotal unique players: {len(merged)}')

    out_path = args.out or os.path.join(BASE_DIR, f'data_sources/jrfu_{args.league}.csv')
    save_csv(merged, out_path)

    print(f"""
次のステップ:
  python3 scripts/apply_csv_to_md.py --csv {out_path} --div {args.league.replace('-a','').replace('-b','').replace('-c','')} --dry-run
  python3 scripts/apply_csv_to_md.py --csv {out_path} --div {args.league.replace('-a','').replace('-b','').replace('-c','')}
""")


if __name__ == '__main__':
    main()
