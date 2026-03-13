# -*- coding: utf-8 -*-
"""
Community Pulse Feature
Analyzes trending topics and sentiment from social media and news
Uses Amazon Bedrock Nova 2 Lite for topic extraction and sentiment analysis
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from collections import Counter
import math

# Fix Windows encoding for emojis
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import boto3

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_json_data, save_json_data, log_cost


# Stopwords for better keyword extraction
STOPWORDS = {
    "about", "there", "their", "would", "could", "should", "these", "those",
    "which", "while", "where", "after", "before", "other", "still", "being",
    "going", "doing", "today", "people", "things", "really", "think", "maybe",
    "something", "someone", "anything", "everything", "nothing", "always",
    "never", "often", "sometimes", "usually", "actually", "basically",
    "literally", "probably", "definitely", "certainly", "obviously",
    # Location names to filter out
    "mumbai", "india", "bandra", "thane", "delhi", "pune", "bangalore",
    "kolkata", "chennai", "hyderabad", "city", "area", "place", "location",
    "andheri", "dadar", "kurla", "borivali", "malad", "goregaon", "powai",
    # Generic legal/news terms to filter out
    "bombay", "court", "accused", "judge", "legal", "case", "cases",
    "notice", "notices", "police", "official", "report", "reported",
    "statement", "according", "sources", "spokesperson",
    # Additional noise words from news headlines
    "update", "latest", "says", "said", "breaking", "news", "issue",
    "matter", "reports",
    # Religious/political terms to filter out
    "prayers", "prayer", "religious", "religion", "namaz", "temple", "mosque",
    "church", "worship", "faith", "spiritual", "divine", "sacred", "holy",
    "ritual", "ceremony", "blessing", "devotion",
    # Generic action/state words
    "right", "rights", "denies", "denied", "permission", "citing", "cited",
    "security", "concern", "concerns", "regarding", "related", "involving",
    "against", "towards", "between", "during", "within", "without",
    # Vague descriptors
    "general", "specific", "particular", "certain", "various", "several",
    "multiple", "different", "similar", "common", "normal", "regular"
}

# Topic synonym mapping for normalization
TOPIC_SYNONYMS = {
    # Traffic-related
    "traffic": "traffic",
    "congestion": "traffic",
    "jam": "traffic",
    "jams": "traffic",
    # Metro/Railway
    "metro": "metro_transport",
    "railway": "metro_transport",
    "train": "metro_transport",
    "trains": "metro_transport",
    "subway": "metro_transport",
    # Airport
    "airport": "airport_transport",
    "flights": "airport_transport",
    "flight": "airport_transport",
    # Housing
    "housing": "housing",
    "real_estate": "housing",
    "apartments": "housing",
    "apartment": "housing",
    "homes": "housing",
    "property": "housing",
    # Infrastructure
    "construction": "infrastructure",
    "infrastructure": "infrastructure",
    "development": "infrastructure",
    "roads": "infrastructure",
    "bridge": "infrastructure",
    "bridges": "infrastructure"
}


def clean_word(word: str) -> str:
    """
    Clean a word by removing punctuation
    
    Args:
        word: Raw word with potential punctuation
        
    Returns:
        Cleaned word
    """
    return word.strip('.,!?;:()[]"\'')


def normalize_topic(word: str) -> str:
    """
    Normalize a keyword to its canonical civic topic
    
    Args:
        word: Raw keyword
        
    Returns:
        Normalized topic name or original word if no mapping exists
    """
    return TOPIC_SYNONYMS.get(word.lower(), word.lower())


def format_topic_name(topic: str) -> str:
    """
    Convert normalized topic to human-readable title
    
    Args:
        topic: Normalized topic (e.g., "airport_transport")
        
    Returns:
        Human-readable title (e.g., "Airport Transport")
    """
    return topic.replace('_', ' ').title()


def is_quality_topic(topic: str, post_count: int, min_posts: int = 2) -> bool:
    """
    Check if a topic meets quality criteria
    
    Args:
        topic: Topic keyword
        post_count: Number of posts mentioning this topic
        min_posts: Minimum posts required (default: 2)
        
    Returns:
        True if topic is high quality, False otherwise
    """
    # Must appear in at least min_posts different posts
    if post_count < min_posts:
        return False
    
    # Prefer multi-word topics (with underscore) over single words
    # Single words must be very specific civic terms
    if '_' not in topic:
        # Allow specific civic single-word topics
        civic_keywords = {
            'traffic', 'housing', 'pollution', 'water', 'electricity',
            'sanitation', 'waste', 'garbage', 'drainage', 'flooding'
        }
        if topic.lower() not in civic_keywords:
            return False
    
    return True


class CommunityPulse:
    """Analyze community sentiment and trending topics"""
    
    def __init__(self, target_area: Optional[str] = None):
        """
        Initialize Community Pulse system
        
        Args:
            target_area: Optional specific area to analyze (e.g., "Mumbai")
        """
        print("📊 Initializing Community Pulse System...\n")
        
        self.target_area = target_area or "Mumbai"
        
        # Cost tracking
        self.tokens_used = 0
        self.estimated_cost = 0.0
        
        # Initialize Bedrock client
        try:
            self.bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            print("✓ Connected to Amazon Bedrock\n")
        except Exception as e:
            print(f"❌ Failed to connect to Bedrock: {e}")
            raise
    
    def load_data_sources(self) -> Dict[str, List]:
        """Load all data sources from data/ directory"""
        print("📊 Loading data sources...")
        
        # Load from centralized data directory
        social_data = load_json_data('social.json', default=[])
        news_data = load_json_data('news.json', default=[])
        
        # Handle both dict and list formats
        def extract_list(data):
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data.get('events', data.get('posts', data.get('articles', [])))
            return []
        
        data = {
            "social": extract_list(social_data),
            "news": extract_list(news_data)
        }
        
        print(f"   Social posts: {len(data['social'])}")
        print(f"   News articles: {len(data['news'])}")
        print()
        
        return data
    
    def extract_basic_topics(self, social: List[Dict], news: List[Dict]) -> Dict:
        """
        Extract basic topics and metrics from social and news data
        
        Args:
            social: List of social media posts
            news: List of news articles
            
        Returns:
            Dictionary with basic topic analysis
        """
        print("🔍 Extracting basic topics and metrics...")
        
        # Extract keywords from social posts
        social_keywords = []
        social_sentiments = []
        total_engagement = 0
        
        # Track keywords per post for diversity control AND quality filtering
        post_keywords = []
        topic_post_tracker = {}  # Track which posts mention each topic
        
        for post_idx, post in enumerate(social):
            # Combine title and content for better topic extraction
            title = post.get('title', '')
            content = post.get('content', '')
            text = f"{title} {content}".lower()
            
            # Get engagement for weighting
            engagement = post.get('engagement', {})
            engagement_score = engagement.get('upvotes', 0) + engagement.get('comments', 0)
            total_engagement += engagement_score
            
            # Improved keyword extraction with stopword filtering
            words = []
            for w in text.split():
                cleaned = clean_word(w)
                if (cleaned.isalpha() and 
                    len(cleaned) > 4 and 
                    cleaned.lower() not in STOPWORDS):
                    # Normalize to canonical topic
                    normalized = normalize_topic(cleaned)
                    words.append(normalized)
            
            # Topic diversity control: limit each topic to max 3 mentions per post
            word_counts = Counter(words[:15])  # Top 15 words per post
            diverse_words = []
            for word, count in word_counts.items():
                diverse_words.extend([word] * min(3, count))  # Max 3 per topic per post
            
            # Track which posts mention each topic (for quality filtering)
            for word in set(diverse_words):  # Use set to count each topic once per post
                if word not in topic_post_tracker:
                    topic_post_tracker[word] = set()
                topic_post_tracker[word].add(post_idx)
            
            # Weight keywords by engagement (highly engaged posts contribute more)
            # Cap at 5 to prevent single viral posts from dominating
            weight = min(5, max(1, engagement_score // 10))
            for word in diverse_words:
                social_keywords.extend([word] * weight)
            
            post_keywords.append({
                'keywords': diverse_words,
                'engagement': engagement_score
            })
            
            # Get sentiment if available
            sentiment = post.get('sentiment', 'neutral')
            social_sentiments.append(sentiment)
        
        # Extract topics from news
        news_categories = []
        news_keywords = []
        
        for article in news:
            category = article.get('category', 'General')
            news_categories.append(category)
            
            # Extract keywords from title with improved filtering
            title = article.get('title', '').lower()
            words = []
            for w in title.split():
                cleaned = clean_word(w)
                if (cleaned.isalpha() and 
                    len(cleaned) > 4 and 
                    cleaned.lower() not in STOPWORDS):
                    # Normalize to canonical topic
                    normalized = normalize_topic(cleaned)
                    words.append(normalized)
            
            news_keywords.extend(words[:5])  # Top 5 meaningful words per title
        
        # Count occurrences
        social_keyword_counts = Counter(social_keywords)
        news_keyword_counts = Counter(news_keywords)
        news_category_counts = Counter(news_categories)
        sentiment_counts = Counter(social_sentiments)
        
        # Calculate trend scores (mentions * log(engagement + 1))
        topic_scores = {}
        for topic, mentions in social_keyword_counts.items():
            # Apply quality filter: topic must appear in at least 2 posts
            post_count = len(topic_post_tracker.get(topic, set()))
            if not is_quality_topic(topic, post_count, min_posts=2):
                continue  # Skip low-quality topics
            
            # Calculate total engagement for this topic
            topic_engagement = sum(
                pk['engagement'] for pk in post_keywords 
                if topic in pk['keywords']
            )
            # Trend score with logarithmic engagement weighting
            trend_score = mentions * math.log(topic_engagement + 1)
            topic_scores[topic] = {
                'mentions': mentions,
                'engagement': topic_engagement,
                'trend_score': trend_score,
                'post_count': post_count
            }
        
        # Sort by trend score
        sorted_topics = sorted(
            topic_scores.items(),
            key=lambda x: x[1]['trend_score'],
            reverse=True
        )
        
        # Normalize trend scores to 0-10 scale using min-max normalization
        if sorted_topics:
            max_score = sorted_topics[0][1]['trend_score']
            min_score = sorted_topics[-1][1]['trend_score'] if len(sorted_topics) > 1 else 0
            
            for topic, data in sorted_topics:
                if max_score > min_score:
                    normalized = ((data['trend_score'] - min_score) / (max_score - min_score)) * 10
                else:
                    normalized = 10.0  # If all scores are equal
                data['normalized_score'] = round(normalized, 1)
        
        # Get top topics with normalized scores
        top_social_topics = [
            {
                "topic": topic,
                "mentions": data['mentions'],
                "engagement": data['engagement'],
                "trend_score": data['normalized_score']
            }
            for topic, data in sorted_topics[:10]
        ]
        
        top_news_topics = [
            {"topic": word, "mentions": count}
            for word, count in news_keyword_counts.most_common(10)
        ]
        
        # News categories
        news_categories_list = [
            {"category": cat, "count": count}
            for cat, count in news_category_counts.most_common()
        ]
        
        # Sentiment distribution
        total_posts = len(social_sentiments)
        sentiment_distribution = {
            "positive": sentiment_counts.get('positive', 0),
            "neutral": sentiment_counts.get('neutral', 0),
            "negative": sentiment_counts.get('negative', 0),
            "positive_pct": round(sentiment_counts.get('positive', 0) / total_posts * 100, 1) if total_posts > 0 else 0,
            "neutral_pct": round(sentiment_counts.get('neutral', 0) / total_posts * 100, 1) if total_posts > 0 else 0,
            "negative_pct": round(sentiment_counts.get('negative', 0) / total_posts * 100, 1) if total_posts > 0 else 0
        }
        
        print(f"   Top social topics: {len(top_social_topics)}")
        print(f"   Top news topics: {len(top_news_topics)}")
        print(f"   News categories: {len(news_categories_list)}")
        print(f"   Total engagement: {total_engagement}")
        print()
        
        return {
            "top_social_topics": top_social_topics,
            "top_news_topics": top_news_topics,
            "news_categories": news_categories_list,
            "sentiment_distribution": sentiment_distribution,
            "total_social_posts": len(social),
            "total_news_articles": len(news),
            "total_engagement": total_engagement
        }
    
    def generate_community_insights(self, basic_topics: Dict) -> Dict:
        """
        Generate community insights using Nova 2 Lite
        
        Args:
            basic_topics: Basic topic analysis data
            
        Returns:
            Community insights and trending topics
        """
        print("🤖 Generating community insights with Nova 2 Lite...")
        
        # Prepare context for Nova
        context = {
            "target_area": self.target_area,
            "top_social_topics": basic_topics.get('top_social_topics', [])[:5],
            "top_news_topics": basic_topics.get('top_news_topics', [])[:5],
            "news_categories": basic_topics.get('news_categories', [])[:5],
            "sentiment": basic_topics.get('sentiment_distribution', {}),
            "total_posts": basic_topics.get('total_social_posts', 0),
            "total_articles": basic_topics.get('total_news_articles', 0)
        }
        
        prompt = f"""You are an AI system analyzing community discussions and news signals for the city of {context['target_area']}.

