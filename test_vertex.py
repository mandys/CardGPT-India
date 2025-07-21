#!/usr/bin/env python3
"""
Test script for Vertex AI Search functionality
Run this to verify that Vertex AI Search is working correctly,
including metadata filtering.
"""

import os
import sys
import time
from pprint import pprint
from src.vertex_retriever import VertexRetriever

def run_test():
    """
    A minimal script to test the connection and a basic query
    to your Vertex AI Search data store.
    """
    print("--- Starting Vertex AI Search Connection Test ---")

    # 1. Load Configuration from Environment Variables
    try:
        project_id = os.environ["GCP_PROJECT_ID"]
        location = os.environ["GCP_LOCATION"]
        data_store_id = os.environ["GCP_DATA_STORE_ID"]
        print(f"✅ Configuration loaded from environment.")
        print(f"   - Project ID: {project_id}")
        print(f"   - Location: {location}")
        print(f"   - Data Store ID: {data_store_id}")
    except KeyError as e:
        print(f"❌ ERROR: Environment variable {e} is not set.")
        print("   Please run the 'export' commands from the instructions.")
        return

    # 2. Initialize the Search Service Client
    try:
        retriever = VertexRetriever(
            project_id=project_id,
            location=location,
            data_store_id=data_store_id
        )
        print("✅ Successfully initialized Google Cloud client.")
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize Google Cloud client.")
        print(f"   This might be an authentication issue. Did you run 'gcloud auth application-default login'?")
        print(f"   Details: {e}")
        return

    # 3. Perform a Simple, Unfiltered Search
    print("\n🚀 Attempting a simple search with query: 'credit card'")
    try:
        response = retriever.search_similar_documents(
            query_text="credit card",
            top_k=1
        )
        print("✅ API Call Succeeded!")
        print(f"   Found {len(response)} total results.")

        if response:
            print("\n--- RAW API RESPONSE (First Result from simple search) ---")
            pprint(response[0])
        else:
            print("   ⚠️  WARNING: Simple search returned no results.")

    except Exception as e:
        print(f"❌ ERROR: The simple search failed unexpectedly.")
        print(f"   Details: {e}")
        return # Stop here if basic search fails

    # --- NEW: Test Card Filtering ---
    print("\n🎯 Testing Card Filtering...")
    test_card = "Axis Atlas"
    test_query_filtered = "welcome benefits"
    print(f"   - Query: '{test_query_filtered}'")
    print(f"   - Filter: cardName = '{test_card}'")
    
    try:
        filtered_results = retriever.search_similar_documents(
            query_text=test_query_filtered,
            top_k=3,
            card_filter=test_card
        )

        print(f"   - Found {len(filtered_results)} results for the filtered query.")
        
        if not filtered_results:
            print("   - ⚠️ WARNING: Filtered search returned no results. Cannot verify filter logic.")

        filter_passed = True
        for i, result in enumerate(filtered_results, 1):
            retrieved_card_name = result.get('cardName', 'Unknown')
            print(f"     -> Result {i}: {retrieved_card_name} (Similarity: {result.get('similarity', 0):.3f})")
            if retrieved_card_name != test_card:
                filter_passed = False
                print(f"       ❌ FAILED: Expected card '{test_card}', but got '{retrieved_card_name}'.")

        if filter_passed and filtered_results:
            print("   ✅ SUCCESS: All returned documents correctly match the card filter.")
        elif not filtered_results:
            pass # Not a failure, just a warning
        else:
            print("   ❌ FAILED: One or more documents did not match the card filter.")

    except Exception as e:
        print(f"   ❌ ERROR: Card filtering test failed with an exception: {e}")
    
    # Test different cards
    print("\n🎯 Testing Multiple Card Filters...")
    test_cards = ["Axis Atlas", "ICICI EPM", "HSBC Premier"]
    
    for card in test_cards:
        print(f"\n   Testing card: {card}")
        try:
            results = retriever.search_similar_documents(
                query_text="rewards",
                top_k=2,
                card_filter=card
            )
            print(f"   - Found {len(results)} results for {card}")
            
            if results:
                for i, result in enumerate(results, 1):
                    card_name = result.get('cardName', 'Unknown')
                    section = result.get('section', 'unknown')
                    similarity = result.get('similarity', 0)
                    print(f"     -> Result {i}: {card_name} - {section} (Similarity: {similarity:.3f})")
                    
                    if card_name != card:
                        print(f"       ❌ FAILED: Expected {card}, got {card_name}")
                    else:
                        print(f"       ✅ SUCCESS: Correct card filter")
            else:
                print(f"   - ⚠️ WARNING: No results found for {card}")
                
        except Exception as e:
            print(f"   ❌ ERROR: Test failed for {card}: {e}")
    
    # Test health check
    print("\n🏥 Testing Health Check...")
    try:
        health = retriever.health_check()
        print(f"   - Status: {health.get('status', 'unknown')}")
        print(f"   - Vertex AI Accessible: {health.get('vertex_ai_accessible', 'unknown')}")
        if 'performance_stats' in health:
            stats = health['performance_stats']
            print(f"   - Total Searches: {stats.get('total_searches', 0)}")
            print(f"   - Error Rate: {stats.get('error_rate', 0):.1%}")
            print(f"   - Service Health: {stats.get('service_health', 'unknown')}")
    except Exception as e:
        print(f"   ❌ ERROR: Health check failed: {e}")
    
    # --- END OF NEW TEST ---

if __name__ == "__main__":
    run_test()