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
            for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%Y年%m月%d日"):
                try:
                    birth_date = datetime.strptime(birth_date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
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
    def format_career_item(year, team):
        """キャリア遍歴の整形ルール (GEMINI.md 参照)"""
        # ルール: 低い順から新しい順、同一チームは統合など
        # ここでは単一アイテムの整形を提供
        return f"{year}: {team}"
