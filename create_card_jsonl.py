#!/usr/bin/env python3
"""
Generate separate JSONL file for individual credit cards
Creates modular card-specific JSONL files for incremental Google Cloud uploads
"""

import json
import base64
import hashlib
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_chunks_from_node(data: Dict[str, Any], path: str, card_name: str, max_chunk_size: int = 1000) -> List[Dict[str, Any]]:
    """Create chunks from a data node with card name context"""
    chunks = []
    
    def process_node(node: Any, current_path: str, current_section: str) -> None:
        if isinstance(node, dict):
            # Create section-level chunks for major sections
            major_sections = ['fees', 'rewards', 'eligibility', 'welcome_benefits', 'lounge_access', 
                            'insurance', 'dining_benefits', 'renewal_benefits', 'miles_transfer']
            
            if any(section in current_path for section in major_sections):
                section_name = next((section for section in major_sections if section in current_path), current_section)
                content = json.dumps(node, indent=2, ensure_ascii=False)
                
                if len(content) <= max_chunk_size:
                    # Create single chunk for the section
                    chunk_id = hashlib.md5(f"{card_name}_{current_path}".encode()).hexdigest()
                    chunks.append({
                        "id": chunk_id,
                        "cardName": card_name,
                        "section": section_name,
                        "path": current_path,
                        "content": content
                    })
                else:
                    # Split large sections into smaller chunks
                    for key, value in node.items():
                        process_node(value, f"{current_path}.{key}", section_name)
            else:
                # Process nested objects
                for key, value in node.items():
                    section = key if current_path == path else current_section
                    process_node(value, f"{current_path}.{key}", section)
        
        elif isinstance(node, (list, str, int, float, bool)) or node is None:
            # Create chunk for leaf values
            content = json.dumps({current_path.split('.')[-1]: node}, indent=2, ensure_ascii=False)
            
            if len(content) > 50:  # Only create chunks for meaningful content
                chunk_id = hashlib.md5(f"{card_name}_{current_path}".encode()).hexdigest()
                chunks.append({
                    "id": chunk_id,
                    "cardName": card_name,
                    "section": current_section,
                    "path": current_path,
                    "content": content
                })
    
    process_node(data, path, "general")
    return chunks

def create_card_jsonl(card_file: Path, output_file: Path) -> bool:
    """Create JSONL file for a single credit card"""
    try:
        logger.info(f"🚀 Creating JSONL for: {card_file.name}")
        
        # Load card data
        with open(card_file, 'r', encoding='utf-8') as f:
            card_data = json.load(f)
        
        card_name = card_data.get("card", {}).get("name", "Unknown Card")
        logger.info(f"📋 Processing: {card_name}")
        
        # Create chunks
        chunks = create_chunks_from_node(card_data["card"], "card", card_name)
        logger.info(f"📦 Created {len(chunks)} chunks")
        
        # Write JSONL file
        with open(output_file, 'w', encoding='utf-8') as f_out:
            for chunk in chunks:
                # Encode content to Base64 (matching Vertex AI Search format)
                content_bytes = chunk["content"].encode('utf-8')
                content_base64 = base64.b64encode(content_bytes).decode('utf-8')
                
                vertex_doc = {
                    "id": chunk["id"],
                    "struct_data": {
                        "cardName": chunk["cardName"],
                        "section": chunk["section"]
                    },
                    "content": {
                        "mime_type": "text/plain",
                        "raw_bytes": content_base64
                    }
                }
                f_out.write(json.dumps(vertex_doc) + '\n')
        
        logger.info(f"✅ Successfully created {output_file}")
        logger.info(f"📊 File size: {output_file.stat().st_size} bytes")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create JSONL: {e}")
        return False

def main():
    """CLI interface for creating card-specific JSONL files"""
    parser = argparse.ArgumentParser(
        description="Create separate JSONL file for individual credit cards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_card_jsonl.py data/hdfc-infinia.json
  python create_card_jsonl.py data/hdfc-infinia.json --output hdfc-infinia-data.jsonl
  python create_card_jsonl.py data/new-card.json --output new-card-data.jsonl
        """
    )
    
    parser.add_argument('card_file', help='Path to the card JSON file')
    parser.add_argument('--output', '-o', 
                       help='Output JSONL file name (default: auto-generated from card file)')
    
    args = parser.parse_args()
    
    # Validate input file
    card_file = Path(args.card_file)
    if not card_file.exists():
        logger.error(f"❌ Card file not found: {card_file}")
        return 1
    
    # Determine output file
    if args.output:
        output_file = Path(args.output)
    else:
        # Auto-generate output filename: hdfc-infinia.json -> hdfc-infinia-data.jsonl
        base_name = card_file.stem  # hdfc-infinia
        output_file = Path(f"{base_name}-data.jsonl")
    
    # Create JSONL
    success = create_card_jsonl(card_file, output_file)
    
    if success:
        print(f"\n🎉 Successfully created {output_file}")
        print(f"📋 Ready for Google Cloud upload:")
        print(f"   gsutil cp {output_file} gs://your-bucket-name/cards/")
        print(f"")
        print(f"📊 Next steps:")
        print(f"   1. Upload the JSONL file to Google Cloud Storage")
        print(f"   2. Use Vertex AI Search console to import incrementally")
        print(f"   3. Test queries with the new card data")
        return 0
    else:
        logger.error("❌ Failed to create JSONL file")
        return 1

if __name__ == "__main__":
    exit(main())