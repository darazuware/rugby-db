import requests
import json
import os
import time
from player_utils import PlayerDataProcessor

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.unitedrugby.com/"
}

def scrape_urc_players_graphql(club_slug):
    """URC GraphQL を用いてクラブの選手データを一括取得"""
    url = "https://www.unitedrugby.com/graphql"
    print(f"Fetching URC players for {club_slug} via GraphQL...")
    
    # 以前の調査で見つけた GetStandingData と同様に、
    # 選手リスト用の persistedQuery を特定する必要があるが、
    # ここでは一般的な Squad クエリを試行（または汎用的な検索）
    # URCのサイトでは stats.unitedrugby.com が実体。
    
    # フォールバックとして stats.unitedrugby.com/clubs/{slug}/players を解析
    stats_url = f"https://stats.unitedrugby.com/clubs/{club_slug}/players"
    try:
        res = requests.get(stats_url, headers=HEADERS)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 選手カードの抽出
        player_data = []
        # stats サイトの構造に合わせた抽出
        # ... logic ...
        # 現時点では器だけ作成
        return []
    except Exception as e:
        print(f"Error for {club_slug}: {e}")
        return []

from bs4 import BeautifulSoup

def main():
    with open("data/urc_teams_deep.json", "r") as f:
        teams = json.load(f)
        
    all_players = {}
    for slug, info in list(teams.items())[:3]: # テスト
        players = scrape_urc_players_graphql(slug)
        all_players[slug] = players
        time.sleep(1)
        
    output_path = "data/urc_players_detailed.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_players, f, ensure_ascii=False, indent=2)
    print(f"URC player data saved to {output_path}")

if __name__ == "__main__":
    main()
