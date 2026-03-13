"""
Simple News Summarization (No heavy dependencies)
Uses extractive summarization - picks the most important sentences
"""

import json
import re
from typing import List, Dict
from collections import Counter


class SimpleNewsSummarizer:
    """Simple extractive summarizer - no AI model needed"""
    
    def __init__(self):
        print("📝 Simple summarizer ready (no model download needed)\n")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def sentence_score(self, sentence: str, word_freq: Dict[str, int]) -> float:
        """Score a sentence based on word frequency"""
        words = re.findall(r'\w+', sentence.lower())
        if not words:
            return 0
        
        score = sum(word_freq.get(word, 0) for word in words)
        return score / len(words)  # Normalize by sentence length
    
    def extractive_summary(self, text: str, num_sentences: int = 2) -> str:
        """Extract the most important sentences"""
        if not text or len(text) < 50:
            return text
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if len(sentences) <= num_sentences:
            return text
        
        # Calculate word frequency
        words = re.findall(r'\w+', text.lower())
        word_freq = Counter(words)
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        for word in stop_words:
            word_freq.pop(word, None)
        
        # Score sentences
        sentence_scores = [(sent, self.sentence_score(sent, word_freq)) for sent in sentences]
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top sentences
        top_sentences = sentence_scores[:num_sentences]
        
        # Return in original order
        summary_sentences = []
        for sent in sentences:
            if any(sent == top[0] for top in top_sentences):
                summary_sentences.append(sent)
        
        return '. '.join(summary_sentences) + '.'
    
    def summarize_article(self, article: Dict) -> Dict:
        """Summarize a single article"""
        try:
            # Get the content to summarize
            content = article.get('summary', '') or article.get('description', '')
            
            if not content or len(content) < 50:
                article['ai_summary'] = content
                article['summarized'] = False
                return article
            
            # Create summary
            summary = self.extractive_summary(content, num_sentences=2)
            
            article['ai_summary'] = summary
            article['summarized'] = True
            article['original_summary'] = content
            
            return article
            
        except Exception as e:
            print(f"⚠️  Error summarizing article: {str(e)}")
            article['ai_summary'] = article.get('summary', '')
            article['summarized'] = False
            return article
    
    def summarize_batch(self, articles: List[Dict], max_articles: int = None) -> List[Dict]:
        """Summarize multiple articles"""
        if max_articles is None:
            max_articles = len(articles)
        
        print(f"📝 Summarizing {min(len(articles), max_articles)} articles...\n")
        
        summarized = []
        for i, article in enumerate(articles[:max_articles]):
            print(f"   [{i+1}/{min(len(articles), max_articles)}] {article['title'][:60]}...")
            summarized_article = self.summarize_article(article)
            summarized.append(summarized_article)
        
        print(f"\n✓ Summarized {len(summarized)} articles\n")
        return summarized
    
    def save_to_file(self, articles: List[Dict], filename: str = "summarized_news.json"):
        """Save summarized articles to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(articles)} summarized articles to {filename}")


def main():
    """Test the summarizer"""
    # Load collected news
    print("📰 Loading collected news...\n")
    try:
        with open('collected_news.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("❌ collected_news.json not found. Run news_collector.py first!")
        return
    
    print(f"Found {len(articles)} articles\n")
    
    # Initialize summarizer
    summarizer = SimpleNewsSummarizer()
    
    # Summarize all articles
    summarized = summarizer.summarize_batch(articles)
    
    # Save results
    summarizer.save_to_file(summarized)
    
    # Show example
    if summarized:
        print("\n" + "="*80)
        print("📄 Example Summary:")
        print("="*80)
        article = summarized[0]
        print(f"\nTitle: {article['title']}")
        print(f"Source: {article['source']}")
        if article.get('original_summary'):
            print(f"\nOriginal ({len(article['original_summary'])} chars):")
            print(f"{article['original_summary'][:300]}...")
        print(f"\nAI Summary ({len(article['ai_summary'])} chars):")
        print(f"{article['ai_summary']}")
        print("\n" + "="*80)


if __name__ == "__main__":
    main()
