import re
from datetime import datetime

class PlayerDataProcessor:
    @staticmethod
    def calculate_age(birth_date_str):
        """生年月日(YYYY-MM-DD or YYYY/MM/DD)から現在の年齢を算出"""
        if not birth_date_str or birth_date_str == "None":
            return None
        try:
            # 様々な形式に対応
            birth_date = None
            for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%d/%m/%Y", "%Y年%m月%d日"):
                try:
                    birth_date = datetime.strptime(birth_date_str, fmt)
                    break
                except ValueError:
                    continue
            
            if not birth_date:
                # 年のみの抽出を試みる (例: //2005, 2005..)
                year_match = re.search(r'(\d{4})', birth_date_str)
                if year_match:
                    year = int(year_match.group(1))
                    today = datetime.today()
                    return today.year - year
                return None
                
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        except Exception:
            return None

    @staticmethod
    def extract_caps(text):
        """テキストから代表キャップ数を抽出 (例: '82 caps', 'Caps: 15')"""
        if not text: return None
        match = re.search(r'(\d+)\s*(?:caps|test|キャップ)', text, re.I)
        if match:
            return int(match.group(1))
        # 単純な数値のみの場合（文脈が必要な場合が多いが）
        match = re.search(r'(?:caps|test|表示|代表)[:：]\s*(\d+)', text, re.I)
        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def check_data_deficiencies(player_data):
        """データ不備（キャップ・遍歴欠落）を検知し、品質レポート用の情報を返す"""
        deficiencies = []
        name = player_data.get("name", "Unknown")
        
        # 代表キャップの欠落チェック
        if player_data.get("caps") is None:
            deficiencies.append("代表キャップ数が不明または記載なし")
            
        # キャリア遍歴の欠落チェック
        career = player_data.get("career", [])
        if not career:
            deficiencies.append("キャリア遍歴（チーム遍歴）の記載なし")
            
        return {
            "name": name,
            "status": "不備あり" if deficiencies else "正常",
            "details": deficiencies
        }

    @staticmethod
    def generate_quality_report(all_players_results, output_path="data/quality_report.txt"):
        """品質レポートを出力 (GEMINI.md 第2項)"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=== 選手データ品質レポート ===\n\n")
            for player in all_players_results:
                report = PlayerDataProcessor.check_data_deficiencies(player)
                if report["details"]:
                    f.write(f"【{report['name']}】\n")
                    for d in report["details"]:
                        f.write(f"  - {d}\n")
                    f.write("\n")
        print(f"Quality report generated at {output_path}")

    @staticmethod
    def generate_player_slug(name_en, player_id, scraped_url=""):
        """
        選手のスラッグ（URLの一部）を生成する。
        1. scraped_url (all.rugby) があればその末尾を使用
        2. 英語名があれば正規化して使用
        3. いずれもなければ player_id を使用
        """
        if scraped_url and 'all.rugby/player/' in str(scraped_url):
            url_id = str(scraped_url).rstrip('/').split('/')[-1]
            if url_id: return url_id
        
        if not name_en or str(name_en).lower() == 'nan':
            return f"player-{player_id}"
            
        # 記号を除去し、スペースをハイフンに変換
        slug = re.sub(r'[^a-z0-9]+', '-', str(name_en).lower()).strip('-')
        # 重複回避のために ID を付与 (※all.rugby ID がない場合)
        return f"{slug}-{player_id}"

    @staticmethod
    def get_safe_attr(row, attr_name, default=''):
        """
        Pandas の行（Series または辞書）から値を安全に取得する。
        NaN や 'nan' などの文字列漏れを防ぐ。
        """
        try:
            val = row.get(attr_name)
            import pandas as pd
            if pd.isna(val) or str(val).lower() == 'nan' or val is None:
                return default
            return str(val).strip()
        except Exception:
            return default

    @staticmethod
    def consolidate_career_history(career_str):
        """
        キャリア遍歴の文字列を解析し、同じチームの期間が連続・重複している場合は統合する。
        例: WP (2020-2021) -> Stormers (2021-2021) -> WP (2021-2021)
        => WP (2020-2021), Stormers (2021-2021)
        """
        if not career_str or str(career_str).lower() == 'nan':
            return ""
        
        # アイテムに分割 (-> または , で区切られていると想定)
        items = re.split(r'\s*(?:->|,)\s*', career_str)
        career_data = []
        
        for item in items:
            # "Team Name (Start - End)" または "Team Name (Year)" を抽出
            match = re.match(r'(.*?)\s*\(\s*(\d{4})\s*(?:-\s*(\d{4}|))?\s*\)', item)
            if match:
                team = match.group(1).strip()
                start = int(match.group(2))
                end = match.group(3)
                if not end:
                    end = start
                else:
                    try:
                        end = int(end)
                    except ValueError:
                        end = 9999 # 現在進行形など
                
                career_data.append({"team": team, "start": start, "end": end})
            else:
                # 形式が合わない場合はそのまま保持を試みるが、パースできないものは無視するか検討
                pass

        if not career_data:
            return career_str # パース失敗時は元の文字列を返す
        
        # チームごとにグループ化
        from collections import defaultdict
        team_ranges = defaultdict(list)
        for d in career_data:
            team_ranges[d['team']].append([d['start'], d['end']])
        
        merged_career = []
        for team, ranges in team_ranges.items():
            # 範囲をマージ
            ranges.sort()
            merged = []
            if not ranges: continue
            
            curr_start, curr_end = ranges[0]
            for next_start, next_end in ranges[1:]:
                # 連続または重複している場合 (翌年までを連続とみなすか？ GEMINI.md は「連続または重複」)
                # ラグビーのシーズン性を考慮し、1年以内の空きは連続とみなすロジックもありだが、
                # まずは重複・隣接のみ。
                if next_start <= curr_end + 1:
                    curr_end = max(curr_end, next_end)
                else:
                    merged.append((curr_start, curr_end))
                    curr_start, curr_end = next_start, next_end
            merged.append((curr_start, curr_end))
            
            for m_start, m_end in merged:
                merged_career.append({"team": team, "start": m_start, "end": m_end})
        
        # 開始年順にソート
        merged_career.sort(key=lambda x: x['start'])
        
        # 文字列に変換
        result_items = []
        for d in merged_career:
            team_name = d['team']
            # capitalize if it's not and requested in general? 
            # (GEMINI.md says just use team name, but usually title case is better)
            
            # 現在進行形の表示 (9999 or 最新の所属)
            if d['end'] >= 2025: # 2025年以降なら現在進行形として扱う (物理基準日参照)
                year_str = f"{d['start']} - "
            elif d['start'] == d['end']:
                year_str = f"{d['start']}"
            else:
                year_str = f"{d['start']} - {d['end']}"
            
            result_items.append(f"{team_name} ({year_str})")
        
        return " -> ".join(result_items)

    @staticmethod
    def format_career_item(year, team):
        """キャリア遍歴の整形ルール (GEMINI.md 参照)"""
        # ルール: 低い順から新しい順、同一チームは統合など
        # ここでは単一アイテムの整形を提供
        return f"{year}: {team}"
