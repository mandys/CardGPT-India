#!/usr/bin/env python3
"""
Check available Gemini models with current API key
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    print("❌ GEMINI_API_KEY not found")
    exit(1)

try:
    genai.configure(api_key=gemini_api_key)
    
    print("🔍 Available Gemini models:")
    models = genai.list_models()
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  ✅ {model.name}")
            if 'flash' in model.name.lower() or '2.5' in model.name:
                print(f"      👆 CANDIDATE for Flash/2.5 models")
    
    # Test specific model names
    test_models = [
        "models/gemini-2.0-flash-thinking-exp-01-21",  # Our current mapping
        "models/gemini-2.5-flash-lite",                # Direct name
        "models/gemini-flash-thinking-exp",            # Alternative
    ]
    
    print("\n🧪 Testing specific model names:")
    for model_name in test_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say 'test'")
            print(f"  ✅ {model_name} - WORKS")
        except Exception as e:
            print(f"  ❌ {model_name} - ERROR: {str(e)[:100]}")

except Exception as e:
    print(f"❌ API Error: {e}")