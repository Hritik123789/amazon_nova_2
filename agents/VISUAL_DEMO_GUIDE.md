# 🎬 Visual Demo Guide for Judges

## 5-Minute Demo Script with Visuals

---

## 🎯 Opening (30 seconds)

### What to Say
"Hi, I'm [Your Name] and this is **CityPulse** - a civic transparency platform for Mumbai's 20 million residents. We use all 4 Amazon Nova models to monitor construction permits, analyze news, and keep citizens informed about what's happening in their neighborhoods."

### What to Show
- **Screen**: CityPulse frontend homepage
- **Highlight**: "Powered by Amazon Nova" badge
- **Point to**: Real-time news feed

---

## 📰 Demo 1: News Collection & Analysis (1 minute)

### What to Say
"Every day, we collect news from Mumbai's top sources - Mid-Day, Hindustan Times, Times of India. Today we collected 170 articles. Now watch as **Amazon Nova 2 Lite** analyzes them for civic relevance."

### What to Show
```bash
# Terminal command
python agents/news-synthesis/local_news_agent_nova.py
```

### Visual Output
```
🤖 Initializing Nova News Agent (Amazon Bedrock Nova 2 Lite)...
✓ Connected to Amazon Bedrock

📰 Loaded 170 articles from collected_news.json
⚠️  COST CONTROL: Processing only 10 articles

🔍 Analyzing 10 articles with Amazon Nova 2 Lite...

Processing 1/10: BMC issues e-auction notices to 34 defaulters...
  💰 Tokens: 687, Cost: $0.000651
  ✓ Relevant! Category: Civic, Mentions: BMC

Processing 2/10: Metro 11 extended by 6.9km...
  💰 Tokens: 712, Cost: $0.000673
  ✓ Relevant! Category: Traffic, Mentions: MMRCL

...

✓ Analysis complete! Found 8 relevant articles
💰 Total tokens used: 6,847
💰 Total cost: $0.0065
```

### What to Highlight
- ✅ Real-time analysis
- ✅ Cost tracking ($0.0065)
- ✅ Entity recognition (BMC, MMRCL)
- ✅ Categorization (Civic, Traffic, Real Estate)

---

## 🌉 Demo 2: Bridge to Permits (1 minute)

### What to Say
"We found 7 articles that mention construction or permits. Now **Nova 2 Lite** extracts specific locations and project types to create investigation tasks for our permit monitoring system."

### What to Show
```bash
# Terminal command
python agents/bridge_to_permits_nova.py
```

### Visual Output
```
🌉 Initializing Nova Bridge (Amazon Bedrock Nova 2 Lite)...
✓ Connected to Amazon Bedrock

📰 Loaded 28 analyzed articles
🔍 Found 7 articles, processing 7

🔍 Extracting locations and actions with Nova 2 Lite...

Processing 1/7: GMLR Phase IV approved with ₹800-cr cost escalation...
  💰 Tokens: 423, Cost: $0.000401
  → Location: Goregaon to Mulund, Action: Infrastructure Project

Processing 2/7: Sion ROB may be thrown open by August...
  💰 Tokens: 398, Cost: $0.000377
  → Location: Sion, Action: Road Work

...

💰 Total cost: $0.0033

💾 Saved 7 investigations to pending_investigations_nova.json
```

### What to Highlight
- ✅ AI-powered location extraction
- ✅ Action classification
- ✅ Priority calculation
- ✅ Investigation queue created

---

## 🎙️ Demo 3: Voice Briefing (1 minute)

### What to Say
"For accessibility, we generate daily voice briefings. **Nova 2 Sonic** creates a conversational script that can be converted to speech for citizens who prefer audio updates."

### What to Show
```bash
# Terminal command
python agents/voice_briefing_nova.py
```

