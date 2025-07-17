#!/usr/bin/env python3
"""
Test script for FastAPI backend
Tests all API endpoints and basic functionality
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_endpoint(name, url, method="GET", data=None, expected_status=200):
    """Test a single endpoint"""
    try:
        print(f"Testing {name}...")
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == expected_status:
            print(f"✅ {name} - Status: {response.status_code}")
            return True, response.json()
        else:
            print(f"❌ {name} - Status: {response.status_code}, Expected: {expected_status}")
            print(f"   Response: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {name} - Connection Error: {e}")
        return False, None

def main():
    """Run all tests"""
    print("🚀 Testing Credit Card Assistant FastAPI Backend")
    print("=" * 50)
    
    results = []
    
    # Test 1: Root endpoint
    success, data = test_endpoint("Root Endpoint", BASE_URL)
    results.append(success)
    
    # Test 2: Health check
    success, data = test_endpoint("Health Check", f"{API_BASE}/health")
    results.append(success)
    
    # Test 3: Configuration
    success, config_data = test_endpoint("Configuration", f"{API_BASE}/config")
    results.append(success)
    
    # Test 4: Models
    success, data = test_endpoint("Models", f"{API_BASE}/models")
    results.append(success)
    
    # Test 5: Cards
    success, data = test_endpoint("Cards", f"{API_BASE}/cards")
    results.append(success)
    
    # Test 6: Chat endpoint (if we have config)
    if config_data:
        available_models = config_data.get("available_models", [])
        if available_models:
            model_name = available_models[0]["name"]
            chat_data = {
                "message": "What are the annual fees for credit cards?",
                "model": model_name,
                "query_mode": "General Query",
                "top_k": 3
            }
            success, data = test_endpoint("Chat", f"{API_BASE}/chat", "POST", chat_data)
            results.append(success)
        else:
            print("⚠️  Skipping chat test - no models available")
            results.append(False)
    else:
        print("⚠️  Skipping chat test - no config data")
        results.append(False)
    
    # Test 7: Query enhancement (optional)
    enhance_data = {
        "query": "How many miles for flight spend?"
    }
    success, data = test_endpoint("Query Enhancement", f"{API_BASE}/query/enhance", "POST", enhance_data)
    results.append(success)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Backend is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())