import json
import os
from datetime import datetime
import re
from google import genai
from google.genai import types

class RugbyArticleGenerator:
    """Generate rugby articles using Gemini API with hallucination prevention"""
    
    def __init__(self, api_key=None):
        # Configure Gemini API
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY environment variable.")
        
        self.client = genai.Client(api_key=api_key)
        
        # Load databases
        self.load_databases()
    
    def load_databases(self):
        """Load player, team, and league databases"""
        try:
            with open('unified_player_database.json', 'r') as f:
                self.players = json.load(f)
            
            with open('data/rugby_teams.json', 'r') as f:
                self.teams = json.load(f)
            
            with open('data/rugby_leagues.json', 'r') as f:
                self.leagues = json.load(f)
            
            print(f"✓ Loaded {len(self.players)} players, {len(self.teams)} teams, {len(self.leagues)} leagues")
        except Exception as e:
            print(f"Warning: Could not load databases: {e}")
            self.players = []
            self.teams = []
            self.leagues = []
    
    def normalize_name(self, name):
        """Normalize name by removing spaces and dots"""
        if not name: return ""
        return re.sub(r'[\s\u30fb\.]', '', str(name).lower())

    def match_entities(self, keywords, news_text=""):
        """Match keywords to database entities with improved accuracy and context awareness"""
        matched = {
            'players': [],
            'teams': [],
            'leagues': []
        }
        
        normalized_keywords = [self.normalize_name(k) for k in keywords]
        news_text_lower = news_text.lower()
        
        # Match players
        found_player_ids = set()
        for kw, orig_kw in zip(normalized_keywords, keywords):
            if len(kw) < 2: continue
            
            for player in self.players:
                p_id = player.get('id')
                if p_id in found_player_ids: continue
                
                name_ja = self.normalize_name(player.get('name_ja', ''))
                name_en = self.normalize_name(player.get('name_en', ''))
                
                # Check for exact or highly similar match
                if kw == name_ja or kw == name_en or (len(kw) > 3 and (kw in name_ja or kw in name_en)):
                    # Context validation: if news contains team names associated with player
                    current_team = str(player.get('team', '')).lower()
                    career = " ".join([str(c) for c in player.get('career_history', [])]).lower()
                    
                    # Score based on context match
                    score = 0
                    if current_team and current_team in news_text_lower: score += 5
                    if career and any(team_name in news_text_lower for team_name in career.split()): score += 2
                    
                    matched['players'].append({'data': player, 'score': score})
                    found_player_ids.add(p_id)

        # Sort by score and take top
        matched['players'] = [p['data'] for p in sorted(matched['players'], key=lambda x: x['score'], reverse=True)]
        
        # Match teams
        found_team_names = set()
        for kw in keywords:
            kw_normalized = kw.lower()
            for team in self.teams:
                team_name = str(team.get('name', '')).lower()
                if kw_normalized in team_name:
                    if team_name not in found_team_names:
                        matched['teams'].append(team)
                        found_team_names.add(team_name)
        
        return matched
    
    def generate_article(self, news_item, matched_entities):
        """Generate article with fact-checking"""
        
        category = news_item['category']
        
        # Build fact-based context
        context = self.build_context(matched_entities)
        
        # Create prompt with strict fact requirements
        prompt = self.create_prompt(news_item, context, category)
        
        # Generate article
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            article_text = response.text
            
            # Add data timestamp
            timestamp = datetime.now().strftime('%Y年%m月%d日')
            article_text += f"\n\n---\n*データ更新日: {timestamp}*"
            
            return article_text
            
        except Exception as e:
            print(f"Error generating article: {e}")
            return None
    
    def build_context(self, matched_entities):
        """Build factual context from database"""
        context = []
        
        for player in matched_entities['players'][:20]:  # Increased for list-based news
            p_id = player.get('id')
            p_name = player.get('name_ja')
            p_url = f"/players/{p_id}.html" if p_id else ""
            
            player_info = {
                'id': p_id,
                'name_ja': p_name,
                'name_en': player.get('name_en'),
                'position': player.get('position'),
                'height': player.get('height'),
                'weight': player.get('weight'),
                'age': player.get('age'),
                'team': player.get('team'),
                'caps': player.get('caps', 0),
                'university': player.get('university', '不明'),
                'high_school': player.get('high_school', '不明'),
                'internal_link': p_url,
                'career': player.get('career_history', [])
            }
            context.append(f"選手データ: {json.dumps(player_info, ensure_ascii=False)}")
        
        for team in matched_entities['teams'][:5]:
            t_name = team.get('name')
            t_url = f"/teams/{t_name}.html"
            
            team_info = {
                'name': t_name,
                'league': team.get('league'),
                'stadium': team.get('stadium'),
                'internal_link': t_url
            }
            context.append(f"チームデータ: {json.dumps(team_info, ensure_ascii=False)}")
        
        return "\n".join(context)
    
    def create_prompt(self, news_item, context, category):
        """Create Gemini prompt with a professional journalist persona and ELIMINATE hallucinations"""
        
        base_prompt = f"""
## システムロール（最優先事項）
Role: "Authoritative, formal, and strictly professional sports journalism"
- 文体は権威ある専門紙のスポーツジャーナリズムに準拠すること
- インターネットスラング・過度な誇張表現・俗語・感嘆符の乱用を厳禁とする
- 「爆速」「最強」「神プレー」等のハイパーボリックな表現は使用不可
- 「〜ですね！」「〜でしょう！」等のカジュアルな語尾も不可
- 事実と分析のみで構成し、読者を煽る演出的表現は一切排除する

あなたはラグビー専門ウェブサイト『RugbyPick.com』の編集長であり、世界中のラグビーに精通したベテランスポーツ記者です。
提供されたニュース（元記事）と信頼できるデータベース情報（知識）のみを元に、プロの分析記事を執筆してください。

### 🚨 【重要】執筆スタイルと構造（フィードバックに基づく最優先事項）
1. **リスト形式ニュースの表文化**: 日本代表候補55名発表などの「多数の選手が紹介されるニュース」の場合、必ず**Markdownの表形式**を用いて情報を整理してください。
   - カラム構成例: | 選手名 | ポジション | 年齢 | 所属 | 出身高校 | 出身大学 | 代表歴 |
2. **内部リンクの積極活用**: データベース（知識）に `internal_link` が提供されている場合、必ずそれを使用してリンクを貼ってください。
   - 例: `[田中 真一](/players/lo_0.html)`、`[九州電力キューデンヴォルテクス](/teams/九州電力キューデンヴォルテクス.html)`
3. **学歴（バイオグラフィー）の必須化**: 選手紹介には**「出身高校」「出身大学」**を必ず含めてください。これがラグビーファンの求める標準的な情報です。
4. **事実の厳守**: 元記事の本文またはデータベースにない事実は1文字たりとも捏造しないでください。特に55名などのリストは本文から正確な名前を読み取ってください。
5. **メタ表現・一般論の禁止**: プロの記者として、専門的で躍動感のある日本語で執筆してください。

### 🗞 元記事情報（本文と全文）
タイトル: {news_item['title']}
本文: {news_item.get('full_text', news_item['summary'])}

### 📚 信頼できるデータベース知識（ここにある internal_link や学歴を優先使用すること）
{context if context else "（個別詳細データはありません。元記事の本文情報を最優先し、構造化してください）"}

### 📝 記事構成案
1. **見出し**: ニュースの核心を突く、プロらしいタイトル。
2. **リード**: ニュースの重要性を鮮烈に切り出す。
3. **詳細リスト/表**: リスト系ニュースの場合はここで表形式で全紹介選手を整理。
4. **記者の視点**: 背景（学歴等）を交えた深い分析。
5. **展望**: 未来へのインパクト。

ラグビー記者の情熱を持って、事実に基づいた躍動感あるプロの記事を執筆してください。
"""
        return base_prompt
    
    def add_affiliate_links(self, article_text, category):
        """Add affiliate links based on category"""
        
        affiliates = []
        
        if category in ['transfer', 'callup']:
            affiliates.append({
                'type': 'streaming',
                'text': '\\n\\n## 試合を観るなら\\n\\n新チームの試合はJ SPORTSオンデマンドで視聴可能です。',
                'link': '[J SPORTS オンデマンド](https://affiliate-link-jsports)'
            })
        
        if category == 'match':
            affiliates.append({
                'type': 'streaming',
                'text': '\\n\\n## 見逃し配信\\n\\nDAZNで試合のハイライトが視聴できます。',
                'link': '[DAZN](https://affiliate-link-dazn)'
            })
        
        # Add affiliates to article
        for aff in affiliates:
            article_text += f"\\n{aff['text']} {aff['link']}"
        
        return article_text