Your task is to detect meaningful civic trends affecting residents, not generic news words.
Use the provided topic frequencies to infer what issues people are discussing.

PRIORITIZE REAL URBAN PROBLEMS such as:
- traffic congestion and road conditions
- metro or railway development and delays
- housing affordability and real estate prices
- infrastructure construction projects
- airport or transport connectivity issues
- environmental concerns (pollution, waste, green spaces)
- public services (water supply, sanitation, electricity)
- safety or crime concerns

AVOID:
- generic legal terms (court, accused, judge, notice)
- reporting language (reported, statement, according)
- location names (city names, neighborhoods)
- vague or abstract topics

DATA SUMMARY

Social Posts: {context['total_posts']}
News Articles: {context['total_articles']}

Top Social Topics (with trend scores 0-10):
{json.dumps(context['top_social_topics'], indent=2)}

Top News Topics:
{json.dumps(context['top_news_topics'], indent=2)}

News Categories:
{json.dumps(context['news_categories'], indent=2)}

Sentiment Distribution:
- Positive: {context['sentiment'].get('positive_pct', 0)}%
- Neutral: {context['sentiment'].get('neutral_pct', 0)}%
- Negative: {context['sentiment'].get('negative_pct', 0)}%

TASK

Identify 3-5 meaningful urban topics affecting residents and 2-3 community concerns.

