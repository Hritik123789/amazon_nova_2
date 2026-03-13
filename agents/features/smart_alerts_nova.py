# -*- coding: utf-8 -*-
"""
Smart Alerts System
Generates location-based alerts from permits, news, and social data
Uses Amazon Bedrock Nova 2 Lite for alert generation and prioritization
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Fix Windows encoding for emojis
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import boto3

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_json_data, save_json_data, log_cost


class SmartAlerts:
    """Generate smart location-based alerts"""
    
    def __init__(self, user_location: Dict[str, float]):
        """
        Initialize Smart Alerts system
        
        Args:
            user_location: {"latitude": 19.0760, "longitude": 72.8777, "name": "Mumbai"}
        """
        print("🔔 Initializing Smart Alerts System...\n")
        
        self.location = user_location
        self.radius_km = 2  # Alert radius in kilometers
        
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
        """Load all data sources from centralized data/ directory"""
        print("📊 Loading data sources...")
        
        # Load from centralized data directory
        news_data = load_json_data('news.json', default=[])
        permits_data = load_json_data('permits.json', default=[])
        social_data = load_json_data('social.json', default=[])
        
        # Handle both dict and list formats
        def extract_list(data):
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data.get('events', data.get('posts', data.get('articles', [])))
            return []
        
        data = {
            "news": extract_list(news_data),
            "permits": extract_list(permits_data),
            "social": extract_list(social_data)
        }
        
        print(f"   News articles: {len(data['news'])}")
        print(f"   Permit events: {len(data['permits'])}")
        print(f"   Social posts: {len(data['social'])}")
        print()
        
        return data
    
    def generate_alerts(self) -> List[Dict]:
        """Generate all types of alerts"""
        print("🚨 Generating alerts...\n")
        
        # Load data
        data = self.load_data_sources()
        
        # Generate different types of alerts
        alerts = []
        alerts.extend(self.check_new_permits(data['permits']))
        alerts.extend(self.check_new_businesses(data['news']))
        alerts.extend(self.check_safety_issues(data['news'], data['social']))
        alerts.extend(self.check_social_alerts(data['social']))  # NEW: Social media alerts
        
        # Prioritize alerts
        prioritized_alerts = self.prioritize_alerts(alerts)
        
        print(f"✓ Generated {len(prioritized_alerts)} alerts\n")
        
        return prioritized_alerts
    
    def check_new_permits(self, permits: List[Dict]) -> List[Dict]:
        """Check for new permit-related alerts"""
        alerts = []
        
        for permit in permits[:10]:  # Check top 10 permits
            event_type = permit.get('event_type', '').lower()
            description = permit.get('description', '')
            location = permit.get('location', 'Unknown location')
            
            # Real estate projects
            if 'real_estate' in event_type or 'project' in event_type:
                project_name = permit.get('metadata', {}).get('project_name', 'Unknown Project')
                alerts.append({
                    "alert_id": f"permit-{permit.get('metadata', {}).get('registration_number', 'unknown')}",
                    "type": "development",
                    "title": f"New Development: {project_name}",
                    "message": description,
                    "location": location,
                    "priority": "medium",
                    "source": "permit",
                    "timestamp": permit.get('timestamp', datetime.now().isoformat()),
                    "metadata": permit.get('metadata', {})
                })
            
            # Commercial licenses (liquor, restaurant, etc.)
            elif 'liquor' in event_type or 'license' in event_type or 'commercial' in description.lower():
                alerts.append({
                    "alert_id": f"permit-commercial-{len(alerts)}",
                    "type": "new_business",
                    "title": "New Commercial Activity",
                    "message": description,
                    "location": location,
                    "priority": "low",
                    "source": "permit",
                    "timestamp": permit.get('timestamp', datetime.now().isoformat())
                })
        
        return alerts
    
    def check_new_businesses(self, news: List[Dict]) -> List[Dict]:
        """Check news for new business openings"""
        alerts = []
        
        for article in news[:10]:
            title = article.get('title', '').lower()
            category = article.get('category', '')
            
            # Look for business/restaurant keywords
            if any(keyword in title for keyword in ['opening', 'new', 'launch', 'restaurant', 'shop']):
                alerts.append({
                    "alert_id": f"news-{article.get('article_number', 'unknown')}",
                    "type": "new_business",
                    "title": article.get('title', 'New Business'),
                    "message": article.get('summary', 'Check local news for details'),
                    "location": self.location.get('name', 'Mumbai'),
                    "priority": "medium",
                    "source": "news",
                    "url": article.get('url', ''),
                    "timestamp": datetime.now().isoformat()
                })
        
        return alerts
    
    def check_safety_issues(self, news: List[Dict], social: List[Dict]) -> List[Dict]:
        """Check for safety-related alerts"""
        alerts = []
        
        # Check news for safety issues
        for article in news[:15]:  # Increased from 10 to 15
            title = article.get('title', '').lower()
            category = article.get('category', '')
            
            if category == 'Traffic' or any(keyword in title for keyword in ['closure', 'accident', 'traffic', 'road', 'delay', 'disruption']):
                alerts.append({
                    "alert_id": f"safety-news-{article.get('article_number', len(alerts))}",
                    "type": "safety",
                    "title": "Traffic/Safety Alert",
                    "message": article.get('title', 'Safety issue detected'),
                    "location": self.location.get('name', 'Mumbai'),
                    "priority": "high",
                    "source": "news",
                    "url": article.get('url', ''),
                    "timestamp": datetime.now().isoformat()
                })
        
        return alerts
    
    def check_social_alerts(self, social: List[Dict]) -> List[Dict]:
        """
        Check social media for high-engagement posts that warrant alerts
        
        Args:
            social: List of social media posts
            
        Returns:
            List of social media alerts
        """
        alerts = []
        
        # Filter for high-engagement posts (>50 upvotes or >10 comments)
        for post in social:
            engagement = post.get('engagement', {})
            upvotes = engagement.get('upvotes', 0)
            comments = engagement.get('comments', 0)
            score = engagement.get('score', 0)
            
            # High engagement threshold
            if upvotes > 50 or comments > 10 or score > 100:
                sentiment = post.get('sentiment', 'neutral')
                title = post.get('title', 'Community Discussion')
                
                # Determine alert type based on sentiment and content
                alert_type = "community"
                priority = "medium"
                
                if sentiment == 'negative':
                    alert_type = "concern"
                    priority = "medium"
                elif sentiment == 'positive':
                    alert_type = "opportunity"
                    priority = "low"
                
                alerts.append({
                    "alert_id": f"social-{post.get('id', len(alerts))}",
                    "type": alert_type,
                    "title": f"Trending: {title[:60]}...",
                    "message": post.get('summary', post.get('content', '')[:150]),
                    "location": self.location.get('name', 'Mumbai'),
                    "priority": priority,
                    "source": "social",
                    "url": post.get('url', ''),
                    "timestamp": post.get('timestamp', datetime.now().isoformat()),
                    "engagement": {
                        "upvotes": upvotes,
                        "comments": comments,
                        "score": score
                    },
                    "sentiment": sentiment
                })
        
        return alerts
    
    def prioritize_alerts(self, alerts: List[Dict]) -> List[Dict]:
        """
        Prioritize and score alerts using Nova 2 Lite
        
        Args:
            alerts: List of raw alerts
            
        Returns:
            Sorted list of alerts with priority scores
        """
        if not alerts:
            return []
        
        print("🤖 Prioritizing alerts with Nova 2 Lite...")
        
        # Prepare alerts for Nova
        alert_summaries = []
        for i, alert in enumerate(alerts[:10]):  # Limit to 10 for cost control
            alert_summaries.append({
                "index": i,
                "type": alert['type'],
                "title": alert['title'],
                "priority": alert.get('priority', 'medium')
            })
        
        prompt = f"""Analyze these alerts for a Mumbai resident and assign priority scores (1-10, where 10 is most urgent).

