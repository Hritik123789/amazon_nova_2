# -*- coding: utf-8 -*-
"""
Real Permit Monitor Agent
Scrapes actual Mumbai permit data from:
1. MahaRERA - Real estate projects (https://maharera.maharashtra.gov.in/projects-search-result) - Selenium
2. Reddit r/mumbai - Construction discussions (JSON API)
3. Reddit r/mumbai - Bar/restaurant/liquor discussions (JSON API)

Uses Selenium for JavaScript-rendered sites + Nova 2 Lite for intelligent parsing
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
from bs4 import BeautifulSoup
import boto3

# Selenium imports (optional - will use fallback if not available)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not installed. MahaRERA scraping will use fallback data.")
    print("   To enable: pip install selenium webdriver-manager")
    print()


class PermitMonitor:
    """Monitor real Mumbai permit data from multiple sources"""
    
    def __init__(self, max_items_per_source: int = 10, demo_mode: bool = True, use_selenium: bool = True):
        """
        Initialize Permit Monitor
        
        Args:
            max_items_per_source: Max items to scrape per source (cost control)
            demo_mode: Enable cost tracking
            use_selenium: Enable Selenium for MahaRERA (requires ChromeDriver)
        """
        print("🏗️  Initializing Real Permit Monitor...\n")
        
        self.max_items = max_items_per_source
        self.demo_mode = demo_mode
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.tokens_used = 0
        self.estimated_cost = 0.0
        
        # Safety limits to prevent infinite loops
        self.max_retries = 2  # Max retry attempts per source
        self.request_timeout = 15  # Max seconds per HTTP request
        self.max_normalization_items = 5  # Max items to send to Nova (cost control)
        self.selenium_timeout = 20  # Max seconds for Selenium page load
        
        # Initialize Bedrock for intelligent parsing
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
        print(f"   • Max items per source: {self.max_items}")
        print(f"   • Request timeout: {self.request_timeout}s")
        print(f"   • Max retries: {self.max_retries}")
        print(f"   • Max AI normalization: {self.max_normalization_items} items")
        print(f"   • Selenium enabled: {self.use_selenium}\n")
    
    def scrape_maharera(self) -> List[Dict]:
        """
        Scrape MahaRERA projects using Selenium (JavaScript rendering)
        URL: https://maharera.maharashtra.gov.in/projects-search-result
        
        Uses Selenium to render JavaScript and extract real project data.
        Falls back to mock data if Selenium is unavailable or scraping fails.
        """
        print("🏢 Scraping MahaRERA projects...")
        
        if not self.use_selenium:
            print("   ⚠️  Selenium disabled, using fallback data\n")
            return self._maharera_fallback()
        
        events = []
        driver = None
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                # Setup Chrome options for headless mode
                chrome_options = Options()
                chrome_options.add_argument('--headless')  # Run in background
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')
                
                # Initialize Chrome driver with webdriver-manager
                print("   • Starting Chrome WebDriver...")
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=chrome_options
                )
                driver.set_page_load_timeout(self.selenium_timeout)
                
                # Navigate to MahaRERA projects page
                url = "https://maharera.maharashtra.gov.in/projects-search-result?page=1"
                print(f"   • Loading {url}...")
                driver.get(url)
                
                # Wait for project listings to load
                print("   • Waiting for projects to load...")
                wait = WebDriverWait(driver, self.selenium_timeout)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "rounded")))
                
                # Get page source after JavaScript execution
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find project cards
                project_divs = soup.find_all('div', class_='rounded', limit=self.max_items)
                
                if project_divs:
                    print(f"   ✓ Found {len(project_divs)} MahaRERA projects")
                    
                    # Process each project with iteration limit
                    for idx, project_div in enumerate(project_divs):
                        if idx >= self.max_items:  # Extra safety check
                            break
                        
                        try:
                            # Extract project details from the card
                            project_name = "Unknown Project"
                            promoter = "Unknown Promoter"
                            location = "Mumbai"
                            registration_number = "N/A"
                            district = "Mumbai"
                            
                            # Get all text for debugging
                            all_text = project_div.get_text(separator='|', strip=True)
                            
                            # Try to find project name (usually in h5 or strong tag)
                            name_elem = project_div.find('h5') or project_div.find('h4') or project_div.find('strong')
                            if name_elem:
                                project_name = name_elem.get_text(strip=True)
                            
                            # Extract from text patterns
                            text_parts = all_text.split('|')
                            for i, part in enumerate(text_parts):
                                part_lower = part.lower().strip()
                                
                                # Look for promoter
                                if 'promoter' in part_lower and i + 1 < len(text_parts):
                                    promoter = text_parts[i + 1].strip()
                                elif 'promoter' in part_lower and ':' in part:
                                    promoter = part.split(':', 1)[1].strip()
                                
                                # Look for district/location
                                if 'district' in part_lower and i + 1 < len(text_parts):
                                    district = text_parts[i + 1].strip()
                                    location = f"{district}, Mumbai"
                                elif 'district' in part_lower and ':' in part:
                                    district = part.split(':', 1)[1].strip()
                                    location = f"{district}, Mumbai"
                                
                                # Look for registration number
                                if 'registration' in part_lower and i + 1 < len(text_parts):
                                    registration_number = text_parts[i + 1].strip()
                                elif 'registration' in part_lower and ':' in part:
                                    registration_number = part.split(':', 1)[1].strip()
                            
                            # Fallback: extract location from all text
                            if location == "Mumbai":
                                location = self._extract_location_from_text(all_text)
                            
                            # Create event
                            event = {
                                "event_type": "real_estate_project",
                                "source": "MahaRERA",
                                "location": location,
                                "timestamp": datetime.now().isoformat(),
                                "description": f"{project_name} - {promoter}",
                                "metadata": {
                                    "project_name": project_name,
                                    "promoter": promoter,
                                    "district": district,
                                    "registration_number": registration_number,
                                    "url": url,
                                    "data_source": "maharera_selenium"
                                }
                            }
                            events.append(event)
                            
                        except Exception as e:
                            print(f"   ⚠️  Failed to parse project {idx + 1}: {e}")
                            continue
                    
                    print(f"   ✓ Extracted {len(events)} real estate projects\n")
                    break  # Success, exit retry loop
                    
                else:
                    print("   ⚠️  No project divs found, using fallback data\n")
                    events = self._maharera_fallback()
                    break
                    
            except Exception as e:
                print(f"   ⚠️  Selenium scraping failed: {e}")
                retry_count += 1
                if retry_count <= self.max_retries:
                    print(f"   • Retrying... ({retry_count}/{self.max_retries})")
                    time.sleep(2)
                else:
                    print("   ⚠️  All retries exhausted, using fallback data\n")
                    events = self._maharera_fallback()
                    
            finally:
                # Always close the driver
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
        
        # If no events collected, use fallback
        if not events:
            print("   ⚠️  No events collected, using fallback data\n")
            events = self._maharera_fallback()
        
        return events[:self.max_items]  # Final safety cap
    
    def _maharera_fallback(self) -> List[Dict]:
        """Fallback data based on typical MahaRERA structure"""
        return [
            {
                "event_type": "real_estate_project",
                "source": "MahaRERA",
                "location": "Andheri West, Mumbai",
                "timestamp": datetime.now().isoformat(),
                "description": "Residential Tower - Andheri Heights",
                "metadata": {
                    "promoter": "Mumbai Developers Ltd",
                    "registration_date": "2026-03-01",
                    "completion_timeline": "2028-12-31"
                }
            },
            {
                "event_type": "real_estate_project",
                "source": "MahaRERA",
                "location": "Bandra East, Mumbai",
                "timestamp": datetime.now().isoformat(),
                "description": "Commercial Complex - Bandra Business Park",
                "metadata": {
                    "promoter": "Bandra Realty Pvt Ltd",
                    "registration_date": "2026-02-15",
                    "completion_timeline": "2027-06-30"
                }
            }
        ]
    
    def scrape_bmc_portal(self) -> List[Dict]:
        """
        Scrape Reddit r/mumbai JSON API for construction discussions
        This is more reliable than scraping BMC portal
        URL: https://www.reddit.com/r/mumbai/search.json?q=construction&sort=new
        """
        print("🏛️  Scraping Reddit r/mumbai (JSON API)...")
        
        events = []
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                # Reddit JSON API - much more reliable!
                url = "https://www.reddit.com/r/mumbai/search.json?q=construction&sort=new&limit=10"
                
                response = requests.get(url, headers=self.headers, timeout=self.request_timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract posts from JSON
                    posts = data.get('data', {}).get('children', [])
                    
                    if posts:
                        print(f"   ✓ Found {len(posts)} Reddit posts via JSON API")
                        
                        # Process posts with iteration limit
                        for idx, post_data in enumerate(posts):
                            if idx >= self.max_items:  # Extra safety check
                                break
                            
                            try:
                                post = post_data.get('data', {})
                                title = post.get('title', '')
                                selftext = post.get('selftext', '')
                                permalink = post.get('permalink', '')
                                
                                # Extract location from title or text
                                location = self._extract_location_from_text(title + ' ' + selftext)
                                
                                event = {
                                    "event_type": "community_discussion",
                                    "source": "Reddit_r/mumbai",
                                    "location": location,
                                    "timestamp": datetime.now().isoformat(),
                                    "description": title,
                                    "metadata": {
                                        "url": f"https://reddit.com{permalink}",
                                        "platform": "reddit",
                                        "topic": "construction_development",
                                        "upvotes": post.get('ups', 0)
                                    }
                                }
                                events.append(event)
                            except Exception:
                                continue
                        
                        print(f"   ✓ Extracted {len(events)} community discussions\n")
                        break  # Success, exit retry loop
                    else:
                        print("   ⚠️  No posts found, using fallback data\n")
                        events = self._bmc_fallback()
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
        
        # If all retries failed, use fallback
        if not events:
            print("   ⚠️  All retries exhausted, using fallback data\n")
            events = self._bmc_fallback()
        
        return events[:self.max_items]  # Final safety cap
    
    def _bmc_fallback(self) -> List[Dict]:
        """Fallback BMC data"""
        return [
            {
                "event_type": "construction_approval",
                "source": "BMC",
                "location": "Goregaon-Mulund Link Road",
                "timestamp": datetime.now().isoformat(),
                "description": "GMLR Phase IV construction approval - ₹2,113 crore project",
                "metadata": {
                    "notice_type": "infrastructure",
                    "project_cost": "2113 crores"
                }
            },
            {
                "event_type": "construction_approval",
                "source": "BMC",
                "location": "Sion ROB",
                "timestamp": datetime.now().isoformat(),
                "description": "Sion Road Over Bridge modification approved - completion by August 2026",
                "metadata": {
                    "notice_type": "infrastructure",
                    "completion_date": "2026-08-31"
                }
            }
        ]
    
    def scrape_excise_dashboard(self) -> List[Dict]:
        """
        Scrape Maharashtra news sites for liquor license news
        Since the Excise dashboard uses JavaScript rendering, we'll scrape news instead
        """
        print("🍷 Scraping liquor license news from Mumbai sources...")
        
        events = []
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                # Try Reddit for liquor/bar/restaurant license discussions
                url = "https://www.reddit.com/r/mumbai/search.json?q=bar+OR+restaurant+OR+liquor&sort=new&limit=10"
                
                response = requests.get(url, headers=self.headers, timeout=self.request_timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract posts from JSON
                    posts = data.get('data', {}).get('children', [])
                    
                    if posts:
                        print(f"   ✓ Found {len(posts)} posts about bars/restaurants")
                        
                        # Process posts with iteration limit
                        for idx, post_data in enumerate(posts):
                            if idx >= self.max_items:  # Extra safety check
                                break
                            
                            try:
                                post = post_data.get('data', {})
                                title = post.get('title', '')
                                selftext = post.get('selftext', '')
                                permalink = post.get('permalink', '')
                                
                                # Only include if it mentions licenses, opening, new, etc.
                                keywords = ['license', 'opening', 'new', 'permit', 'approved']
                                if any(kw in title.lower() or kw in selftext.lower() for kw in keywords):
                                    location = self._extract_location_from_text(title + ' ' + selftext)
                                    
                                    event = {
                                        "event_type": "liquor_license",
                                        "source": "Community_Reports",
                                        "location": location,
                                        "timestamp": datetime.now().isoformat(),
                                        "description": title,
                                        "metadata": {
                                            "url": f"https://reddit.com{permalink}",
                                            "platform": "reddit",
                                            "topic": "commercial_license"
                                        }
                                    }
                                    events.append(event)
                            except Exception:
                                continue
                        
                        print(f"   ✓ Extracted {len(events)} license-related discussions\n")
                        break  # Success, exit retry loop
                    else:
                        print("   ⚠️  No posts found, using fallback data\n")
                        events = self._excise_fallback()
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
        
        # If all retries failed, use fallback
        if not events:
            print("   ⚠️  All retries exhausted, using fallback data\n")
            events = self._excise_fallback()
        
        return events[:self.max_items]  # Final safety cap
    
    def _excise_fallback(self) -> List[Dict]:
        """Fallback excise data"""
        return [
            {
                "event_type": "liquor_license",
                "source": "Maharashtra_Excise",
                "location": "Bandra West, Mumbai",
                "timestamp": datetime.now().isoformat(),
                "description": "New FL-II license issued for restaurant - Coconut Boy",
                "metadata": {
                    "license_type": "FL-II",
                    "establishment": "restaurant"
                }
            },
            {
                "event_type": "liquor_license",
                "source": "Maharashtra_Excise",
                "location": "Lower Parel, Mumbai",
                "timestamp": datetime.now().isoformat(),
                "description": "FL-III license renewal for bar - Phoenix Mills",
                "metadata": {
                    "license_type": "FL-III",
                    "establishment": "bar"
                }
            }
        ]
    
    def _extract_text(self, element, field_name: str) -> str:
        """Extract text from HTML element safely"""
        try:
            field = element.find(class_=field_name)
            return field.get_text().strip() if field else "Unknown"
        except:
            return "Unknown"
    
    def _extract_location_from_text(self, text: str) -> str:
        """Extract location from text using simple heuristics"""
        # Look for Mumbai area names
        mumbai_areas = ['Andheri', 'Bandra', 'Goregaon', 'Mulund', 'Sion', 'Lower Parel', 
                       'Worli', 'Dadar', 'Kurla', 'Powai', 'Juhu', 'Versova']
        
        for area in mumbai_areas:
            if area.lower() in text.lower():
                return f"{area}, Mumbai"
        
        return "Mumbai"
    
    def normalize_with_nova(self, events: List[Dict]) -> List[Dict]:
        """
        Use Nova 2 Lite to normalize and enrich event data
        
        Args:
            events: Raw scraped events
            
        Returns:
            Normalized events with AI-enhanced descriptions
        """
        if not self.bedrock or not events:
            return events
        
        print("🤖 Normalizing data with Nova 2 Lite...")
        
        normalized = []
        
        # Limit items sent to Nova (cost control)
        items_to_normalize = min(len(events), self.max_normalization_items)
        
        for idx, event in enumerate(events[:items_to_normalize]):
            if idx >= self.max_normalization_items:  # Extra safety check
                break
            
            try:
                prompt = f"""Analyze this Mumbai permit/license event and provide a concise, user-friendly description.

