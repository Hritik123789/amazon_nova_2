# 🧪 Test Nova Integration NOW

## Quick 15-Minute Test ($0.02 total cost)

Let's verify everything works before the big demo.

---

## Step 1: Configure AWS (2 minutes)

```bash
# Configure AWS credentials
aws configure

# Test connection
aws sts get-caller-identity

# Should show your AWS account info
```

**Expected output**:
```json
{
    "UserId": "...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::..."
}
```

---

## Step 2: Test Nova 2 Lite - News Analysis (5 minutes)

**Cost**: ~$0.0013 (2 articles)

```bash
cd agents/news-synthesis

# Set limit to 2 articles for testing
export MAX_ARTICLES=2

# Run Nova news agent
python local_news_agent_nova.py
```

**What to look for**:
- ✅ "Connected to Amazon Bedrock"
- ✅ "Processing 2 articles"
- ✅ Cost estimate shown
- ✅ `analyzed_news_nova.json` created
- ✅ Cost logged to `cost_log.json`

**If it fails**:
- Check AWS credentials: `aws configure list`
- Verify region is `us-east-1`
- Check model access in AWS console

---

## Step 3: Test Nova 2 Lite - Bridge (3 minutes)

**Cost**: ~$0.0007 (1 investigation)

```bash
cd agents

# Set limit to 1 investigation
export MAX_INVESTIGATIONS=1

# Run Nova bridge
python bridge_to_permits_nova.py
```

**What to look for**:
- ✅ "Connected to Amazon Bedrock"
- ✅ "Processing 1 investigation"
- ✅ Location and action extracted
- ✅ `pending_investigations_nova.json` created
- ✅ Cost logged

---

## Step 4: Test Nova 2 Sonic - Voice Briefing (2 minutes)

**Cost**: ~$0.0002

```bash
cd agents

# Run voice briefing
python voice_briefing_nova.py
```

**What to look for**:
- ✅ "Connected to Amazon Bedrock"
- ✅ Briefing script generated
- ✅ `voice_briefing.txt` created
- ✅ Cost logged

---

## Step 5: Check Total Cost (1 minute)

```bash
# View cost log
cat cost_log.json

# Or use Python to sum costs
python -c "import json; logs = json.load(open('cost_log.json')); print(f'Total: ${sum(l.get(\"estimated_cost\", 0) for l in logs):.4f}')"
```

**Expected total**: ~$0.0022 (less than 1 cent!)

---

## Step 6: Test Nova 2 Omni - Image Analysis (Optional, 2 minutes)

**Cost**: ~$0.0016 per image

**Setup**:
```bash
# Create sample images folder
mkdir sample_images

# Add a test image (construction site, permit doc, etc.)
# Or download a sample:
# curl -o sample_images/construction.jpg [URL]
```

**Run**:
```bash
cd agents
python image_analysis_nova.py
```

**What to look for**:
- ✅ Image found and analyzed
- ✅ Analysis text generated
- ✅ `image_analysis_results.json` created

---

## Step 7: Skip Nova Act for Now (Save $$$)

**DON'T RUN** `web_scraper_nova_act.py` yet!

**Why**: It costs $4.75/hour. Save it for the actual demo.

**Instead**: Review the mock data in the script to see what it would return.

---

## ✅ Success Checklist

After testing, you should have:

- [ ] AWS credentials working
- [ ] Nova 2 Lite tested (news + bridge)
- [ ] Nova 2 Sonic tested (voice briefing)
- [ ] Total cost under $0.01
- [ ] `cost_log.json` created with entries
- [ ] All output JSON files generated

---

## 🎯 If Everything Works

**Congratulations!** You're ready for the full demo.

**Next steps**:
1. Review generated files
2. Practice demo script
3. Prepare sample images for Nova 2 Omni
4. Plan Nova Act demo (5 minutes max)

---

## 🚨 If Something Fails

### Error: "Failed to connect to Bedrock"

**Fix**:
```bash
# Re-configure AWS
aws configure

# Verify credentials
aws sts get-caller-identity

# Check region
aws configure get region
# Must be: us-east-1
```

### Error: "Model not found"

**Fix**:
- Go to AWS Console → Bedrock → Model access
- Request access to Nova models
- Wait for approval (usually instant)

### Error: "Access Denied"

**Fix**:
- Check IAM permissions
- Need: `bedrock:InvokeModel` permission
- Add policy: `AmazonBedrockFullAccess`

### Error: "Rate limit exceeded"

**Fix**:
- Wait 1 minute
- Reduce MAX_ARTICLES to 1
- Try again

---

## 💡 Pro Tips

### Tip 1: Use Environment Variables
```bash
# Set once, use everywhere
export MAX_ARTICLES=5
export MAX_INVESTIGATIONS=3
export DEMO_MODE=true
```

### Tip 2: Monitor Costs in Real-Time
```bash
# Watch cost log
watch -n 5 'cat cost_log.json | tail -20'
```

### Tip 3: Test in Order
1. Cheapest first (Nova 2 Lite)
2. Then moderate (Nova 2 Sonic, Omni)
3. Expensive last (Nova Act)

### Tip 4: Keep Limits Low
- Testing: 1-2 items
- Practice: 5-10 items
- Demo: 10-20 items
- Production: Unlimited (with caching)

---

## 📊 Cost Breakdown

| Test | Items | Cost | Time |
|------|-------|------|------|
| News Analysis | 2 articles | $0.0013 | 2 min |
| Bridge | 1 investigation | $0.0007 | 1 min |
| Voice Briefing | 1 script | $0.0002 | 1 min |
| Image Analysis | 1 image | $0.0016 | 1 min |
| **Total** | **5 operations** | **$0.0038** | **5 min** |

**Less than half a cent to test everything!**

---

## 🎉 Ready to Test?

```bash
# Run this complete test sequence
cd agents

# Test 1: News Analysis (2 articles)
export MAX_ARTICLES=2
python news-synthesis/local_news_agent_nova.py

# Test 2: Bridge (1 investigation)
export MAX_INVESTIGATIONS=1
python bridge_to_permits_nova.py

# Test 3: Voice Briefing
python voice_briefing_nova.py

# Check total cost
cat cost_log.json
```

**Total time**: 10 minutes  
**Total cost**: $0.0022  
**Confidence**: 100% 🚀

---

## 📞 Quick Commands Reference

```bash
# Configure AWS
aws configure

# Test connection
aws sts get-caller-identity

# List available models
aws bedrock list-foundation-models --region us-east-1

# Run minimal test
export MAX_ARTICLES=1 && python agents/news-synthesis/local_news_agent_nova.py

# Check costs
cat cost_log.json | grep estimated_cost

# Emergency: Switch to Ollama
python agents/local_news_agent_simple.py
```

---

## ✅ After Successful Test

You'll know it worked when:
1. No error messages
2. JSON files created
3. Cost logged
4. Total cost under $0.01

**Then you're ready for the full demo! 🎊**

Go to `LAST_WEEK_PLAN.md` for the complete week schedule.
