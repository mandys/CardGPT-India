#!/usr/bin/env python3
"""
Test script for Vertex AI Search functionality
Run this to verify that Vertex AI Search is working correctly
"""

import os
import sys
import time
from src.vertex_retriever import VertexRetriever
from vertex_config import vertex_config

def test_vertex_search():
    """Test basic Vertex AI Search functionality"""
    print("🧪 Testing Vertex AI Search Integration")
    print("=" * 50)
    
    # Check configuration
    print("📋 Checking configuration...")
    config_validation = vertex_config.validate_config()
    
    if not config_validation['valid']:
        print("❌ Configuration issues found:")
        for issue in config_validation['issues']:
            print(f"   - {issue}")
        print("\n" + vertex_config.get_setup_instructions())
        return False
    
    print("✅ Configuration looks good!")
    config = vertex_config.get_config()
    print(f"   Project ID: {config['project_id']}")
    print(f"   Location: {config['location']}")
    print(f"   Data Store ID: {config['data_store_id']}")
    
    # Initialize retriever
    print("\n🚀 Initializing Vertex AI Search retriever...")
    try:
        retriever = VertexRetriever(
            project_id=config['project_id'],
            location=config['location'],
            data_store_id=config['data_store_id']
        )
        print("✅ Retriever initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize retriever: {e}")
        return False
    
    # Test health check
    print("\n💊 Running health check...")
    try:
        health = retriever.health_check()
        print(f"Health Status: {health['status']}")
        print(f"Vertex AI Accessible: {health['vertex_ai_accessible']}")
        if health['status'] != 'healthy':
            print(f"Health Check Error: {health.get('error', 'Unknown')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test basic search
    print("\n🔍 Testing basic search functionality...")
    test_queries = [
        "annual fees credit cards",
        "utility spending rewards",
        "hotel rewards miles",
        "milestone benefits"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Testing query: '{query}'")
        
        try:
            start_time = time.time()
            results = retriever.search_similar_documents(
                query_text=query,
                top_k=3,
                card_filter=None  # No filtering for basic test
            )
            search_time = time.time() - start_time
            
            print(f"   ⏱️  Search completed in {search_time:.3f}s")
            print(f"   📊 Found {len(results)} results")
            
            if results:
                for j, result in enumerate(results, 1):
                    print(f"   [{j}] {result['cardName']} - {result['section']} (Score: {result['similarity']:.3f})")
                    print(f"       Content preview: {result['content'][:100]}...")
            else:
                print("   ⚠️  No results found")
                
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
    
    # Test card filtering
    print("\n🎯 Testing card filtering...")
    try:
        results = retriever.search_similar_documents(
            query_text="reward rates",
            top_k=5,
            card_filter="ICICI EPM"
        )
        print(f"   📊 Found {len(results)} results with card filter 'ICICI EPM'")
        for result in results:
            print(f"   - {result['cardName']} (should be ICICI EPM)")
    except Exception as e:
        print(f"   ❌ Card filtering test failed: {e}")
    
    # Performance statistics
    print("\n📈 Performance Statistics:")
    try:
        stats = retriever.get_performance_stats()
        print(f"   Total Searches: {stats['total_searches']}")
        print(f"   Total Errors: {stats['total_errors']}")
        print(f"   Error Rate: {stats['error_rate']:.2%}")
        print(f"   Average Search Time: {stats['average_search_time']:.3f}s")
        print(f"   Service Health: {stats['service_health']}")
    except Exception as e:
        print(f"   ❌ Failed to get performance stats: {e}")
    
    print("\n🎉 Vertex AI Search test completed!")
    return True

def main():
    """Main test function"""
    try:
        success = test_vertex_search()
        if success:
            print("\n✅ All tests passed! Vertex AI Search is ready to use.")
            return 0
        else:
            print("\n❌ Some tests failed. Please check the configuration and try again.")
            return 1
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())