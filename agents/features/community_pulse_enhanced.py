# -*- coding: utf-8 -*-
"""
Enhanced Community Pulse Feature with Embeddings Clustering
Analyzes trending topics with advanced AI techniques
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from collections import Counter
import math

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import boto3

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_json_data, save_json_data, log_cost


# Stopwords (same as before)
STOPWORDS = {
    "about", "there", "their", "would", "could", "should", "these", "those",
    "which", "while", "where", "after", "before", "other", "still", "being",
    "going", "doing", "today", "people", "things", "really", "think", "maybe",
    "mumbai", "india", "bandra", "thane", "delhi", "city", "area", "place",
    "court", "accused", "judge", "legal", "case", "police", "official"
}

# Topic synonyms (expanded)
TOPIC_SYNONYMS = {
    # Traffic
    "traffic": "traffic", "congestion": "traffic", "jam": "traffic",
    "jams": "traffic", "gridlock": "traffic",
    # Metro/Railway
    "metro": "metro_transport", "railway": "metro_transport",
    "train": "metro_transport", "trains": "metro_transport",
    "rail": "metro_transport", "subway": "metro_transport",
    # Airport
    "airport": "airport_transport", "flights": "airport_transport",
    "flight": "airport_transport",
    # Housing
    "housing": "housing", "real_estate": "housing",
    "apartments": "housing", "apartment": "housing",
    "rent": "housing", "property": "housing",
    # Infrastructure
    "construction": "infrastructure", "infrastructure": "infrastructure",
    "development": "infrastructure", "roads": "infrastructure",
    # Waste
    "garbage": "waste_management", "trash": "waste_management",
    "waste": "waste_management"
}


def clean_word(word: str) -> str:
    return word.strip('.,!?;:()[]"\'')


def normalize_topic(word: str) -> str:
    return TOPIC_SYNONYMS.get(word.lower(), word.lower())


def format_topic_name(topic: str) -> str:
    return topic.replace('_', ' ').title()


class EnhancedCommunityPulse:
    """Enhanced Community Pulse with embeddings and relationship detection"""
    
    def __init__(self, target_area: Optional[str] = None):
        print("📊 Initializing Enhanced Community Pulse System...\n")
        
        self.target_area = target_area or "Mumbai"
        self.tokens_used = 0
        self.estimated_cost = 0.0
        
        # Initialize Bedrock
        try:
            self.bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            print("✓ Connected to Amazon Bedrock\n")
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            raise
    
    def get_topic_embedding(self, topic: str) -> List[float]:
        """Get embedding for a topic using Titan Embeddings"""
        try:
            response = self.bedrock.invoke_model(
                modelId='amazon.titan-embed-text-v2:0',
                body=json.dumps({"inputText": topic})
            )
            result = json.loads(response['body'].read())
            return result['embedding']
        except Exception as e:
            print(f"⚠️  Embedding failed for '{topic}': {e}")
            return []
    
    def cluster_topics_with_embeddings(self, topics: List[Dict]) -> Dict:
        """
        Cluster similar topics using Titan Embeddings
        
        Args:
            topics: List of topic dictionaries with 'topic' key
            
        Returns:
            Dictionary with clustered topics
        """
        print("🔬 Clustering topics with Titan Embeddings...")
        
        if len(topics) < 2:
            return {"clusters": [], "message": "Not enough topics to cluster"}
        
        # Get embeddings for top topics
        topic_embeddings = []
        valid_topics = []
        
        for topic_data in topics[:10]:  # Limit to top 10 for cost
            topic = topic_data['topic']
            embedding = self.get_topic_embedding(topic)
            if embedding:
                topic_embeddings.append(embedding)
                valid_topics.append(topic_data)
        
        if len(valid_topics) < 2:
            return {"clusters": [], "message": "Embedding generation failed"}
        
        # Simple clustering: calculate similarity between all pairs
        clusters = []
        used_indices = set()
        
        for i, topic1 in enumerate(valid_topics):
            if i in used_indices:
                continue
            
            cluster = {
                "main_topic": topic1['topic'],
                "related_topics": [],
                "total_mentions": topic1.get('mentions', 0),
                "trend_score": topic1.get('trend_score', 0)
            }
            
            # Find similar topics
            for j, topic2 in enumerate(valid_topics):
                if i == j or j in used_indices:
                    continue
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(
                    topic_embeddings[i],
                    topic_embeddings[j]
                )
                
                # If similarity > 0.7, add to cluster
                if similarity > 0.7:
                    cluster['related_topics'].append({
                        "topic": topic2['topic'],
                        "similarity": round(similarity, 2)
                    })
                    cluster['total_mentions'] += topic2.get('mentions', 0)
                    used_indices.add(j)
            
            used_indices.add(i)
            clusters.append(cluster)
        
        print(f"   Found {len(clusters)} topic clusters\n")
        
        # Track cost (Titan Embeddings: $0.0001 per 1K tokens, ~10 tokens per topic)
        embedding_cost = len(valid_topics) * 0.000001  # Very cheap!
        self.estimated_cost += embedding_cost
        
        return {
            "clusters": clusters,
            "total_topics_analyzed": len(valid_topics),
            "embedding_cost": embedding_cost
        }
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def detect_topic_relationships(self, topics: List[Dict]) -> Dict:
        """
        Detect relationships between topics using Nova 2 Lite
        
        Args:
            topics: List of trending topics
            
        Returns:
            Dictionary with topic relationships
        """
        print("🔗 Detecting topic relationships with Nova 2 Lite...")
        
        if len(topics) < 2:
            return {"relationships": []}
        
        # Get top 5 topics for relationship analysis
        top_topics = [t['topic'] for t in topics[:5]]
        
        prompt = f"""Analyze these civic topics and identify meaningful relationships between them:

