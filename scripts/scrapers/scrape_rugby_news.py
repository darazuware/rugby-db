import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

class RugbyNewsScraper:
    """Scrape rugby news from multiple sources"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        self.sources = {
            'domestic': [
                {
                    'name': 'J SPORTS Rugby',
                    'url': 'https://news.jsports.co.jp/rugby/',
                    'selector': 'article'
                },
                {
                    'name': 'Rugby Republic',
                    'url': 'https://rugby-rp.com/',
                    'selector': 'article'
                },
                {
                    'name': 'League One',
                    'url': 'https://league-one.jp/news/',
                    'selector': '.news-item'
                },
                {
                    'name': 'Japan Rugby',
                    'url': 'https://www.rugby-japan.jp/news/',
                    'selector': 'article'
                }
            ],
            'international': [
                {
                    'name': 'World Rugby',
                    'url': 'https://www.world.rugby/news',
                    'selector': 'article'
                },
                {
                    'name': 'RugbyPass',
                    'url': 'https://www.rugbypass.com/news/',
                    'selector': 'article'
                }
            ]
        }
    
    def scrape_source(self, source):
        """Scrape a single news source"""
        try:
            response = requests.get(source['url'], headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = []
            items = soup.select(source['selector'])[:10]  # Top 10 articles
            
            for item in items:
                article = self.extract_article_data(item, source['name'])
                if article:
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            print(f"Error scraping {source['name']}: {e}")
            return []
    
    async def fetch_full_content(self, url):
        """Fetch full content of the article from its URL"""
        if not url: return ""
        if not url.startswith('http'): 
            # Potentially handle relative URLs if needed, but mostly they are absolute
            return ""
            
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Common content areas for rugby news sites
            content_selectors = [
                '.entry-content', '.article-body', '.news-detail__content', 
                'main article', '.post-content', '.article__body'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Clean up unwanted elements
                    for unwanted in content_elem.select('script, style, .ad, .social-share'):
                        unwanted.decompose()
                    return content_elem.get_text('\n').strip()
            
            # Fallback: get all paragraph text from body
            return "\n".join([p.get_text() for p in soup.find_all('p')])
            
        except Exception as e:
            print(f"Error fetching full content for {url}: {e}")
            return ""

    def extract_article_data(self, item, source_name):
        """Extract article data from HTML element"""
        try:
            # Try to find title
            title_elem = item.find(['h1', 'h2', 'h3', 'h4'])
            if not title_elem:
                return None
            
            title = title_elem.get_text().strip()
            
            # Try to find link
            link_elem = item.find('a')
            url = link_elem.get('href', '') if link_elem else ''
            
            # Ensure URL is absolute
            if url and not url.startswith('http'):
                # Handle relative URLs (this is a bit simplistic but works for most)
                if 'rugby-japan.jp' in source_name.lower():
                    url = 'https://www.rugby-japan.jp' + url
                elif 'league-one.jp' in source_name.lower():
                    url = 'https://league-one.jp' + url
            
            # Try to find summary
            summary_elem = item.find('p')
            summary = summary_elem.get_text().strip() if summary_elem else ""
            
            # Extract initial keywords
            keywords = self.extract_keywords(title + ' ' + summary)
            
            # Categorize
            category = self.categorize_article(title, summary)
            
            return {
                'source': source_name,
                'title': title,
                'url': url,
                'summary': summary[:500],
                'keywords': keywords,
                'category': category,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return None
    
    def extract_keywords(self, text):
        """Extract potential player/team names"""
        keywords = []
        
        # Simple keyword extraction (can be improved with NLP)
        # Look for capitalized words (potential names)
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        keywords.extend(words[:10])  # Top 10
        
        # Japanese names (katakana/kanji patterns)
        japanese_names = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]{2,}', text)
        keywords.extend(japanese_names[:10])
        
        return list(set(keywords))
    
    def categorize_article(self, title, summary):
        """Categorize article by content"""
        text = (title + ' ' + summary).lower()
        
        # Priority categories
        if any(word in text for word in ['移籍', 'transfer', '加入', 'signs', 'joins']):
            return 'transfer'
        
        if any(word in text for word in ['招集', 'call-up', '代表', 'squad', 'selection']):
            return 'callup'
        
        if any(word in text for word in ['怪我', 'injury', '負傷', 'injured', '離脱']):
            return 'injury'
        
        if any(word in text for word in ['退団', 'retirement', '引退', 'retires']):
            return 'retirement'
        
        if any(word in text for word in ['試合', 'match', '結果', 'result', 'score']):
            return 'match'
        
        return 'general'
    
    async def scrape_all(self):
        """Scrape all sources and fetch full content for priority categories"""
        all_articles = []
        
        print("=== Scraping Domestic Sources ===")
        for source in self.sources['domestic']:
            print(f"Scraping {source['name']}...")
            articles = self.scrape_source(source)
            all_articles.extend(articles)
            print(f"  ✓ Found {len(articles)} articles")
        
        print("\n=== Scraping International Sources ===")
        for source in self.sources['international']:
            print(f"Scraping {source['name']}...")
            articles = self.scrape_source(source)
            all_articles.extend(articles)
            print(f"  ✓ Found {len(articles)} articles")
        
        # Priority categories for full text fetching
        priority_categories = ['transfer', 'callup', 'injury', 'retirement']
        
        print("\n=== Fetching Full Content for Priority Articles ===")
        for article in all_articles:
            if article['category'] in priority_categories:
                print(f"Fetching full content for: {article['title'][:40]}...")
                full_content = await self.fetch_full_content(article['url'])
                if full_content:
                    article['full_text'] = full_content
                    # Re-extract keywords with more data
                    extra_keywords = self.extract_keywords(full_content)
                    article['keywords'] = list(set(article['keywords'] + extra_keywords))
                    print(f"  ✓ Fetched {len(full_content)} chars and updated keywords")
        
        # Sort by category priority
        priority = {'transfer': 1, 'callup': 2, 'injury': 3, 'retirement': 4, 'match': 5, 'general': 6}
        all_articles.sort(key=lambda x: priority.get(x['category'], 99))
        
        return all_articles

import asyncio

async def main():
    scraper = RugbyNewsScraper()
    articles = await scraper.scrape_all()
    
    # Save to file
    output_file = 'scraped_news.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Scraping Complete ===")
    print(f"Total articles: {len(articles)}")
    print(f"Saved to: {output_file}")
    
    # Show category breakdown
    categories = {}
    for article in articles:
        cat = article['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nCategory breakdown:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")

if __name__ == "__main__":
    asyncio.run(main())
