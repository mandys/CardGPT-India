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


def create_chunks_from_node(node: dict, path_prefix: str, card_name: str) -> list:
    """Creates a chunk for a dictionary node and recurses for its children."""
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

                if "card" in data:
                    chunks = create_chunks_from_node(data["card"], "card", card_name)
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