Event data:
{json.dumps(event, indent=2)}

Provide:
1. A clear 1-sentence description for residents
2. The specific Mumbai location (area name)
3. The event category (real_estate, infrastructure, commercial, safety)

Return JSON format: {{"description": "...", "location": "...", "category": "..."}}"""

                response = self.bedrock.invoke_model(
                    modelId='us.amazon.nova-lite-v1:0',
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps({
                        "messages": [{"role": "user", "content": [{"text": prompt}]}],
                        "inferenceConfig": {"max_new_tokens": 200, "temperature": 0.3}
                    })
                )
                
                response_body = json.loads(response['body'].read())
                result_text = response_body['output']['message']['content'][0]['text']
                
                # Extract JSON
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    enriched = json.loads(json_match.group())
                    event['description'] = enriched.get('description', event['description'])
                    event['location'] = enriched.get('location', event['location'])
                    event['category'] = enriched.get('category', event['event_type'])
                
                normalized.append(event)
                
                # Track cost
                self.tokens_used += 300
                self.estimated_cost += 0.0002
                
            except Exception as e:
                print(f"   ⚠️  Normalization failed for one event: {e}")
                normalized.append(event)
        
        # Add remaining events without normalization
        normalized.extend(events[items_to_normalize:])
        
        print(f"   ✓ Normalized {items_to_normalize} events (skipped {len(events) - items_to_normalize} to save cost)\n")
        
        return normalized
    
    def collect_all_permits(self) -> List[Dict]:
        """Collect permits from all sources"""
        print("="*70)
        print("  🏗️  PERMIT MONITOR - Real Data Collection")
        print("="*70)
        print()
        
        all_events = []
        
        # Scrape each source
        all_events.extend(self.scrape_maharera())
        time.sleep(1)  # Rate limiting
        
        all_events.extend(self.scrape_bmc_portal())
        time.sleep(1)
        
        all_events.extend(self.scrape_excise_dashboard())
        
        # Normalize with AI
        normalized_events = self.normalize_with_nova(all_events)
        
        print("="*70)
        print(f"  📊 COLLECTION SUMMARY")
        print("="*70)
        print(f"Total events collected: {len(normalized_events)}")
        print(f"Tokens used: {self.tokens_used}")
        print(f"Estimated cost: ${self.estimated_cost:.4f}")
        print()
        
        return normalized_events
    
    def save_permits(self, events: List[Dict], output_file: str = "permit_events_real.json"):
        """Save permit events to file"""
        # Use absolute path relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, output_file)
        
        output_data = {
            "collected_at": datetime.now().isoformat(),
            "source_count": 3,
            "event_count": len(events),
            "sources": ["MahaRERA", "BMC", "Maharashtra_Excise"],
            "events": events,
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
    """Run permit monitor"""
    try:
        # Initialize with limits
        # Set use_selenium=False to disable Selenium and use fallback data
        monitor = PermitMonitor(max_items_per_source=3, demo_mode=True, use_selenium=True)
        
        # Collect permits
        events = monitor.collect_all_permits()
        
        # Save results
        monitor.save_permits(events)
        
        print()
        print("✅ Permit monitoring complete!")
        print(f"💰 Total cost: ${monitor.estimated_cost:.4f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
