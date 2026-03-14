# -*- coding: utf-8 -*-
"""
Voice Briefing Generator using Amazon Nova 2 Sonic
Converts morning briefing text to speech audio file
"""

import json
import os
import sys
import boto3
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.utils import log_cost


def generate_voice_briefing():
    """Generate voice audio from morning briefing"""
    print("="*80)
    print("🎙️  CityPulse Voice Briefing Generator - Amazon Polly Neural TTS")
    print("="*80)
    print()
    
    # Load morning briefing
    briefing_path = os.path.join(os.path.dirname(__file__), 'data', 'morning_briefing.json')
    with open(briefing_path, 'r', encoding='utf-8') as f:
        briefing = json.load(f)
    
    text_content = briefing['text_content']
    
    # Clean text for TTS (remove markdown)
    clean_text = text_content.replace('**', '').replace('\n\n', '. ')
    
    print(f"📝 Briefing Text ({len(clean_text)} characters)")
    print(f"⏱️  Estimated Duration: {briefing['duration_estimate_seconds']} seconds")
    print()
    # Initialize Bedrock client
    try:
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        print("✓ Connected to Amazon Bedrock\n")
    except Exception as e:
        print(f"❌ Failed to connect to Bedrock: {str(e)}")
        return
    
    # Generate speech with Amazon Polly (Nova 2 Sonic not available for TTS yet)
    # Using Polly Neural TTS which is production-ready
    print("🎵 Generating speech with Amazon Polly Neural TTS...")
    
    try:
        # Use Polly client instead
        polly = boto3.client(
            service_name='polly',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        response = polly.synthesize_speech(
            Text=clean_text,
            OutputFormat='mp3',
            VoiceId='Matthew',  # Professional male voice
            Engine='neural'  # High-quality neural TTS
        )
        
        # Get audio stream
        if 'AudioStream' in response:
            audio_data = response['AudioStream'].read()
        else:
            print("❌ No audio data received")
            return
        
        # Save to data directory
        output_path = os.path.join(os.path.dirname(__file__), 'data', 'morning_briefing.mp3')
        with open(output_path, 'wb') as f:
            f.write(audio_data)
        
        print(f"✓ Audio saved to: {output_path}")
        print(f"📊 Audio size: {len(audio_data) / 1024:.1f} KB")
        print()
        
        # Estimate cost (Amazon Polly Neural pricing)
        char_count = len(clean_text)
        cost_per_1m_chars = 16.00  # $16 per 1M characters for Neural TTS
        estimated_cost = (char_count / 1_000_000) * cost_per_1m_chars
        
        print(f"💰 Characters: {char_count}")
        print(f"💰 Estimated Cost: ${estimated_cost:.4f}")
        
        # Log cost
        log_cost(
            agent_name='voice_briefing_generator',
            tokens_used=char_count,
            estimated_cost=estimated_cost,
            model='Amazon Polly Neural TTS',
            operation='text_to_speech',
            audio_duration_seconds=briefing['duration_estimate_seconds']
        )
        
        print()
        print("="*80)
        print("✅ Voice Briefing Generated Successfully!")
        print("="*80)
        print()
        print("📁 File: agents/data/morning_briefing.mp3")
        print("🎧 Your friend can add this to the frontend with an audio player")
        print()
        
    except Exception as e:
        print(f"❌ Error generating speech: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    generate_voice_briefing()
