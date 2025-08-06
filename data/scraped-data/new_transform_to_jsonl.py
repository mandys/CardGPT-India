#!/usr/bin/env python3
"""
Enhanced Transform to JSONL Script for Scraped Credit Card Data
Creates category-level chunks with comprehensive versioning and hashing for easy updates.
"""

import json
import base64
import hashlib
import ast
from pathlib import Path
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_card_aliases(card_name: str) -> list:
    """Generate comprehensive aliases for improved search recall."""
    alias_mappings = {
        'Atlas Credit Card': ['atlas', 'axis atlas', 'axis bank atlas', 'axis atlas credit card'],
        'Infinia Metal Credit Card': ['infinia', 'hdfc infinia', 'infinia metal', 'hdfc infinia metal'],
        'Premier Metal Credit Card': ['premier', 'hsbc premier', 'premier metal', 'hsbc premier metal'],
        'Emeralde Private Metal Credit Card': ['epm', 'icici epm', 'emeralde private metal', 'emeralde', 'icici emeralde']
    }
    
    # Check for matches in card name
    for key, aliases in alias_mappings.items():
        if key.lower() in card_name.lower():
            return aliases
    
    # Fallback - extract key terms from card name
    fallback_aliases = []
    name_lower = card_name.lower()
    if 'atlas' in name_lower:
        fallback_aliases.extend(['atlas', 'axis atlas'])
    if 'infinia' in name_lower:
        fallback_aliases.extend(['infinia', 'hdfc infinia'])
    if 'premier' in name_lower:
        fallback_aliases.extend(['premier', 'hsbc premier'])
    if 'emeralde' in name_lower or 'epm' in name_lower:
        fallback_aliases.extend(['epm', 'icici epm', 'emeralde'])
    
    return fallback_aliases

def generate_content_hash(content: str) -> str:
    """Generate consistent SHA-256 hash for content change detection."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

def format_dict_to_text(data: dict, indent_level: int = 0) -> str:
    """Convert dictionary to readable text format with proper indentation."""
    if not isinstance(data, dict):
        return str(data)
    
    parts = []
    indent = "  " * indent_level
    
    for key, value in data.items():
        key_formatted = key.replace('_', ' ').title()
        
        if isinstance(value, dict):
            nested_text = format_dict_to_text(value, indent_level + 1)
            parts.append(f"{indent}{key_formatted}:\n{nested_text}")
        elif isinstance(value, list):
            if not value:
                parts.append(f"{indent}{key_formatted}: None")
            else:
                list_items = []
                for item in value:
                    if isinstance(item, dict):
                        # Handle dictionary items in lists (like airline partners)
                        dict_str = format_dict_to_text(item, 0).replace('\n', ', ')
                        list_items.append(f"  {indent}- {dict_str}")
                    else:
                        list_items.append(f"  {indent}- {item}")
                parts.append(f"{indent}{key_formatted}:\n" + "\n".join(list_items))
        else:
            parts.append(f"{indent}{key_formatted}: {value}")
    
    return "\n".join(parts)

def parse_text_file_to_dict(file_path: Path) -> dict:
    """Parse text files containing Python dictionary representations."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Remove 'card_data = ' prefix if present
        if content.startswith('card_data = '):
            content = content[12:]
        
        # Use ast.literal_eval for safe parsing
        return ast.literal_eval(content)
    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {e}")
        return {}

def load_card_data(file_path: Path) -> dict:
    """Load card data from JSON or text file."""
    if file_path.suffix == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif file_path.suffix == '.txt':
        return parse_text_file_to_dict(file_path)
    else:
        logger.warning(f"Unsupported file type: {file_path}")
        return {}

def normalize_card_name(raw_card_name: str, bank_name: str = "") -> str:
    """Normalize card names to match our system expectations."""
    card_name_mapping = {
        'Atlas Credit Card': 'Axis Bank Atlas Credit Card',
        'Infinia Metal Credit Card': 'HDFC Infinia Credit Card (Metal Edition)',
        'Premier Metal Credit Card': 'HSBC Premier Credit Card',
        'Emeralde Private Metal Credit Card': 'ICICI Bank Emeralde Private Metal Credit Card'
    }
    
    # Try exact match first
    if raw_card_name in card_name_mapping:
        return card_name_mapping[raw_card_name]
    
    # Try partial matches
    for key, normalized in card_name_mapping.items():
        if key.lower() in raw_card_name.lower():
            return normalized
    
    # Fallback: combine bank + card if available
    if bank_name and bank_name not in raw_card_name:
        return f"{bank_name} {raw_card_name}"
    
    return raw_card_name