Topics: {', '.join(top_topics)}

For each pair of related topics, explain how they connect in the context of urban civic issues.

Examples of good relationships:
- "Traffic" relates to "Airport" because road congestion affects airport access
- "Metro" relates to "Housing" because new metro lines increase property values
- "Construction" relates to "Traffic" because road work causes congestion

Return ONLY valid JSON in this format:
{{
  "relationships": [
    {{
      "topic1": "traffic",
      "topic2": "airport",
      "connection": "Road congestion on highways affects airport accessibility",
      "strength": "high/medium/low"
    }}
  ]
}}

Identify 2-4 meaningful relationships. Return JSON only."""

        try:
            response = self.bedrock.invoke_model(
                modelId='us.amazon.nova-lite-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [{
                        "role": "user",
                        "content": [{"text": prompt}]
                    }],
                    "inferenceConfig": {
                        "max_new_tokens": 500,
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
            
            # Calculate cost
            cost = ((input_tokens / 1000) * 0.00006 +
                   (output_tokens / 1000) * 0.00024)
            self.estimated_cost += cost
            
            # Parse JSON
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                relationships = json.loads(json_match.group())
                print(f"   Found {len(relationships.get('relationships', []))} relationships\n")
                return relationships
            else:
                print("   No relationships detected\n")
                return {"relationships": []}
            
        except Exception as e:
            print(f"⚠️  Relationship detection failed: {e}\n")
            return {"relationships": []}
    
    def load_data_sources(self) -> Dict[str, List]:
        """Load all data sources from data/ directory"""
        print("📊 Loading data sources...")
        
        social_data = load_json_data('social.json', default=[])
        news_data = load_json_data('news.json', default=[])
        
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
        """Extract basic topics and metrics from social and news data"""
        print("🔍 Extracting basic topics and metrics...")
        
        social_keywords = []
        social_sentiments = []
        total_engagement = 0
        
        post_keywords = []
        topic_post_tracker = {}
        
        for post_idx, post in enumerate(social):
            title = post.get('title', '')
            content = post.get('content', '')
            text = f"{title} {content}".lower()
            
            engagement = post.get('engagement', {})
            engagement_score = engagement.get('upvotes', 0) + engagement.get('comments', 0)
            total_engagement += engagement_score
            
            words = []
            for w in text.split():
                cleaned = clean_word(w)
                if (cleaned.isalpha() and 
                    len(cleaned) > 4 and 
                    cleaned.lower() not in STOPWORDS):
                    normalized = normalize_topic(cleaned)
                    words.append(normalized)
            
            word_counts = Counter(words[:15])
            diverse_words = []
            for word, count in word_counts.items():
                diverse_words.extend([word] * min(3, count))
            
            for word in set(diverse_words):
                if word not in topic_post_tracker:
                    topic_post_tracker[word] = set()
                topic_post_tracker[word].add(post_idx)
            
            weight = min(5, max(1, engagement_score // 10))
            for word in diverse_words:
                social_keywords.extend([word] * weight)
            
            post_keywords.append({
                'keywords': diverse_words,
                'engagement': engagement_score
            })
            
            sentiment = post.get('sentiment', 'neutral')
            social_sentiments.append(sentiment)
        
        news_categories = []
        news_keywords = []
        
        for article in news:
            category = article.get('category', 'General')
            news_categories.append(category)
            
            title = article.get('title', '').lower()
            words = []
            for w in title.split():
                cleaned = clean_word(w)
                if (cleaned.isalpha() and 
                    len(cleaned) > 4 and 
                    cleaned.lower() not in STOPWORDS):
                    normalized = normalize_topic(cleaned)
                    words.append(normalized)
            
            news_keywords.extend(words[:5])
        
        social_keyword_counts = Counter(social_keywords)
        news_keyword_counts = Counter(news_keywords)
        news_category_counts = Counter(news_categories)
        sentiment_counts = Counter(social_sentiments)
        
        topic_scores = {}
        for topic, mentions in social_keyword_counts.items():
            post_count = len(topic_post_tracker.get(topic, set()))
            if post_count < 2:  # Quality filter
                continue
            
            topic_engagement = sum(
                pk['engagement'] for pk in post_keywords 
                if topic in pk['keywords']
            )
            trend_score = mentions * math.log(topic_engagement + 1)
            topic_scores[topic] = {
                'mentions': mentions,
                'engagement': topic_engagement,
                'trend_score': trend_score,
                'post_count': post_count
            }
        
        sorted_topics = sorted(
            topic_scores.items(),
            key=lambda x: x[1]['trend_score'],
            reverse=True
        )
        
        if sorted_topics:
            max_score = sorted_topics[0][1]['trend_score']
            min_score = sorted_topics[-1][1]['trend_score'] if len(sorted_topics) > 1 else 0
            
            for topic, data in sorted_topics:
                if max_score > min_score:
                    normalized = ((data['trend_score'] - min_score) / (max_score - min_score)) * 10
                else:
                    normalized = 10.0
                data['normalized_score'] = round(normalized, 1)
        
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
        
        news_categories_list = [
            {"category": cat, "count": count}
            for cat, count in news_category_counts.most_common()
        ]
        
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
    
    def generate_community_insights(self, basic_topics: Dict, 
                                   clusters: Dict = None,
                                   relationships: Dict = None) -> Dict:
        """Generate enhanced community insights with clustering and relationships"""
        print("🤖 Generating enhanced community insights with Nova 2 Lite...")
        
        context = {
            "target_area": self.target_area,
            "top_social_topics": basic_topics.get('top_social_topics', [])[:5],
            "sentiment": basic_topics.get('sentiment_distribution', {}),
            "total_posts": basic_topics.get('total_social_posts', 0),
            "clusters": clusters.get('clusters', []) if clusters else [],
            "relationships": relationships.get('relationships', []) if relationships else []
        }
        
        # Enhanced prompt with clustering and relationship context
        cluster_context = ""
        if context['clusters']:
            cluster_context = f"\n\nTopic Clusters (similar topics grouped together):\n{json.dumps(context['clusters'][:3], indent=2)}"
        
        relationship_context = ""
        if context['relationships']:
            relationship_context = f"\n\nTopic Relationships:\n{json.dumps(context['relationships'], indent=2)}"
        
        prompt = f"""Analyze community discussions for {context['target_area']}.

