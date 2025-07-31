# In transform_to_jsonl.py

import json
import base64
from pathlib import Path
import logging

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


def _clean_id(text: str) -> str:
    """Clean text to create valid Vertex AI document IDs"""
    import re
    # Replace spaces and special characters with underscores
    cleaned = re.sub(r'[^a-zA-Z0-9_-]', '_', text)
    # Remove multiple consecutive underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    # Truncate to 120 chars to leave room for prefixes
    if len(cleaned) > 120:
        cleaned = cleaned[:120]
    return cleaned

def create_chunks_from_node(node: dict, path_prefix: str, card_name: str) -> list:
    """Creates a chunk for a dictionary node and recurses for its children."""
    chunks = []
    if not isinstance(node, dict):
        return []

    # Create a single, comprehensive chunk for the current dictionary node
    clean_card_name = _clean_id(card_name.lower())
    clean_path = _clean_id(path_prefix.replace('.', '_'))
    chunk_id = f"{clean_card_name}_{clean_path}"
    
    # Ensure ID is under 128 characters
    if len(chunk_id) > 127:
        # Truncate while keeping the most important parts
        max_card_len = 40
        max_path_len = 80
        truncated_card = clean_card_name[:max_card_len] if len(clean_card_name) > max_card_len else clean_card_name
        truncated_path = clean_path[:max_path_len] if len(clean_path) > max_path_len else clean_path
        chunk_id = f"{truncated_card}_{truncated_path}"
    
    content = _format_dict_to_text(node)
    
    chunks.append({
        "id": chunk_id,
        "content": content,
        "cardName": card_name,
        "section": path_prefix.split('.')[-1]
    })
    
    # Process both nested dictionaries AND important string fields
    for key, value in node.items():
        if isinstance(value, dict):
            clean_key = _clean_id(key)
            new_path = f"{path_prefix}.{clean_key}"
            chunks.extend(create_chunks_from_node(value, new_path, card_name))
        elif isinstance(value, (str, int, float)) or value is None:
            # Create dedicated chunks for ALL simple value fields (string, number, null)
            clean_key = _clean_id(key)
            string_chunk_id = f"{clean_card_name}_{clean_path}_{clean_key}"
            
            # Ensure string chunk ID is under 128 characters
            if len(string_chunk_id) > 127:
                # Truncate keeping the most important parts
                max_card_len = 30
                max_path_len = 50
                max_key_len = 40
                truncated_card = clean_card_name[:max_card_len] if len(clean_card_name) > max_card_len else clean_card_name
                truncated_path = clean_path[:max_path_len] if len(clean_path) > max_path_len else clean_path
                truncated_key = clean_key[:max_key_len] if len(clean_key) > max_key_len else clean_key
                string_chunk_id = f"{truncated_card}_{truncated_path}_{truncated_key}"
            
            if isinstance(value, str):
                string_content = f"{key.replace('_', ' ').title()}: {value}"
            elif value is None:
                string_content = f"{key.replace('_', ' ').title()}: Not available"
            else:
                string_content = f"{key.replace('_', ' ').title()}: {str(value)}"
            
            chunks.append({
                "id": string_chunk_id,
                "content": string_content,
                "cardName": card_name,
                "section": key
            })
            
    return chunks

def transform_data():
    data_path = Path("data")
    output_file = Path("card_data.jsonl")
    json_files = list(data_path.glob("*.json"))
    logger.info(f"Found {len(json_files)} source files...")

    with open(output_file, 'w', encoding='utf-8') as f_out:
        total_chunks = 0
        for json_file in json_files:
            logger.info(f"Processing {json_file.name}...")
            with open(json_file, 'r', encoding='utf-8') as f_in:
                data = json.load(f_in)
                card_name = data.get("card", {}).get("name", "Unknown Card")

                # Process both card and common_terms sections
                sections_to_process = []
                if "card" in data:
                    sections_to_process.append(("card", data["card"]))
                if "common_terms" in data:
                    sections_to_process.append(("common_terms", data["common_terms"]))
                
                for section_name, section_data in sections_to_process:
                    chunks = create_chunks_from_node(section_data, section_name, card_name)
                    for chunk in chunks:
                        # --- THIS IS THE CRITICAL FIX ---
                        # Encode the text content to bytes, then to a Base64 string
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
                                "raw_bytes": content_base64  # Use raw_bytes instead of text
                            }
                        }
                        # --- END OF FIX ---
                        f_out.write(json.dumps(vertex_doc) + '\n')
                        total_chunks += 1
    logger.info(f"✅ Successfully created {output_file.name} with {total_chunks} chunks.")

if __name__ == "__main__":
    transform_data()