"""
Test the complete workflow from News Agent to Permit Monitor
"""

import json

print("="*80)
print("🔄 COMPLETE WORKFLOW TEST")
print("="*80)
print()

# Step 1: News Agent Output
print("📰 Step 1: News Agent Output")
print("-" * 80)
with open('news-synthesis/analyzed_news.json', 'r', encoding='utf-8') as f:
    analyzed = json.load(f)

total_articles = len(analyzed)
permit_needed = sum(1 for a in analyzed if a.get('permit_check_required'))

print(f"Total articles analyzed: {total_articles}")
print(f"Articles needing permit checks: {permit_needed}")
print()

# Step 2: Bridge Processing
print("🌉 Step 2: Bridge to Permits")
print("-" * 80)
print("Bridge script extracts:")
print("  - Location (AI-powered)")
print("  - Action type (AI-powered)")
print("  - Priority (calculated)")
print("  - RERA check (for Real Estate)")
print()

# Step 3: Permit Monitor Output
print("🔍 Step 3: Permit Monitor Investigations")
print("-" * 80)
with open('permit-monitor/pending_investigations.json', 'r', encoding='utf-8') as f:
    investigations = json.load(f)

total_inv = len(investigations)
high = sum(1 for i in investigations if i['priority'] == 'HIGH')
medium = sum(1 for i in investigations if i['priority'] == 'MEDIUM')
low = sum(1 for i in investigations if i['priority'] == 'LOW')

print(f"Total investigations created: {total_inv}")
print(f"  🔴 High Priority: {high}")
print(f"  🟡 Medium Priority: {medium}")
print(f"  🟢 Low Priority: {low}")
print()

# Show sample investigation
if investigations:
    print("📋 Sample Investigation:")
    print("-" * 80)
    sample = investigations[0]
    print(f"ID: {sample['investigation_id']}")
    print(f"Title: {sample['title']}")
    print(f"Location: {sample['location']}")
    print(f"Action: {sample['action']}")
    print(f"Priority: {sample['priority']}")
    print(f"Category: {sample['category']}")
    print(f"Relevance: {sample['relevance_score']}/10")
    print()

print("="*80)
print("✅ Workflow Complete!")
print("="*80)
print()
print("Data Flow:")
print("  News Agent → analyzed_news.json")
print("  Bridge → pending_investigations.json")
print("  Permit Monitor → (ready to process)")