DATA SUMMARY

Social Posts: {context['total_posts']}

Top Topics (with trend scores 0-10):
{json.dumps(context['top_social_topics'], indent=2)}
{cluster_context}
{relationship_context}

Sentiment Distribution:
- Positive: {context['sentiment'].get('positive_pct', 0)}%
- Neutral: {context['sentiment'].get('neutral_pct', 0)}%
- Negative: {context['sentiment'].get('negative_pct', 0)}%

TASK: Identify 3-5 meaningful urban topics and 2-3 community concerns.

Use ONLY these categories: transport, infrastructure, housing, environment, safety, public_services, development

Use ONLY these Mumbai regions: Western Suburbs, Central Mumbai, Eastern Suburbs, South Mumbai, Navi Mumbai

Output ONLY valid JSON:

{{
  "trending_topics": [
    {{
      "topic": "...",
      "trend_score": 1-10,
      "category": "transport/infrastructure/housing/etc",
      "sentiment": "positive/neutral/negative",
      "description": "Must mention frequency and engagement"
    }}
  ],
  "community_concerns": [
    {{
      "concern": "Must relate to trending topics",
      "severity": "high/medium/low",
      "affected_areas": ["Western Suburbs", etc],
      "recommendation": "Specific actionable steps"
    }}
  ],
  "overall_sentiment": {{
    "mood": "positive/neutral/negative",
    "key_drivers": ["topics"],
    "notable_changes": ["trends"]
  }}
}}

