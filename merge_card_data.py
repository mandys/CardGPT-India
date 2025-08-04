import json
from pathlib import Path
import logging
from datetime import datetime
from ast import literal_eval # Import literal_eval

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_json_file(filepath: Path):
    """Safely loads a JSON file, or attempts to parse as a Python literal if JSON fails."""
    if not filepath.exists():
        logger.warning(f"File not found: {filepath}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # If standard JSON fails, try to evaluate as a Python literal
                logger.info(f"Attempting literal_eval for {filepath}...")
                # Remove variable assignment if present
                if content.strip().startswith("card_data ="):
                    content = content.split("=", 1)[1].strip()
                return literal_eval(content)
    except (json.JSONDecodeError, ValueError, SyntaxError) as e:
        logger.error(f"Error parsing data from {filepath}: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while reading {filepath}: {e}")
        return None

def deep_merge_dicts(source: dict, destination: dict) -> dict:
    """
    Deep merges two dictionaries. Values from source overwrite values in destination.
    If a value is a dictionary, it is merged recursively.
    """
    for key, value in source.items():
        if isinstance(value, dict) and key in destination and isinstance(destination[key], dict):
            destination[key] = deep_merge_dicts(value, destination[key])
        else:
            destination[key] = value
    return destination

def merge_card_data(old_data: dict, new_data: dict) -> dict:
    """
    Merges old and new card data into a unified structure.
    New data takes precedence for overlapping fields.
    Common terms from old data are added as a top-level key.
    Detailed spending categories from old data are merged into new reward_points.categories.
    """
    unified_data = {}

    # Start with new data as the base, as it's the preferred format
    if new_data:
        unified_data = new_data.copy()
    
    # Add common_terms from old data if available
    if old_data and "common_terms" in old_data:
        unified_data["common_terms"] = old_data["common_terms"]
    
    # Merge detailed spending_categories from old data into new reward_points.categories
    if old_data and "card" in old_data and "spending_categories" in old_data["card"]:
        old_spending_categories = old_data["card"]["spending_categories"]
        
        if "reward_points" not in unified_data:
            unified_data["reward_points"] = {}
        if "categories" not in unified_data["reward_points"]:
            unified_data["reward_points"]["categories"] = {}
        
        # Deep merge old spending categories into the new categories
        # This ensures detailed fields from old data are retained
        unified_data["reward_points"]["categories"] = deep_merge_dicts(
            old_spending_categories,
            unified_data["reward_points"]["categories"]
        )
    
    # Add a last_updated timestamp
    unified_data["last_updated"] = datetime.now().isoformat()

    return unified_data

def main():
    data_dir = Path("data")
    
    card_pairs = {
        "axis-atlas": {"old": "axis-atlas.json", "new": "axis-atlas-new.txt"},
        "hdfc-infinia": {"old": "hdfc-infinia.json", "new": "hdfc-infinia-new.txt"},
        "icici-epm": {"old": "icici-epm.json", "new": "icici-epm.txt"},
        "hsbc-premier": {"old": "hsbc-premier.json", "new": None} # No new data for HSBC
    }

    for card_key, files in card_pairs.items():
        logger.info(f"Processing card: {card_key}")
        
        old_filepath = data_dir / files["old"]
        new_filepath = data_dir / files["new"] if files["new"] else None
        
        old_data = load_json_file(old_filepath)
        
        new_data = None
        if new_filepath and new_filepath.exists():
            # New files are also JSON, but stored as .txt
            new_data = load_json_file(new_filepath)
        elif new_filepath:
            logger.warning(f"New data file not found for {card_key}: {new_filepath}. Proceeding with old data only.")

        if old_data is None and new_data is None:
            logger.error(f"Skipping {card_key}: No data found for old or new format.")
            continue
        
        unified_card_data = {}
        if old_data and new_data:
            unified_card_data = merge_card_data(old_data, new_data) # Pass full old_data
        elif old_data: # Only old data available (e.g., HSBC Premier initially)
            # Convert old structure to new unified structure
            unified_card_data = old_data["card"].copy()
            unified_card_data["common_terms"] = old_data["common_terms"]
            # Flatten old spending_categories into reward_points.categories if it exists
            if "spending_categories" in unified_card_data and "rewards" in unified_card_data:
                if "categories" not in unified_card_data["rewards"]:
                    unified_card_data["rewards"]["categories"] = {}
                unified_card_data["rewards"]["categories"] = deep_merge_dicts(
                    unified_card_data.pop("spending_categories"), # Remove from top-level card
                    unified_card_data["rewards"]["categories"]
                )
            # Add meta if not present
            if "meta" not in unified_card_data:
                unified_card_data["meta"] = {
                    "bank": unified_card_data.get("bank", "Unknown Bank"),
                    "card": unified_card_data.get("name", "Unknown Card"),
                    "rating": "N/A" # Default rating
                }
        elif new_data: # Only new data available (shouldn't happen for these cards, but for future)
            unified_card_data = new_data.copy()
        
        if unified_card_data:
            output_filepath = data_dir / f"{card_key}-unified.json"
            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(unified_card_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully created unified data for {card_key} at {output_filepath}")
        else:
            logger.error(f"Failed to create unified data for {card_key}.")

if __name__ == "__main__":
    from datetime import datetime # Import here for main function scope
    main()
