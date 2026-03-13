# 🔌 Agent API Integration Guide

## For Next.js + Laravel Integration

All agents output JSON files. Your backend just needs to read these files or call the Python scripts.

---

## 📦 Agent Outputs

### 1. News Analysis Agent
**Script**: `agents/news-synthesis/local_news_agent_nova.py`

**Output File**: `agents/news-synthesis/analyzed_news_nova.json`

**JSON Structure**:
```json
[
  {
    "article_number": 1,
    "title": "BMC issues e-auction notices...",
    "category": "Civic",
    "mentions": ["BMC"],
    "permit_check_required": false,
    "relevance_score": 8,
    "url": "https://...",
    "summary": "...",
    "analyzed_by": "Amazon Nova 2 Lite"
  }
]
```

**Laravel Endpoint**:
```php
Route::get('/api/news', function () {
    $json = file_get_contents(base_path('agents/news-synthesis/analyzed_news_nova.json'));
    return response()->json(json_decode($json));
});
```

**Next.js API Route** (`pages/api/news.js`):
```javascript
import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  const filePath = path.join(process.cwd(), 'agents/news-synthesis/analyzed_news_nova.json');
  const jsonData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  res.status(200).json(jsonData);
}
```

---

### 2. Permit Investigation Agent
**Script**: `agents/bridge_to_permits_nova.py`

**Output File**: `agents/permit-monitor/pending_investigations_nova.json`

**JSON Structure**:
```json
[
  {
    "investigation_id": "INV-001",
    "source": "Nova News Agent",
    "title": "GMLR Phase IV approved...",
    "location": "Goregaon to Mulund",
    "action": "Infrastructure Project",
    "priority": "MEDIUM",
    "category": "Civic",
    "relevance_score": 5,
    "news_url": "https://...",
    "created_at": "2026-03-09T...",
    "status": "Pending Investigation",
    "analyzed_by": "Amazon Nova 2 Lite"
  }
]
```

**Laravel Endpoint**:
```php
Route::get('/api/permits', function () {
    $json = file_get_contents(base_path('agents/permit-monitor/pending_investigations_nova.json'));
    return response()->json(json_decode($json));
});
```

**Next.js API Route** (`pages/api/permits.js`):
```javascript
import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  const filePath = path.join(process.cwd(), 'agents/permit-monitor/pending_investigations_nova.json');
  const jsonData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  res.status(200).json(jsonData);
}
```

---

### 3. Voice Briefing Agent
**Script**: `agents/voice_briefing_nova.py`

**Output File**: `agents/voice_briefing.txt`

**Text Structure**:
```
Good morning, Mumbai! Here's your civic update for today.

Top story: The BMC has approved the GMLR Phase IV project...
```

**Laravel Endpoint**:
```php
Route::get('/api/briefing', function () {
    $text = file_get_contents(base_path('agents/voice_briefing.txt'));
    return response()->json(['script' => $text]);
});
```

**Next.js API Route** (`pages/api/briefing.js`):
```javascript
import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  const filePath = path.join(process.cwd(), 'agents/voice_briefing.txt');
  const text = fs.readFileSync(filePath, 'utf8');
  res.status(200).json({ script: text });
}
```

---

### 4. Image Analysis Agent
**Script**: `agents/image_analysis_nova.py`

**Output File**: `agents/image_analysis_results.json`

**JSON Structure**:
```json
[
  {
    "image_path": "sample_images/construction_site_1.jpg",
    "analysis": "This image shows a large-scale construction site...",
    "analyzed_at": "2026-03-09T...",
    "analyzed_by": "Amazon Nova 2 Omni",
    "tokens_used": 1456,
    "cost": 0.001623
  }
]
```

**Laravel Endpoint**:
```php
Route::get('/api/images', function () {
    $json = file_get_contents(base_path('agents/image_analysis_results.json'));
    return response()->json(json_decode($json));
});
```

**Next.js API Route** (`pages/api/images.js`):
```javascript
import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  const filePath = path.join(process.cwd(), 'agents/image_analysis_results.json');
  const jsonData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  res.status(200).json(jsonData);
}
```

---

### 5. Web Scraping Agent
**Script**: `agents/web_scraper_nova_act.py`

**Output File**: `agents/scraped_data_nova_act.json`

**JSON Structure**:
```json
{
  "bmc_permits": {
    "url": "https://portal.mcgm.gov.in",
    "scraped_at": "2026-03-09T...",
    "permits_found": [
      {
        "permit_id": "BMC/2026/001234",
        "project_name": "Residential Redevelopment - Andheri West",
        "location": "Andheri West, Mumbai",
        "permit_type": "Construction",
        "status": "Approved",
        "issue_date": "2026-03-01",
        "expiry_date": "2027-03-01"
      }
    ],
    "total_permits": 3
  },
  "rera_projects": {
    "location": "Mumbai",
    "scraped_at": "2026-03-09T...",
    "projects_found": [
      {
        "rera_number": "P51900000001",
        "project_name": "Lodha Crown",
        "developer": "Lodha Developers",
        "location": "Thane, Mumbai",
        "status": "Registered"
      }
    ],
    "total_projects": 2
  },
  "total_cost": 0.3706
}
```