CRITICAL RULES:

1. CATEGORY ENFORCEMENT - Use ONLY these exact categories (do not invent new ones):
   - transport
   - infrastructure
   - housing
   - environment
   - safety
   - public_services
   - development

2. AFFECTED AREAS - Use ONLY these specific Mumbai regions:
   - Western Suburbs
   - Central Mumbai
   - Eastern Suburbs
   - South Mumbai
   - Navi Mumbai
   Do NOT use: "downtown", "city center", "major highways", "nearby areas"

3. TOPIC DESCRIPTIONS - Must reference BOTH:
   - Mention frequency (e.g., "mentioned X times")
   - Engagement level (e.g., "high engagement of Y")
   Example: "Frequent mentions (6) combined with high engagement (1316) suggest growing public concern about airport connectivity."

4. COMMUNITY CONCERNS - Must derive directly from trending topics:
   - If "traffic" is trending → concern about "traffic congestion"
   - If "metro_transport" is trending → concern about "metro reliability" or "metro delays"
   - If "housing" is trending → concern about "housing affordability"
   - If "airport_transport" is trending → concern about "airport connectivity"
   Do NOT introduce concerns unrelated to the trending topics.

5. RECOMMENDATIONS - Must be specific and actionable:
   - Good: "Implement real-time traffic monitoring systems on Western Express Highway"
   - Bad: "Improve traffic management"

