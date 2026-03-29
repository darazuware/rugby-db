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
        数値型で .0 で終わる場合は整数として扱う。
        """
        # アトリビュート名の名寄せマッピング
        mapping = {
            'Full_Name': ['name_ja', 'Full_Name', '選手名_カタカナ'],
            'Player_Name': ['name_en', 'Player_Name'],
            'Height': ['height', 'Height'],
            'Weight': ['weight', 'Weight'],
            'Position': ['position', 'Position'],
            'Birth_Date': ['birth_date', 'Birth_Date'],
            'Nationality': ['country', 'Nationality'],
            'Current_Team': ['team', 'Current_Team'],
            'Scraped_Url': ['scraped_url', 'Scraped_Url'],
            'High_School': ['high_school', 'High_School'],
            'University': ['university', 'University'],
            'Junior_High_School': ['junior_high_school', 'Junior_High_School'],
            'Rugby_School': ['rugby_school', 'Rugby_School'],
            'Representative_Caps': ['caps', 'Representative_Caps'],
            'League_One_Caps': ['league_one_caps', 'League_One_Caps'],
        }

        # マッピングから候補を取得
        candidates = mapping.get(attr_name, [attr_name])
        
        val = None
        for cand in candidates:
            if cand in row:
                val = row.get(cand)
                import pandas as pd
                if not (pd.isna(val) or str(val).lower() == 'nan' or val is None):
                    break
                else:
                    val = None
        
        if val is None:
            return default
            
        try:
            # 数値型または数値文字列の末尾 .0 を削除
            val_str = str(val).strip()
            if val_str.endswith('.0'):
                return val_str[:-2]
            return val_str
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
            # "Team Name (Start - End)" または "Team Name (Year - )" または "Team Name (Year)" を抽出
            # ハイフンがあるかないかで現在進行形かどうかを判断するため、ハイフン部分をキャプチャ対象に含める検討も。
            # 現状は match.group(3) が None か "" かで判断。
            match = re.match(r'(.*?)\s*\(\s*(\d{4})\s*(?:-\s*(\d{4}|))?\s*\)', item)
            if match:
                team = match.group(1).strip()
                start = int(match.group(2))
                end_match = match.group(3)
                
                # 全体の文字列にハイフンが含まれているか確認 (正規表現の不完全さを補完)
                # match.group(0) は item 全体 (括弧部分含む)
                has_hyphen = '-' in match.group(0)
                
                if end_match:
                    try:
                        end = int(end_match)
                    except ValueError:
                        end = 9999
                elif has_hyphen:
                    # ハイフンがあるが end_match が空（またはパース不可）なら現在進行
                    end = 9999
                else:
                    # ハイフンがない場合は単発年
                    end = start
                
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
        
        # 開始年順にソート (開始年が同じ場合は、終了年が新しい方を後、または 9999 を優先)
        merged_career.sort(key=lambda x: (x['start'], x['end']))
        
        # 文字列に変換
        result_items = []
        for d in merged_career:
            team_name = d['team']
            
            # 現在進行形の表示 (9999 or 最新の所属)
            # 基準日(2026年)以降、または 9999 の場合を「現在進行」とする
            if d['end'] >= 2026 or d['end'] == 9999: 
                year_str = f"{d['start']} - "
            elif d['start'] == d['end']:
                year_str = f"{d['start']}"
            else:
                year_str = f"{d['start']} - {d['end']}"
            
            result_items.append(f"{team_name} ({year_str})")
        
        # もし最後のアイテムが現在所属チーム(Astro frontmatterのteam)と一致し、
        # まだハイフンが付いていない場合は、整合性を保つためにハイフンを付与する検討が必要。
        # ただし、この関数は抽象的な整形のみを行うため、基本は end=9999 に依存する。
        
        return " -> ".join(result_items)

    @staticmethod
    def get_yearly_career(career_str, player_country=""):
        """
        キャリア遍歴の文字列を解析し、年ごとの所属チームリストを生成する。
        代表チーム（国名が入っているもの）は除外する。
        """
        if not career_str or str(career_str).lower() == 'nan':
            return []
        
        # 代表チームとみなすキーワード。player_country も動的に追加
        representative_keywords = {"Japan", "New Zealand", "South Africa", "Australia", "France", "England", "Wales", "Scotland", "Ireland", "Italy", "Fiji", "Samoa", "Tonga", "Argentina", "Georgia", "Uruguay", "USA", "Canada", "Namibia", "Chile", "Portugal", "Romania", "Namibia", "representative", "national", "代表", "XV", "All Blacks", "Springboks", "Wallabies", "Pumas", "Flying Fijians", "Manu Samoa", "Ikale Tahi"}
        if player_country:
            representative_keywords.add(player_country)

        # アイテムに分割
        items = re.split(r'\s*(?:->|,)\s*', career_str)
        career_data = []
        
        for item in items:
            # チーム名 (開始年 - 終了年) または (開始年 - ) または (開始年)
            # より寛容な正規表現に変更
            match = re.search(r'([^(]+)\s*\(\s*(\d{4})\s*(?:[-\s]*(\d{4}|))?\s*\)', item)
            if match:
                team = match.group(1).strip()
                
                # 代表チームかどうかの判定 (単語境界を考慮)
                is_rep = False
                team_lower = team.lower()
                for kw in representative_keywords:
                    kw_lower = kw.lower()
                    # 国名などの短いキーワードは単語として存在するか確認
                    pattern = r'\b' + re.escape(kw_lower) + r'\b'
                    if re.search(pattern, team_lower):
                        is_rep = True
                        break
                if is_rep: continue

                start = int(match.group(2))
                end_match = match.group(3)
                
                has_hyphen = '-' in match.group(0)
                
                if end_match:
                    try:
                        end = int(end_match)
                    except ValueError:
                        end = 2026 # 現在進行を 2026 とする
                elif has_hyphen:
                    end = 2026
                else:
                    end = start
                
                career_data.append({"team": team, "start": start, "end": end})

        if not career_data:
            return []
        
        # 年ごとのマップを作成 {year: set([team1, team2])}
        yearly_map = {}
        min_year = 9999
        max_year = 0
        
        for d in career_data:
            for y in range(d['start'], d['end'] + 1):
                if y > 2026: continue # 未来は除外
                if y not in yearly_map:
                    yearly_map[y] = set()
                yearly_map[y].add(d['team'])
                min_year = min(min_year, y)
                max_year = max(max_year, y)
        
        if not yearly_map: return []

        # 最小年から最大年（または現在）までのリストを作成
        result = []
        for y in range(min_year, max_year + 1):
            teams = sorted(list(yearly_map.get(y, [])))
            result.append({"year": y, "teams": teams})
            
        return result

    @staticmethod
    def format_career_item(year, team):
        """キャリア遍歴の整形ルール (GEMINI.md 参照)"""
        # ルール: 低い順から新しい順、同一チームは統合など
        # ここでは単一アイテムの整形を提供
        return f"{year}: {team}"
