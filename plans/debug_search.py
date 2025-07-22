#!/usr/bin/env python3
"""
Debug Search Tool
Quick diagnostic script to test search pipeline components
"""

import json
import sys
import os
from pathlib import Path

# Add backend to path so we can import services
sys.path.append(str(Path(__file__).parent.parent / "backend"))

def check_json_data(query_keywords):
    """Check if information exists in JSON source files"""
    print("=== STEP 1: CHECKING JSON SOURCE DATA ===")
    
    data_dir = Path(__file__).parent.parent / "data"
    json_files = list(data_dir.glob("*.json"))
    
    found_results = []
    
    for json_file in json_files:
        print(f"\n📁 Checking {json_file.name}...")
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                content_str = json.dumps(data, indent=2).lower()
                
                matches = []
                for keyword in query_keywords:
                    if keyword.lower() in content_str:
                        matches.append(keyword)
                
                if matches:
                    print(f"   ✅ Found keywords: {matches}")
                    found_results.append((json_file.name, matches))
                else:
                    print(f"   ❌ No keywords found")
                    
        except Exception as e:
            print(f"   ⚠️  Error reading {json_file}: {e}")
    
    return found_results

def check_jsonl_data(query_keywords):
    """Check if information exists in JSONL chunks"""
    print("\n=== STEP 3: CHECKING JSONL OUTPUT ===")
    
    jsonl_file = Path(__file__).parent.parent / "card_data.jsonl"
    
    if not jsonl_file.exists():
        print("❌ card_data.jsonl not found! Run 'python transform_to_jsonl.py' first")
        return []
    
    print(f"📄 Checking {jsonl_file.name}...")
    
    found_chunks = []
    try:
        with open(jsonl_file, 'r') as f:
            for i, line in enumerate(f, 1):
                chunk = json.loads(line)
                
                # Decode base64 content
                import base64
                if 'content' in chunk and 'raw_bytes' in chunk['content']:
                    try:
                        content_bytes = base64.b64decode(chunk['content']['raw_bytes'])
                        content_text = content_bytes.decode('utf-8').lower()
                        
                        matches = []
                        for keyword in query_keywords:
                            if keyword.lower() in content_text:
                                matches.append(keyword)
                        
                        if matches:
                            found_chunks.append({
                                'chunk_id': chunk.get('id', f'chunk_{i}'),
                                'card_name': chunk.get('struct_data', {}).get('cardName', 'Unknown'),
                                'section': chunk.get('struct_data', {}).get('section', 'Unknown'),
                                'matches': matches,
                                'content_preview': content_text[:200] + "..."
                            })
                    except Exception as e:
                        print(f"   ⚠️  Error decoding chunk {i}: {e}")
                        
    except Exception as e:
        print(f"❌ Error reading JSONL: {e}")
        return []
    
    if found_chunks:
        print(f"✅ Found {len(found_chunks)} relevant chunks:")
        for chunk in found_chunks[:3]:  # Show first 3
            print(f"   📋 {chunk['chunk_id']} ({chunk['card_name']} - {chunk['section']})")
            print(f"      Matches: {chunk['matches']}")
            print(f"      Preview: {chunk['content_preview'][:100]}...")
    else:
        print("❌ No relevant chunks found in JSONL")
    
    return found_chunks

def test_vertex_search(query_text):
    """Test Vertex AI search retrieval"""
    print(f"\n=== STEP 4: TESTING VERTEX AI SEARCH ===")
    print(f"🔍 Query: {query_text}")
    
    try:
        from services.vertex_retriever import VertexRetriever
        
        # Check environment variables
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = os.getenv('VERTEX_AI_LOCATION', 'global')
        data_store_id = os.getenv('VERTEX_AI_DATA_STORE_ID')
        
        if not all([project_id, data_store_id]):
            print("❌ Missing environment variables:")
            print(f"   GOOGLE_CLOUD_PROJECT: {project_id}")
            print(f"   VERTEX_AI_DATA_STORE_ID: {data_store_id}")
            return []
        
        retriever = VertexRetriever(project_id, location, data_store_id)
        results = retriever.search_similar_documents(query_text, top_k=5)
        
        print(f"✅ Retrieved {len(results)} documents:")
        for i, doc in enumerate(results[:3], 1):
            print(f"   📄 Document {i}:")
            print(f"      Content: {doc.get('content', '')[:150]}...")
            print(f"      Metadata: {doc.get('metadata', {})}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error testing Vertex AI search: {e}")
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_search.py <query>")
        print("Example: python debug_search.py 'cash withdrawal charges axis'")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    keywords = query.split()
    
    print(f"🔍 DEBUGGING SEARCH FOR: '{query}'")
    print("=" * 60)
    
    # Step 1: Check JSON source data
    json_results = check_json_data(keywords)
    
    # Step 3: Check JSONL chunks (skip step 2 for now)
    jsonl_results = check_jsonl_data(keywords)
    
    # Step 4: Test Vertex AI search
    search_results = test_vertex_search(query)
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print(f"   📁 JSON files with keywords: {len(json_results)}")
    print(f"   📋 JSONL chunks with keywords: {len(jsonl_results)}")
    print(f"   🔍 Vertex AI results: {len(search_results)}")
    
    if json_results and not jsonl_results:
        print("\n⚠️  ISSUE: Data exists in JSON but not in JSONL chunks!")
        print("   → Check transform_to_jsonl.py chunking logic (Step 2)")
    elif jsonl_results and not search_results:
        print("\n⚠️  ISSUE: Data exists in JSONL but not retrieved by search!")
        print("   → Check Vertex AI search parameters (Step 4)")
    elif json_results and jsonl_results and search_results:
        print("\n✅ All steps working - issue likely in LLM prompt (Step 5)")

if __name__ == "__main__":
    main()