def transform_scraped_data():
    """
    Transform scraped credit card data into category-level JSONL chunks 
    with comprehensive versioning and hashing for Vertex AI Search.
    """
    # Look for scraped data files in current directory
    data_files = []
    current_dir = Path(".")
    
    # Find all JSON and text files (excluding the script itself)
    for pattern in ["*.json", "*.txt"]:
        for file_path in current_dir.glob(pattern):
            if file_path.name != "new_transform_to_jsonl.py":
                data_files.append(file_path)
    
    if not data_files:
        logger.error("❌ No data files found! Expected JSON or TXT files in current directory.")
        return
    
    logger.info(f"Found {len(data_files)} data files to process: {[f.name for f in data_files]}")
    
    # Output file in scraped-data folder
    output_file = Path("card_data.jsonl")
    
    with open(output_file, 'w', encoding='utf-8') as f_out:
        total_chunks = 0
        
        for data_file in data_files:
            logger.info(f"Processing {data_file.name}...")
            
            # Load data based on file type
            card_data = load_card_data(data_file)
            if not card_data:
                logger.warning(f"Skipping {data_file.name} - no data loaded")
                continue
            
            # Extract card metadata
            meta = card_data.get("meta", {})
            raw_card_name = meta.get("card", "Unknown Card")
            bank_name = meta.get("bank", "")
            
            # Normalize card name for consistency
            normalized_card_name = normalize_card_name(raw_card_name, bank_name)
            logger.info(f"Processing card: {normalized_card_name}")
            
            # Generate aliases for this card
            aliases = generate_card_aliases(normalized_card_name)
            
            # Process each major section as a separate chunk
            for section_name, section_data in card_data.items():
                if section_name == 'meta':  # Skip metadata section
                    continue
                
                # Create unique chunk ID
                chunk_id = f"{normalized_card_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}_{section_name}"
                
                # Format section data to human-readable text
                base_content = format_dict_to_text(section_data)
                
                # Enhance content with card context and aliases
                final_content = f"Card: {normalized_card_name}\nSection: {section_name.replace('_', ' ').title()}\n\n{base_content}"
                
                # Add aliases to improve search recall
                if aliases:
                    final_content += f"\n\nAlso known as: {', '.join(aliases)}"
                
                # Generate versioning metadata
                content_hash = generate_content_hash(final_content)
                updated_at = datetime.now(timezone.utc).isoformat()
                
                # Encode content for Vertex AI
                content_base64 = base64.b64encode(final_content.encode('utf-8')).decode('utf-8')
                
                # Create Vertex AI document with rich metadata
                vertex_doc = {
                    "id": chunk_id,
                    "content": {
                        "mime_type": "text/plain",
                        "raw_bytes": content_base64
                    },
                    "struct_data": {
                        "cardName": normalized_card_name,
                        "section": section_name,
                        "aliases": aliases,
                        "updated_at": updated_at,
                        "content_hash": content_hash,
                        "schema_version": "3.0",  # Updated for scraped data format
                        "source_file": data_file.name,
                        "data_source": "scraped_reviews_reddit"
                    }
                }
                
                # Write to JSONL file
                f_out.write(json.dumps(vertex_doc, ensure_ascii=False) + '\n')
                total_chunks += 1
                
                logger.debug(f"Created chunk: {chunk_id} ({len(final_content)} chars)")
        
        logger.info(f"✅ Successfully created {output_file.name} with {total_chunks} category-level chunks")
        logger.info(f"📊 Average ~{total_chunks//len(data_files)} chunks per card (reduced overlap)")
        logger.info(f"🔄 Schema version 3.0 with comprehensive hashing for easy updates")

if __name__ == "__main__":
    transform_scraped_data()