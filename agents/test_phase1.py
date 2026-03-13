#!/usr/bin/env python3
"""
Phase 1 Testing Script
Tests all existing Nova agents with minimal data
Cost: ~$0.01
"""

import os
import sys
import json
import subprocess
from datetime import datetime

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def test_aws_credentials():
    """Test AWS credentials are configured"""
    print_header("Step 1: Testing AWS Credentials")
    
    try:
        result = subprocess.run(
            ['aws', 'sts', 'get-caller-identity'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            identity = json.loads(result.stdout)
            print("✅ AWS Credentials Valid")
            print(f"   Account: {identity.get('Account', 'Unknown')}")
            print(f"   User: {identity.get('Arn', 'Unknown').split('/')[-1]}")
            return True
        else:
            print("❌ AWS Credentials Invalid")
            print(f"   Error: {result.stderr}")
            print("\n💡 Run: aws configure")
            return False
            
    except FileNotFoundError:
        print("❌ AWS CLI not installed")
        print("💡 Install: pip install awscli")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_news_agent():
    """Test News Analysis Agent (Nova 2 Lite)"""
    print_header("Step 2: Testing News Analysis Agent (Nova 2 Lite)")
    
    print("📰 Testing with 2 articles...")
    print("💰 Estimated cost: $0.0013\n")
    
    # Set environment variables
    os.environ['MAX_ARTICLES'] = '2'
    os.environ['DEMO_MODE'] = 'true'
    
    try:
        result = subprocess.run(
            [sys.executable, 'news-synthesis/local_news_agent_nova.py'],
            capture_output=True,
            text=True,
            timeout=120,
            cwd='agents'
        )
        
        if result.returncode == 0:
            print("✅ News Agent Completed Successfully")
            
            # Check output file
            output_file = 'agents/news-synthesis/analyzed_news_nova.json'
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    data = json.load(f)
                print(f"   Articles analyzed: {len(data)}")
                print(f"   Output: {output_file}")
            
            return True
        else:
            print("❌ News Agent Failed")
            print(f"   Error: {result.stderr[-500:]}")  # Last 500 chars
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ News Agent Timeout (>2 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_bridge_agent():
    """Test Bridge Agent (Nova 2 Lite)"""
    print_header("Step 3: Testing Bridge Agent (Nova 2 Lite)")
    
    print("🌉 Testing with 1 investigation...")
    print("💰 Estimated cost: $0.0005\n")
    
    # Set environment variables
    os.environ['MAX_INVESTIGATIONS'] = '1'
    os.environ['DEMO_MODE'] = 'true'
    
    try:
        result = subprocess.run(
            [sys.executable, 'bridge_to_permits_nova.py'],
            capture_output=True,
            text=True,
            timeout=120,
            cwd='agents'
        )
        
        if result.returncode == 0:
            print("✅ Bridge Agent Completed Successfully")
            
            # Check output file
            output_file = 'agents/permit-monitor/pending_investigations_nova.json'
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    data = json.load(f)
                print(f"   Investigations created: {len(data)}")
                print(f"   Output: {output_file}")
            
            return True
        else:
            print("❌ Bridge Agent Failed")
            print(f"   Error: {result.stderr[-500:]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Bridge Agent Timeout (>2 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_voice_agent():
    """Test Voice Briefing Agent (Nova 2 Sonic)"""
    print_header("Step 4: Testing Voice Briefing Agent (Nova 2 Sonic)")
    
    print("🎙️  Generating voice briefing...")
    print("💰 Estimated cost: $0.0002\n")
    
    try:
        result = subprocess.run(
            [sys.executable, 'voice_briefing_nova.py'],
            capture_output=True,
            text=True,
            timeout=120,
            cwd='agents'
        )
        
        if result.returncode == 0:
            print("✅ Voice Agent Completed Successfully")
            
            # Check output file
            output_file = 'agents/voice_briefing.txt'
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    content = f.read()
                print(f"   Briefing length: {len(content)} characters")
                print(f"   Output: {output_file}")
            
            return True
        else:
            print("❌ Voice Agent Failed")
            print(f"   Error: {result.stderr[-500:]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Voice Agent Timeout (>2 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_cost_log():
    """Check total cost from cost_log.json"""
    print_header("Step 5: Cost Summary")
    
    try:
        cost_file = 'agents/cost_log.json'
        if os.path.exists(cost_file):
            with open(cost_file, 'r') as f:
                logs = json.load(f)
            
            total_cost = sum(log.get('estimated_cost', 0) for log in logs)
            
            print(f"💰 Total operations: {len(logs)}")
            print(f"💰 Total cost: ${total_cost:.4f}")
            print(f"💰 Remaining budget: ${100 - total_cost:.2f}")
            
            if total_cost < 0.02:
                print("\n✅ Cost is under $0.02 - Perfect!")
            else:
                print(f"\n⚠️  Cost is ${total_cost:.4f} - Higher than expected")
            
            return True
        else:
            print("⚠️  No cost_log.json found")
            print("   Agents may not have run successfully")
            return False
            
    except Exception as e:
        print(f"❌ Error reading cost log: {str(e)}")
        return False

def main():
    """Run all Phase 1 tests"""
    print("="*70)
    print("  🚀 PHASE 1 TESTING - Nova Agent Verification")
    print("="*70)
    print("\nThis will test all existing Nova agents with minimal data")
    print("Expected cost: ~$0.01")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        return
    
    results = {
        'aws_credentials': False,
        'news_agent': False,
        'bridge_agent': False,
        'voice_agent': False,
        'cost_check': False
    }
    
    # Run tests
    results['aws_credentials'] = test_aws_credentials()
    
    if not results['aws_credentials']:
        print("\n❌ Cannot proceed without valid AWS credentials")
        print("💡 Run: aws configure")
        return
    
    results['news_agent'] = test_news_agent()
    results['bridge_agent'] = test_bridge_agent()
    results['voice_agent'] = test_voice_agent()
    results['cost_check'] = check_cost_log()
    
    # Final summary
    print_header("PHASE 1 TEST SUMMARY")
    
    for test_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\n📊 Results: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Phase 1 Complete - Ready for Phase 2")
        print("\n📝 Next: Update YOUR_NEXT_TASKS.md")
        print("   Mark Phase 1, Task 1.1 as complete ✅")
    else:
        print("\n⚠️  Some tests failed")
        print("💡 Check error messages above")
        print("💡 Read TEST_NOVA_NOW.md for troubleshooting")

if __name__ == "__main__":
    main()
