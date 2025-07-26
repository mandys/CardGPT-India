#!/usr/bin/env python3
"""
Generate separate JSONL file for individual credit cards
Creates modular card-specific JSONL files for incremental Google Cloud uploads
"""

import json
import base64
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _format_dict_to_text(data: dict) -> str:
    """Recursively formats a dictionary into a readable indented string."""
    parts = []
    for key, value in data.items():
        key_formatted = key.replace('_', ' ').title()
        if isinstance(value, dict):
            # For nested dictionaries, we'll format them recursively.
            nested_text = _format_dict_to_text(value)
            parts.append(f"{key_formatted}:\n{nested_text}")
        elif isinstance(value, list):
            # Format lists cleanly
            list_items = ", ".join(map(str, value))
            parts.append(f"{key_formatted}: {list_items}")
        else:
            parts.append(f"{key_formatted}: {value}")
    return "\n".join(parts)

def create_chunks_from_node(node: dict, path_prefix: str, card_name: str) -> list:
    """Creates a chunk for a dictionary node and recurses for its children - EXACT COPY of transform_to_jsonl.py"""
    chunks = []
    if not isinstance(node, dict):
        return []

    # Create a single, comprehensive chunk for the current dictionary node
    chunk_id = f"{card_name.lower().replace(' ', '_')}_{path_prefix.replace('.', '_')}"
    content = _format_dict_to_text(node)
    
    chunks.append({
        "id": chunk_id,
        "content": content,
        "cardName": card_name,
        "section": path_prefix.split('.')[-1]
    })
    
    # Recurse into nested dictionaries to create more granular chunks
    for key, value in node.items():
        if isinstance(value, dict):
            new_path = f"{path_prefix}.{key}"
            chunks.extend(create_chunks_from_node(value, new_path, card_name))
            
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
        
        # Create chunks using EXACT same logic as transform_to_jsonl.py
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