# -*- coding: utf-8 -*-
"""
Real Social Listening Agent
Monitors Mumbai social media for community intelligence:
1. Reddit r/mumbai - General discussions (JSON API)
2. Reddit r/india - Mumbai-filtered discussions (JSON API)
3. Sentiment analysis with Nova 2 Lite

Uses Reddit JSON API + Nova 2 Lite for intelligent sentiment analysis
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
import time

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import boto3


class SocialListener:
    """Monitor real Mumbai social media discussions"""
    
    def __init__(self, max_posts_per_source: int = 10, demo_mode: bool = True):
        """
        Initialize Social Listener
        
        Args:
            max_posts_per_source: Max posts to collect per source (cost control)
            demo_mode: Enable cost tracking
        """
        print("👂 Initializing Real Social Listener...\n")
        
        self.max_posts = max_posts_per_source
        self.demo_mode = demo_mode
        self.tokens_used = 0
        self.estimated_cost = 0.0
        
        # Safety limits to prevent infinite loops
        self.max_retries = 2  # Max retry attempts per source
        self.request_timeout = 15  # Max seconds per HTTP request
        self.max_sentiment_analysis = 10  # Max posts to analyze with Nova (cost control)
        
        # Initialize Bedrock for sentiment analysis
        try:
            self.bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            print("✓ Connected to Amazon Bedrock\n")
        except Exception as e:
            print(f"❌ Bedrock connection failed: {e}")
            self.bedrock = None
        
        # Request headers to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"🔒 Safety limits enabled:")
        print(f"   • Max posts per source: {self.max_posts}")
        print(f"   • Request timeout: {self.request_timeout}s")
        print(f"   • Max retries: {self.max_retries}")
        print(f"   • Max AI sentiment analysis: {self.max_sentiment_analysis} posts\n")
    
    def scrape_reddit_mumbai(self, query: str = "", sort: str = "new", limit: int = 25) -> List[Dict]:
        """
        Scrape Reddit r/mumbai using JSON API
        
        Args:
            query: Search query (empty for all posts)
            sort: Sort order (new, hot, top)
            limit: Max posts to fetch
        
        Returns:
            List of post dictionaries
        """
        print(f"📱 Scraping Reddit r/mumbai (query: '{query or 'all posts'}')...")
        
        posts = []
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                # Build URL
                if query:
                    url = f"https://www.reddit.com/r/mumbai/search.json?q={query}&restrict_sr=on&sort={sort}&limit={limit}"
                else:
                    url = f"https://www.reddit.com/r/mumbai/{sort}.json?limit={limit}"
                
                response = requests.get(url, headers=self.headers, timeout=self.request_timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract posts from JSON
                    post_list = data.get('data', {}).get('children', [])
                    
                    if post_list:
                        print(f"   ✓ Found {len(post_list)} posts")
                        
                        # Process posts with iteration limit
                        for idx, post_data in enumerate(post_list):
                            if idx >= self.max_posts:  # Extra safety check
                                break
                            
                            try:
                                post = post_data.get('data', {})
                                
                                # Extract post details
                                post_dict = {
                                    "id": post.get('id', ''),
                                    "source": "reddit_r/mumbai",
                                    "author": post.get('author', 'unknown'),
                                    "title": post.get('title', ''),
                                    "content": post.get('selftext', ''),
                                    "url": f"https://reddit.com{post.get('permalink', '')}",
                                    "created_utc": post.get('created_utc', 0),
                                    "timestamp": datetime.fromtimestamp(post.get('created_utc', 0)).isoformat(),
                                    "engagement": {
                                        "upvotes": post.get('ups', 0),
                                        "downvotes": post.get('downs', 0),
                                        "comments": post.get('num_comments', 0),
                                        "score": post.get('score', 0)
                                    },
                                    "subreddit": post.get('subreddit', 'mumbai'),
                                    "flair": post.get('link_flair_text', None)
                                }
                                posts.append(post_dict)
                                
                            except Exception as e:
                                continue
                        
                        print(f"   ✓ Extracted {len(posts)} posts\n")
                        break  # Success, exit retry loop
                    else:
                        print("   ⚠️  No posts found\n")
                        break
                else:
                    print(f"   ⚠️  HTTP {response.status_code}, retrying... ({retry_count + 1}/{self.max_retries})")
                    retry_count += 1
                    time.sleep(2)
                    
            except requests.Timeout:
                print(f"   ⚠️  Request timeout, retrying... ({retry_count + 1}/{self.max_retries})")
                retry_count += 1
                time.sleep(2)
            except Exception as e:
                print(f"   ⚠️  Scraping failed: {e}, retrying... ({retry_count + 1}/{self.max_retries})")
                retry_count += 1
                time.sleep(2)
        
        return posts[:self.max_posts]  # Final safety cap
    
    def scrape_reddit_india_mumbai(self) -> List[Dict]:
        """
        Scrape Reddit r/india filtered for Mumbai discussions
        """
        print("📱 Scraping Reddit r/india (Mumbai filter)...")
        
        posts = []
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                # Search r/india for Mumbai-related posts
                url = f"https://www.reddit.com/r/india/search.json?q=mumbai&restrict_sr=on&sort=new&limit=25"
                
                response = requests.get(url, headers=self.headers, timeout=self.request_timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract posts from JSON
                    post_list = data.get('data', {}).get('children', [])
                    
                    if post_list:
                        print(f"   ✓ Found {len(post_list)} Mumbai-related posts")
                        
                        # Process posts with iteration limit
                        for idx, post_data in enumerate(post_list):
                            if idx >= self.max_posts:  # Extra safety check
                                break
                            
                            try:
                                post = post_data.get('data', {})
                                
                                # Extract post details
                                post_dict = {
                                    "id": post.get('id', ''),
                                    "source": "reddit_r/india",
                                    "author": post.get('author', 'unknown'),
                                    "title": post.get('title', ''),
                                    "content": post.get('selftext', ''),
                                    "url": f"https://reddit.com{post.get('permalink', '')}",
                                    "created_utc": post.get('created_utc', 0),
                                    "timestamp": datetime.fromtimestamp(post.get('created_utc', 0)).isoformat(),
                                    "engagement": {
                                        "upvotes": post.get('ups', 0),
                                        "downvotes": post.get('downs', 0),
                                        "comments": post.get('num_comments', 0),
                                        "score": post.get('score', 0)
                                    },
                                    "subreddit": post.get('subreddit', 'india'),
                                    "flair": post.get('link_flair_text', None)
                                }
                                posts.append(post_dict)
                                
                            except Exception as e:
                                continue
                        
                        print(f"   ✓ Extracted {len(posts)} posts\n")
                        break  # Success, exit retry loop
                    else:
                        print("   ⚠️  No posts found\n")
                        break
                else:
                    print(f"   ⚠️  HTTP {response.status_code}, retrying... ({retry_count + 1}/{self.max_retries})")
                    retry_count += 1
                    time.sleep(2)
                    
            except requests.Timeout:
                print(f"   ⚠️  Request timeout, retrying... ({retry_count + 1}/{self.max_retries})")
                retry_count += 1
                time.sleep(2)
            except Exception as e:
                print(f"   ⚠️  Scraping failed: {e}, retrying... ({retry_count + 1}/{self.max_retries})")
                retry_count += 1
                time.sleep(2)
        
        return posts[:self.max_posts]  # Final safety cap
    
    def analyze_sentiment_with_nova(self, posts: List[Dict]) -> List[Dict]:
        """
        Use Nova 2 Lite to analyze sentiment and extract topics
        
        Args:
            posts: Raw posts
            
        Returns:
            Posts with sentiment and topics added
        """
        if not self.bedrock or not posts:
            return posts
        
        print("🤖 Analyzing sentiment with Nova 2 Lite...")
        
        analyzed_posts = []
        
        # Limit posts sent to Nova (cost control)
        posts_to_analyze = min(len(posts), self.max_sentiment_analysis)
        
        for idx, post in enumerate(posts[:posts_to_analyze]):
            if idx >= self.max_sentiment_analysis:  # Extra safety check
                break
            
            try:
                # Combine title and content for analysis
                text = f"{post['title']} {post['content']}"[:500]  # Limit to 500 chars
                
                prompt = f"""Analyze this Mumbai social media post and provide:
