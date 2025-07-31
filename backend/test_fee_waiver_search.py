#!/usr/bin/env python3
"""
Test fee waiver search to verify HDFC Infinia data is retrievable
"""

import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_fee_waiver_search():
    """Test fee waiver search with enhanced query"""
    
    try:
        from services.vertex_retriever import VertexRetriever
        
        # Initialize retriever
        gcp_project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        gcp_location = os.getenv("VERTEX_AI_LOCATION", "global")
        gcp_data_store_id = os.getenv("VERTEX_AI_DATA_STORE_ID")
        
        if not all([gcp_project_id, gcp_data_store_id]):
            print("❌ Missing GCP configuration. Please set GOOGLE_CLOUD_PROJECT and VERTEX_AI_DATA_STORE_ID")
            return False
        
        retriever = VertexRetriever(gcp_project_id, gcp_location, gcp_data_store_id)
        
        # Test the specific query that was failing
        test_query = "Annual fee waiver conditions for HDFC Infinia vs Atlas"
        
        print(f"🔍 Testing Query: {test_query}")
        print("=" * 60)
        
        # Search with top_k=10
        results = retriever.search_similar_documents(
            query_text=test_query,
            card_filter=None,
            top_k=10,
            use_mmr=False
        )
        
        print(f"📊 Results: {len(results)} documents found")
        print("-" * 40)
        
        # Check for HDFC Infinia and Axis Atlas
        hdfc_found = False
        atlas_found = False
        
        for i, doc in enumerate(results):
            card_name = doc.get('cardName', 'Unknown')
            section = doc.get('section', 'Unknown')
            content_preview = doc.get('content', '')[:100] + "..." if len(doc.get('content', '')) > 100 else doc.get('content', '')
            
            print(f"{i+1}. {card_name} - {section}")
            print(f"   Content: {content_preview}")
            print()
            
            if 'hdfc' in card_name.lower() or 'infinia' in card_name.lower():
                hdfc_found = True
            if 'axis' in card_name.lower() or 'atlas' in card_name.lower():
                atlas_found = True
        
        # Summary
        print("🎯 SEARCH RESULTS ANALYSIS:")
        print("=" * 40)
        print(f"Total Results: {len(results)}/10")
        print(f"HDFC Infinia Found: {'✅ Yes' if hdfc_found else '❌ No'}")
        print(f"Axis Atlas Found: {'✅ Yes' if atlas_found else '❌ No'}")
        
        # Check if fee waiver specifically found
        fee_waiver_results = [doc for doc in results if 'fee_waiver' in doc.get('section', '').lower() or 'waiver' in doc.get('content', '').lower()]
        print(f"Fee Waiver Results: {len(fee_waiver_results)}")
        
        for doc in fee_waiver_results:
            print(f"  - {doc.get('cardName')} ({doc.get('section')})")
        
        return len(results) >= 5 and hdfc_found and atlas_found
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def test_local_jsonl():
    """Test if the local JSONL has both cards' fee waiver data"""
    
    print("\n🔬 TESTING LOCAL JSONL DATA:")
    print("=" * 40)
    
    try:
        import json
        import base64
        
        hdfc_fee_waiver = None
        atlas_fee_waiver = None
        
        with open('/Users/mandiv/Downloads/cursor/supavec-clone/card_data.jsonl', 'r') as f:
            for line in f:
                doc = json.loads(line)
                
                if 'fee_waiver' in doc.get('struct_data', {}).get('section', ''):
                    card_name = doc.get('struct_data', {}).get('cardName', '')
                    
                    # Decode content
                    raw_bytes = doc.get('content', {}).get('raw_bytes', '')
                    if raw_bytes:
                        content = base64.b64decode(raw_bytes).decode('utf-8')
                        
                        if 'hdfc' in card_name.lower() or 'infinia' in card_name.lower():
                            hdfc_fee_waiver = content
                            print(f"✅ HDFC Infinia: {content}")
                        elif 'axis' in card_name.lower() or 'atlas' in card_name.lower():
                            atlas_fee_waiver = content
                            print(f"✅ Axis Atlas: {content}")
        
        print(f"\nLocal JSONL Status:")
        print(f"HDFC Infinia fee waiver: {'✅ Found' if hdfc_fee_waiver else '❌ Missing'}")
        print(f"Axis Atlas fee waiver: {'✅ Found' if atlas_fee_waiver else '❌ Missing'}")
        
        return hdfc_fee_waiver is not None and atlas_fee_waiver is not None
        
    except Exception as e:
        print(f"❌ Local JSONL test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Fee Waiver Search System")
    print("==================================")
    
    # Test local data first
    local_success = test_local_jsonl()
    
    print("\n" + "="*60)
    
    # Test search if data is available
    if local_success:
        print("Local data looks good. Testing search...")
        search_success = test_fee_waiver_search()
        
        print(f"\n🎯 FINAL RESULTS:")
        print(f"Local JSONL Test: {'✅ PASS' if local_success else '❌ FAIL'}")
        print(f"Vertex AI Search: {'✅ PASS' if search_success else '❌ FAIL'}")
        
        if not search_success:
            print("\n💡 NOTE: Search failure might be due to:")
            print("1. Vertex AI data store not updated with new JSONL")
            print("2. Need to reindex the data store")
            print("3. Query enhancement not working as expected")
    else:
        print("❌ Local data test failed. Please fix JSONL generation first.")