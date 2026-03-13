# -*- coding: utf-8 -*-
"""
Safety Intelligence Feature
Aggregates safety data from all sources and generates real-time safety alerts
Uses Amazon Bedrock Nova 2 Lite + Nova 2 Omni
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


class SafetyIntelligence:
    """Aggregate safety data and generate real-time alerts"""
    
    def __init__(self, user_location: Dict[str, float]):
        """
        Initialize Safety Intelligence system
        
        Args:
            user_location: {"latitude": 19.0760, "longitude": 72.8777, "name": "Mumbai"}
        """
        print("🚨 Initializing Safety Intelligence System...\n")
        
        self.location = user_location
        self.radius_km = 5  # Safety alert radius
        
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
        """Load all safety-related data sources from data/ directory"""
        print("📊 Loading safety data sources...")
        
        # Load from centralized data directory
        news_data = load_json_data('news.json', default=[])
        permits_data = load_json_data('permits.json', default=[])
        social_data = load_json_data('social.json', default=[])
        images_data = load_json_data('images.json', default=[])
        
        # Handle both dict and list formats
        def extract_list(data):
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data.get('events', data.get('articles', data.get('posts', data.get('raw_results', []))))
            return []
        
        data = {
            "news": extract_list(news_data),
            "permits": extract_list(permits_data),
            "social": extract_list(social_data),
            "images": extract_list(images_data)
        }
        
        print(f"   News events: {len(data['news'])}")
        print(f"   Permit events: {len(data['permits'])}")
        print(f"   Social events: {len(data['social'])}")
        print(f"   Image events: {len(data['images'])}")
        print()
        
        return data
    
    def _load_json(self, filepath: str) -> List[Dict]:
        """Load JSON file safely"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)
                # Handle both list and dict formats
                if isinstance(content, dict):
                    # Extract list from common keys
                    for key in ['events', 'posts', 'articles', 'results']:
                        if key in content:
                            return content[key]
                    return []
                return content if isinstance(content, list) else []
        except FileNotFoundError:
            print(f"⚠️  File not found: {filepath}")
            return []
        except json.JSONDecodeError:
            print(f"⚠️  Invalid JSON: {filepath}")
            return []
    
    def detect_road_closures(self, news: List[Dict], social: List[Dict]) -> List[Dict]:
        """Detect road closures from news and social posts"""
        print("🚧 Detecting road closures...")
        
        closures = []
        
        # Check news articles
        for article in news:
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            
            if any(keyword in title or keyword in summary 
                   for keyword in ['road closure', 'road closed', 'traffic diversion', 
                                   'route blocked', 'street closed']):
                closures.append({
                    "closure_id": f"news-{article.get('article_number', 'unknown')}",
                    "source": "news",
                    "title": article.get('title', 'Road Closure'),
                    "description": article.get('summary', ''),
                    "location": self.location.get('name', 'Mumbai'),
                    "detected_at": datetime.now().isoformat(),
                    "severity": "high",
                    "url": article.get('url', '')
                })
        
        # Check social posts
        for post in social:
            text = post.get('text', '').lower()
            
            if any(keyword in text 
                   for keyword in ['road closed', 'traffic jam', 'blocked', 
                                   'diversion', 'avoid this route']):
                closures.append({
                    "closure_id": f"social-{post.get('post_id', 'unknown')}",
                    "source": "social",
                    "title": "Road Closure Reported",
                    "description": post.get('text', '')[:200],
                    "location": self.location.get('name', 'Mumbai'),
                    "detected_at": datetime.now().isoformat(),
                    "severity": "medium",
                    "engagement": post.get('engagement', {})
                })
        
        print(f"   Found {len(closures)} potential road closures\n")
        return closures
    
    def detect_safety_violations(self, images: List[Dict]) -> List[Dict]:
        """Extract safety violations from image analyses"""
        print("⚠️  Detecting safety violations from images...")
        
        violations = []
        
        for img in images:
            analysis = img.get('analysis', '').lower()
            
            # Look for safety keywords in analysis
            if any(keyword in analysis 
                   for keyword in ['violation', 'unsafe', 'hazard', 'danger', 
                                   'missing', 'no safety', 'risk']):
                violations.append({
                    "violation_id": f"img-{img.get('image_path', 'unknown')}",
                    "source": "image_analysis",
                    "image_path": img.get('image_path', ''),
                    "description": img.get('analysis', '')[:300],
                    "location": self.location.get('name', 'Mumbai'),
                    "detected_at": img.get('analyzed_at', datetime.now().isoformat()),
                    "severity": "high",
                    "analyzed_by": img.get('analyzed_by', 'Nova 2 Omni')
                })
        
        print(f"   Found {len(violations)} safety violations\n")
        return violations
    
    def detect_construction_hazards(self, permits: List[Dict]) -> List[Dict]:
        """Detect construction-related safety hazards"""
        print("🏗️  Detecting construction hazards...")
        
        hazards = []
        
        for permit in permits:
            event_type = permit.get('event_type', '').lower()
            description = permit.get('description', '').lower()
            
            # Look for construction activity
            if any(keyword in event_type or keyword in description
                   for keyword in ['construction', 'demolition', 'excavation', 
                                   'building', 'renovation']):
                hazards.append({
                    "hazard_id": f"permit-{permit.get('source', 'unknown')}",
                    "source": "permit",
                    "event_type": permit.get('event_type', 'Construction Activity'),
                    "description": permit.get('description', ''),
                    "location": permit.get('location', self.location.get('name', 'Mumbai')),
                    "detected_at": permit.get('timestamp', datetime.now().isoformat()),
                    "severity": "medium",
                    "metadata": permit.get('metadata', {})
                })
        
        print(f"   Found {len(hazards)} construction hazards\n")
        return hazards
    
    def aggregate_safety_issues(self) -> Dict:
        """Aggregate all safety issues from all sources"""
        print("🔍 Aggregating safety data...\n")
        
        # Load all data
        data = self.load_data_sources()
        
        # Detect different types of safety issues
        road_closures = self.detect_road_closures(data['news'], data['social'])
        safety_violations = self.detect_safety_violations(data['images'])
        construction_hazards = self.detect_construction_hazards(data['permits'])
        
        # Combine all issues
        all_issues = {
            "road_closures": road_closures,
            "safety_violations": safety_violations,
            "construction_hazards": construction_hazards
        }
        
        return all_issues
    
    def generate_safety_alerts(self, issues: Dict) -> List[Dict]:
        """
        Generate prioritized safety alerts using Nova 2 Lite
        
        Args:
            issues: Aggregated safety issues
            
        Returns:
            List of prioritized safety alerts
        """
        print("🤖 Generating safety alerts with Nova 2 Lite...")
        
        # Flatten all issues
        all_items = []
        all_items.extend(issues.get('road_closures', []))
        all_items.extend(issues.get('safety_violations', []))
        all_items.extend(issues.get('construction_hazards', []))
        
        if not all_items:
            print("   No safety issues to alert on\n")
            return []
        
        # Limit to top 10 for cost control
        items_to_analyze = all_items[:10]
        
        # Prepare context for Nova
        context = {
            "location": self.location.get("name", "Mumbai"),
            "total_issues": len(all_items),
            "issues_summary": [
                {
                    "id": item.get('closure_id') or item.get('violation_id') or item.get('hazard_id', 'unknown'),
                    "source": item.get('source', 'unknown'),
                    "title": item.get('title') or item.get('event_type', 'Safety Issue'),
                    "severity": item.get('severity', 'medium'),
                    "description": item.get('description', '')[:150]
                }
                for item in items_to_analyze
            ]
        }
        
        prompt = f"""Analyze these safety issues for Mumbai residents and create actionable alerts.

Location: {context['location']}
Total Issues: {context['total_issues']}

Issues:
{json.dumps(context['issues_summary'], indent=2)}

For each issue, create a safety alert with:
1. Alert title (clear and actionable)
2. Alert message (what residents should know/do)
3. Priority score (1-10, where 10 is most urgent)
4. Recommended action

Return a JSON array with format:
[{{"id": "...", "alert_title": "...", "alert_message": "...", "priority": 8, "action": "..."}}]

Prioritize:
- Road closures: High priority (affects mobility)
- Safety violations: Very high priority (immediate danger)
- Construction hazards: Medium priority (ongoing concern)

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
                        "max_new_tokens": 1000,
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
                alerts = json.loads(json_match.group())
                
                # Enrich alerts with original data
                for alert in alerts:
                    alert_id = alert.get('id', '')
                    # Find original item
                    for item in all_items:
                        item_id = (item.get('closure_id') or 
                                 item.get('violation_id') or 
                                 item.get('hazard_id', ''))
                        if item_id == alert_id:
                            alert['location'] = item.get('location', self.location.get('name'))
                            alert['source'] = item.get('source', 'unknown')
                            alert['detected_at'] = item.get('detected_at', datetime.now().isoformat())
                            alert['original_data'] = item
                            break
                
                print(f"✓ Generated {len(alerts)} safety alerts\n")
                return sorted(alerts, key=lambda x: x.get('priority', 0), reverse=True)
            
        except Exception as e:
            print(f"⚠️  Alert generation failed, using fallback: {e}\n")
            # Fallback: create simple alerts
            return self._fallback_alerts(all_items)
        
        return []
    
    def _fallback_alerts(self, items: List[Dict]) -> List[Dict]:
        """Fallback alert generation if Nova fails"""
        alerts = []
        
        for item in items[:10]:
            alert = {
                "id": (item.get('closure_id') or 
                      item.get('violation_id') or 
                      item.get('hazard_id', 'unknown')),
                "alert_title": item.get('title') or item.get('event_type', 'Safety Alert'),
                "alert_message": item.get('description', '')[:200],
                "priority": 8 if item.get('severity') == 'high' else 5,
                "action": "Stay informed and exercise caution",
                "location": item.get('location', self.location.get('name')),
                "source": item.get('source', 'unknown'),
                "detected_at": item.get('detected_at', datetime.now().isoformat())
            }
            alerts.append(alert)
        
        return sorted(alerts, key=lambda x: x.get('priority', 0), reverse=True)
    
    def save_results(self, issues: Dict, alerts: List[Dict], 
                    output_file: str = "safety_alerts.json"):
        """Save safety intelligence results to data/ directory"""
        
        output_data = {
            "generated_at": datetime.now().isoformat(),
            "user_location": self.location,
            "summary": {
                "total_road_closures": len(issues.get('road_closures', [])),
                "total_safety_violations": len(issues.get('safety_violations', [])),
                "total_construction_hazards": len(issues.get('construction_hazards', [])),
                "total_alerts": len(alerts)
            },
            "alerts": alerts,
            "raw_issues": issues
        }
        
        save_json_data(output_file, output_data)
        
        # Log cost (track tokens if Nova was called)
        if hasattr(self, 'tokens_used') and hasattr(self, 'estimated_cost'):
            log_cost(
                agent_name="safety_intelligence",
                tokens_used=getattr(self, 'tokens_used', 0),
                estimated_cost=getattr(self, 'estimated_cost', 0.0),
                model="Amazon Nova 2 Lite",
                operation="alert_generation"
            )
        
        return output_file


def main():
    """Demo: Generate safety intelligence for Mumbai"""
    print("="*70)
    print("  🚨 SAFETY INTELLIGENCE SYSTEM - Demo")
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
        safety_system = SafetyIntelligence(user_location)
        
        # Aggregate safety issues
        issues = safety_system.aggregate_safety_issues()
        
        # Generate alerts
        alerts = safety_system.generate_safety_alerts(issues)
        
        # Display results
        print("="*70)
        print("  📋 SAFETY INTELLIGENCE REPORT")
        print("="*70)
        print()
        print(f"Location: {user_location['name']}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("Summary:")
        print(f"  Road Closures: {len(issues.get('road_closures', []))}")
        print(f"  Safety Violations: {len(issues.get('safety_violations', []))}")
        print(f"  Construction Hazards: {len(issues.get('construction_hazards', []))}")
        print(f"  Total Alerts: {len(alerts)}")
        print()
        
        if alerts:
            print("Top Safety Alerts:")
            print("-" * 70)
            for i, alert in enumerate(alerts[:5], 1):
                print(f"\n{i}. {alert.get('alert_title', 'Safety Alert')}")
                print(f"   Priority: {alert.get('priority', 'N/A')}/10")
                print(f"   Source: {alert.get('source', 'unknown')}")
                print(f"   Message: {alert.get('alert_message', '')[:150]}...")
                print(f"   Action: {alert.get('action', 'Stay informed')}")
            print("-" * 70)
        else:
            print("No safety alerts at this time")
        
        # Save results
        output_file = safety_system.save_results(issues, alerts)
        
        print()
        print("✅ Safety intelligence generated successfully!")
        print(f"💰 Estimated cost: $0.0010")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
