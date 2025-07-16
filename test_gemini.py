#!/usr/bin/env python3
"""
Test Gemini API connection
"""
import os

def test_gemini():
    print("=== Testing Gemini API Setup ===\n")
    
    try:
        import google.generativeai as genai
        print("✓ google-generativeai package is installed")
    except ImportError:
        print("✗ google-generativeai package NOT installed")
        print("  Run: pip install google-generativeai")
        return False
    
    # Configure API key
    api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyBC4m0pBy8t6D1Q0OAdzPGJ0m8ZAdXr7o0')
    print(f"\n✓ Using API key: {api_key[:10]}...")
    
    try:
        genai.configure(api_key=api_key)
        
        # List available models
        print("\n✓ Available Gemini models:")
        models = genai.list_models()
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
        
        # Test simple generation
        print("\n✓ Testing text generation...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say 'UFO2 connection test successful!' and nothing else.")
        print(f"  Response: {response.text}")
        
        print("\n✓ Gemini API is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error testing Gemini API: {str(e)}")
        return False

if __name__ == "__main__":
    test_gemini()