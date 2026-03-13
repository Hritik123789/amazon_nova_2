# -*- coding: utf-8 -*-
"""
Investment Insights Feature
Analyzes development trends and identifies investment hotspots
Uses Amazon Bedrock Nova 2 Lite for trend analysis
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from collections import Counter

# Fix Windows encoding for emojis
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import boto3

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_json_data, save_json_data, log_cost, create_standard_event


# Mumbai neighborhood mapping for granular location extraction
MUMBAI_NEIGHBORHOODS = {
    # Western Suburbs
    'bandra': 'Bandra West',
    'bandra west': 'Bandra West',
    'bandra east': 'Bandra East',
    'andheri': 'Andheri',
    'andheri west': 'Andheri West',
    'andheri east': 'Andheri East',
    'juhu': 'Juhu',
    'versova': 'Versova',
    'goregaon': 'Goregaon',
    'goregaon west': 'Goregaon West',
    'goregaon east': 'Goregaon East',
    'malad': 'Malad',
    'malad west': 'Malad West',
    'malad east': 'Malad East',
    'kandivali': 'Kandivali',
    'borivali': 'Borivali',
    'dahisar': 'Dahisar',
    'jogeshwari': 'Jogeshwari',
    'vile parle': 'Vile Parle',
    'santacruz': 'Santacruz',
    'khar': 'Khar',
    
    # Central Mumbai
    'dadar': 'Dadar',
    'matunga': 'Matunga',
    'mahim': 'Mahim',
    'parel': 'Parel',
    'lower parel': 'Lower Parel',
    'worli': 'Worli',
    'byculla': 'Byculla',
    'chinchpokli': 'Chinchpokli',
    
    # Eastern Suburbs
    'kurla': 'Kurla',
    'ghatkopar': 'Ghatkopar',
    'vikhroli': 'Vikhroli',
    'bhandup': 'Bhandup',
    'mulund': 'Mulund',
    'powai': 'Powai',
    'kanjurmarg': 'Kanjurmarg',
    'chembur': 'Chembur',
    
    # South Mumbai
    'colaba': 'Colaba',
    'fort': 'Fort',
    'churchgate': 'Churchgate',
    'marine lines': 'Marine Lines',
    'nariman point': 'Nariman Point',
    'cuffe parade': 'Cuffe Parade',
    'malabar hill': 'Malabar Hill',
    'breach candy': 'Breach Candy',
    'tardeo': 'Tardeo',
    'grant road': 'Grant Road',
    
    # Navi Mumbai
    'vashi': 'Vashi',
    'nerul': 'Nerul',
    'belapur': 'Belapur',
    'kharghar': 'Kharghar',
    'panvel': 'Panvel',
    'airoli': 'Airoli',
    'ghansoli': 'Ghansoli',
    'kopar khairane': 'Kopar Khairane',
    
    # Thane
    'thane west': 'Thane West',
    'thane east': 'Thane East',
    'ghodbunder': 'Ghodbunder Road',
    'majiwada': 'Majiwada',
    'wagle estate': 'Wagle Estate'
}


class InvestmentInsights:
    """Analyze development trends for investment intelligence"""
    
    @staticmethod
    def normalize_location(location: str) -> str:
        """
        Normalize location strings to extract primary area name
        
        Args:
            location: Raw location string (e.g., "Thane, Mumbai")
            
        Returns:
            Normalized location (e.g., "Thane")
        """
        if not location or location == "Unknown location":
            return "Unknown"
        # Extract first part before comma
        return location.split(",")[0].strip()
    
    @staticmethod
    def extract_neighborhood(text: str) -> Optional[str]:
        """
        Extract specific Mumbai neighborhood from text
        
        Args:
            text: Text containing potential neighborhood name (project name, description, location)
            
        Returns:
            Neighborhood name if found, None otherwise
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Check for neighborhood mentions
        for keyword, neighborhood in MUMBAI_NEIGHBORHOODS.items():
            if keyword in text_lower:
                return neighborhood
        
        return None
    
    def __init__(self, target_area: Optional[str] = None):
        """
        Initialize Investment Insights system
        
        Args:
            target_area: Optional specific area to analyze (e.g., "Andheri West")
        """
        print("💰 Initializing Investment Insights System...\n")
        
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
        permits_data = load_json_data('permits.json', default=[])
        news_data = load_json_data('news.json', default=[])
        
        # Handle both dict and list formats
        def extract_list(data):
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data.get('events', data.get('raw_events', data.get('articles', [])))
            return []
        
        data = {
            "permits": extract_list(permits_data),
            "news": extract_list(news_data)
        }
        
        print(f"   Permit events: {len(data['permits'])}")
        print(f"   News articles: {len(data['news'])}")
        print()
        
        return data
    
    def analyze_development_trends(self, permits: List[Dict], news: List[Dict]) -> Dict:
        """
        Analyze development trends from permits and news
        
        Args:
            permits: List of permit events
            news: List of news articles
            
        Returns:
            Dictionary with trend analysis
        """
        print("📈 Analyzing development trends...")
        
        # Extract and normalize locations from permits
        locations = []
        project_types = []
        
        for permit in permits:
            # Filter locations outside target area
            raw_location = permit.get('location', '')
            if self.target_area.lower() not in raw_location.lower():
                continue
            
            # Try to extract neighborhood from multiple sources
            neighborhood = None
            
            # 1. Check project name
            project_name = permit.get('metadata', {}).get('project_name', '')
            neighborhood = self.extract_neighborhood(project_name)
            
            # 2. Check description if not found
            if not neighborhood:
                description = permit.get('description', '')
                neighborhood = self.extract_neighborhood(description)
            
            # 3. Check raw location
            if not neighborhood:
                neighborhood = self.extract_neighborhood(raw_location)
            
            # 4. Fallback to normalized district-level location
            if not neighborhood:
                neighborhood = self.normalize_location(raw_location)
            
            if neighborhood and neighborhood != "Unknown":
                locations.append(neighborhood)
            
            # Improved project type classification
            event_type = permit.get('event_type', '').lower()
            description = permit.get('description', '').lower()
            
            # Check description first (more specific)
            if 'commercial' in description or 'shop' in description or 'office' in description:
                project_types.append('commercial')
            elif 'residential' in description or 'apartment' in description or 'housing' in description:
                project_types.append('residential')
            elif 'construction' in event_type or 'real_estate' in event_type or 'building' in description:
                project_types.append('real_estate')
            elif 'infrastructure' in description or 'road' in description or 'metro' in description:
                project_types.append('infrastructure')
            else:
                project_types.append('other')
        
        # Count occurrences
        location_counts = Counter(locations)
        project_type_counts = Counter(project_types)
        
        total_permits = len(permits)
        
        # Identify hotspots with growth scores (top 5 locations)
        hotspots = [
            {
                "location": loc,
                "activity_count": count,
                "growth_score": round(count / total_permits, 3) if total_permits > 0 else 0
            }
            for loc, count in location_counts.most_common(5)
        ]
        
        # Project type distribution (sorted by count)
        project_distribution = [
            {"type": ptype, "count": count}
            for ptype, count in project_type_counts.most_common()
        ]
        
        # Extract development signals from news
        development_news_count = 0
        development_keywords = [
            'construction', 'metro', 'infrastructure', 'project', 
            'development', 'building', 'real estate', 'property'
        ]
        
        for article in news:
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            
            # Check if any development keyword is present
            if any(keyword in title or keyword in summary for keyword in development_keywords):
                development_news_count += 1
        
        print(f"   Found {len(hotspots)} development hotspots")
        print(f"   Project types: {len(project_distribution)}")
        print(f"   Development news articles: {development_news_count}")
        print()
        
        return {
            "hotspots": hotspots,
            "project_distribution": project_distribution,
            "total_permits": total_permits,
            "total_locations": len(location_counts),
            "development_news_count": development_news_count
        }
    
    def generate_insights(self, trends: Dict) -> Dict:
        """
        Generate investment insights using Nova 2 Lite
        
        Args:
            trends: Development trend data
            
        Returns:
            Investment insights and recommendations
        """
        print("🤖 Generating investment insights with Nova 2 Lite...")
        
        # Prepare context for Nova
        context = {
            "target_area": self.target_area,
            "hotspots": trends.get('hotspots', []),
            "project_distribution": trends.get('project_distribution', []),
            "total_permits": trends.get('total_permits', 0),
            "development_news_count": trends.get('development_news_count', 0)
        }
        
        prompt = f"""Analyze this Mumbai real estate development data and provide investment insights.

Target Area: {context['target_area']}
Total Development Permits: {context['total_permits']}
Development News Articles: {context['development_news_count']}

Development Hotspots (with growth scores):
{json.dumps(context['hotspots'], indent=2)}

Project Type Distribution:
{json.dumps(context['project_distribution'], indent=2)}

IMPORTANT INSTRUCTIONS:
1. If locations are district-level (Mumbai, Thane, Nagpur), provide specific neighborhood recommendations within those districts
2. For Mumbai, suggest specific neighborhoods like: Bandra West, Andheri East, Powai, Lower Parel, Worli
3. For Thane, suggest: Thane West, Ghodbunder Road, Majiwada
4. Growth score = activity_count / total_permits (higher = more concentrated activity)
5. Focus on actionable, neighborhood-level insights

Provide investment insights in JSON format:
{{
  "hotspot_analysis": [
    {{
      "location": "...",
      "investment_potential": "high/medium/low",
      "reasoning": "...",
      "recommendation": "...",
      "suggested_neighborhoods": ["Specific neighborhood 1", "Specific neighborhood 2"]
    }}
  ],
  "market_trends": {{
    "dominant_sector": "commercial/residential/mixed",
    "growth_indicators": ["..."],
    "risk_factors": ["..."]
  }},
  "investment_recommendations": [
    {{
      "strategy": "...",
      "target_areas": ["Specific neighborhoods, not just cities"],
      "timeframe": "short-term/medium-term/long-term",
      "confidence": "high/medium/low"
    }}
  ]
}}

Consider the growth_score (activity_count / total_permits) when evaluating investment potential.
Higher growth scores indicate concentrated development activity.

Only return the JSON, no other text."""

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
                return self._fallback_insights(trends)
            
        except Exception as e:
            print(f"⚠️  Insight generation failed: {e}\n")
            return self._fallback_insights(trends)
    
    def _fallback_insights(self, trends: Dict) -> Dict:
        """Fallback insights if Nova fails"""
        hotspots = trends.get('hotspots', [])
        project_dist = trends.get('project_distribution', [])
        
        # Simple analysis
        hotspot_analysis = []
        for hotspot in hotspots[:3]:
            hotspot_analysis.append({
                "location": hotspot['location'],
                "investment_potential": "medium",
                "reasoning": f"Active development with {hotspot['activity_count']} permits",
                "recommendation": "Monitor for further development activity"
            })
        
        # Determine dominant sector
        dominant_sector = "mixed"
        if project_dist:
            dominant = max(project_dist, key=lambda x: x['count'])
            dominant_sector = dominant['type']
        
        return {
            "hotspot_analysis": hotspot_analysis,
            "market_trends": {
                "dominant_sector": dominant_sector,
                "growth_indicators": ["Active permit activity", "Multiple projects"],
                "risk_factors": ["Market volatility", "Regulatory changes"]
            },
            "investment_recommendations": [
                {
                    "strategy": "Diversified portfolio approach",
                    "target_areas": [h['location'] for h in hotspots[:3]],
                    "timeframe": "medium-term",
                    "confidence": "medium"
                }
            ]
        }
    
    def save_results(self, trends: Dict, insights: Dict, 
                    output_file: str = "investment_insights.json"):
        """Save investment insights to data/ directory"""
        
        output_data = {
            "generated_at": datetime.now().isoformat(),
            "target_area": self.target_area,
            "trends": trends,
            "insights": insights,
            "metadata": {
                "tokens_used": self.tokens_used,
                "estimated_cost": self.estimated_cost
            }
        }
        
        save_json_data(output_file, output_data)
        
        # Log cost
        log_cost(
            agent_name="investment_insights",
            tokens_used=self.tokens_used,
            estimated_cost=self.estimated_cost,
            model="Amazon Nova 2 Lite",
            operation="trend_analysis"
        )
        
        return output_file


