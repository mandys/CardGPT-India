#!/usr/bin/env python3
"""
Incremental Update System for Credit Card RAG Data
Generates only changed chunks to eliminate 20-30 minute downtime

Usage:
    python incremental_update.py                    # Detect changes and generate delta
    python incremental_update.py --full-rebuild     # Force full rebuild with new versioning
    python incremental_update.py --check-changes    # Check what has changed without generating
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
import logging
import hashlib
from typing import Dict, Tuple, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IncrementalUpdater:
    def __init__(self):
        self.data_path = Path("data")
        self.output_file = Path("card_data.jsonl")
        self.delta_file = Path("card_data_delta.jsonl")
        self.state_file = Path(".incremental_state.json")
        
    def load_previous_state(self) -> Dict:
        """Load previous file states for change detection"""
        if not self.state_file.exists():
            return {}
        
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load previous state: {e}")
            return {}
    
    def save_current_state(self, state: Dict):
        """Save current file states for future change detection"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def get_file_hash(self, file_path: Path) -> str:
        """Generate hash of file contents for change detection"""
        if not file_path.exists():
            return ""
        
        with open(file_path, 'rb') as f:
            content = f.read()
            return hashlib.sha256(content).hexdigest()
    
    def get_current_state(self) -> Dict:
        """Get current state of all JSON files"""
        current_state = {}
        json_files = list(self.data_path.glob("*.json"))
        
        for json_file in json_files:
            file_hash = self.get_file_hash(json_file)
            file_stat = json_file.stat()
            
            current_state[str(json_file)] = {
                "hash": file_hash,
                "last_modified": file_stat.st_mtime,
                "size": file_stat.st_size
            }
            
        return current_state
    
    def detect_changes(self) -> Tuple[List[Path], Dict]:
        """Detect which files have changed since last run"""
        previous_state = self.load_previous_state()
        current_state = self.get_current_state()
        
        changed_files = []
        json_files = list(self.data_path.glob("*.json"))
        
        for json_file in json_files:
            file_key = str(json_file)
            current_info = current_state.get(file_key, {})
            previous_info = previous_state.get(file_key, {})
            
            # Check if file is new or hash has changed
            if (current_info.get("hash") != previous_info.get("hash") or
                not previous_info):  # New file
                changed_files.append(json_file)
                logger.info(f"📝 Detected changes in: {json_file.name}")
        
        if not changed_files:
            logger.info("✅ No changes detected in JSON files")
        
        return changed_files, current_state
    
    def generate_chunks_for_files(self, files: List[Path], is_delta: bool = True) -> int:
        """Generate chunks for specific files only"""
        # Import the enhanced transform functions
        from transform_to_jsonl import create_chunks_from_node, get_file_metadata
        
        output_file = self.delta_file if is_delta else self.output_file
        
        with open(output_file, 'w', encoding='utf-8') as f_out:
            total_chunks = 0
            generation_time = datetime.now(timezone.utc).isoformat()
            
            for json_file in files:
                logger.info(f"🔄 Processing {json_file.name}...")
                
                # Get file metadata for tracking changes
                file_metadata = get_file_metadata(json_file)
                
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
                        chunks = create_chunks_from_node(section_data, section_name, card_name, file_metadata)
                        
                        for chunk in chunks:
                            # Encode the text content to bytes, then to a Base64 string
                            content_bytes = chunk["content"].encode('utf-8')
                            content_base64 = __import__('base64').b64encode(content_bytes).decode('utf-8')

                            # Enhanced structured data with versioning for incremental updates
                            vertex_doc = {
                                "id": chunk["id"],
                                "struct_data": {
                                    "cardName": chunk["cardName"],
                                    "section": chunk["section"],
                                    "aliases": chunk.get("aliases", []),
                                    "updated_at": chunk["metadata"]["updated_at"],
                                    "version": chunk["metadata"]["version"],
                                    "content_hash": chunk["metadata"]["content_hash"],
                                    "chunk_type": chunk["metadata"]["chunk_type"],
                                    "generation_time": generation_time,
                                    "file_last_modified": chunk["metadata"]["file_metadata"].get("last_modified"),
                                    "incremental_update_ready": True,
                                    "is_delta_update": is_delta
                                },
                                "content": {
                                    "mime_type": "text/plain",
                                    "raw_bytes": content_base64
                                }
                            }
                            
                            f_out.write(json.dumps(vertex_doc) + '\n')
                            total_chunks += 1
        
        return total_chunks
    
    def run_incremental_update(self) -> Tuple[bool, int]:
        """Run incremental update process"""
        changed_files, current_state = self.detect_changes()
        
        if not changed_files:
            return False, 0
        
        # Generate delta chunks for changed files only
        chunk_count = self.generate_chunks_for_files(changed_files, is_delta=True)
        
        # Save current state for next run
        self.save_current_state(current_state)
        
        logger.info(f"✅ Generated delta update: {self.delta_file.name} with {chunk_count} chunks")
        return True, chunk_count
    
    def run_full_rebuild(self) -> int:
        """Run full rebuild with new versioning system"""
        json_files = list(self.data_path.glob("*.json"))
        current_state = self.get_current_state()
        
        # Generate full chunks with new versioning
        chunk_count = self.generate_chunks_for_files(json_files, is_delta=False)
        
        # Save current state
        self.save_current_state(current_state)
        
        logger.info(f"✅ Full rebuild complete: {self.output_file.name} with {chunk_count} chunks")
        return chunk_count
    
    def check_changes_only(self):
        """Check what has changed without generating files"""
        changed_files, _ = self.detect_changes()
        
        if not changed_files:
            logger.info("🔍 No changes detected")
            return
        
        logger.info(f"🔍 Found changes in {len(changed_files)} files:")
        for file_path in changed_files:
            logger.info(f"  📝 {file_path.name}")

def main():
    parser = argparse.ArgumentParser(description="Incremental update system for credit card RAG data")
    parser.add_argument("--full-rebuild", action="store_true", 
                       help="Force full rebuild with new versioning")
    parser.add_argument("--check-changes", action="store_true",
                       help="Check what has changed without generating files")
    
    args = parser.parse_args()
    updater = IncrementalUpdater()
    
    try:
        if args.check_changes:
            updater.check_changes_only()
        elif args.full_rebuild:
            chunk_count = updater.run_full_rebuild()
            logger.info(f"🚀 Full rebuild completed with {chunk_count} chunks")
        else:
            # Default: incremental update
            has_changes, chunk_count = updater.run_incremental_update()
            
            if has_changes:
                logger.info(f"🚀 Incremental update completed with {chunk_count} delta chunks")
                logger.info(f"📄 Delta file ready for upload: {updater.delta_file.name}")
            else:
                logger.info("✅ No updates needed - all files are current")
                
    except Exception as e:
        logger.error(f"❌ Update failed: {e}")
        raise

if __name__ == "__main__":
    main()