def main():
    # Example usage
    print("=== Rugby Article Generator (Gemini API) ===\\n")
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  GEMINI_API_KEY not set!")
        print("Please set it with: export GEMINI_API_KEY='your-api-key'")
        print("Get your key from: https://makersuite.google.com/app/apikey")
        return
    
    try:
        generator = RugbyArticleGenerator(api_key)
        
        # Load scraped news
        with open('scraped_news.json', 'r') as f:
            news_items = json.load(f)
        
        print(f"Loaded {len(news_items)} news items\\n")
        
        # Generate articles for top 5 priority items
        for i, news_item in enumerate(news_items[:5]):
            print(f"[{i+1}/5] Generating article: {news_item['title'][:50]}...")
            
            # Match entities using title + summary OR full_text if available
            news_content = news_item.get('full_text', news_item['title'] + " " + news_item['summary'])
            matched = generator.match_entities(news_item['keywords'], news_content)
            print(f"  Matched: {len(matched['players'])} players, {len(matched['teams'])} teams")
            
            # Generate article
            article = generator.generate_article(news_item, matched)
            
            if article:
                # Add affiliates
                article = generator.add_affiliate_links(article, news_item['category'])
                
                # Save article
                filename = f"news_article_{i+1}_{news_item['category']}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(article)
                
                print(f"  ✓ Saved to {filename}\\n")
            else:
                print(f"  ✗ Failed to generate\\n")
        
        print("=== Generation Complete ===")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
