#!/usr/bin/env python3
"""
Test Gemini 2.5 Flash-Lite with actual query
"""
import os
from dotenv import load_dotenv
from services.llm import LLMService

load_dotenv()

# Test the exact query that failed
test_query = "For a yearly spend of 7.5L on Atlas, how many miles i earn? include the points that i earn on milestone as well and give me total for 7.5L spend"
test_documents = [
    {
        "cardName": "Axis Bank Atlas Credit Card",
        "section": "reward_earning",
        "content": "Base rate: 2 miles per ₹100 spend. Hotels: 5 miles per ₹100. Milestone: ₹15L = 25K miles."
    }
]

try:
    llm = LLMService(os.getenv('GEMINI_API_KEY'))
    print(f"✅ LLM Service initialized. Gemini available: {llm.gemini_available}")
    
    if llm.gemini_available:
        print("\n🧪 Testing Gemini 2.5 Flash-Lite...")
        
        # Test with streaming
        def print_chunk(chunk):
            print(chunk, end='', flush=True)
            
        print("📝 Response:")
        full_response = ""
        for chunk_text, is_final, metadata in llm.generate_answer_stream(
            question=test_query,
            context_documents=test_documents,
            model_choice="gemini-2.5-flash-lite"
        ):
            print(chunk_text, end='', flush=True)
            full_response += chunk_text
        
        print(f"\n\n📊 Success! Generated {len(full_response)} characters")
        print(f"  Model: gemini-2.5-flash-lite")
        
    else:
        print("❌ Gemini not available")

except Exception as e:
    print(f"❌ Error: {e}")