1. Sentiment (positive, neutral, or negative)
2. Main topics (up to 3 keywords)
3. Brief summary (1 sentence)

Post: {text}

Return JSON format: {{"sentiment": "positive|neutral|negative", "topics": ["topic1", "topic2"], "summary": "..."}}"""

                response = self.bedrock.invoke_model(
                    modelId='us.amazon.nova-lite-v1:0',
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps({
                        "messages": [{"role": "user", "content": [{"text": prompt}]}],
                        "inferenceConfig": {"max_new_tokens": 150, "temperature": 0.3}
                    })
                )
                
                response_body = json.loads(response['body'].read())
                result_text = response_body['output']['message']['content'][0]['text']
                
                # Extract JSON
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                    post['sentiment'] = analysis.get('sentiment', 'neutral')
                    post['topics'] = analysis.get('topics', [])
                    post['summary'] = analysis.get('summary', post['title'])
                else:
                    # Fallback
                    post['sentiment'] = 'neutral'
                    post['topics'] = []
                    post['summary'] = post['title']
                
                analyzed_posts.append(post)
                
                # Track cost
                self.tokens_used += 250
                self.estimated_cost += 0.0002
                
            except Exception as e:
                print(f"   ⚠️  Sentiment analysis failed for post {idx + 1}: {e}")
                # Add post without sentiment
                post['sentiment'] = 'neutral'
                post['topics'] = []
                post['summary'] = post['title']
                analyzed_posts.append(post)
        
        # Add remaining posts without analysis
        for post in posts[posts_to_analyze:]:
            post['sentiment'] = 'neutral'
            post['topics'] = []
            post['summary'] = post['title']
            analyzed_posts.append(post)
        
        print(f"   ✓ Analyzed {posts_to_analyze} posts (skipped {len(posts) - posts_to_analyze} to save cost)\n")
        
        return analyzed_posts
    
    def collect_all_posts(self) -> List[Dict]:
        """Collect posts from all sources"""
        print("="*70)
        print("  👂 SOCIAL LISTENER - Real Data Collection")
        print("="*70)
        print()
        
        all_posts = []
        
        # Scrape Reddit r/mumbai (general)
        all_posts.extend(self.scrape_reddit_mumbai(query="", sort="new"))
        time.sleep(1)  # Rate limiting
        
        # Scrape Reddit r/india (Mumbai filter)
        all_posts.extend(self.scrape_reddit_india_mumbai())
        time.sleep(1)
        
        # Analyze sentiment with AI
        analyzed_posts = self.analyze_sentiment_with_nova(all_posts)
        
        print("="*70)
        print(f"  📊 COLLECTION SUMMARY")
        print("="*70)
        print(f"Total posts collected: {len(analyzed_posts)}")
        print(f"Tokens used: {self.tokens_used}")
        print(f"Estimated cost: ${self.estimated_cost:.4f}")
        print()
        
        return analyzed_posts
    
    def get_sentiment_summary(self, posts: List[Dict]) -> Dict:
        """Calculate sentiment distribution"""
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        
        for post in posts:
            sentiment = post.get('sentiment', 'neutral')
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        total = len(posts) if posts else 1
        return {
            "positive": round(sentiment_counts["positive"] / total * 100, 1),
            "neutral": round(sentiment_counts["neutral"] / total * 100, 1),
            "negative": round(sentiment_counts["negative"] / total * 100, 1),
            "total_posts": total
        }
    
    def get_trending_topics(self, posts: List[Dict], top_n: int = 10) -> List[Dict]:
        """Extract trending topics from posts"""
        topic_counts = {}
        
        for post in posts:
            for topic in post.get('topics', []):
                if topic:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Sort by count
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"topic": topic, "count": count} for topic, count in sorted_topics[:top_n]]
    
    def save_posts(self, posts: List[Dict], output_file: str = "collected_social_nova.json"):
        """Save collected posts to file"""
        # Use absolute path relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, output_file)
        
        # Calculate statistics
        sentiment_summary = self.get_sentiment_summary(posts)
        trending_topics = self.get_trending_topics(posts)
        
        output_data = {
            "collected_at": datetime.now().isoformat(),
            "source_count": 2,
            "post_count": len(posts),
            "sources": ["reddit_r/mumbai", "reddit_r/india"],
            "sentiment_summary": sentiment_summary,
            "trending_topics": trending_topics,
            "posts": posts,
            "cost_tracking": {
                "tokens_used": self.tokens_used,
                "estimated_cost": self.estimated_cost
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved to: {output_path}")
        return output_path


def main():
    """Run social listener"""
    try:
        # Initialize with limits
        listener = SocialListener(max_posts_per_source=10, demo_mode=True)
        
        # Collect posts
        posts = listener.collect_all_posts()
        
        # Save results
        listener.save_posts(posts)
        
        # Display summary
        sentiment = listener.get_sentiment_summary(posts)
        trending = listener.get_trending_topics(posts, top_n=5)
        
        print()
        print("✅ Social listening complete!")
        print(f"💰 Total cost: ${listener.estimated_cost:.4f}")
        print()
        print("📊 Sentiment Distribution:")
        print(f"   Positive: {sentiment['positive']}%")
        print(f"   Neutral: {sentiment['neutral']}%")
        print(f"   Negative: {sentiment['negative']}%")
        print()
        if trending:
            print("🔥 Top Trending Topics:")
            for item in trending[:5]:
                print(f"   • {item['topic']}: {item['count']} mentions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
