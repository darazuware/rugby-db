import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def main():
    url = "https://www.majorleague.rugby/standings/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 順位表データの抽出 (MLR 公式サイトの構造に合わせる)
        # 通常、table 要素内にデータがある
        standings = []
        
        # 2024年シーズンのデータを探す (構造は動的に変わる可能性があるため柔軟に)
        tables = soup.find_all("table")
        if not tables:
            print("No tables found on the standings page.")
            return

        # MLR は Eastern / Western Conference に分かれている場合が多い
        for table in tables:
            rows = table.find_all("tr")[1:] # ヘッダーを飛ばす
            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 10: continue
                
                team_name = cols[1].get_text(separator=" ", strip=True)
                # "Houston SaberCats Houston SaberCats" のような重複を排除
                parts = team_name.split()
                if len(parts) >= 2 and len(parts) % 2 == 0:
                    mid = len(parts) // 2
                    if parts[:mid] == parts[mid:]:
                        team_name = " ".join(parts[:mid])
                
                team_name = team_name.replace("*", "").strip()
                
                # 日本語名とフラグを取得（既存のロジックがあれば利用、なければフォールバック）
                # 今回はスクリプト単体で完結させるため、簡易的なマッピングを利用
                
                data = {
                    "rank": cols[0].get_text(strip=True),
                    "team": team_name,
                    "played": cols[2].get_text(strip=True),
                    "won": cols[3].get_text(strip=True),
                    "lost": cols[4].get_text(strip=True),
                    "drawn": cols[5].get_text(strip=True),
                    "pts_for": cols[6].get_text(strip=True),
                    "pts_against": cols[7].get_text(strip=True),
                    "diff": cols[8].get_text(strip=True),
                    "points": cols[11].get_text(strip=True) if len(cols) > 11 else "0"
                }
                standings.append(data)
        
        # マッピングデータの読み込み
        with open("data/team_names_jp.json", "r", encoding="utf-8") as f:
            team_names_jp = json.load(f).get("mlr", {})
        with open("data/teams.json", "r", encoding="utf-8") as f:
            teams_meta = [t for t in json.load(f) if t.get("league") == "mlr"]

        resolved_standings = []
        # スクリーピングで得られたチームを処理
        scraped_teams = {s["team"]: s for s in standings}
        
        # teams.json の全チームをベースに作成
        for t_meta in teams_meta:
            orig_name = t_meta["team_name"]
            # 日本語名とフラグを検索
            jp_data = team_names_jp.get(orig_name, {})
            # スクレイピング結果から数値データを取得（なければ 0）
            stats = scraped_teams.get(orig_name, {
                "rank": "-", "played": "0", "won": "0", "lost": "0", 
                "drawn": "0", "pts_for": "0", "pts_against": "0", 
                "diff": "0", "points": "0"
            })
            
            resolved_standings.append({
                "rank": stats["rank"],
                "team_name": orig_name,
                "display_name": jp_data.get("jp", orig_name),
                "flag": jp_data.get("flag", "🇺🇸"),
                "slug": t_meta.get("slug", ""),
                "played": stats["played"],
                "won": stats["won"],
                "drawn": stats["drawn"],
                "lost": stats["lost"],
                "diff": stats["diff"],
                "points": stats["points"]
            })

        # 既存の standings.json を読み込んで MLR セクションを更新
        json_path = "data/standings.json"
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                all_standings = json.load(f)
        else:
            all_standings = {}
            
        all_standings["mlr"] = {
            "standings": sorted(resolved_standings, key=lambda x: (x["points"], x["diff"]), reverse=True),
            "results": []
        }
        all_standings["last_updated"] = datetime.now().isoformat()
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_standings, f, ensure_ascii=False, indent=4)
            
        print(f"Successfully integrated {len(resolved_standings)} teams for MLR and updated {json_path}")
        
    except Exception as e:
        print(f"Error scraping MLR standings: {e}")

if __name__ == "__main__":
    main()
