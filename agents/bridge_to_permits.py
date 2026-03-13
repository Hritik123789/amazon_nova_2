"""
Bridge to Permits - Connects News Agent to Permit Monitor Agent
Extracts high-priority permit investigations from analyzed news
"""

import json
import re
import ollama
from typing import List, Dict, Optional
from datetime import datetime


class PermitBridge:
    """Bridge between News Agent and Permit Monitor Agent"""
    
    def __init__(self, use_ollama: bool = True):
        """Initialize bridge with optional Ollama for location/action extraction"""
        self.use_ollama = use_ollama
        self.model = "llama3.1:latest" if use_ollama else None
        
        # Mumbai location patterns
        self.location_keywords = [
            'Andheri', 'Bandra', 'Juhu', 'Thane', 'Goregaon', 'Mulund', 
            'Kandivali', 'Versova', 'Dahisar', 'Kalina', 'Wadala', 
            'Sion', 'Ghatkopar', 'Cuffe Parade', 'Vashi', 'Navi Mumbai',
            'Mumbai', 'Mumbra', 'Raigad', 'MHADA', 'CIDCO'
        ]
    
    def load_analyzed_news(self, filename: str = "news-synthesis/analyzed_news.json") -> List[Dict]:
        """Load analyzed news from News Agent"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            print(f"📰 Loaded {len(articles)} analyzed articles\n")
            return articles
        except FileNotFoundError:
            print(f"❌ {filename} not found!")
            return []
    
    def filter_permit_required(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles that require permit checks"""
        permit_articles = [a for a in articles if a.get('permit_check_required', False)]
        print(f"🔍 Found {len(permit_articles)} articles requiring permit checks\n")
        return permit_articles
    
    def extract_location_simple(self, text: str) -> Optional[str]:
        """Extract location using simple keyword matching"""
        text_lower = text.lower()
        for location in self.location_keywords:
            if location.lower() in text_lower:
                return location
        return "Mumbai (General)"
    
    def extract_location_ai(self, title: str, summary: str) -> Optional[str]:
        """Extract location using Ollama AI"""
        if not self.use_ollama:
            return self.extract_location_simple(title + " " + summary)
        
        try:
            prompt = f"""Extract the specific Mumbai location/area from this news article.

Title: {title}
Summary: {summary}

Return ONLY the location name (e.g., "Bandra", "Thane", "Goregaon"). If no specific location, return "Mumbai (General)"."""

            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            location = response['message']['content'].strip()
            # Clean up the response
            location = location.replace('"', '').replace("'", "").strip()
            return location if location else "Mumbai (General)"
            
        except Exception as e:
            print(f"⚠️  AI extraction failed, using fallback: {str(e)}")
            return self.extract_location_simple(title + " " + summary)
    
    def extract_action_ai(self, title: str, summary: str) -> str:
        """Extract action/project type using Ollama AI"""
        if not self.use_ollama:
            return self.extract_action_simple(title + " " + summary)
        
        try:
            prompt = f"""Identify the type of construction/development action from this news article.

Title: {title}
Summary: {summary}

Choose ONE from: Redevelopment, New Construction, Infrastructure Project, Road Work, Metro Project, Demolition, Renovation, Other

Return ONLY the action type."""

            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            action = response['message']['content'].strip()
            # Clean up the response
            action = action.replace('"', '').replace("'", "").strip()
            return action if action else "Infrastructure Project"
            
        except Exception as e:
            print(f"⚠️  AI extraction failed, using fallback: {str(e)}")
            return self.extract_action_simple(title + " " + summary)
    
    def extract_action_simple(self, text: str) -> str:
        """Extract action using simple keyword matching"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['redevelop', 'redevelopment']):
            return "Redevelopment"
        elif any(word in text_lower for word in ['new building', 'new construction', 'new project']):
            return "New Construction"
        elif any(word in text_lower for word in ['metro', 'underground', 'tunnel']):
            return "Metro Project"
        elif any(word in text_lower for word in ['road', 'highway', 'bridge', 'rob']):
            return "Road Work"
        elif any(word in text_lower for word in ['demolish', 'demolition', 'encroachment']):
            return "Demolition"
        else:
            return "Infrastructure Project"
    
    def enrich_permit_articles(self, articles: List[Dict]) -> List[Dict]:
        """Enrich articles with location and action information"""
        enriched = []
        
        print("🔍 Extracting locations and actions...\n")
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', '')
            summary = article.get('summary', '')
            
            print(f"Processing {i}/{len(articles)}: {title[:60]}...")
            
            # Extract location and action
            location = self.extract_location_ai(title, summary)
            action = self.extract_action_ai(title, summary)
            
            # Add to article
            enriched_article = article.copy()
            enriched_article['location'] = location
            enriched_article['action'] = action
            enriched_article['priority'] = self.calculate_priority(article)
            
            enriched.append(enriched_article)
            
            print(f"  → Location: {location}, Action: {action}, Priority: {enriched_article['priority']}")
        
        print()
        return enriched
    
    def calculate_priority(self, article: Dict) -> str:
        """Calculate investigation priority based on article attributes"""
        relevance = article.get('relevance_score', 5)
        category = article.get('category', '')
        
        if relevance >= 8 and category == 'Real Estate':
            return "HIGH"
        elif relevance >= 7:
            return "MEDIUM"
        else:
            return "LOW"
    
    def mock_rera_check(self, title: str, location: str) -> Dict:
        """Mock RERA agent check for real estate projects"""
        # Simulate RERA database lookup
        mock_rera_data = {
            'rera_registered': False,
            'registration_number': None,
            'developer_name': 'Unknown',
            'project_status': 'Under Investigation',
            'compliance_issues': [],
            'recommendation': 'Requires manual verification'
        }
        
        # Add some intelligence based on keywords
        if 'redevelop' in title.lower():
            mock_rera_data['compliance_issues'].append('Redevelopment project - verify existing tenant rights')
        
        if 'mhada' in title.lower():
            mock_rera_data['compliance_issues'].append('MHADA project - check government approvals')
        
        if 'fraud' in title.lower() or 'illegal' in title.lower():
            mock_rera_data['compliance_issues'].append('⚠️ ALERT: Potential fraud/illegal activity mentioned')
            mock_rera_data['recommendation'] = '🚨 URGENT: Immediate investigation required'
        
        return mock_rera_data
    
    def generate_permit_investigations(self, enriched_articles: List[Dict]) -> List[Dict]:
        """Generate permit investigation tasks for Permit Monitor Agent"""
        investigations = []
        
        for article in enriched_articles:
            investigation = {
                'investigation_id': f"INV-{article['article_number']:03d}",
                'source': 'News Agent',
                'title': article['title'],
                'location': article['location'],
                'action': article['action'],
                'priority': article['priority'],
                'category': article.get('category', 'Unknown'),
                'relevance_score': article.get('relevance_score', 0),
                'news_url': article.get('url', ''),
                'created_at': datetime.now().isoformat(),
                'status': 'Pending Investigation',
                'rera_check': None
            }
            
            # Add RERA check for Real Estate projects
            if article.get('category') == 'Real Estate':
                investigation['rera_check'] = self.mock_rera_check(
                    article['title'], 
                    article['location']
                )
            
            investigations.append(investigation)
        
        return investigations
    
    def print_summary(self, investigations: List[Dict]):
        """Print high-priority investigations summary"""
        print("="*80)
        print("🚨 HIGH PRIORITY INVESTIGATIONS FOR PERMIT MONITOR AGENT")
        print("="*80)
        print()
        
        # Group by priority
        high_priority = [i for i in investigations if i['priority'] == 'HIGH']
        medium_priority = [i for i in investigations if i['priority'] == 'MEDIUM']
        low_priority = [i for i in investigations if i['priority'] == 'LOW']
        
        print(f"📊 Summary:")
        print(f"  Total Investigations: {len(investigations)}")
        print(f"  🔴 High Priority: {len(high_priority)}")
        print(f"  🟡 Medium Priority: {len(medium_priority)}")
        print(f"  🟢 Low Priority: {len(low_priority)}")
        print()
        
        # Print high priority details
        if high_priority:
            print("="*80)
            print("🔴 HIGH PRIORITY INVESTIGATIONS")
            print("="*80)
            for inv in high_priority:
                print(f"\n{inv['investigation_id']}: {inv['title']}")
                print(f"  📍 Location: {inv['location']}")
                print(f"  🏗️  Action: {inv['action']}")
                print(f"  📂 Category: {inv['category']}")
                print(f"  ⭐ Relevance: {inv['relevance_score']}/10")
                
                if inv['rera_check']:
                    print(f"  🏛️  RERA Status: {inv['rera_check']['project_status']}")
                    if inv['rera_check']['compliance_issues']:
                        print(f"  ⚠️  Issues: {', '.join(inv['rera_check']['compliance_issues'])}")
                    print(f"  💡 Recommendation: {inv['rera_check']['recommendation']}")
                
                print(f"  🔗 Source: {inv['news_url']}")
        
        # Print medium priority summary
        if medium_priority:
            print("\n" + "="*80)
            print("🟡 MEDIUM PRIORITY INVESTIGATIONS")
            print("="*80)
            for inv in medium_priority:
                print(f"\n{inv['investigation_id']}: {inv['title'][:70]}...")
                print(f"  📍 {inv['location']} | 🏗️ {inv['action']} | ⭐ {inv['relevance_score']}/10")
        
        # Print low priority summary
        if low_priority:
            print("\n" + "="*80)
            print("🟢 LOW PRIORITY INVESTIGATIONS")
            print("="*80)
            for inv in low_priority:
                print(f"{inv['investigation_id']}: {inv['title'][:70]}... ({inv['location']})")
        
        print("\n" + "="*80)
    
    def save_investigations(self, investigations: List[Dict], filename: str = "permit-monitor/pending_investigations.json"):
        """Save investigations for Permit Monitor Agent"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(investigations, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved {len(investigations)} investigations to {filename}")


def main():
    """Main execution"""
    print("="*80)
    print("🌉 Bridge to Permits - News Agent → Permit Monitor Agent")
    print("="*80)
    print()
    
    # Initialize bridge
    bridge = PermitBridge(use_ollama=True)
    
    # Load analyzed news
    articles = bridge.load_analyzed_news()
    if not articles:
        return
    
    # Filter for permit-required articles
    permit_articles = bridge.filter_permit_required(articles)
    if not permit_articles:
        print("⚠️  No articles require permit checks")
        return
    
    # Enrich with location and action
    enriched = bridge.enrich_permit_articles(permit_articles)
    
    # Generate investigations
    investigations = bridge.generate_permit_investigations(enriched)
    
    # Print summary
    bridge.print_summary(investigations)
    
    # Save for Permit Monitor Agent
    bridge.save_investigations(investigations)
    
    print("\n✅ Bridge complete! Permit Monitor Agent can now process these investigations.")


if __name__ == "__main__":
    main()
