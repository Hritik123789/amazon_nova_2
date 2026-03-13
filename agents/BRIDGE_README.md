# Bridge to Permits - Agent Integration

## Overview

The `bridge_to_permits.py` script connects the **News Agent** output to the **Permit Monitor Agent**, creating a seamless data flow for permit investigations.

## What It Does

1. **Loads** analyzed news from `news-synthesis/analyzed_news.json`
2. **Filters** articles where `permit_check_required` is `True`
3. **Extracts** location and action type using AI (Ollama)
4. **Generates** structured investigation tasks for the Permit Monitor Agent
5. **Performs** mock RERA checks for Real Estate projects
6. **Saves** investigations to `permit-monitor/pending_investigations.json`

## Data Flow

```
News Agent (analyzed_news.json)
         ↓
   Bridge Script
         ↓
  - Filter permit_check_required
  - Extract Location (AI)
  - Extract Action (AI)
  - Calculate Priority
  - Mock RERA Check
         ↓
Permit Monitor Agent (pending_investigations.json)
```

## Usage

### Basic Usage

```bash
cd agents
python bridge_to_permits.py
```

### With Ollama (Recommended)

The script uses Ollama by default for intelligent location and action extraction:

```bash
# Make sure Ollama is running
ollama list

# Run the bridge
python bridge_to_permits.py
```

### Without Ollama (Fallback)

If Ollama is not available, the script falls back to simple keyword matching.

## Output

### Console Output

The script prints a detailed summary:

- **Total investigations** found
- **Priority breakdown** (High/Medium/Low)
- **Detailed information** for each investigation:
  - Location
  - Action type
  - Category
  - Relevance score
  - RERA status (for Real Estate)
  - Source URL

### File Output

Creates `permit-monitor/pending_investigations.json` with structured data:

```json
{
  "investigation_id": "INV-041",
  "source": "News Agent",
  "title": "Sion ROB may be thrown open by August",
  "location": "Sion",
  "action": "Infrastructure Project",
  "priority": "MEDIUM",
  "category": "Civic",
  "relevance_score": 8,
  "news_url": "https://...",
  "created_at": "2026-03-09T22:36:57.591253",
  "status": "Pending Investigation",
  "rera_check": null
}
```

## Features

### 1. AI-Powered Location Extraction

Uses Ollama to intelligently extract specific Mumbai locations:
- Andheri, Bandra, Juhu, Thane, Goregaon, etc.
- Falls back to "Mumbai (General)" if no specific location

### 2. AI-Powered Action Classification

Identifies the type of construction/development:
- Redevelopment
- New Construction
- Infrastructure Project
- Road Work
- Metro Project
- Demolition
- Other

### 3. Priority Calculation

Automatically assigns priority based on:
- **HIGH**: Relevance ≥8 AND Real Estate category
- **MEDIUM**: Relevance ≥7
- **LOW**: Relevance <7

### 4. Mock RERA Agent

For Real Estate projects, performs a mock RERA check:
- Registration status
- Developer information
- Compliance issues
- Recommendations

Example RERA check output:
```json
{
  "rera_registered": false,
  "registration_number": null,
  "developer_name": "Unknown",
  "project_status": "Under Investigation",
  "compliance_issues": [
    "Redevelopment project - verify existing tenant rights"
  ],
  "recommendation": "Requires manual verification"
}
```

### 5. Fraud Detection

Automatically flags articles mentioning fraud or illegal activity:
```
⚠️ ALERT: Potential fraud/illegal activity mentioned
🚨 URGENT: Immediate investigation required
```

## Example Output

```
================================================================================
🚨 HIGH PRIORITY INVESTIGATIONS FOR PERMIT MONITOR AGENT
================================================================================

📊 Summary:
  Total Investigations: 7
  🔴 High Priority: 0
  🟡 Medium Priority: 3
  🟢 Low Priority: 4

================================================================================
🟡 MEDIUM PRIORITY INVESTIGATIONS
================================================================================

INV-041: Sion ROB may be thrown open by August
  📍 Location: Sion
  🏗️  Action: Infrastructure Project
  📂 Category: Civic
  ⭐ Relevance: 8/10
  🔗 Source: https://www.hindustantimes.com/...
```

## Integration with Permit Monitor Agent

The Permit Monitor Agent can now:

1. Load `pending_investigations.json`
2. Process each investigation
3. Cross-reference with permit databases
4. Flag discrepancies
5. Generate alerts for citizens

## Improvements Made

### Fixed "Mentions" Bug

The original `local_news_agent_simple.py` had a bug where it used simple string matching for mentions. This has been fixed:

**Before:**
```python
# Simple string matching - missed "Mumbai civic chief" = BMC
if 'bmc' in title.lower():
    mentions_list.append('BMC')
```

**After:**
```python
# AI determines mentions intelligently
ENTITIES: comma-separated list (e.g., BMC, Andheri, MHADA, BEST)
```

Now the AI can recognize:
- "Mumbai civic chief" → BMC
- "Brihanmumbai Municipal Corporation" → BMC
- "civic body" → BMC
- And other implicit references

## Next Steps

1. **Real RERA Integration**: Replace mock RERA check with actual RERA API
2. **BMC Permit API**: Integrate with real BMC permit database
3. **Automated Alerts**: Send notifications for high-priority investigations
4. **Dashboard Integration**: Display investigations in frontend
5. **AWS Bedrock Nova**: Migrate from Ollama to Nova for production

## Files Created

```
agents/
├── bridge_to_permits.py ✅
├── BRIDGE_README.md ✅
├── news-synthesis/
│   └── analyzed_news.json (input)
└── permit-monitor/
    └── pending_investigations.json (output)
```

## Dependencies

- `ollama` - For AI-powered extraction
- `json` - For data handling
- `re` - For pattern matching
- `datetime` - For timestamps

## Testing

```bash
# Test with current analyzed news
cd agents
python bridge_to_permits.py

# Check output
cat permit-monitor/pending_investigations.json
```

## Benefits

✅ **Automated** - No manual filtering needed
✅ **Intelligent** - AI extracts location and action
✅ **Structured** - Clean JSON output for downstream agents
✅ **Prioritized** - Automatic priority assignment
✅ **Traceable** - Links back to original news source
✅ **Extensible** - Easy to add more checks (RERA, BMC, etc.)
