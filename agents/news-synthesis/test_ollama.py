"""
Simple test to verify Ollama connection
"""

import ollama

print("Testing Ollama connection...")

try:
    response = ollama.chat(
        model='llama3.1:latest',
        messages=[{
            'role': 'user',
            'content': 'Say hello in one sentence.'
        }]
    )
    
    print("\n✓ Ollama is working!")
    print(f"Response: {response['message']['content']}")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
