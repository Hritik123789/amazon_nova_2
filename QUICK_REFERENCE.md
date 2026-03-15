# Quick Reference Card

## 🚀 Run Commands

### Run All Agents (Parallel - RECOMMENDED!)
```bash
python agents/run_all_agents.py --parallel
```
**Duration**: 27.6 seconds (2.66x faster!)

### Run All Agents (Sequential)
```bash
python agents/run_all_agents.py
```
**Duration**: 73.5 seconds

### Run with Caching (Best Performance!)
```bash
python agents/run_all_agents.py --parallel --cache --cache-ttl 6
```
**Duration**: 2-27 seconds (depends on cache)  
**Cost**: 83% cheaper with cache!

### Run Just Enhanced Community Pulse
```bash
python agents/features/community_pulse_enhanced.py
```

---

## 📊 Output Files

All files in `agents/data/`:

| File | Description | Size |
|------|-------------|------|
| `news.json` | News articles with analysis | ~17 KB |
| `social.json` | Reddit posts with sentiment | ~32 KB |
| `permits.json` | Building permits | ~4 KB |
| `bmc_permits.json` | Ward-level permits | ~8 KB |
| `images.json` | Image analysis results | ~4 KB |
| `morning_briefing.json` | Daily briefing | ~2 KB |
| `smart_alerts.json` | Personalized alerts | ~9 KB |
| `safety_alerts.json` | Safety warnings | ~4 KB |
| `investment_insights.json` | Investment analysis | ~3 KB |
| `community_pulse.json` | **Enhanced** with clusters & relationships | ~7 KB |

---

## 💰 Cost Breakdown

| Agent | Cost per Run |
|-------|--------------|
| Voice Briefing | $0.0171 |
| News Analysis | $0.0022 |
| RAG Q&A | $0.0012 |
| **Community Pulse (Enhanced)** | **$0.0007** |
| Investment Insights | $0.0002 |
| Smart Alerts | $0.0001 |
| Safety Intelligence | $0.0001 |
| Others | $0.0000 |
| **TOTAL** | **$0.0215** |

**Budget**: $100 = 4,651 runs = 6.4 months (hourly)

---

## 🎯 Hackathon Scores

| Category | Score | Evidence |
|----------|-------|----------|
| Agentic AI | 10/10 | 10 agents, orchestration |
| Multimodal | 10/10 | Text, images, audio, embeddings |
| Voice AI | 7/10 | Voice generation (Nova Sonic) |
| UI Automation | 6/10 | Selenium scraping |
| **TOTAL** | **33/40** | **Strong submission!** |

---

## 🆕 What's New (Enhanced Community Pulse)

### Before:
```json
{
  "trending_topics": [...]
}
```

### After:
```json
{
  "trending_topics": [...],
  "topic_clusters": {
    "clusters": [...]
  },
  "topic_relationships": {
    "relationships": [...]
  }
}
```

### Technologies:
- **Amazon Titan Embeddings v2** - Semantic clustering
- **Amazon Nova 2 Lite** - Relationship detection

### Cost Impact:
- Before: $0.0003
- After: $0.0007
- Increase: +$0.0004 (+133%)
- Features: +200% (2 major new features)

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `HANDOFF_TO_FRIEND.md` | Frontend integration guide |
| `RAG_INTEGRATION_GUIDE.md` | Q&A system guide |
| `ENHANCED_FEATURES_COMPLETE.md` | Enhancement details |
| `DEMO_COMPARISON.md` | Before/after comparison |
| `WHATS_NEXT.md` | Action items |
| `QUICK_REFERENCE.md` | This file! |

---

## 🎤 30-Second Pitch

"CityPulse is an AI-powered civic intelligence platform using Amazon Nova and Titan. We have 10 agents that analyze news, social media, permits, and images to provide citizens with personalized insights. Our enhanced Community Pulse uses Titan Embeddings for semantic topic clustering and Nova 2 Lite for intelligent relationship detection - demonstrating true multimodal understanding. All this runs for just $0.02 per cycle, making it production-ready for any city."

---

## ❓ Judge Questions (Quick Answers)

**Q: Why embeddings?**  
A: Semantic understanding beyond keywords. "Traffic" and "congestion" are similar in meaning, embeddings detect this automatically.

**Q: Production-ready?**  
A: Yes! $0.02 per run = $15/month for hourly updates. $100 lasts 6+ months.

**Q: Multimodal?**  
A: Text (Nova Lite), Images (Nova Omni), Audio (Nova Sonic), Embeddings (Titan). 4 modalities!

**Q: Scale to other cities?**  
A: Absolutely! Just change data sources. Architecture is city-agnostic.

**Q: Data privacy?**  
A: Public data only (Reddit, news, government permits). No personal information.

**Q: What's next?**  
A: Real-time voice Q&A, Nova Act automation, mobile app, more cities.

---

## 🐛 Troubleshooting

### AWS Credentials Expired
```bash
aws configure
# Enter your credentials
```

### Import Errors
```bash
cd agents
python -m pip install -r requirements.txt
```

### Encoding Errors (Windows)
Already fixed! UTF-8 encoding is set in all files.

### Cost Tracking Not Working
Check `agents/cost_log.json` exists and is writable.

---

## 📞 Contact Info

**GitHub**: https://github.com/Hritik123789/Amazon_nova  
**AWS Region**: us-east-1  
**Python Version**: 3.8+  
**Platform**: Windows (bash shell)

---

## ✅ Pre-Submission Checklist

- [ ] Run `python agents/run_all_agents.py` successfully
- [ ] Check all 10 output files exist
- [ ] Verify `community_pulse.json` has new fields
- [ ] Test cost tracking in `cost_log.json`
- [ ] Friend has `HANDOFF_TO_FRIEND.md`
- [ ] Demo video recorded
- [ ] Presentation rehearsed
- [ ] GitHub repo cleaned
- [ ] README updated
- [ ] Ready to submit!

---

**Last Updated**: March 15, 2026  
**Status**: Production Ready ✅  
**Hackathon**: Amazon Nova Challenge  
**Team**: Ready to win! 🏆
