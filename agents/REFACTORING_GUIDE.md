# 🔧 CityPulse Refactoring Guide

This document shows the code changes needed to implement the refactoring improvements.

---

## 1. Utils Module Created

**File**: `agents/utils/__init__.py`

✅ **Created** - Provides:
- `get_data_path(filename)` - Get absolute path to data files
- `load_json_data(filename, default)` - Load JSON from data/ directory
- `save_json_data(filename, data)` - Save JSON to data/ directory
- `create_standard_event(...)` - Create standardized event structure
- `log_cost(agent_name, tokens, cost, ...)` - Log costs centrally
- `get_total_cost()` - Get total cost from all operations

---

## 2. Social Listener Refactoring

**File**: `agents/social-listening/social_listener_nova.py`

### Changes Needed:

#### A. Add imports at top (after existing imports):
```python
# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import save_json_data, create_standard_event, log_cost
```

#### B. Update `save_results()` method:
```python
def save_results(self, posts: List[Dict], output_file: str = "social.json"):
    """Save results to data/ directory with standardized schema"""
    
    # Convert to standardized events
    standardized_events = []
    for post in posts:
        event = create_standard_event(
            event_id=f"social-{post.get('post_id', 'unknown')}",
            source="social_listener",
            event_type="social_discussion",
            location=post.get('subreddit', 'mumbai'),
            description=post.get('text', '')[:200],
            severity=self._map_sentiment_to_severity(post.get('sentiment', 'neutral')),
            metadata={
                "original_post": post,
                "sentiment": post.get('sentiment'),
                "engagement": post.get('engagement', {}),
                "url": post.get('url', '')
            }
        )
        standardized_events.append(event)
    
    # Save with both formats (for compatibility)
    output_data = {
        "generated_at": datetime.now().isoformat(),
        "total_posts": len(posts),
        "posts": posts,  # Original format
        "events": standardized_events  # Standardized format
    }
    
    save_json_data(output_file, output_data)
    
    # Log cost
    log_cost(
        agent_name="social_listener",
        tokens_used=self.tokens_used,
        estimated_cost=self.estimated_cost,
        model="Amazon Nova 2 Lite",
        operation="sentiment_analysis"
    )
    
    return output_file

def _map_sentiment_to_severity(self, sentiment: str) -> str:
    """Map sentiment to severity level"""
    mapping = {
        "positive": "low",
        "neutral": "medium",
        "negative": "high"
    }
    return mapping.get(sentiment, "medium")
```

---

## 3. Permit Monitor Refactoring

**File**: `agents/permit-monitor/permit_monitor_real.py`

### Changes Needed:

#### A. Add imports:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import save_json_data, create_standard_event, log_cost
```

#### B. Update `save_results()` method:
```python
def save_results(self, events: List[Dict], output_file: str = "permits.json"):
    """Save results to data/ directory with standardized schema"""
    
    # Convert to standardized events
    standardized_events = []
    for event in events:
        std_event = create_standard_event(
            event_id=f"permit-{event.get('source', 'unknown')}",
            source="permit_monitor",
            event_type="permit_event",
            location=event.get('location', 'Mumbai'),
            description=event.get('description', ''),
            severity=self._determine_severity(event),
            metadata={
                "original_event": event,
                "event_type": event.get('event_type'),
                "source_url": event.get('metadata', {}).get('url', '')
            }
        )
        standardized_events.append(std_event)
    
    output_data = {
        "generated_at": datetime.now().isoformat(),
        "total_events": len(events),
        "events": standardized_events,
        "raw_events": events  # Keep original format
    }
    
    save_json_data(output_file, output_data)
    
    # Log cost
    log_cost(
        agent_name="permit_monitor",
        tokens_used=self.tokens_used,
        estimated_cost=self.estimated_cost,
        model="Amazon Nova 2 Lite",
        operation="permit_normalization"
    )
    
    return output_file

def _determine_severity(self, event: Dict) -> str:
    """Determine severity based on event type"""
    event_type = event.get('event_type', '').lower()
    if 'demolition' in event_type or 'closure' in event_type:
        return "high"
    elif 'construction' in event_type:
        return "medium"
    return "low"
```

---

## 4. Image Analysis Refactoring

**File**: `agents/image_analysis_nova.py`

### Changes Needed:

#### A. Add imports:
```python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import save_json_data, create_standard_event, log_cost
```

#### B. Update `save_analysis()` method:
```python
def save_analysis(self, results: list, filename: str = "images.json"):
    """Save analysis results to data/ directory with standardized schema"""
    
    # Convert to standardized events
    standardized_events = []
    for result in results:
        event = create_standard_event(
            event_id=f"image-{os.path.basename(result['image_path'])}",
            source="image_analyzer",
            event_type="safety_violation",
            location="Mumbai",
            description=result['analysis'][:200],
            severity=self._extract_severity(result['analysis']),
            metadata={
                "image_path": result['image_path'],
                "full_analysis": result['analysis'],
                "analyzed_by": result['analyzed_by'],
                "analyzed_at": result['analyzed_at']
            }
        )
        standardized_events.append(event)
    
    output_data = {
        "generated_at": datetime.now().isoformat(),
        "total_images": len(results),
        "events": standardized_events,
        "raw_results": results  # Keep original format
    }
    
    save_json_data(filename, output_data)
    
    # Log cost
    log_cost(
        agent_name="image_analyzer",
        tokens_used=self.tokens_used,
        estimated_cost=self.estimated_cost,
        model="Amazon Nova 2 Omni",
        operation="image_analysis"
    )
    
    print(f"💰 Total cost: ${self.estimated_cost:.4f}")

