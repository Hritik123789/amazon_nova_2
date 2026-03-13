"""
Local News Agent using CrewAI and Ollama
Processes Mumbai news articles with free local LLM
"""

import json
import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama
from typing import List, Dict

# Set environment to use Ollama
os.environ["OPENAI_API_KEY"] = "NA"  # Dummy value to bypass OpenAI check


class LocalNewsAgent:
    """Mumbai news analyst using local LLM"""
    
    def __init__(self):
        """Initialize with Ollama LLM"""
        print("🤖 Initializing Local News Agent with Ollama (llama3.1:latest)...\n")
        
        # Configure Ollama with llama3.1
        self.llm = ChatOllama(
            model="llama3.1:latest",
            base_url="http://localhost:11434",
            temperature=0.7
        )
        
        # Create Mumbai Local Expert Agent
        self.news_analyst = Agent(
            role='Mumbai Local Expert',
            goal='Analyze Mumbai news articles and categorize them by relevance and type',
            backstory="""You are an expert on Mumbai local affairs with deep knowledge of 
            neighborhoods like Andheri, civic issues handled by BMC (Brihanmumbai Municipal Corporation),
            traffic patterns, and real estate developments. You can quickly identify news that matters
            to local residents and categorize it appropriately.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
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
    
    def create_analysis_task(self, articles: List[Dict]) -> Task:
        """Create task for analyzing news articles"""
        
        # Prepare article summaries for the agent
        articles_text = "\n\n".join([
            f"Article {i+1}:\nTitle: {article['title']}\nSummary: {article.get('summary', 'N/A')}\nSource: {article['source']}"
            for i, article in enumerate(articles[:50])  # Limit to 50 for performance
        ])
        
        task = Task(
            description=f"""Analyze these Mumbai news articles and:
            
1. Filter for articles specifically mentioning 'Andheri' or 'BMC' (Brihanmumbai Municipal Corporation)
2. For each relevant article, categorize it as one of: [Civic, Traffic, Real Estate]
3. If the article mentions new buildings, construction, or redevelopment, add a 'permit_check_required' flag
4. Return a structured JSON list with this format:
   {{
     "article_number": <number>,
     "title": "<title>",
     "category": "<Civic|Traffic|Real Estate>",
     "mentions": ["Andheri" or "BMC"],
     "permit_check_required": <true|false>,
     "relevance_score": <1-10>
   }}

Articles to analyze:
{articles_text}

Return ONLY valid JSON array, no other text.""",
            agent=self.news_analyst,
            expected_output="A JSON array of analyzed articles with categories and flags"
        )
        
        return task
    
    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process articles using CrewAI"""
        
        if not articles:
            print("⚠️  No articles to process")
            return []
        
        print(f"🔍 Analyzing {min(len(articles), 50)} articles with local LLM...\n")
        
        # Create task
        analysis_task = self.create_analysis_task(articles)
        
        # Create crew
        crew = Crew(
            agents=[self.news_analyst],
            tasks=[analysis_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute
        try:
            result = crew.kickoff()
            print("\n✓ Analysis complete!\n")
            
            # Parse result
            analyzed = self.parse_result(result, articles)
            return analyzed
            
        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            return []
    
    def parse_result(self, result, original_articles: List[Dict]) -> List[Dict]:
        """Parse CrewAI result and merge with original articles"""
        try:
            # Try to extract JSON from result
            result_str = str(result)
            
            # Find JSON array in result
            start = result_str.find('[')
            end = result_str.rfind(']') + 1
            
            if start != -1 and end > start:
                json_str = result_str[start:end]
                analyzed = json.loads(json_str)
                
                # Merge with original articles
                for item in analyzed:
                    article_num = item.get('article_number', 0) - 1
                    if 0 <= article_num < len(original_articles):
                        original_articles[article_num].update({
                            'category': item.get('category'),
                            'mentions': item.get('mentions', []),
                            'permit_check_required': item.get('permit_check_required', False),
                            'relevance_score': item.get('relevance_score', 0),
                            'analyzed': True
                        })
                
                # Filter only analyzed articles
                return [a for a in original_articles if a.get('analyzed')]
            else:
                print("⚠️  Could not parse JSON from result")
                return []
                
        except Exception as e:
            print(f"⚠️  Error parsing result: {str(e)}")
            return []
    
    def save_results(self, analyzed: List[Dict], filename: str = "analyzed_news.json"):
        """Save analyzed articles"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analyzed, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(analyzed)} analyzed articles to {filename}")


def main():
    """Main execution"""
    print("="*80)
    print("Mumbai Local News Agent - Powered by CrewAI + Ollama")
    print("="*80 + "\n")
    
    # Initialize agent
    agent = LocalNewsAgent()
    
    # Load collected news
    articles = agent.load_collected_news()
    
    if not articles:
        return
    
    # Process articles
    analyzed = agent.process_articles(articles)
    
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