def main():
    """Demo: Generate investment insights for Mumbai"""
    print("="*70)
    print("  💰 INVESTMENT INSIGHTS SYSTEM - Demo")
    print("="*70)
    print()
    
    # Target area (can be customized)
    target_area = "Mumbai"
    
    try:
        # Initialize system
        insights_system = InvestmentInsights(target_area)
        
        # Load data
        data = insights_system.load_data_sources()
        
        # Analyze trends
        trends = insights_system.analyze_development_trends(
            data['permits'],
            data['news']
        )
        
        # Generate insights
        insights = insights_system.generate_insights(trends)
        
        # Display results
        print("="*70)
        print("  📊 INVESTMENT INSIGHTS REPORT")
        print("="*70)
        print()
        print(f"Target Area: {target_area}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Trends Summary
        print("Development Trends:")
        print(f"  Total Permits: {trends['total_permits']}")
        print(f"  Active Locations: {trends['total_locations']}")
        print(f"  Development News: {trends.get('development_news_count', 0)} articles")
        print()
        
        # Hotspots
        if trends['hotspots']:
            print("Top Development Hotspots:")
            for i, hotspot in enumerate(trends['hotspots'][:5], 1):
                growth_pct = hotspot['growth_score'] * 100
                print(f"  {i}. {hotspot['location']} ({hotspot['activity_count']} permits, {growth_pct:.1f}% growth score)")
            print()
        
        # Project Distribution
        if trends['project_distribution']:
            print("Project Type Distribution:")
            for proj in trends['project_distribution']:
                print(f"  - {proj['type'].title()}: {proj['count']}")
            print()
        
        # Investment Insights
        print("-" * 70)
        print("Investment Analysis:")
        print("-" * 70)
        
        # Hotspot Analysis
        if insights.get('hotspot_analysis'):
            print("\nHotspot Investment Potential:")
            for analysis in insights['hotspot_analysis']:
                print(f"\n  📍 {analysis['location']}")
                print(f"     Potential: {analysis['investment_potential'].upper()}")
                print(f"     Reasoning: {analysis['reasoning']}")
                print(f"     Recommendation: {analysis['recommendation']}")
        
        # Market Trends
        if insights.get('market_trends'):
            trends_data = insights['market_trends']
            print(f"\n  📈 Market Trends:")
            print(f"     Dominant Sector: {trends_data.get('dominant_sector', 'N/A').title()}")
            if trends_data.get('growth_indicators'):
                print(f"     Growth Indicators: {', '.join(trends_data['growth_indicators'][:3])}")
            if trends_data.get('risk_factors'):
                print(f"     Risk Factors: {', '.join(trends_data['risk_factors'][:3])}")
        
        # Recommendations
        if insights.get('investment_recommendations'):
            print(f"\n  💡 Investment Recommendations:")
            for i, rec in enumerate(insights['investment_recommendations'], 1):
                print(f"\n     {i}. {rec['strategy']}")
                print(f"        Target Areas: {', '.join(rec.get('target_areas', [])[:3])}")
                print(f"        Timeframe: {rec['timeframe'].title()}")
                print(f"        Confidence: {rec['confidence'].upper()}")
        
        print()
        print("-" * 70)
        
        # Save results
        output_file = insights_system.save_results(trends, insights)
        
        print()
        print("✅ Investment insights generated successfully!")
        print(f"💰 Estimated cost: ${insights_system.estimated_cost:.6f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