def _extract_severity(self, analysis: str) -> str:
    """Extract severity from analysis text"""
    analysis_lower = analysis.lower()
    if any(word in analysis_lower for word in ['violation', 'danger', 'critical', 'unsafe']):
        return "high"
    elif any(word in analysis_lower for word in ['concern', 'issue', 'missing']):
        return "medium"
    return "low"
```

---

## 5. Safety Intelligence Refactoring

**File**: `agents/features/safety_intelligence_nova.py`

### Changes Needed:

#### A. Add imports:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_json_data, save_json_data, log_cost
```

#### B. Update `load_data_sources()` method:
```python
def load_data_sources(self) -> Dict[str, List]:
    """Load all safety-related data sources from data/ directory"""
    print("📊 Loading safety data sources...")
    
    # Load from centralized data directory
    news_data = load_json_data('news.json', default={})
    permits_data = load_json_data('permits.json', default={})
    social_data = load_json_data('social.json', default={})
    images_data = load_json_data('images.json', default={})
    
    # Extract events (standardized format)
    data = {
        "news": news_data.get('events', news_data.get('articles', [])),
        "permits": permits_data.get('events', permits_data.get('raw_events', [])),
        "social": social_data.get('events', social_data.get('posts', [])),
        "images": images_data.get('events', images_data.get('raw_results', []))
    }
    
    print(f"   News events: {len(data['news'])}")
    print(f"   Permit events: {len(data['permits'])}")
    print(f"   Social events: {len(data['social'])}")
    print(f"   Image events: {len(data['images'])}")
    print()
    
    return data
```

#### C. Update `save_results()` method:
```python
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
    
    # Log cost (if any Nova calls were made)
    if hasattr(self, 'tokens_used') and self.tokens_used > 0:
        log_cost(
            agent_name="safety_intelligence",
            tokens_used=self.tokens_used,
            estimated_cost=self.estimated_cost,
            model="Amazon Nova 2 Lite",
            operation="alert_generation"
        )
    
    return output_file
```

---

## 6. Morning Briefing Refactoring

**File**: `agents/features/morning_briefing_nova.py`

### Changes Needed:

#### A. Add imports:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_json_data, save_json_data, log_cost
```

#### B. Update data loading methods:
```python
def load_news(self) -> List[Dict]:
    """Load analyzed news articles from data/ directory"""
    data = load_json_data('news.json', default={})
    return data.get('events', data.get('articles', []))

def load_permits(self) -> List[Dict]:
    """Load permit events from data/ directory"""
    data = load_json_data('permits.json', default={})
    return data.get('events', data.get('raw_events', []))

def load_social(self) -> List[Dict]:
    """Load social media posts from data/ directory"""
    data = load_json_data('social.json', default={})
    return data.get('events', data.get('posts', []))
```

#### C. Update `save_briefing()` method:
```python
def save_briefing(self, briefing: Dict, output_file: str = "morning_briefing.json"):
    """Save briefing to data/ directory"""
    save_json_data(output_file, briefing)
    
    # Log cost
    if hasattr(self, 'tokens_used'):
        log_cost(
            agent_name="morning_briefing",
            tokens_used=self.tokens_used,
            estimated_cost=self.estimated_cost,
            model="Amazon Nova 2 Lite",
            operation="briefing_generation"
        )
    
    return output_file
```

---

## 7. Smart Alerts Refactoring

**File**: `agents/features/smart_alerts_nova.py`

### Changes Needed:

#### A. Add imports:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_json_data, save_json_data, log_cost
```

#### B. Update `load_data_sources()` method:
```python
def load_data_sources(self) -> Dict[str, List]:
    """Load all data sources from data/ directory"""
    print("📊 Loading data sources...")
    
    news_data = load_json_data('news.json', default={})
    permits_data = load_json_data('permits.json', default={})
    social_data = load_json_data('social.json', default={})
    
    data = {
        "news": news_data.get('events', news_data.get('articles', [])),
        "permits": permits_data.get('events', permits_data.get('raw_events', [])),
        "social": social_data.get('events', social_data.get('posts', []))
    }
    
    print(f"   News events: {len(data['news'])}")
    print(f"   Permit events: {len(data['permits'])}")
    print(f"   Social events: {len(data['social'])}")
    print()
    
    return data
```

