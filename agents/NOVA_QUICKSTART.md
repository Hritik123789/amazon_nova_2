# Amazon Nova Quick Start Guide

## 🚀 Last Week Sprint - All 4 Nova Models

You have **5 new scripts** ready to showcase all 4 Amazon Nova models!

## 📋 Prerequisites

1. **AWS Credentials** configured:
   ```bash
   aws configure
   # Enter your AWS Access Key ID
   # Enter your AWS Secret Access Key
   # Region: us-east-1
   ```

2. **Python dependencies**:
   ```bash
   pip install boto3
   ```

3. **Existing data** (from Ollama agents):
   - `news-synthesis/collected_news.json` (170 articles)
   - `news-synthesis/analyzed_news.json` (28 relevant articles)

## 🎯 The 5 Nova Scripts

### 1️⃣ News Analysis (Nova 2 Lite)
**File**: `agents/news-synthesis/local_news_agent_nova.py`

**What it does**: Analyzes Mumbai news articles for civic relevance

**Cost**: ~$0.0065 for 10 articles

**Run**:
```bash
cd agents/news-synthesis
python local_news_agent_nova.py
```

**Output**: `analyzed_news_nova.json`

---

### 2️⃣ Bridge to Permits (Nova 2 Lite)
**File**: `agents/bridge_to_permits_nova.py`

**What it does**: Extracts locations and actions from permit-required articles

**Cost**: ~$0.0033 for 7 investigations

**Run**:
```bash
cd agents
python bridge_to_permits_nova.py
```

**Output**: `permit-monitor/pending_investigations_nova.json`

---

### 3️⃣ Voice Briefing (Nova 2 Sonic)
**File**: `agents/voice_briefing_nova.py`

**What it does**: Generates daily civic briefing script (text-to-speech ready)

**Cost**: ~$0.0002 per briefing (text input)

**Run**:
```bash
cd agents
python voice_briefing_nova.py
```

**Output**: `voice_briefing.txt`

---

### 4️⃣ Image Analysis (Nova 2 Omni)
**File**: `agents/image_analysis_nova.py`

**What it does**: Analyzes construction site images and permit documents

**Cost**: ~$0.0016 per image

**Setup**:
```bash
# Create sample images folder
mkdir sample_images

# Add your images (construction sites, permit docs, etc.)
# Supported: .jpg, .jpeg, .png
```

**Run**:
```bash
cd agents
python image_analysis_nova.py
```

**Output**: `image_analysis_results.json`

---

### 5️⃣ Web Scraping (Nova Act) ⚠️ EXPENSIVE
**File**: `agents/web_scraper_nova_act.py`

**What it does**: Scrapes BMC and RERA websites for permit data

**Cost**: $4.75 per hour (~$0.40 for 5-minute demo)

**⚠️ WARNING**: This is your most expensive operation!

**Run**:
```bash
cd agents
python web_scraper_nova_act.py
```

**Output**: `scraped_data_nova_act.json`

**💡 TIP**: Use mock data for practice, run live only for judges!

---

## 🎪 Master Demo Script

**File**: `agents/demo_all_nova_models.py`

**What it does**: Runs all 5 scripts in sequence with cost tracking

**Run**:
```bash
cd agents
python demo_all_nova_models.py
```

This will:
1. Guide you through each step
2. Let you skip expensive operations
3. Track total cost in `cost_log.json`
4. Show final cost summary

**Estimated total cost**: $0.85 - $1.50 (depending on Nova Act usage)

---

## 💰 Cost Control Features

All scripts include:
- ✅ Default limits (10 articles, 7 investigations, 5 images)
- ✅ Cost estimation before running
- ✅ User confirmation for expensive operations
- ✅ Real-time cost tracking
- ✅ Cost logging to `cost_log.json`

### Environment Variables

Control limits without editing code:

```bash
# News analysis
export MAX_ARTICLES=5

# Bridge processing
export MAX_INVESTIGATIONS=3

# Demo mode (enables cost tracking)
export DEMO_MODE=true
```

---

## 📊 Cost Tracking

All operations log to `cost_log.json`:

```json
{
  "timestamp": "2026-03-09T...",
  "operation": "news_analysis",
  "model": "Amazon Nova 2 Lite",
  "total_articles": 10,
  "tokens_used": 7000,
  "estimated_cost": 0.0065
}
```

**Check your spending**:
```bash
cat cost_log.json | grep estimated_cost
```

---

## 🎯 Recommended Demo Flow

### For Judges (Live Demo)
1. **News Analysis** (Nova 2 Lite) - 10 articles → $0.0065
2. **Bridge Processing** (Nova 2 Lite) - 7 investigations → $0.0033
3. **Voice Briefing** (Nova 2 Sonic) - 1 briefing → $0.0002
4. **Image Analysis** (Nova 2 Omni) - 3 images → $0.0048
5. **Web Scraping** (Nova Act) - 5-minute demo → $0.40

**Total**: ~$0.42 per complete demo

**You can run 2-3 full demos per day safely!**

### For Practice (Use Cached Results)
- Run Ollama versions (FREE)
- Use existing JSON outputs
- Show video recordings of Nova demos
- Only run Nova live for final judge presentation

---

## 🚨 Emergency Cost Control

If costs are running high:

1. **Reduce limits**:
   ```bash
   export MAX_ARTICLES=5
   export MAX_INVESTIGATIONS=3
   ```

2. **Skip Nova Act**:
   - Use mock data (already in script)
   - Show cached results
   - Explain capability without running

3. **Use Ollama fallback**:
   - All functionality works with Ollama
   - Switch back to free local AI
   - Nova is for demo only

---

## ✅ Pre-Demo Checklist

### 1 Day Before
- [ ] Test each Nova script with 1-2 samples
- [ ] Verify AWS credentials work
- [ ] Check cost_log.json totals
- [ ] Prepare sample images for Nova 2 Omni
- [ ] Record backup video of Nova demos

### Demo Day
- [ ] Run master demo script once for practice
- [ ] Check remaining budget
- [ ] Have Ollama versions ready as backup
- [ ] Keep Nova Act demo under 5 minutes
- [ ] Monitor cost_log.json in real-time

---

## 🎓 What to Tell Judges

### Architecture Highlight
"We use a **dual-mode architecture**:
- **Development**: Ollama (free local AI) for rapid iteration
- **Production**: Amazon Nova for scalable cloud deployment
- This keeps costs low while maintaining full functionality"

### All 4 Nova Models
1. **Nova 2 Lite**: News analysis and permit processing (cost-effective)
2. **Nova 2 Sonic**: Voice briefings for accessibility (text-to-speech)
3. **Nova 2 Omni**: Image analysis of construction sites (multimodal)
4. **Nova Act**: Automated web scraping of government portals (agentic)

### Cost Optimization
"Built-in cost controls:
- Article limits
- User confirmations
- Real-time tracking
- Estimated costs before execution"

---

## 🐛 Troubleshooting

### "Failed to connect to Bedrock"
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify region
aws configure get region
# Should be: us-east-1
```

### "Model not found"
- Ensure you have access to Nova models in your AWS account
- Check model IDs:
  - Nova 2 Lite: `us.amazon.nova-lite-v1:0`
  - Nova 2 Omni: `us.amazon.nova-pro-v1:0`

### "Cost too high"
- Reduce MAX_ARTICLES and MAX_INVESTIGATIONS
- Skip Nova Act demos
- Use cached results

---

## 📞 Quick Commands

```bash
# Run complete demo
python agents/demo_all_nova_models.py

# Individual scripts
python agents/news-synthesis/local_news_agent_nova.py
python agents/bridge_to_permits_nova.py
python agents/voice_briefing_nova.py
python agents/image_analysis_nova.py
python agents/web_scraper_nova_act.py

# Check costs
cat cost_log.json

# Test AWS connection
aws bedrock list-foundation-models --region us-east-1
```

---

## 🎉 You're Ready!

You now have:
- ✅ All 4 Nova models integrated
- ✅ Cost tracking and controls
- ✅ Master demo script
- ✅ Ollama fallback for safety
- ✅ Complete workflow from news → permits → briefings

**Go build something amazing! 🚀**