Return JSON only."""

        try:
            response = self.bedrock.invoke_model(
                modelId='us.amazon.nova-lite-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [{
                        "role": "user",
                        "content": [{"text": prompt}]
                    }],
                    "inferenceConfig": {
                        "max_new_tokens": 1000,
                        "temperature": 0.5
                    }
                })
            )
            
            response_body = json.loads(response['body'].read())
            result_text = response_body['output']['message']['content'][0]['text']
            
            usage = response_body.get('usage', {})
            input_tokens = usage.get('inputTokens', 0)
            output_tokens = usage.get('outputTokens', 0)
            self.tokens_used += (input_tokens + output_tokens)
            
            cost = ((input_tokens / 1000) * 0.00006 +
                   (output_tokens / 1000) * 0.00024)
            self.estimated_cost += cost
            
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                insights = json.loads(json_match.group())
                
                # Add enhanced features to insights
                if clusters:
                    insights['topic_clusters'] = clusters
                if relationships:
                    insights['topic_relationships'] = relationships
                
                print("✓ Enhanced insights generated successfully\n")
                return insights
            else:
                print("⚠️  Could not parse insights\n")
                return {}
            
        except Exception as e:
            print(f"⚠️  Insight generation failed: {e}\n")
            return {}
    
    def save_results(self, basic_topics: Dict, insights: Dict, 
                    output_file: str = "community_pulse.json"):
        """Save enhanced community pulse results"""
        
        output_data = {
            "generated_at": datetime.now().isoformat(),
            "target_area": self.target_area,
            "basic_topics": basic_topics,
            "insights": insights,
            "metadata": {
                "tokens_used": self.tokens_used,
                "estimated_cost": self.estimated_cost,
                "enhanced_features": ["embeddings_clustering", "topic_relationships"]
            }
        }
        
        save_json_data(output_file, output_data)
        
        log_cost(
            agent_name="community_pulse_enhanced",
            tokens_used=self.tokens_used,
            estimated_cost=self.estimated_cost,
            model="Amazon Nova 2 Lite + Titan Embeddings",
            operation="enhanced_topic_analysis"
        )
        
        return output_file


def main():
    """Run Enhanced Community Pulse with full workflow"""
    print("="*70)
    print("  📊 ENHANCED COMMUNITY PULSE SYSTEM")
    print("="*70)
    print()
    
    try:
        pulse = EnhancedCommunityPulse("Mumbai")
        
        # Load data sources
        data = pulse.load_data_sources()
        
        # Extract basic topics
        basic_topics = pulse.extract_basic_topics(
            data['social'],
            data['news']
        )
        
        # Get top topics for enhancement
        top_topics = basic_topics.get('top_social_topics', [])
        
        if len(top_topics) >= 2:
            # Apply embeddings clustering
            clusters = pulse.cluster_topics_with_embeddings(top_topics)
            
            # Detect topic relationships
            relationships = pulse.detect_topic_relationships(top_topics)
        else:
            clusters = None
            relationships = None
            print("⚠️  Not enough topics for clustering/relationships\n")
        
        # Generate enhanced insights
        insights = pulse.generate_community_insights(
            basic_topics,
            clusters,
            relationships
        )
        
        # Display results
        print("="*70)
        print("  � ENHANCED COMMUNITY PULSE REPORT")
        print("="*70)
        print()
        print(f"Target Area: Mumbai")
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
        print(f"  Positive: {sentiment['positive_pct']}%")
        print(f"  Neutral: {sentiment['neutral_pct']}%")
        print(f"  Negative: {sentiment['negative_pct']}%")
        print()
        
        # Topic Clusters (NEW!)
        if clusters and clusters.get('clusters'):
            print("-" * 70)
            print("Topic Clusters (Similar Topics Grouped):")
            print("-" * 70)
            for i, cluster in enumerate(clusters['clusters'][:3], 1):
                print(f"\n  Cluster {i}: {format_topic_name(cluster['main_topic'])}")
                print(f"  Total Mentions: {cluster['total_mentions']}")
                if cluster['related_topics']:
                    print(f"  Related Topics:")
                    for rel in cluster['related_topics'][:2]:
                        print(f"    - {format_topic_name(rel['topic'])} (similarity: {rel['similarity']})")
            print()
        
        # Topic Relationships (NEW!)
        if relationships and relationships.get('relationships'):
            print("-" * 70)
            print("Topic Relationships:")
            print("-" * 70)
            for i, rel in enumerate(relationships['relationships'], 1):
                topic1 = format_topic_name(rel['topic1'])
                topic2 = format_topic_name(rel['topic2'])
                print(f"\n  {i}. {topic1} ↔ {topic2}")
                print(f"     Connection: {rel['connection']}")
                print(f"     Strength: {rel['strength'].upper()}")
            print()
        
        # Trending Topics
        if insights.get('trending_topics'):
            print("-" * 70)
            print("Trending Topics:")
            print("-" * 70)
            for i, topic in enumerate(insights['trending_topics'][:4], 1):
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
                print(f"\n  • {concern['concern'].title()}")
                print(f"    Severity: {concern['severity'].upper()}")
                print(f"    Affected Areas: {', '.join(concern.get('affected_areas', []))}")
                print(f"    Recommendation: {concern['recommendation']}")
        
        print()
        print("-" * 70)
        
        # Save results
        output_file = pulse.save_results(basic_topics, insights)
        
        print()
        print("✅ Enhanced community pulse generated successfully!")
        print(f"💰 Estimated cost: ${pulse.estimated_cost:.6f}")
        print(f"📁 Saved to: agents/data/{output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
