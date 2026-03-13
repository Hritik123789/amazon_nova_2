# -*- coding: utf-8 -*-
"""
BMC Ward-Level Permit Monitor
Monitors Mumbai BMC building permits by ward with structured permit stage tracking.

Focuses on:
- Ward-level monitoring (e.g., Ward A, Ward K-West)
- Permit stages: IOD, CC, BCC/OCC
- Structured insights for CityPulse platform
- Deduplication and caching
- Neighborhood impact tagging

Designed for hackathon prototype - limited to 1-2 wards to avoid rate limits.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import hashlib

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import boto3

# Add parent directory to path for cache manager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cache_manager import get_cache_manager


class BMCWardMonitor:
    """Monitor BMC building permits by ward with structured tracking"""
    
    # Mumbai BMC Wards (24 wards total, focusing on key areas)
    WARDS = {
        'A': {'name': 'Colaba', 'neighborhoods': ['Colaba', 'Cuffe Parade', 'Navy Nagar']},
        'B': {'name': 'Dongri', 'neighborhoods': ['Dongri', 'Bhuleshwar', 'Kalbadevi']},
        'C': {'name': 'Mandvi', 'neighborhoods': ['Mandvi', 'Mazgaon', 'Dockyard Road']},
        'D': {'name': 'Tardeo', 'neighborhoods': ['Tardeo', 'Grant Road', 'Charni Road']},
        'E': {'name': 'Byculla', 'neighborhoods': ['Byculla', 'Agripada', 'Nagpada']},
        'F-North': {'name': 'Matunga', 'neighborhoods': ['Matunga', 'Sion', 'Dharavi']},
        'F-South': {'name': 'Parel', 'neighborhoods': ['Parel', 'Lower Parel', 'Elphinstone']},
        'G-North': {'name': 'Dadar', 'neighborhoods': ['Dadar', 'Mahim', 'Shivaji Park']},
        'G-South': {'name': 'Worli', 'neighborhoods': ['Worli', 'Prabhadevi', 'Sewri']},
        'H-East': {'name': 'Bandra East', 'neighborhoods': ['Bandra East', 'Kalanagar']},
        'H-West': {'name': 'Bandra West', 'neighborhoods': ['Bandra West', 'Khar West']},
        'K-East': {'name': 'Andheri East', 'neighborhoods': ['Andheri East', 'Chakala', 'MIDC']},
        'K-West': {'name': 'Andheri West', 'neighborhoods': ['Andheri West', 'Versova', 'Lokhandwala']},
        'L': {'name': 'Kurla', 'neighborhoods': ['Kurla', 'Sakinaka', 'Chandivali']},
        'M-East': {'name': 'Chembur', 'neighborhoods': ['Chembur', 'Tilak Nagar']},
        'M-West': {'name': 'Mankhurd', 'neighborhoods': ['Mankhurd', 'Govandi']},
        'N': {'name': 'Ghatkopar', 'neighborhoods': ['Ghatkopar', 'Vikhroli']},
        'P-North': {'name': 'Goregaon', 'neighborhoods': ['Goregaon', 'Malad', 'Kandivali']},
        'P-South': {'name': 'Jogeshwari', 'neighborhoods': ['Jogeshwari', 'Vile Parle']},
        'R-Central': {'name': 'Borivali', 'neighborhoods': ['Borivali', 'Dahisar']},
        'S': {'name': 'Bhandup', 'neighborhoods': ['Bhandup', 'Mulund', 'Kanjurmarg']},
        'T': {'name': 'Mulund', 'neighborhoods': ['Mulund', 'Nahur']},
    }
    
    # Ward coordinates (approximate center points for map visualization)
    WARD_COORDINATES = {
        'A': {'lat': 18.9067, 'lon': 72.8147},  # Colaba
        'B': {'lat': 18.9558, 'lon': 72.8347},  # Dongri
        'C': {'lat': 18.9697, 'lon': 72.8456},  # Mandvi
        'D': {'lat': 18.9697, 'lon': 72.8156},  # Tardeo
        'E': {'lat': 18.9761, 'lon': 72.8339},  # Byculla
        'F-North': {'lat': 19.0270, 'lon': 72.8570},  # Matunga
        'F-South': {'lat': 19.0089, 'lon': 72.8386},  # Parel
        'G-North': {'lat': 19.0176, 'lon': 72.8462},  # Dadar
        'G-South': {'lat': 19.0176, 'lon': 72.8186},  # Worli
        'H-East': {'lat': 19.0596, 'lon': 72.8656},  # Bandra East
        'H-West': {'lat': 19.0596, 'lon': 72.8295},  # Bandra West
        'K-East': {'lat': 19.1136, 'lon': 72.8697},  # Andheri East
        'K-West': {'lat': 19.1350, 'lon': 72.8250},  # Andheri West
        'L': {'lat': 19.0728, 'lon': 72.8826},  # Kurla
        'M-East': {'lat': 19.0633, 'lon': 72.8997},  # Chembur
        'M-West': {'lat': 19.0433, 'lon': 72.9233},  # Mankhurd
        'N': {'lat': 19.0864, 'lon': 72.9081},  # Ghatkopar
        'P-North': {'lat': 19.1653, 'lon': 72.8497},  # Goregaon
        'P-South': {'lat': 19.1350, 'lon': 72.8497},  # Jogeshwari
        'R-Central': {'lat': 19.2304, 'lon': 72.8581},  # Borivali
        'S': {'lat': 19.1439, 'lon': 72.9342},  # Bhandup
        'T': {'lat': 19.1728, 'lon': 72.9564},  # Mulund
    }
    
    # Permit stages
    PERMIT_STAGES = {
        'IOD': 'Intimation of Disapproval',
        'CC': 'Commencement Certificate',
        'BCC': 'Building Completion Certificate',
        'OCC': 'Occupancy Certificate'
    }
    
    # Project types
    PROJECT_TYPES = [
        'Residential',
        'Commercial',
        'Mixed Use',
        'Industrial',
        'Institutional',
        'Infrastructure'
    ]
    
    def __init__(self, target_wards: List[str] = None, demo_mode: bool = True, use_cache: bool = True):
        """
        Initialize BMC Ward Monitor
        
        Args:
            target_wards: List of ward codes to monitor (e.g., ['K-West', 'H-West'])
            demo_mode: Enable cost tracking
            use_cache: Use caching to avoid repeated scraping
        """
        print("🏛️  Initializing BMC Ward Monitor...\n")
        
        # Default to monitoring 2 wards for hackathon prototype
        self.target_wards = target_wards or ['K-West', 'H-West']
        self.demo_mode = demo_mode
        self.use_cache = use_cache
        self.tokens_used = 0
        self.estimated_cost = 0.0
        
        # Validate wards
        for ward in self.target_wards:
            if ward not in self.WARDS:
                print(f"⚠️  Warning: Ward '{ward}' not recognized")
        
        # Initialize cache
        if self.use_cache:
            self.cache = get_cache_manager()
            self.processed_permits_file = os.path.join(
                os.path.dirname(__file__),
                '.processed_permits.json'
            )
            self.processed_permits = self._load_processed_permits()
        else:
            self.cache = None
            self.processed_permits = set()
        
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
        
        print(f"📍 Monitoring wards: {', '.join(self.target_wards)}")
        print(f"💾 Caching: {'ENABLED' if self.use_cache else 'DISABLED'}")
        print(f"🔍 Deduplication: {'ENABLED' if self.use_cache else 'DISABLED'}")
        print()
    
    def _load_processed_permits(self) -> Set[str]:
        """Load set of already processed permit IDs"""
        try:
            if os.path.exists(self.processed_permits_file):
                with open(self.processed_permits_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_ids', []))
        except Exception as e:
            print(f"⚠️  Could not load processed permits: {e}")
        return set()
    
    def _save_processed_permits(self):
        """Save processed permit IDs"""
        try:
            with open(self.processed_permits_file, 'w') as f:
                json.dump({
                    'processed_ids': list(self.processed_permits),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save processed permits: {e}")
    
    def _generate_permit_id(self, permit_data: Dict) -> str:
        """Generate unique ID for permit based on key fields"""
        # Create hash from ward + project name + location
        key_str = f"{permit_data.get('ward', '')}_{permit_data.get('project_name', '')}_{permit_data.get('location', '')}"
        return hashlib.md5(key_str.encode()).hexdigest()[:16]
    
    def _is_duplicate(self, permit_id: str) -> bool:
        """Check if permit has already been processed"""
        return permit_id in self.processed_permits
    
    def _mark_as_processed(self, permit_id: str):
        """Mark permit as processed"""
        self.processed_permits.add(permit_id)
    
    def scrape_ward_permits(self, ward_code: str) -> List[Dict]:
        """
        Scrape permits for a specific ward
        
        Note: Since BMC AutoDCR portal requires authentication and has rate limits,
        this implementation uses simulated data based on typical BMC permit patterns.
        
        In production, this would integrate with BMC AutoDCR API or scrape the portal.
        
        Args:
            ward_code: Ward code (e.g., 'K-West')
            
        Returns:
            List of permit dictionaries
        """
        print(f"📋 Scraping permits for Ward {ward_code} ({self.WARDS.get(ward_code, {}).get('name', 'Unknown')})...")
        
        # Check cache first
        if self.use_cache and self.cache:
            cache_key = f"bmc_ward_{ward_code}"
            cached_data = self.cache.get(cache_key, ttl_hours=12)  # 12-hour cache for permits
            
            if cached_data:
                print(f"   💾 Using cached data for Ward {ward_code}")
                return cached_data
        
        # Simulate BMC permit data (in production, this would scrape BMC AutoDCR)
        permits = self._generate_simulated_permits(ward_code)
        
        # Cache the results
        if self.use_cache and self.cache:
            cache_key = f"bmc_ward_{ward_code}"
            self.cache.set(cache_key, permits)
        
        print(f"   ✓ Found {len(permits)} permits in Ward {ward_code}\n")
        return permits
    
    def _generate_simulated_permits(self, ward_code: str) -> List[Dict]:
        """
        Generate simulated permit data based on typical BMC patterns
        
        In production, replace this with actual BMC AutoDCR scraping
        """
        ward_info = self.WARDS.get(ward_code, {})
        neighborhoods = ward_info.get('neighborhoods', ['Unknown'])
        ward_coords = self.WARD_COORDINATES.get(ward_code, {'lat': 19.0760, 'lon': 72.8777})
        
        # Simulate 3-5 permits per ward
        permits = []
        
        # Example permit patterns
        permit_templates = [
            {
                'permit_stage': 'CC',
                'project_type': 'Residential',
                'project_name': f'Residential Tower - {neighborhoods[0]}',
                'status': 'Approved',
                'floors': 15,
                'units': 45,
                'impact': 'New residential tower construction expected in the area'
            },
            {
                'permit_stage': 'IOD',
                'project_type': 'Commercial',
                'project_name': f'Commercial Complex - {neighborhoods[0]}',
                'status': 'Filed',
                'floors': 8,
                'units': 20,
                'impact': 'New commercial development planned'
            },
            {
                'permit_stage': 'BCC',
                'project_type': 'Mixed Use',
                'project_name': f'Mixed Use Development - {neighborhoods[0]}',
                'status': 'Completed',
                'floors': 20,
                'units': 60,
                'impact': 'Mixed-use building nearing completion'
            }
        ]
        
        for i, template in enumerate(permit_templates):
            neighborhood = neighborhoods[i % len(neighborhoods)]
            
            # Create metadata first
            metadata = {
                'floors': template['floors'],
                'units': template['units'],
                'estimated_completion': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
            }
            
            permit = {
                'ward': ward_code,
                'ward_name': ward_info.get('name', 'Unknown'),
                'location': neighborhood,
                'permit_stage': template['permit_stage'],
                'permit_stage_full': self.PERMIT_STAGES[template['permit_stage']],
                'project_type': template['project_type'],
                'project_name': template['project_name'],
                'status': template['status'],
                'date_detected': datetime.now().strftime('%Y-%m-%d'),
                'metadata': metadata,
                'impact_summary': template['impact'],
                'neighborhood_impact': self._assess_neighborhood_impact({
                    'permit_stage': template['permit_stage'],
                    'project_type': template['project_type'],
                    'metadata': metadata
                }),
                'geo': ward_coords.copy(),  # Add geolocation
                'timeline_stage': self._get_timeline_stage(template['permit_stage']),  # Add timeline
                'agent_metadata': {
                    'agent': 'permit_monitor',
                    'source': 'BMC Ward Monitor',
                    'confidence': 0.85,
                    'version': '2.0'
                }
            }
            
            # Calculate impact score
            permit['impact_score'] = self._calculate_impact_score(permit)
            
            permits.append(permit)
        
        return permits
    
    def _assess_neighborhood_impact(self, permit_data: Dict) -> List[str]:
        """
        Assess potential neighborhood impact of permit
        
        Args:
            permit_data: Permit information
            
        Returns:
            List of impact tags
        """
        impacts = []
        
        # Construction impact
        if permit_data['permit_stage'] in ['CC', 'IOD']:
            impacts.append('construction')
        
        # Housing impact
        if permit_data['project_type'] in ['Residential', 'Mixed Use']:
            impacts.append('new_housing')
        
        # Commercial impact
        if permit_data['project_type'] in ['Commercial', 'Mixed Use']:
            impacts.append('commercial_development')
        
        # Large project impact - FIX: Read floors from metadata
        floors = permit_data.get('metadata', {}).get('floors', 0)
        if floors > 10:
            impacts.append('high_rise')
        
        return impacts
    
    def _calculate_impact_score(self, permit: Dict) -> int:
        """
        Calculate development impact score (1-10) using Python logic
        
        Scoring rules:
        - +3 if permit_stage == "CC" (construction starting)
        - +2 if project_type == "Commercial"
        - +2 if floors > 10
        - +1 if project_type == "Mixed Use"
        - +1 if units > 40
        
        Args:
            permit: Permit dictionary
            
        Returns:
            Impact score (1-10)
        """
        score = 0
        
        # Construction starting (high impact)
        if permit.get('permit_stage') == 'CC':
            score += 3
        
        # Commercial development
        if permit.get('project_type') == 'Commercial':
            score += 2
        
        # High-rise building
        metadata = permit.get('metadata', {})
        floors = metadata.get('floors', 0)
        if floors > 10:
            score += 2
        
        # Mixed use
        if permit.get('project_type') == 'Mixed Use':
            score += 1
        
        # Large project (many units)
        units = metadata.get('units', 0)
        if units > 40:
            score += 1
        
        # Ensure score is between 1 and 10
        score = max(1, min(10, score))
        
        return score
    
    def _get_timeline_stage(self, permit_stage: str) -> str:
        """
        Classify permit into timeline category
        
        Args:
            permit_stage: Permit stage code (IOD, CC, BCC, OCC)
            
        Returns:
            Timeline stage description
        """
        timeline_map = {
            'IOD': 'Planning',
            'CC': 'Construction Starting',
            'BCC': 'Near Completion',
            'OCC': 'Completed'
        }
        return timeline_map.get(permit_stage, 'Unknown')
    
    def enrich_with_nova(self, permits: List[Dict]) -> List[Dict]:
        """
        Use Nova 2 Lite to enrich permit data with insights
        
        Args:
            permits: Raw permit data
            
        Returns:
            Enriched permits with AI-generated insights
        """
        if not self.bedrock or not permits:
            return permits
        
        print("🤖 Enriching permits with Nova 2 Lite...")
        
        enriched = []
        
        # Limit AI enrichment to save costs (max 5 permits)
        permits_to_enrich = min(len(permits), 5)
        
        for idx, permit in enumerate(permits[:permits_to_enrich]):
            try:
                prompt = f"""Analyze this Mumbai BMC building permit and provide insights for residents:

