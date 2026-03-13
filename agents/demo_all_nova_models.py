"""
MASTER DEMO: All 4 Amazon Nova Models
Showcases complete CityPulse workflow using all Nova capabilities
"""

import json
import os
from datetime import datetime


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_cost_summary():
    """Print cost summary from log"""
    try:
        with open('cost_log.json', 'r') as f:
            logs = json.load(f)
        
        total_cost = sum(log.get('estimated_cost', 0) for log in logs)
        
        print_header("💰 COST SUMMARY")
        print(f"Total operations: {len(logs)}")
        print(f"Total cost: ${total_cost:.4f}")
        print(f"Remaining budget (from $100): ${100 - total_cost:.2f}")
        print()
        
        # Breakdown by model
        by_model = {}
        for log in logs:
            model = log.get('model', 'Unknown')
            cost = log.get('estimated_cost', 0)
            by_model[model] = by_model.get(model, 0) + cost
        
        print("Cost by model:")
        for model, cost in sorted(by_model.items(), key=lambda x: x[1], reverse=True):
            print(f"  {model}: ${cost:.4f}")
        
    except FileNotFoundError:
        print("⚠️  No cost log found yet")


def main():
    """Run complete demo of all 4 Nova models"""
    
    print("="*80)
    print("  🚀 CITYPULSE - COMPLETE AMAZON NOVA DEMO")
    print("  Showcasing all 4 Nova Models")
    print("="*80)
    print()
    print("This demo will run:")
    print("  1️⃣  Nova 2 Lite - News Analysis")
    print("  2️⃣  Nova 2 Lite - Bridge to Permits")
    print("  3️⃣  Nova 2 Sonic - Voice Briefing")
    print("  4️⃣  Nova 2 Omni - Image Analysis")
    print("  5️⃣  Nova Act - Web Scraping (EXPENSIVE!)")
    print()
    print("💰 Estimated total cost: ~$0.85 - $1.50 (depending on Nova Act usage)")
    print()
    
    confirm = input("Continue with full demo? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Demo cancelled")
        return
    
    print()
    
    # Step 1: News Analysis (Nova 2 Lite)
    print_header("1️⃣  STEP 1: News Analysis with Nova 2 Lite")
    print("Analyzing Mumbai news articles...")
    print("💡 Run: python agents/news-synthesis/local_news_agent_nova.py")
    print()
    
    run_step1 = input("Run Step 1 now? (yes/skip): ")
    if run_step1.lower() == 'yes':
        os.system("python agents/news-synthesis/local_news_agent_nova.py")
    else:
        print("⏭️  Skipped - using existing analyzed_news.json")
    
    print()
    input("Press Enter to continue to Step 2...")
    
    # Step 2: Bridge Processing (Nova 2 Lite)
    print_header("2️⃣  STEP 2: Bridge to Permits with Nova 2 Lite")
    print("Extracting locations and actions from permit-required articles...")
    print("💡 Run: python agents/bridge_to_permits_nova.py")
    print()
    
    run_step2 = input("Run Step 2 now? (yes/skip): ")
    if run_step2.lower() == 'yes':
        os.system("python agents/bridge_to_permits_nova.py")
    else:
        print("⏭️  Skipped")
    
    print()
    input("Press Enter to continue to Step 3...")
    
    # Step 3: Voice Briefing (Nova 2 Sonic)
    print_header("3️⃣  STEP 3: Voice Briefing with Nova 2 Sonic")
    print("Generating daily civic briefing script...")
    print("💡 Run: python agents/voice_briefing_nova.py")
    print()
    
    run_step3 = input("Run Step 3 now? (yes/skip): ")
    if run_step3.lower() == 'yes':
        os.system("python agents/voice_briefing_nova.py")
    else:
        print("⏭️  Skipped")
    
    print()
    input("Press Enter to continue to Step 4...")
    
    # Step 4: Image Analysis (Nova 2 Omni)
    print_header("4️⃣  STEP 4: Image Analysis with Nova 2 Omni")
    print("Analyzing construction site and permit images...")
    print("💡 Run: python agents/image_analysis_nova.py")
    print()
    print("⚠️  Note: Place sample images in 'sample_images/' folder first")
    print()
    
    run_step4 = input("Run Step 4 now? (yes/skip): ")
    if run_step4.lower() == 'yes':
        os.system("python agents/image_analysis_nova.py")
    else:
        print("⏭️  Skipped")
    
    print()
    input("Press Enter to continue to Step 5...")
    
    # Step 5: Web Scraping (Nova Act)
    print_header("5️⃣  STEP 5: Web Scraping with Nova Act")
    print("⚠️  WARNING: This is the MOST EXPENSIVE step!")
    print("💰 Cost: $4.75 per hour (~$0.40 for 5-minute demo)")
    print()
    print("Scraping BMC and RERA websites for permit data...")
    print("💡 Run: python agents/web_scraper_nova_act.py")
    print()
    
    run_step5 = input("Run Step 5 now? (yes/skip): ")
    if run_step5.lower() == 'yes':
        os.system("python agents/web_scraper_nova_act.py")
    else:
        print("⏭️  Skipped - recommended to use cached results for practice")
    
    # Final Summary
    print()
    print_header("✅ DEMO COMPLETE!")
    
    print("📊 Generated Files:")
    print("  - news-synthesis/analyzed_news_nova.json (Nova 2 Lite)")
    print("  - permit-monitor/pending_investigations_nova.json (Nova 2 Lite)")
    print("  - voice_briefing.txt (Nova 2 Sonic)")
    print("  - image_analysis_results.json (Nova 2 Omni)")
    print("  - scraped_data_nova_act.json (Nova Act)")
    print("  - cost_log.json (Cost tracking)")
    print()
    
    # Show cost summary
    print_cost_summary()
    
    print()
    print("="*80)
    print("  🎉 ALL 4 AMAZON NOVA MODELS DEMONSTRATED!")
    print("="*80)
    print()
    print("Next steps:")
    print("  1. Review generated files")
    print("  2. Check cost_log.json for spending")
    print("  3. Integrate with frontend")
    print("  4. Prepare Devpost submission")
    print()
    print("💡 For hackathon judges:")
    print("  - Show this complete workflow")
    print("  - Highlight cost optimization (Ollama for dev, Nova for demo)")
    print("  - Emphasize all 4 Nova models working together")
    print()


if __name__ == "__main__":
    main()