### Visual Output
```
🎙️  Initializing Voice Briefing (Amazon Nova 2 Sonic)...
✓ Connected to Amazon Bedrock

📰 Loaded 28 analyzed articles

🔍 Generating voice briefing script...
💰 Script generation - Tokens: 1,234, Cost: $0.000148

================================================================================
📝 VOICE BRIEFING SCRIPT
================================================================================
Good morning, Mumbai! Here's your civic update for today.

Top story: The BMC has approved the GMLR Phase IV project, which will cut 
travel time from Goregaon to Mulund to just 20 minutes. The project cost has 
increased to 2,113 crores, but it's expected to significantly ease traffic 
congestion.

In Sion, the long-awaited ROB may finally open by August. The BMC has approved 
design modifications that will improve traffic flow in the area.

And in Bandra, the Metro 11 line has been extended by 6.9 kilometers, now 
connecting Wadala to Bandra Terminus. This will make commuting much easier for 
thousands of residents.

Stay informed, stay engaged. Visit CityPulse for more details.
================================================================================

💾 Saved briefing script to voice_briefing.txt
💰 Total cost: $0.0002
```

### What to Highlight
- ✅ Conversational tone
- ✅ Top 3 stories highlighted
- ✅ TTS-ready format
- ✅ Extremely low cost ($0.0002)

---

## 🖼️ Demo 4: Image Analysis (1 minute)

### What to Say
"Citizens can upload photos of construction sites. **Nova 2 Omni**, our multimodal model, analyzes the images to detect safety issues, verify permits, and identify project types."

### What to Show
```bash
# Terminal command
python agents/image_analysis_nova.py
```

### Visual Output
```
🖼️  Initializing Image Analyzer (Amazon Nova 2 Omni)...
✓ Connected to Amazon Bedrock

📸 Found 3 images to analyze

🔍 Analyzing image: construction_site_1.jpg...
💰 Tokens: 1,456, Cost: $0.001623

================================================================================
📊 Analysis for construction_site_1.jpg:
================================================================================
This image shows a large-scale construction site with the following observations:

1. Construction Type: High-rise residential building (appears to be 20+ floors)
2. Permit Signage: Visible BMC permit board showing project approval
3. Safety Concerns: 
   - Workers visible without hard hats (safety violation)
   - Scaffolding appears unstable on the left side
   - No visible safety netting
4. Project Scale: Large (estimated 50,000+ sq ft)
5. Potential Issues:
   - Safety equipment compliance needs verification
   - Scaffolding requires immediate inspection
   - Recommend site visit by BMC safety officer

Recommendation: Flag for immediate safety inspection.
================================================================================

💾 Saved analysis to image_analysis_results.json
💰 Total cost: $0.0048
```

### What to Highlight
- ✅ Multimodal AI (image + text)
- ✅ Safety concern detection
- ✅ Permit verification
- ✅ Actionable recommendations

---

## 🤖 Demo 5: Web Scraping (1 minute)

### What to Say
"Finally, **Nova Act**, our agentic AI, automates web scraping of government portals. It monitors the BMC website and RERA database for new permits and project registrations."

### What to Show
```bash
# Terminal command
python agents/web_scraper_nova_act.py
```

### Visual Output
```
🤖 Initializing Web Scraper (Amazon Nova Act)...
⚠️  WARNING: Nova Act costs $4.75 per agent hour!
✓ Connected to Amazon Bedrock

⚠️  COST WARNING:
   Nova Act: $4.75 per agent hour
   5-minute demo: ~$0.40

Continue with demo? (yes/no): yes

================================================================================
DEMO 1: Scraping BMC Portal for Permits
================================================================================

🌐 Scraping: https://portal.mcgm.gov.in...
⏱️  Timer started - monitoring cost...

✓ Scraping complete!
⏱️  Elapsed time: 2.34 minutes
💰 Estimated cost: $0.1853

📊 Results:
   Found 3 permits
   - BMC/2026/001234: Residential Redevelopment - Andheri West (Approved)
   - BMC/2026/001235: Road Widening - Goregaon (Under Review)
   - BMC/2026/001236: Metro Station Construction - Bandra (Approved)

================================================================================
💰 TOTAL SESSION COST: $0.3706
================================================================================
```

### What to Highlight
- ✅ Automated web scraping
- ✅ Real-time permit monitoring
- ✅ Cost tracking (most expensive operation)
- ✅ Agentic AI capabilities

---

## 🎯 Closing (30 seconds)

### What to Say
"That's CityPulse - all 4 Amazon Nova models working together. We've built cost controls into every step. Development uses free Ollama for rapid iteration, production uses Nova for scalable cloud deployment. This architecture keeps costs predictable - just $137 per year for continuous citywide monitoring."

