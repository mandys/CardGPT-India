#!/usr/bin/env python3
"""
Test script to verify end-to-end preference flow
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_preference_flow():
    """Test the complete preference flow"""
    
    print("🧪 Testing preference flow...")
    
    # Step 1: Test streaming endpoint with mock JWT token
    print("\n1. Testing streaming endpoint with authorization header...")
    
    streaming_payload = {
        "message": "best card for travel",
        "model": "gemini-2.5-flash-lite",
        "query_mode": "General Query",
        "card_filter": None,
        "top_k": 8,
        "user_preferences": {
            "travel_type": "domestic",
            "lounge_access": "family",
            "fee_willingness": "5000-10000"
        },
        "session_id": "test_session_123"
    }
    
    # Simulate JWT token (this would be invalid but tests header passing)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token_for_header_testing"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/stream",
            headers=headers,
            json=streaming_payload,
            stream=True,
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers sent: {headers}")
        
        if response.status_code == 200:
            print("   ✅ Streaming endpoint accepts authorization header")
            
            # Read first few chunks to see logs
            chunk_count = 0
            for line in response.iter_lines():
                if line and chunk_count < 5:  # Just read first few chunks
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str != '[DONE]':
                            try:
                                chunk_data = json.loads(data_str)
                                print(f"   Chunk {chunk_count}: {chunk_data.get('type', 'unknown')}")
                                chunk_count += 1
                            except json.JSONDecodeError:
                                pass
                if chunk_count >= 5:
                    break
                    
        else:
            print(f"   ❌ Streaming endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error testing streaming endpoint: {e}")
    
    print("\n✅ Test completed - check backend logs for detailed preference flow")

if __name__ == "__main__":
    test_preference_flow()