Output ONLY valid JSON in this exact format:

{{
  "trending_topics": [
    {{
      "topic": "...",
      "trend_score": 1-10,
      "category": "transport/infrastructure/housing/environment/safety/public_services/development",
      "sentiment": "positive/neutral/negative",
      "description": "Must mention both frequency and engagement metrics from the data"
    }}
  ],
  "community_concerns": [
    {{
      "concern": "Must relate directly to a trending topic above",
      "severity": "high/medium/low",
      "affected_areas": ["Western Suburbs", "Central Mumbai", etc. - use ONLY the 5 regions listed above"],
      "recommendation": "Specific, actionable steps authorities can implement"
    }}
  ],
  "overall_sentiment": {{
    "mood": "positive/neutral/negative",
    "key_drivers": ["specific topics from trending_topics"],
    "notable_changes": ["observable trends based on the data"]
  }}
}}

Return JSON only. Do not include explanations or text outside the JSON."""

        try:
            response = self.bedrock.invoke_model(
                modelId='us.amazon.nova-lite-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ],
                    "inferenceConfig": {
                        "max_new_tokens": 1000,
                        "temperature": 0.5
                    }
                })
            )
            
            response_body = json.loads(response['body'].read())
            result_text = response_body['output']['message']['content'][0]['text']
            
            # Track usage
            usage = response_body.get('usage', {})
            input_tokens = usage.get('inputTokens', 0)
            output_tokens = usage.get('outputTokens', 0)
            self.tokens_used += (input_tokens + output_tokens)
            
            # Calculate cost (Nova 2 Lite pricing)
            cost_per_1k_input = 0.00006
            cost_per_1k_output = 0.00024
            cost = ((input_tokens / 1000) * cost_per_1k_input +
                   (output_tokens / 1000) * cost_per_1k_output)
            self.estimated_cost += cost
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                insights = json.loads(json_match.group())
                print("✓ Insights generated successfully\n")
                return insights
            else:
                print("⚠️  Could not parse insights, using fallback\n")
                return self._fallback_insights(basic_topics)
            
        except Exception as e:
            print(f"⚠️  Insight generation failed: {e}\n")
            return self._fallback_insights(basic_topics)
    
    def _fallback_insights(self, basic_topics: Dict) -> Dict:
        """Fallback insights if Nova fails"""
        top_social = basic_topics.get('top_social_topics', [])
        sentiment = basic_topics.get('sentiment_distribution', {})
        
        # Create simple trending topics
        trending_topics = []
        for i, topic_data in enumerate(top_social[:3], 1):
            trending_topics.append({
                "topic": topic_data['topic'],
                "trend_score": 10 - i,
                "category": "social",
                "sentiment": "neutral",
                "description": f"Frequently mentioned in community discussions"
            })
        
        # Determine overall mood
        pos_pct = sentiment.get('positive_pct', 0)
        neg_pct = sentiment.get('negative_pct', 0)
        
        if pos_pct > neg_pct + 20:
            mood = "positive"
        elif neg_pct > pos_pct + 20:
            mood = "negative"
        else:
            mood = "neutral"
        
        return {
            "trending_topics": trending_topics,
            "community_concerns": [
                {
                    "concern": "General community discussions",
                    "severity": "medium",
                    "affected_areas": [self.target_area],
                    "recommendation": "Monitor ongoing discussions"
                }
            ],
            "overall_sentiment": {
                "mood": mood,
                "key_drivers": ["Community engagement", "Local discussions"],
                "notable_changes": []
            }
        }
    
    def save_results(self, basic_topics: Dict, insights: Dict, 
                    output_file: str = "community_pulse.json"):
        """Save community pulse results to data/ directory"""
        
        output_data = {
            "generated_at": datetime.now().isoformat(),
            "target_area": self.target_area,
            "basic_topics": basic_topics,
            "insights": insights,
            "metadata": {
                "tokens_used": self.tokens_used,
                "estimated_cost": self.estimated_cost
            }
        }
        
        save_json_data(output_file, output_data)
        
        # Log cost
        log_cost(
            agent_name="community_pulse",
            tokens_used=self.tokens_used,
            estimated_cost=self.estimated_cost,
            model="Amazon Nova 2 Lite",
            operation="topic_analysis"
        )
        
        return output_file


def main():
    """Demo: Generate community pulse for Mumbai"""
    print("="*70)
    print("  📊 COMMUNITY PULSE SYSTEM - Demo")
    print("="*70)
    print()
    
    # Target area
    target_area = "Mumbai"
    
    try:
        # Initialize system
        pulse_system = CommunityPulse(target_area)
        
        # Load data
        data = pulse_system.load_data_sources()
        
        # Extract basic topics
        basic_topics = pulse_system.extract_basic_topics(
            data['social'],
            data['news']
        )
        
        # Generate insights
        insights = pulse_system.generate_community_insights(basic_topics)
        
        # Display results
        print("="*70)
        print("  📊 COMMUNITY PULSE REPORT")
        print("="*70)
        print()
        print(f"Target Area: {target_area}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Data Summary
        print("Data Summary:")
        print(f"  Social Posts: {basic_topics['total_social_posts']}")
        print(f"  News Articles: {basic_topics['total_news_articles']}")
        print(f"  Total Engagement: {basic_topics['total_engagement']}")
        print()
        
        # Sentiment
        sentiment = basic_topics['sentiment_distribution']
        print("Community Sentiment:")
        print(f"  Positive: {sentiment['positive_pct']}% ({sentiment['positive']} posts)")
        print(f"  Neutral: {sentiment['neutral_pct']}% ({sentiment['neutral']} posts)")
        print(f"  Negative: {sentiment['negative_pct']}% ({sentiment['negative']} posts)")
        print()
        
        # Trending Topics
        print("-" * 70)
        print("Trending Topics:")
        print("-" * 70)
        
        if insights.get('trending_topics'):
            # Limit to maximum 4 topics for concise report
            for i, topic in enumerate(insights['trending_topics'][:4], 1):
                # Format topic name for display
                topic_name = format_topic_name(topic['topic'])
                category_name = format_topic_name(topic['category'])
                print(f"\n  {i}. {topic_name}")
                print(f"     Trend Score: {topic['trend_score']}/10")
                print(f"     Category: {category_name}")
                print(f"     Sentiment: {topic['sentiment'].title()}")
                print(f"     {topic['description']}")
        
        # Community Concerns
        if insights.get('community_concerns'):
            print()
            print("-" * 70)
            print("Community Concerns:")
            print("-" * 70)
            
            for i, concern in enumerate(insights['community_concerns'], 1):
                # Format concern name for better display
                concern_name = concern['concern'].title()
                print(f"\n  • {concern_name}")
                print(f"    Severity: {concern['severity'].upper()}")
                print(f"    Affected Areas: {', '.join(concern.get('affected_areas', []))}")
                print(f"    Recommendation: {concern['recommendation']}")
        
        # Overall Sentiment
        if insights.get('overall_sentiment'):
            overall = insights['overall_sentiment']
            print()
            print("-" * 70)
            print("Overall Community Mood:")
            print("-" * 70)
            print(f"\n  Mood: {overall['mood'].upper()}")
            if overall.get('key_drivers'):
                # Format key drivers for display
                formatted_drivers = [format_topic_name(driver) for driver in overall['key_drivers'][:3]]
                print(f"  Key Drivers: {', '.join(formatted_drivers)}")
            if overall.get('notable_changes'):
                print(f"  Notable Changes: {', '.join(overall['notable_changes'][:3])}")
        
        print()
        print("-" * 70)
        
        # Save results
        output_file = pulse_system.save_results(basic_topics, insights)
        
        print()
        print("✅ Community pulse generated successfully!")
        print(f"💰 Estimated cost: ${pulse_system.estimated_cost:.6f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
