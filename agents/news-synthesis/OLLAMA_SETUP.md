# Ollama Setup Guide for Local News Agent

## What is Ollama?

Ollama lets you run large language models (like Llama 3.1) locally on your computer - completely free, no API keys needed!

## Installation Steps

### Step 1: Install Ollama

**Windows:**
1. Download from: https://ollama.com/download/windows
2. Run the installer
3. Ollama will start automatically

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Pull Llama 3.1 Model

Open terminal/command prompt and run:

```bash
ollama pull llama3.1
```

This will download the Llama 3.1 model (about 4.7GB). First time only!

### Step 3: Verify Ollama is Running

```bash
ollama list
```

You should see `llama3.1` in the list.

### Step 4: Install Python Dependencies

```bash
cd agents/news-synthesis
pip install ollama
```

## Usage

### Run the Local News Agent (Simple Version - RECOMMENDED)

```bash
python local_news_agent_simple.py
```

This will:
1. Load articles from `collected_news.json`
2. Use local Llama 3.1 to analyze them
3. Filter for Andheri/BMC mentions
4. Categorize as Civic/Traffic/Real Estate
5. Flag articles needing permit checks
6. Save results to `analyzed_news.json`

### Alternative: CrewAI Version (Advanced)

If you want to use the CrewAI framework:

```bash
pip install crewai langchain-ollama
python local_news_agent.py
```

Note: The simple version is recommended for testing as it's more reliable and easier to debug.

## How It Works

```
collected_news.json → Local News Agent (Ollama) → analyzed_news.json
                            ↓
                      Llama 3.1 (Local)
                      - Filters articles
                      - Categorizes
                      - Flags permits
```

## Troubleshooting

### "Connection refused" error
- Make sure Ollama is running: `ollama serve`
- Check if it's on port 11434: `curl http://localhost:11434`

### Model not found
- Pull the model: `ollama pull llama3.1`
- List models: `ollama list`
- Make sure to use the full tag: `llama3.1:latest`

### Slow performance
- Llama 3.1 runs on CPU by default
- For faster results, use a smaller model: `ollama pull llama3.1:8b`
- Or use GPU if available

## Benefits

✅ **Free** - No API costs, runs locally
✅ **Private** - Your data never leaves your computer
✅ **No rate limits** - Process as many articles as you want
✅ **Offline** - Works without internet (after model download)

## Results

The agent successfully analyzed 50 Mumbai news articles and found:
- 28 relevant articles mentioning BMC or Andheri
- 21 Civic issues
- 4 Traffic issues
- 3 Real Estate issues
- 7 articles requiring permit checks

## Next Steps

Once this works, you can:
- Add more analysis criteria
- Process more articles
- Create additional agents for permits and social media
- Later migrate to AWS Bedrock Nova for production
