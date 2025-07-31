#!/usr/bin/env python3
"""
Validate JSONL file for Vertex AI Search compliance
Check ID patterns and lengths
"""

import json
import re

def validate_jsonl_ids():
    """Validate all document IDs in the JSONL file"""
    
    # Vertex AI Search ID requirements
    valid_pattern = re.compile(r'^[a-zA-Z0-9_-]+$')
    max_length = 128
    
    valid_count = 0
    invalid_count = 0
    issues = []
    
    with open('card_data.jsonl', 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                doc = json.loads(line)
                doc_id = doc.get('id', '')
                
                # Check pattern
                if not valid_pattern.match(doc_id):
                    invalid_chars = [c for c in doc_id if not re.match(r'[a-zA-Z0-9_-]', c)]
                    issues.append(f"Line {line_num}: Invalid characters in ID '{doc_id}': {set(invalid_chars)}")
                    invalid_count += 1
                    continue
                
                # Check length
                if len(doc_id) > max_length:
                    issues.append(f"Line {line_num}: ID too long ({len(doc_id)} chars): '{doc_id}'")
                    invalid_count += 1
                    continue
                
                valid_count += 1
                
            except json.JSONDecodeError as e:
                issues.append(f"Line {line_num}: JSON decode error: {e}")
                invalid_count += 1
    
    # Report results
    print("🔍 JSONL Validation Results")
    print("=" * 40)
    print(f"✅ Valid IDs: {valid_count}")
    print(f"❌ Invalid IDs: {invalid_count}")
    print(f"📊 Total documents: {valid_count + invalid_count}")
    
    if issues:
        print(f"\n❌ ISSUES FOUND ({len(issues)}):")
        print("-" * 40)
        for issue in issues[:10]:  # Show first 10 issues
            print(issue)
        if len(issues) > 10:
            print(f"... and {len(issues) - 10} more issues")
    else:
        print("\n🎉 ALL IDs ARE VALID!")
        print("✅ Ready for upload to Vertex AI Search")
    
    return invalid_count == 0

if __name__ == "__main__":
    success = validate_jsonl_ids()
    exit(0 if success else 1)