#### C. Update `save_alerts()` method:
```python
def save_alerts(self, alerts: List[Dict], output_file: str = "smart_alerts.json"):
    """Save alerts to data/ directory"""
    output_data = {
        "generated_at": datetime.now().isoformat(),
        "user_location": self.location,
        "alert_count": len(alerts),
        "alerts": alerts
    }
    
    save_json_data(output_file, output_data)
    
    # Log cost
    if hasattr(self, 'tokens_used'):
        log_cost(
            agent_name="smart_alerts",
            tokens_used=self.tokens_used,
            estimated_cost=self.estimated_cost,
            model="Amazon Nova 2 Lite",
            operation="alert_prioritization"
        )
    
    return output_file
```

---

## 8. News Agent Refactoring

**File**: `agents/news-synthesis/local_news_agent_nova.py`

### Changes Needed:

#### A. Add imports:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import save_json_data, create_standard_event, log_cost
```

#### B. Update save method to use standardized schema:
```python
def save_results(self, articles: List[Dict], output_file: str = "news.json"):
    """Save results with standardized schema"""
    
    # Convert to standardized events
    standardized_events = []
    for article in articles:
        event = create_standard_event(
            event_id=f"news-{article.get('article_number', 'unknown')}",
            source="news_agent",
            event_type="news_event",
            location=article.get('location', 'Mumbai'),
            description=article.get('summary', article.get('title', '')),
            severity=self._map_category_to_severity(article.get('category', '')),
            metadata={
                "original_article": article,
                "category": article.get('category'),
                "url": article.get('url', ''),
                "entities": article.get('entities', [])
            }
        )
        standardized_events.append(event)
    
    output_data = {
        "generated_at": datetime.now().isoformat(),
        "total_articles": len(articles),
        "events": standardized_events,
        "articles": articles  # Keep original format
    }
    
    save_json_data(output_file, output_data)
    
    # Log cost
    log_cost(
        agent_name="news_agent",
        tokens_used=self.tokens_used,
        estimated_cost=self.estimated_cost,
        model="Amazon Nova 2 Lite",
        operation="news_analysis"
    )

def _map_category_to_severity(self, category: str) -> str:
    """Map news category to severity"""
    high_severity = ['Traffic', 'Crime', 'Accident', 'Emergency']
    if category in high_severity:
        return "high"
    return "medium"
```

---

## 9. Migration Steps

### Step 1: Install Utils Module
```bash
# Utils module already created at agents/utils/__init__.py
# No installation needed
```

### Step 2: Create Data Directory
```bash
cd agents
mkdir -p data
```

### Step 3: Update Each Agent
Apply the code changes above to each agent file.

### Step 4: Test Each Agent
```bash
# Test social listener
cd agents
python social-listening/social_listener_nova.py

# Test permit monitor
python permit-monitor/permit_monitor_real.py

# Test image analysis
cd ..
python agents/image_analysis_nova.py

# Test safety intelligence
cd agents
python features/safety_intelligence_nova.py
```

### Step 5: Verify Data Directory
```bash
ls -la agents/data/
# Should see:
# - social.json
# - permits.json
# - images.json
# - safety_alerts.json
# - news.json
# - morning_briefing.json
# - smart_alerts.json
```

### Step 6: Verify Cost Log
```bash
cat agents/cost_log.json
# Should see entries from all agents
```

---

## 10. Benefits After Refactoring

✅ **Path Independence**: Scripts work from any directory  
✅ **Unified Schema**: All agents output standardized events  
✅ **Centralized Data**: All outputs in `agents/data/`  
✅ **Cost Tracking**: All costs logged to single file  
✅ **Backward Compatible**: Original formats preserved  
✅ **Easier Integration**: Frontend can consume standardized events  

---

## 11. Standardized Event Schema

All agents now output events in this format:

```json
{
  "id": "social-abc123",
  "source": "social_listener",
  "type": "social_discussion",
  "location": "mumbai",
  "timestamp": "2026-03-11T22:30:00",
  "description": "Discussion about new metro line...",
  "severity": "medium",
  "metadata": {
    "sentiment": "positive",
    "engagement": {"upvotes": 45, "comments": 12},
    "url": "https://reddit.com/..."
  }
}
```

### Event Types by Agent:
- **permit_monitor** → `permit_event`
- **social_listener** → `social_discussion`
- **image_analyzer** → `safety_violation`
- **news_agent** → `news_event`

### Severity Levels:
- `low` - Informational
- `medium` - Notable
- `high` - Important
- `critical` - Urgent

---

## 12. Next Steps

After applying these changes:

1. ✅ Test each agent individually
2. ✅ Verify data/ directory has all outputs
3. ✅ Check cost_log.json has entries
4. ✅ Update frontend integration to use standardized events
5. ✅ Continue with Phase 2 remaining tasks (Investment Insights, Community Pulse)

---

**Status**: Ready to apply refactoring 🚀
