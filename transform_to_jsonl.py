#!/usr/bin/env python3
"""
Data Transformation Script for Vertex AI Search
Converts structured JSON files to JSONL format with proper metadata.

This script fixes the poor retrieval results by:
1. Converting single JSON files to structured JSONL format
2. Adding proper metadata (cardName, section) to each chunk
3. Enabling precise filtering in Vertex AI Search
4. Taking back control of chunking instead of relying on Google's auto-chunker
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _extract_card_name(filename: str) -> str:
    """Extract card name from filename."""
    if 'axis-atlas' in filename.lower():
        return 'Axis Atlas'
    elif 'icici-epm' in filename.lower():
        return 'ICICI EPM'
    elif 'hsbc-premier' in filename.lower():
        return 'HSBC Premier'
    else:
        # Fallback: capitalize and clean filename
        return filename.replace('.json', '').replace('-', ' ').title()

def _format_dict_to_text(data: Dict, indent: int = 0) -> str:
    """Convert dictionary to readable text format."""
    if not isinstance(data, dict):
        return str(data)
    
    text_parts = []
    indent_str = "  " * indent
    
    for key, value in data.items():
        key_formatted = key.replace('_', ' ').title()
        if isinstance(value, dict):
            text_parts.append(f"{indent_str}{key_formatted}:")
            text_parts.append(_format_dict_to_text(value, indent + 1))
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                text_parts.append(f"{indent_str}{key_formatted}:")
                for i, item in enumerate(value):
                    text_parts.append(f"{indent_str}  {i+1}. {_format_dict_to_text(item, indent + 1)}")
            else:
                list_items = ", ".join(str(item) for item in value)
                text_parts.append(f"{indent_str}{key_formatted}: {list_items}")
        else:
            text_parts.append(f"{indent_str}{key_formatted}: {value}")
    
    return "\n".join(text_parts)

def _traverse_and_chunk(data: Dict, card_name: str, filename: str, prefix: str = "") -> List[Dict]:
    """
    Recursively traverse the data structure and create chunks.
    Reuses the excellent chunking logic from retriever.py but adapted for JSONL.
    """
    chunks = []
    
    if not isinstance(data, dict):
        return chunks
    
    for key, value in data.items():
        current_prefix = f"{prefix}_{key}" if prefix else key
        chunk_id = f"{card_name.lower().replace(' ', '_')}_{current_prefix}"
        
        if isinstance(value, dict):
            # Create a chunk for this section
            content = _format_dict_to_text({key: value})
            
            chunks.append({
                "id": chunk_id,
                "content": content,
                "cardName": card_name,
                "section": key,
                "filename": filename
            })
            
            # Recursively process nested structures
            nested_chunks = _traverse_and_chunk(value, card_name, filename, current_prefix)
            chunks.extend(nested_chunks)
            
        elif isinstance(value, list):
            # Handle arrays
            if value and isinstance(value[0], dict):
                # Array of objects
                for i, item in enumerate(value):
                    item_id = f"{chunk_id}_{i}"
                    content = _format_dict_to_text({f"{key}_{i}": item})
                    chunks.append({
                        "id": item_id,
                        "content": content,
                        "cardName": card_name,
                        "section": key,
                        "filename": filename
                    })
            else:
                # Array of simple values
                content = f"{key.replace('_', ' ').title()}: {', '.join(str(item) for item in value)}"
                chunks.append({
                    "id": chunk_id,
                    "content": content,
                    "cardName": card_name,
                    "section": key,
                    "filename": filename
                })
        else:
            # Simple key-value pair
            content = f"{key.replace('_', ' ').title()}: {value}"
            chunks.append({
                "id": chunk_id,
                "content": content,
                "cardName": card_name,
                "section": key,
                "filename": filename
            })
    
    return chunks

def transform_data(data_directory: str = "data", output_file: str = "card_data.jsonl") -> bool:
    """
    Transform JSON files to JSONL format for Vertex AI Search.
    
    Args:
        data_directory: Path to directory containing JSON files
        output_file: Output JSONL file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    data_path = Path(data_directory)
    output_path = Path(output_file)
    
    if not data_path.exists():
        logger.error(f"❌ Data directory not found at {data_path.absolute()}")
        return False
    
    json_files = list(data_path.glob("*.json"))
    if not json_files:
        logger.error(f"❌ No JSON files found in {data_path.absolute()}")
        return False
    
    logger.info(f"🔍 Found {len(json_files)} source JSON files to process...")
    
    all_chunks = []
    
    for json_file in json_files:
        try:
            logger.info(f"📄 Processing {json_file.name}...")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                card_data = json.load(f)
            
            card_name = _extract_card_name(json_file.name)
            logger.info(f"🏦 Detected card: {card_name}")
            
            # Process both common_terms and card sections
            file_chunks = []
            
            # Process common_terms section
            if 'common_terms' in card_data:
                common_chunks = _traverse_and_chunk(
                    card_data['common_terms'], 
                    card_name, 
                    json_file.name, 
                    'common_terms'
                )
                file_chunks.extend(common_chunks)
            
            # Process card section
            if 'card' in card_data:
                card_chunks = _traverse_and_chunk(
                    card_data['card'], 
                    card_name, 
                    json_file.name, 
                    'card'
                )
                file_chunks.extend(card_chunks)
            
            # Convert to Vertex AI format
            for chunk in file_chunks:
                vertex_chunk = {
                    "id": chunk["id"].replace(".", "_"),  # Vertex needs IDs without dots
                    "jsonData": chunk["content"],  # The actual content
                    "cardName": chunk["cardName"],
                    "section": chunk["section"],
                    "filename": chunk["filename"]
                }
                all_chunks.append(vertex_chunk)
            
            logger.info(f"✅ Generated {len(file_chunks)} chunks from {json_file.name}")
            
        except Exception as e:
            logger.error(f"❌ Error processing {json_file.name}: {e}")
            return False
    
    # Write all chunks to JSONL file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for chunk in all_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
        
        logger.info(f"🎉 Successfully created {output_path.name} with {len(all_chunks)} chunks")
        
        # Log summary statistics
        card_counts = {}
        section_counts = {}
        
        for chunk in all_chunks:
            card_name = chunk["cardName"]
            section = chunk["section"]
            
            card_counts[card_name] = card_counts.get(card_name, 0) + 1
            section_counts[section] = section_counts.get(section, 0) + 1
        
        logger.info("📊 Chunk Statistics:")
        logger.info(f"  Cards: {dict(card_counts)}")
        logger.info(f"  Top sections: {dict(sorted(section_counts.items(), key=lambda x: x[1], reverse=True)[:5])}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error writing output file: {e}")
        return False

def main():
    """Main function to run the transformation."""
    logger.info("🚀 Starting JSON to JSONL transformation for Vertex AI Search...")
    
    success = transform_data()
    
    if success:
        logger.info("✅ Transformation completed successfully!")
        logger.info("📋 Next steps:")
        logger.info("  1. Upload card_data.jsonl to Google Cloud Storage")
        logger.info("  2. Create new Vertex AI data store with structured data (JSONL)")
        logger.info("  3. Set 'id' field as document ID")
        logger.info("  4. Mark 'cardName' as filterable in schema")
        logger.info("  5. Update vertex_retriever.py to use metadata filtering")
    else:
        logger.error("❌ Transformation failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())