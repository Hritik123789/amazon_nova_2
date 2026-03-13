"""
Simple Local News Agent using Ollama directly
Processes Mumbai news articles without CrewAI complexity
"""

import json
import ollama
from typing import List, Dict


class SimpleLocalNewsAgent:
    """Mumbai news analyst using Ollama directly"""
    
    def __init__(self):
        """Initialize"""
        print("🤖 Initializing Simple Local News Agent with Ollama (llama3.1:latest)...\n")
        self.model = "llama3.1:latest"
        print("✓ Agent initialized!\n")
    
    def load_collected_news(self, filename: str = "collected_news.json") -> List[Dict]:
        """Load news from NewsCollector output"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            print(f"📰 Loaded {len(articles)} articles from {filename}\n")
            return articles
        except FileNotFoundError:
            print(f"❌ {filename} not found. Run news_collector.py first!")
            return []
    
    def analyze_article(self, article: Dict, article_num: int) -> Dict:
        """Analyze a single article using Ollama"""
        
        prompt = f"""Analyze this Mumbai news article:

Title: {article['title']}
Summary: {article.get('summary', 'N/A')}

Tasks:
1. Does it mention 'Andheri', 'BMC' (Brihanmumbai Municipal Corporation), or other Mumbai civic bodies? Answer: yes or no
2. List which entities are mentioned (e.g., BMC, Andheri, MHADA, BEST, etc.)
3. If yes, categorize as: Civic, Traffic, or Real Estate
4. Does it mention new buildings, construction, or redevelopment? Answer: yes or no
5. Rate relevance to local Mumbai residents (1-10)

Respond in this exact format:
MENTIONS: yes/no
ENTITIES: comma-separated list (e.g., BMC, Andheri) or "none"
CATEGORY: Civic/Traffic/Real Estate (only if mentions is yes)
PERMIT_CHECK: yes/no
RELEVANCE: number 1-10
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )
            
            result = response['message']['content']
            
            # Parse response
            mentions = 'yes' in result.split('MENTIONS:')[1].split('\n')[0].lower()
            
            if not mentions:
                return None
            
            # Extract entities mentioned
            try:
                entities_line = result.split('ENTITIES:')[1].split('\n')[0].strip()
                if entities_line.lower() != 'none':
                    mentions_list = [e.strip() for e in entities_line.split(',')]
                else:
                    mentions_list = []
            except:
                mentions_list = []
            
            # Extract category
            try:
                category_line = result.split('CATEGORY:')[1].split('\n')[0].strip()
                if 'Civic' in category_line:
                    category = 'Civic'
                elif 'Traffic' in category_line:
                    category = 'Traffic'
                elif 'Real Estate' in category_line:
                    category = 'Real Estate'
                else:
                    category = 'Civic'  # default
            except:
                category = 'Civic'
            
            # Extract permit check
            try:
                permit_check = 'yes' in result.split('PERMIT_CHECK:')[1].split('\n')[0].lower()
            except:
                permit_check = False
            
            # Extract relevance
            try:
                relevance_line = result.split('RELEVANCE:')[1].split('\n')[0].strip()
                relevance = int(''.join(filter(str.isdigit, relevance_line)))
                if relevance < 1 or relevance > 10:
                    relevance = 5
            except:
                relevance = 5
            
            return {
                'article_number': article_num,
                'title': article['title'],
                'category': category,
                'mentions': mentions_list,
                'permit_check_required': permit_check,
                'relevance_score': relevance,
                'url': article.get('url', ''),
                'summary': article.get('summary', '')
            }
            
        except Exception as e:
            print(f"⚠️  Error analyzing article {article_num}: {str(e)}")
            return None
    
    def process_articles(self, articles: List[Dict], limit: int = 50) -> List[Dict]:
        """Process articles using Ollama"""
        
        if not articles:
            print("⚠️  No articles to process")
            return []
        
        print(f"🔍 Analyzing up to {min(len(articles), limit)} articles with Ollama...\n")
        
        analyzed = []
        for i, article in enumerate(articles[:limit], 1):
            print(f"Processing article {i}/{min(len(articles), limit)}: {article['title'][:60]}...")
            
            result = self.analyze_article(article, i)
            if result:
                analyzed.append(result)
                print(f"  ✓ Relevant! Category: {result['category']}, Mentions: {', '.join(result['mentions'])}")
            else:
                print(f"  - Not relevant")
        
        print(f"\n✓ Analysis complete! Found {len(analyzed)} relevant articles\n")
        return analyzed
    
    def save_results(self, analyzed: List[Dict], filename: str = "analyzed_news.json"):
        """Save analyzed articles"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analyzed, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(analyzed)} analyzed articles to {filename}")


def main():
    """Main execution"""
    print("="*80)
    print("Mumbai Local News Agent - Powered by Ollama (Simple Version)")
    print("="*80 + "\n")
    
    # Initialize agent
    agent = SimpleLocalNewsAgent()
    
    # Load collected news
    articles = agent.load_collected_news()
    
    if not articles:
        return
    
    # Process articles
    analyzed = agent.process_articles(articles, limit=50)
    
    # Save results
    if analyzed:
        agent.save_results(analyzed)
        
        # Show summary
        print("\n" + "="*80)
        print("📊 Analysis Summary:")
        print("="*80)
        print(f"Total articles analyzed: {len(analyzed)}")
        
        # Category breakdown
        categories = {}
        permit_required = 0
        for article in analyzed:
            cat = article.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
            if article.get('permit_check_required'):
                permit_required += 1
        
        print(f"\nCategories:")
        for cat, count in categories.items():
            print(f"  {cat}: {count}")
        
        print(f"\nArticles requiring permit check: {permit_required}")
        
        # Show sample
        if analyzed:
            print("\n" + "="*80)
            print("📄 Sample Analyzed Article:")
            print("="*80)
            sample = analyzed[0]
            print(f"Title: {sample['title']}")
            print(f"Category: {sample.get('category', 'N/A')}")
            print(f"Mentions: {', '.join(sample.get('mentions', []))}")
            print(f"Permit Check Required: {sample.get('permit_check_required', False)}")
            print(f"Relevance Score: {sample.get('relevance_score', 'N/A')}/10")
    else:
        print("\n⚠️  No articles matched the criteria")


if __name__ == "__main__":
    main()