### What to Show
- **Screen**: Cost summary dashboard
```
💰 DEMO SESSION COST SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Operation                Model              Cost        Items
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
News Analysis           Nova 2 Lite        $0.0065     10 articles
Bridge Processing       Nova 2 Lite        $0.0033     7 investigations
Voice Briefing          Nova 2 Sonic       $0.0002     1 script
Image Analysis          Nova 2 Omni        $0.0048     3 images
Web Scraping            Nova Act           $0.3706     2 portals
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL DEMO COST                            $0.3854
REMAINING BUDGET                           $99.61
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Final Slide
```
🏆 CITYPULSE - CIVIC TRANSPARENCY FOR MUMBAI

✅ All 4 Amazon Nova Models
✅ Real-time News Monitoring
✅ Automated Permit Tracking
✅ Voice Accessibility
✅ Image Analysis
✅ Cost-Optimized Architecture

📊 Impact: 20M+ Mumbai residents
💰 Cost: $137/year for continuous monitoring
🚀 Scalable to any city globally

Thank you!
```

---

## 🎨 Visual Assets to Prepare

### Screenshots Needed
1. **Frontend homepage** - CityPulse interface
2. **News feed** - Real Mumbai articles
3. **Permit dashboard** - Investigation queue
4. **Cost tracking** - Real-time spending
5. **Architecture diagram** - Ollama + Nova dual-mode

### Demo Data
1. **Sample images** (3-5 images):
   - Construction site photos
   - Permit documents
   - BMC signage
   - Safety violations

2. **Cached results** (backup):
   - `analyzed_news_nova.json`
   - `pending_investigations_nova.json`
   - `voice_briefing.txt`
   - `image_analysis_results.json`

### Video Recording
- Record full 5-minute demo
- Have backup in case live demo fails
- Upload to YouTube (unlisted)
- Embed in Devpost submission

---

## 💡 Presentation Tips

### Do's
- ✅ Show real data (170 Mumbai articles)
- ✅ Highlight cost tracking
- ✅ Emphasize all 4 Nova models
- ✅ Demonstrate social impact
- ✅ Keep timing tight (5 minutes)

### Don'ts
- ❌ Don't run Nova Act live (too expensive, use cached)
- ❌ Don't skip cost summary
- ❌ Don't forget to mention Ollama fallback
- ❌ Don't go over time

### If Something Fails
- Have backup video ready
- Show cached JSON results
- Explain architecture with diagrams
- Switch to Ollama version

---

## 🎯 Key Messages

### Technical Excellence
"All 4 Amazon Nova models - Lite for analysis, Sonic for voice, Omni for images, Act for automation."

### Cost Optimization
"Built-in cost controls. Development uses free Ollama, production uses Nova. Predictable spending."

### Social Impact
"20 million Mumbai residents get transparency into construction permits and civic projects."

### Scalability
"Cloud-based architecture. Can scale to any city. Just $137/year for continuous monitoring."

---

## 📊 Backup Slides

### Slide 1: Problem
- Mumbai has 20M+ residents
- Thousands of construction projects
- Limited transparency
- Citizens can't track permits

### Slide 2: Solution
- CityPulse monitors news and permits
- AI-powered analysis
- Voice accessibility
- Image verification
- Automated web scraping

### Slide 3: Technology
- All 4 Amazon Nova models
- Dual-mode architecture (Ollama + Nova)
- Cost-optimized design
- Real-time monitoring

### Slide 4: Impact
- 20M+ potential users
- Civic transparency
- Government accountability
- Scalable globally

### Slide 5: Business Model
- Freemium (basic free, premium paid)
- Government contracts
- API access for developers
- NGO partnerships

---

## ✅ Pre-Demo Checklist

### Technical
- [ ] AWS credentials configured
- [ ] All scripts tested
- [ ] Sample images prepared
- [ ] Backup video recorded
- [ ] Cost log cleared

### Presentation
- [ ] Demo script practiced
- [ ] Timing verified (5 minutes)
- [ ] Backup slides ready
- [ ] Questions anticipated
- [ ] Elevator pitch memorized

### Backup Plan
- [ ] Cached JSON results ready
- [ ] Video uploaded
- [ ] Ollama version tested
- [ ] Architecture diagrams printed

---

**You're ready to impress the judges! 🚀**