**Laravel Endpoint**:
```php
Route::get('/api/scraped', function () {
    $json = file_get_contents(base_path('agents/scraped_data_nova_act.json'));
    return response()->json(json_decode($json));
});
```

**Next.js API Route** (`pages/api/scraped.js`):
```javascript
import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  const filePath = path.join(process.cwd(), 'agents/scraped_data_nova_act.json');
  const jsonData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  res.status(200).json(jsonData);
}
```

---

### 6. Social Listening Agent
**Script**: `agents/social-listening/social_collector.py`

**Output File**: `agents/social-listening/collected_social.json`

**JSON Structure**:
```json
[
  {
    "post_id": "social_001",
    "platform": "Facebook",
    "author": "Mumbai Residents Group",
    "content": "New pothole on SV Road near Andheri station...",
    "location": "Andheri",
    "category": "Infrastructure",
    "sentiment": "Negative",
    "timestamp": "2026-03-09T10:30:00",
    "engagement": {
      "likes": 45,
      "comments": 12,
      "shares": 8
    }
  }
]
```

**Laravel Endpoint**:
```php
Route::get('/api/social', function () {
    $json = file_get_contents(base_path('agents/social-listening/collected_social.json'));
    return response()->json(json_decode($json));
});
```

**Next.js API Route** (`pages/api/social.js`):
```javascript
import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  const filePath = path.join(process.cwd(), 'agents/social-listening/collected_social.json');
  const jsonData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  res.status(200).json(jsonData);
}
```

---

## 🔄 Running Agents

### Option 1: Manual (For Demo)
```bash
# Run each agent manually
python agents/news-synthesis/local_news_agent_nova.py
python agents/bridge_to_permits_nova.py
python agents/voice_briefing_nova.py
python agents/image_analysis_nova.py
python agents/web_scraper_nova_act.py
```

### Option 2: Laravel Artisan Command
```php
// app/Console/Commands/RunAgents.php
Artisan::command('agents:run', function () {
    exec('python ' . base_path('agents/news-synthesis/local_news_agent_nova.py'));
    exec('python ' . base_path('agents/bridge_to_permits_nova.py'));
    exec('python ' . base_path('agents/voice_briefing_nova.py'));
    $this->info('Agents executed successfully!');
});
```

### Option 3: Next.js API Route (Trigger Agents)
```javascript
// pages/api/run-agents.js
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export default async function handler(req, res) {
  try {
    await execAsync('python agents/news-synthesis/local_news_agent_nova.py');
    await execAsync('python agents/bridge_to_permits_nova.py');
    await execAsync('python agents/voice_briefing_nova.py');
    res.status(200).json({ message: 'Agents executed successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
```

---

## 📊 Dashboard Stats Endpoint

**Laravel**:
```php
Route::get('/api/stats', function () {
    $news = json_decode(file_get_contents(base_path('agents/news-synthesis/analyzed_news_nova.json')));
    $permits = json_decode(file_get_contents(base_path('agents/permit-monitor/pending_investigations_nova.json')));
    
    return response()->json([
        'total_articles' => count($news),
        'total_permits' => count($permits),
        'high_priority' => count(array_filter($permits, fn($p) => $p->priority === 'HIGH')),
        'medium_priority' => count(array_filter($permits, fn($p) => $p->priority === 'MEDIUM')),
        'low_priority' => count(array_filter($permits, fn($p) => $p->priority === 'LOW')),
    ]);
});
```

**Next.js**:
```javascript
// pages/api/stats.js
import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  const newsPath = path.join(process.cwd(), 'agents/news-synthesis/analyzed_news_nova.json');
  const permitsPath = path.join(process.cwd(), 'agents/permit-monitor/pending_investigations_nova.json');
  
  const news = JSON.parse(fs.readFileSync(newsPath, 'utf8'));
  const permits = JSON.parse(fs.readFileSync(permitsPath, 'utf8'));
  
  res.status(200).json({
    total_articles: news.length,
    total_permits: permits.length,
    high_priority: permits.filter(p => p.priority === 'HIGH').length,
    medium_priority: permits.filter(p => p.priority === 'MEDIUM').length,
    low_priority: permits.filter(p => p.priority === 'LOW').length,
  });
}
```

---

## 🗂️ File Structure for Integration

```
project/
├── agents/                          # Your Python agents
│   ├── news-synthesis/
│   │   ├── local_news_agent_nova.py
│   │   └── analyzed_news_nova.json  ← Read this
│   ├── permit-monitor/
│   │   └── pending_investigations_nova.json  ← Read this
│   ├── social-listening/
│   │   └── collected_social.json    ← Read this
│   ├── voice_briefing.txt           ← Read this
│   ├── image_analysis_results.json  ← Read this
│   └── scraped_data_nova_act.json   ← Read this
│
├── backend/ (Laravel)               # Your friend's work
│   └── routes/api.php               # Add endpoints above
│
└── frontend/ (Next.js)              # Your friend's work
    └── pages/api/                   # Add API routes above
```

---

## ✅ That's It!

Your friend just needs to:
1. Read the JSON files
2. Create API endpoints
3. Display the data

**No complex integration needed!** 🎉