Location: {self.location.get('name', 'Mumbai')}
Alerts:
{json.dumps(alert_summaries, indent=2)}

Consider:
- Safety/Traffic alerts: 8-10 (highest priority)
- Community concerns (negative sentiment): 6-8
- Development projects: 5-7
- New business openings: 4-6
- Community opportunities (positive sentiment): 3-5

Return a JSON array with format: [{{"index": 0, "score": 8, "reason": "Safety concern"}}]
Only return the JSON array, no other text."""

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
                        "max_new_tokens": 500,
                        "temperature": 0.3
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
            json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
            if json_match:
                scores = json.loads(json_match.group())
                
                # Apply scores to alerts
                for score_data in scores:
                    idx = score_data['index']
                    if idx < len(alerts):
                        alerts[idx]['priority_score'] = score_data['score']
                        alerts[idx]['priority_reason'] = score_data.get('reason', '')
            
            print("✓ Prioritization complete\n")
            
        except Exception as e:
            print(f"⚠️  Prioritization failed, using defaults: {e}\n")
            # Fallback: assign default scores
            for alert in alerts:
                if alert['type'] == 'safety':
                    alert['priority_score'] = 9
                elif alert['type'] == 'new_business':
                    alert['priority_score'] = 6
                else:
                    alert['priority_score'] = 5
        
        # Sort by priority score (highest first)
        sorted_alerts = sorted(alerts, key=lambda x: x.get('priority_score', 5), reverse=True)
        
        return sorted_alerts
    
    def save_alerts(self, alerts: List[Dict], output_file: str = "smart_alerts.json"):
        """Save alerts to centralized data/ directory"""
        
        output_data = {
            "generated_at": datetime.now().isoformat(),
            "user_location": self.location,
            "alert_count": len(alerts),
            "alerts": alerts,
            "metadata": {
                "tokens_used": self.tokens_used,
                "estimated_cost": self.estimated_cost
            }
        }
        
        save_json_data(output_file, output_data)
        
        # Log cost
        log_cost(
            agent_name="smart_alerts",
            tokens_used=self.tokens_used,
            estimated_cost=self.estimated_cost,
            model="Amazon Nova 2 Lite",
            operation="alert_prioritization"
        )
        
        return output_file


def main():
    """Demo: Generate smart alerts for Mumbai user"""
    print("="*70)
    print("  🔔 SMART ALERTS SYSTEM - Demo")
    print("="*70)
    print()
    
    # Example user location (Mumbai)
    user_location = {
        "latitude": 19.0760,
        "longitude": 72.8777,
        "name": "Mumbai"
    }
    
    try:
        # Initialize system
        alerts_system = SmartAlerts(user_location)
        
        # Generate alerts
        alerts = alerts_system.generate_alerts()
        
        # Display results
        print("="*70)
        print("  📋 GENERATED ALERTS")
        print("="*70)
        print()
        
        if alerts:
            print(f"Total alerts: {len(alerts)}\n")
            
            # Show top 5 alerts
            for i, alert in enumerate(alerts[:5], 1):
                print(f"{i}. [{alert['type'].upper()}] {alert['title']}")
                print(f"   Priority Score: {alert.get('priority_score', 'N/A')}/10")
                print(f"   Message: {alert['message'][:80]}...")
                print(f"   Source: {alert['source']}")
                print()
        else:
            print("No alerts generated")
        
        # Save to file
        output_file = alerts_system.save_alerts(alerts)
        
        print()
        print("✅ Smart alerts generated successfully!")
        print(f"💰 Estimated cost: ${alerts_system.estimated_cost:.6f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