Permit Details:
- Ward: {permit['ward']} ({permit['ward_name']})
- Location: {permit['location']}
- Stage: {permit['permit_stage_full']}
- Type: {permit['project_type']}
- Project: {permit['project_name']}
- Status: {permit['status']}

Provide:
1. A resident-friendly summary (1 sentence)
2. Potential impact on the neighborhood (traffic, amenities, property values)
3. Timeline estimate

Return JSON: {{"summary": "...", "impact": "...", "timeline": "..."}}"""

                response = self.bedrock.invoke_model(
                    modelId='us.amazon.nova-lite-v1:0',
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps({
                        "messages": [{"role": "user", "content": [{"text": prompt}]}],
                        "inferenceConfig": {"max_new_tokens": 250, "temperature": 0.5}
                    })
                )
                
                response_body = json.loads(response['body'].read())
                result_text = response_body['output']['message']['content'][0]['text']
                
                # Extract JSON
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    insights = json.loads(json_match.group())
                    permit['ai_summary'] = insights.get('summary', permit['impact_summary'])
                    permit['ai_impact'] = insights.get('impact', '')
                    permit['ai_timeline'] = insights.get('timeline', '')
                
                enriched.append(permit)
                
                # Track cost
                self.tokens_used += 350
                self.estimated_cost += 0.0003
                
            except Exception as e:
                print(f"   ⚠️  Enrichment failed for permit {idx + 1}: {e}")
                enriched.append(permit)
        
        # Add remaining permits without enrichment
        enriched.extend(permits[permits_to_enrich:])
        
        print(f"   ✓ Enriched {permits_to_enrich} permits (skipped {len(permits) - permits_to_enrich} to save cost)\n")
        
        return enriched
    
    def deduplicate_permits(self, permits: List[Dict]) -> List[Dict]:
        """
        Remove duplicate permits that have already been processed
        
        Args:
            permits: List of permits
            
        Returns:
            Deduplicated list of permits
        """
        if not self.use_cache:
            return permits
        
        print("🔍 Deduplicating permits...")
        
        new_permits = []
        duplicate_count = 0
        
        for permit in permits:
            permit_id = self._generate_permit_id(permit)
            
            if not self._is_duplicate(permit_id):
                permit['permit_id'] = permit_id
                new_permits.append(permit)
                self._mark_as_processed(permit_id)
            else:
                duplicate_count += 1
        
        print(f"   ✓ Found {len(new_permits)} new permits ({duplicate_count} duplicates filtered)\n")
        
        # Save processed permits
        if new_permits:
            self._save_processed_permits()
        
        return new_permits
    
    def analyze_development_trends(self, permits: List[Dict]) -> Dict:
        """
        Analyze development trends per ward using Python logic (no LLM calls)
        
        Args:
            permits: List of permits
            
        Returns:
            Dictionary with trend analysis per ward
        """
        print("📊 Analyzing development trends...")
        
        trends_by_ward = {}
        
        # Group permits by ward
        permits_by_ward = {}
        for permit in permits:
            ward = permit['ward']
            if ward not in permits_by_ward:
                permits_by_ward[ward] = []
            permits_by_ward[ward].append(permit)
        
        # Analyze each ward
        for ward, ward_permits in permits_by_ward.items():
            # Count by project type
            type_counts = {}
            for permit in ward_permits:
                ptype = permit['project_type']
                type_counts[ptype] = type_counts.get(ptype, 0) + 1
            
            # Count by permit stage
            stage_counts = {}
            for permit in ward_permits:
                stage = permit['permit_stage']
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
            
            # Calculate ratios
            total = len(ward_permits)
            residential_count = type_counts.get('Residential', 0)
            commercial_count = type_counts.get('Commercial', 0)
            
            residential_ratio = round(residential_count / total, 2) if total > 0 else 0
            commercial_ratio = round(commercial_count / total, 2) if total > 0 else 0
            
            # Calculate construction activity score (1-10)
            # Based on: CC permits (active construction), total permits, high-rise count
            cc_count = stage_counts.get('CC', 0)
            high_rise_count = sum(1 for p in ward_permits if 'high_rise' in p.get('neighborhood_impact', []))
            
            construction_activity_score = min(10, (cc_count * 3) + (total // 2) + high_rise_count)
            construction_activity_score = max(1, construction_activity_score)
            
            # Find top project type
            top_type = max(type_counts.items(), key=lambda x: x[1]) if type_counts else ('Unknown', 0)
            
            # Find dominant stage
            top_stage = max(stage_counts.items(), key=lambda x: x[1]) if stage_counts else ('Unknown', 0)
            
            # Generate trend description
            ward_name = self.WARDS.get(ward, {}).get('name', ward)
            trend_description = self._generate_trend_description(
                ward, ward_name, top_type, top_stage, len(ward_permits), type_counts, stage_counts
            )
            
            trends_by_ward[ward] = {
                'ward': ward,
                'ward_name': ward_name,
                'permit_count': len(ward_permits),
                'top_project_type': top_type[0],
                'top_project_type_count': top_type[1],
                'top_permit_stage': top_stage[0],
                'top_permit_stage_count': top_stage[1],
                'residential_ratio': residential_ratio,
                'commercial_ratio': commercial_ratio,
                'construction_activity_score': construction_activity_score,
                'project_type_breakdown': type_counts,
                'permit_stage_breakdown': stage_counts,
                'trend': trend_description
            }
        
        print(f"   ✓ Analyzed trends for {len(trends_by_ward)} wards\n")
        
        return trends_by_ward
    
    def _generate_trend_description(self, ward: str, ward_name: str, top_type: tuple, 
                                    top_stage: tuple, total_permits: int, 
                                    type_counts: Dict, stage_counts: Dict) -> str:
        """
        Generate human-readable trend description using Python logic
        
        Args:
            ward: Ward code
            ward_name: Ward name
            top_type: (type_name, count) tuple
            top_stage: (stage_name, count) tuple
            total_permits: Total permit count
            type_counts: Project type breakdown
            stage_counts: Permit stage breakdown
            
        Returns:
            Trend description string
        """
        type_name, type_count = top_type
        stage_name, stage_count = top_stage
        
        # Calculate percentages
        type_percentage = (type_count / total_permits * 100) if total_permits > 0 else 0
        
        # Determine trend intensity
        if type_percentage >= 60:
            intensity = "strong"
        elif type_percentage >= 40:
            intensity = "moderate"
        else:
            intensity = "emerging"
        
        # Build description based on top type and stage
        descriptions = []
        
        # Primary trend (project type)
        if type_name == 'Residential':
            if intensity == "strong":
                descriptions.append(f"Strong residential expansion in {ward_name}")
            else:
                descriptions.append(f"Residential development increasing in {ward_name}")
        elif type_name == 'Commercial':
            descriptions.append(f"Commercial development {intensity}ly growing in {ward_name}")
        elif type_name == 'Mixed Use':
            descriptions.append(f"Mixed-use projects driving development in {ward_name}")
        else:
            descriptions.append(f"{type_name} development active in {ward_name}")
        
        # Add stage context
        if stage_name == 'CC' and stage_count >= 2:
            descriptions.append(f"{stage_count} projects starting construction")
        elif stage_name == 'BCC' and stage_count >= 2:
            descriptions.append(f"{stage_count} projects nearing completion")
        elif stage_name == 'IOD' and stage_count >= 2:
            descriptions.append(f"{stage_count} projects under review")
        
        # Add diversity note if multiple types
        if len(type_counts) >= 3:
            descriptions.append("diverse project portfolio")
        
        return ". ".join(descriptions) + "."
    
    def monitor_wards(self) -> tuple:
        """
        Monitor all target wards and collect permits
        
        Returns:
            Tuple of (new_permits, all_permits, development_trends)
        """
        print("="*70)
        print("  🏛️  BMC WARD MONITOR - Structured Permit Tracking")
        print("="*70)
        print()
        
        all_permits = []
        
        # Scrape each ward
        for ward_code in self.target_wards:
            permits = self.scrape_ward_permits(ward_code)
            all_permits.extend(permits)
        
        # Deduplicate
        new_permits = self.deduplicate_permits(all_permits)
        
        # Analyze development trends (Python logic only - no LLM cost)
        development_trends = self.analyze_development_trends(all_permits)
        
        # Enrich with AI (only for new permits)
        enriched_permits = self.enrich_with_nova(new_permits)
        
        print("="*70)
        print(f"  📊 MONITORING SUMMARY")
        print("="*70)
        print(f"Wards monitored: {len(self.target_wards)}")
        print(f"Total permits found: {len(all_permits)}")
        print(f"New permits: {len(new_permits)}")
        print(f"Duplicates filtered: {len(all_permits) - len(new_permits)}")
        print(f"Tokens used: {self.tokens_used}")
        print(f"Estimated cost: ${self.estimated_cost:.4f}")
        print()
        
        return enriched_permits, all_permits, development_trends
    
    def save_permits(self, permits: List[Dict], development_trends: Dict, output_file: str = None):
        """
        Save permits and development trends to JSON file
        
        Args:
            permits: List of permits
            development_trends: Development trend analysis per ward
            output_file: Output filename (default: bmc_ward_permits.json)
        """
        if output_file is None:
            output_file = "bmc_ward_permits.json"
        
        # Use absolute path relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, output_file)
        
        # Group by ward
        permits_by_ward = {}
        for permit in permits:
            ward = permit['ward']
            if ward not in permits_by_ward:
                permits_by_ward[ward] = []
            permits_by_ward[ward].append(permit)
        
        # Calculate statistics
        stats = {
            'total_permits': len(permits),
            'by_ward': {ward: len(perms) for ward, perms in permits_by_ward.items()},
            'by_stage': {},
            'by_type': {},
            'by_status': {}
        }
        
        for permit in permits:
            stage = permit['permit_stage']
            ptype = permit['project_type']
            status = permit['status']
            
            stats['by_stage'][stage] = stats['by_stage'].get(stage, 0) + 1
            stats['by_type'][ptype] = stats['by_type'].get(ptype, 0) + 1
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        # Convert development_trends dict to list for JSON
        development_summary = list(development_trends.values())
        
        output_data = {
            'collected_at': datetime.now().isoformat(),
            'wards_monitored': self.target_wards,
            'permit_count': len(permits),
            'statistics': stats,
            'development_summary': development_summary,
            'permits': permits,
            'cost_tracking': {
                'tokens_used': self.tokens_used,
                'estimated_cost': self.estimated_cost
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved to: {output_path}")
        
        # Also save to centralized data directory
        data_dir = os.path.join(os.path.dirname(script_dir), 'data')
        if os.path.exists(data_dir):
            data_output_path = os.path.join(data_dir, 'bmc_permits.json')
            with open(data_output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Also saved to: {data_output_path}")
        
        return output_path
    
    def generate_insights_for_agents(self, permits: List[Dict]) -> Dict:
        """
        Generate structured insights for other CityPulse agents
        
        Args:
            permits: List of permits
            
        Returns:
            Insights dictionary for investment, community, and alert agents
        """
        insights = {
            'investment_opportunities': [],
            'community_alerts': [],
            'development_trends': []
        }
        
        for permit in permits:
            # Investment insights
            if permit['project_type'] in ['Residential', 'Mixed Use'] and permit['status'] in ['Approved', 'Filed']:
                insights['investment_opportunities'].append({
                    'location': permit['location'],
                    'ward': permit['ward'],
                    'type': 'new_development',
                    'description': f"{permit['project_name']} - {permit['permit_stage_full']}",
                    'impact': permit['impact_summary']
                })
            
            # Community alerts
            if permit['permit_stage'] == 'CC' and permit['status'] == 'Approved':
                insights['community_alerts'].append({
                    'location': permit['location'],
                    'ward': permit['ward'],
                    'type': 'construction_starting',
                    'description': f"Construction starting: {permit['project_name']}",
                    'impact_tags': permit['neighborhood_impact']
                })
            
            # Development trends
            insights['development_trends'].append({
                'ward': permit['ward'],
                'project_type': permit['project_type'],
                'permit_stage': permit['permit_stage'],
                'date': permit['date_detected']
            })
        
        return insights


def main():
    """Run BMC Ward Monitor"""
    try:
        print("="*70)
        print("BMC Ward Monitor - Structured Permit Tracking")
        print("="*70)
        print()

        # Initialize monitor for 2 wards (hackathon prototype)
        monitor = BMCWardMonitor(
            target_wards=['K-West', 'H-West'],
            demo_mode=True,
            use_cache=True
        )

        # Monitor wards
        new_permits, all_permits, development_trends = monitor.monitor_wards()
        
        # For display: use all permits (including cached ones)
        display_permits = all_permits
        
        # Save results (only if there are new permits)
        if new_permits:
            monitor.save_permits(new_permits, development_trends)
        
        # Generate insights for other agents (use new permits only)
        insights = monitor.generate_insights_for_agents(new_permits) if new_permits else {
            'investment_opportunities': [],
            'community_alerts': [],
            'development_trends': []
        }

        print()
        print("="*70)
        print("📊 INSIGHTS FOR CITYPULSE AGENTS")
        print("="*70)
        print(f"Investment opportunities: {len(insights['investment_opportunities'])}")
        print(f"Community alerts: {len(insights['community_alerts'])}")
        print(f"Development trends: {len(insights['development_trends'])}")
        print()

        # Display development trends
        if development_trends:
            print("="*70)
            print("📈 DEVELOPMENT TRENDS")
            print("="*70)
            for ward_code, trend_data in development_trends.items():
                print(f"\n{ward_code} - {trend_data['ward_name']}")
                print(f"  Permits: {trend_data['permit_count']}")
                print(f"  Top Type: {trend_data['top_project_type']} ({trend_data['top_project_type_count']})")
                print(f"  Top Stage: {trend_data['top_permit_stage']} ({trend_data['top_permit_stage_count']})")
                print(f"  Residential Ratio: {trend_data['residential_ratio']}")
                print(f"  Commercial Ratio: {trend_data['commercial_ratio']}")
                print(f"  Construction Activity: {trend_data['construction_activity_score']}/10")
                print(f"  Trend: {trend_data['trend']}")

        # Display sample permits (use cached data if no new permits)
        if display_permits:
            print()
            print("="*70)
            print("📋 SAMPLE PERMITS" + (" (from cache)" if len(new_permits) == 0 else ""))
            print("="*70)
            for permit in display_permits[:3]:
                print(f"\n{permit['ward']} - {permit['location']}")
                print(f"  Stage: {permit['permit_stage_full']}")
                print(f"  Type: {permit['project_type']}")
                print(f"  Status: {permit['status']}")
                print(f"  Impact Score: {permit.get('impact_score', 'N/A')}/10")
                print(f"  Timeline: {permit.get('timeline_stage', 'N/A')}")
                print(f"  Impact: {permit['impact_summary']}")
        else:
            print("\n⚠️  No permits available for display")

        print()
        print("✅ BMC Ward monitoring complete!")
        print(f"💰 Total cost: ${monitor.estimated_cost:.4f}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()



if __name__ == "__main__":
    main()
