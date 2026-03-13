# -*- coding: utf-8 -*-
"""
Migration Script: Move existing data files to centralized data/ directory
"""

import json
import os
import shutil
from datetime import datetime


def migrate_file(old_path, new_filename, description):
    """Migrate a single file to data/ directory"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    old_full_path = os.path.join(base_dir, old_path)
    new_full_path = os.path.join(base_dir, 'data', new_filename)
    
    if os.path.exists(old_full_path):
        try:
            # Copy file to new location
            shutil.copy2(old_full_path, new_full_path)
            print(f"✅ Migrated: {description}")
            print(f"   From: {old_path}")
            print(f"   To: data/{new_filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to migrate {description}: {e}")
            return False
    else:
        print(f"⚠️  Not found: {old_path}")
        return False


def main():
    print("="*70)
    print("  📦 DATA MIGRATION TO data/ DIRECTORY")
    print("="*70)
    print()
    
    # Ensure data directory exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    print(f"✓ Data directory ready: {data_dir}\n")
    
    # Migration mappings
    migrations = [
        {
            "old_path": "news-synthesis/analyzed_news.json",
            "new_filename": "news.json",
            "description": "News Analysis Data"
        },
        {
            "old_path": "permit-monitor/permit_events_real.json",
            "new_filename": "permits.json",
            "description": "Permit Events Data"
        },
        {
            "old_path": "social-listening/collected_social_nova.json",
            "new_filename": "social.json",
            "description": "Social Listening Data"
        },
        {
            "old_path": "../image_analysis_results.json",
            "new_filename": "images.json",
            "description": "Image Analysis Data"
        },
        {
            "old_path": "features/safety_intelligence.json",
            "new_filename": "safety_alerts.json",
            "description": "Safety Intelligence Alerts"
        },
        {
            "old_path": "features/morning_briefing.json",
            "new_filename": "morning_briefing.json",
            "description": "Morning Briefing Data"
        },
        {
            "old_path": "features/smart_alerts.json",
            "new_filename": "smart_alerts.json",
            "description": "Smart Alerts Data"
        }
    ]
    
    # Perform migrations
    success_count = 0
    for migration in migrations:
        if migrate_file(
            migration["old_path"],
            migration["new_filename"],
            migration["description"]
        ):
            success_count += 1
        print()
    
    # Summary
    print("="*70)
    print("  📊 MIGRATION SUMMARY")
    print("="*70)
    print(f"Successfully migrated: {success_count}/{len(migrations)} files")
    print()
    
    # List data directory contents
    print("Data directory contents:")
    if os.path.exists(data_dir):
        files = os.listdir(data_dir)
        if files:
            for f in sorted(files):
                filepath = os.path.join(data_dir, f)
                size = os.path.getsize(filepath)
                print(f"  - {f} ({size:,} bytes)")
        else:
            print("  (empty)")
    
    print()
    print("✅ Migration complete!")
    print()
    print("Next steps:")
    print("1. Test each agent to verify they work with new paths")
    print("2. Update remaining agents with refactored code")
    print("3. Remove old data files once verified")


if __name__ == "__main__":
    main()
