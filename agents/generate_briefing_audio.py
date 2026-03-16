#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate audio for morning briefing using Amazon Polly
"""

import json
import os
import sys
import re
import boto3

def generate_briefing_audio():
    """Generate audio file from morning briefing JSON"""
    
    # Load briefing data
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    briefing_file = os.path.join(data_dir, 'morning_briefing.json')
    
    if not os.path.exists(briefing_file):
        print(f"❌ Briefing file not found: {briefing_file}")
        return False
    
    with open(briefing_file, 'r', encoding='utf-8') as f:
        briefing = json.load(f)
    
    # Get text content
    text_content = briefing.get('text_content', '')
    
    if not text_content:
        print("❌ No text content in briefing")
        return False
    
    # Clean text for TTS (remove markdown)
    clean_text = re.sub(r'\*\*', '', text_content)
    clean_text = clean_text.strip()
    
    print(f"📝 Text length: {len(clean_text)} characters")
    print(f"📝 First 100 chars: {clean_text[:100]}...")
    print()
    
    # Initialize Polly
    try:
        polly = boto3.client('polly', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        print("✓ Connected to Amazon Polly")
    except Exception as e:
        print(f"❌ Failed to connect to Polly: {e}")
        return False
    
    # Generate speech
    try:
        print("🎙️ Generating audio with Amazon Polly Neural TTS...")
        response = polly.synthesize_speech(
            Text=clean_text,
            OutputFormat='mp3',
            VoiceId='Matthew',
            Engine='neural'
        )
        
        # Save audio file
        audio_data = response['AudioStream'].read()
        audio_file = os.path.join(data_dir, 'morning_briefing.mp3')
        
        with open(audio_file, 'wb') as f:
            f.write(audio_data)
        
        file_size = len(audio_data) / 1024  # KB
        print(f"✓ Audio generated: {audio_file}")
        print(f"✓ File size: {file_size:.1f} KB")
        print(f"✓ Duration: ~{briefing.get('duration_estimate_seconds', 0):.0f} seconds")
        print()
        print("✅ SUCCESS! Audio file ready for playback")
        return True
        
    except Exception as e:
        print(f"❌ Error generating audio: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("="*70)
    print("  🎙️ MORNING BRIEFING AUDIO GENERATOR")
    print("="*70)
    print()
    
    success = generate_briefing_audio()
    
    if not success:
        sys.exit(1)
