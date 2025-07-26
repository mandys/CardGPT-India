#!/usr/bin/env python3
"""
CardGPT Automated Card Addition Pipeline
Comprehensive automation for adding new credit cards to the CardGPT system.

Usage:
    python add_new_card.py <path_to_card_json> [options]
    
Options:
    --dry-run: Validate only, don't make changes
    --force: Skip validation errors and proceed
    --rebuild-all: Rebuild entire JSONL from all cards
    --output-dir: Specify output directory (default: current)

Example:
    python add_new_card.py data/new_card.json --dry-run
    python add_new_card.py data/hdfc_regalia.json --rebuild-all
"""

import json
import logging
import shutil
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import subprocess

# Import our validation framework
try:
    from data_validation import CardDataValidator, ValidationError, CompletenessResult
except ImportError:
    print("Error: data_validation.py not found. Please ensure it's in the same directory.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('card_addition.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CardAdditionPipeline:
    """Automated pipeline for adding new credit cards to CardGPT"""
    
    def __init__(self, data_dir: str = "data", output_file: str = "card_data.jsonl"):
        self.data_dir = Path(data_dir)
        self.output_file = Path(output_file)
        self.backup_dir = Path("backups")
        self.validator = CardDataValidator()
        
        # Create necessary directories
        self.backup_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # Pipeline statistics
        self.stats = {
            'validation_errors': 0,
            'warnings': 0,
            'cards_processed': 0,
            'cards_added': 0,
            'total_chunks': 0
        }
    
    def add_card(self, card_file: Path, dry_run: bool = False, force: bool = False, 
                 rebuild_all: bool = False) -> bool:
        """
        Add a new credit card to the system
        
        Args:
            card_file: Path to the new card JSON file
            dry_run: If True, only validate without making changes
            force: If True, proceed despite validation errors
            rebuild_all: If True, rebuild entire JSONL from all cards
            
        Returns:
            bool: True if card was successfully added
        """
        logger.info(f"🚀 Starting card addition pipeline for: {card_file.name}")
        
        try:
            # Step 1: Load and parse card data
            card_data = self._load_card_data(card_file)
            if not card_data:
                return False
            
            card_name = card_data.get('card', {}).get('name', 'Unknown Card')
            card_id = card_data.get('card', {}).get('id', 'unknown_id')
            
            logger.info(f"📋 Processing: {card_name} (ID: {card_id})")
            
            # Step 2: Comprehensive validation
            validation_passed = self._validate_card_data(card_data, force)
            if not validation_passed and not force:
                logger.error("❌ Validation failed. Use --force to proceed anyway.")
                return False
            
            # Step 3: Check for duplicates
            if self._check_duplicate_card(card_id, card_file):
                logger.error(f"❌ Card with ID '{card_id}' already exists.")
                return False
            
            if dry_run:
                logger.info("✅ DRY RUN: Card validation passed. Would proceed with addition.")
                return True
            
            # Step 4: Create backup
            backup_success = self._create_backup()
            if not backup_success:
                logger.error("❌ Failed to create backup. Aborting for safety.")
                return False
            
            # Step 5: Copy card file to data directory
            target_file = self.data_dir / card_file.name
            if not self._copy_card_file(card_file, target_file):
                return False
            
            # Step 6: Rebuild JSONL
            if rebuild_all:
                success = self._rebuild_all_jsonl()
            else:
                success = self._add_card_to_jsonl(card_data)
            
            if not success:
                logger.error("❌ Failed to update JSONL. Rolling back changes.")
                self._rollback_changes(target_file)
                return False
            
            # Step 7: Final validation
            if not self._validate_jsonl_integrity():
                logger.error("❌ JSONL integrity check failed. Rolling back.")
                self._rollback_changes(target_file)
                return False
            
            # Step 8: Success!
            self.stats['cards_added'] += 1
            logger.info(f"✅ Successfully added {card_name} to CardGPT system!")
            logger.info(f"📊 Pipeline Stats: {self.stats}")
            
            # Step 9: Generate post-addition report
            self._generate_addition_report(card_data, card_file)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed with error: {str(e)}")
            return False
    
    def _load_card_data(self, card_file: Path) -> Optional[Dict[str, Any]]:
        """Load and parse card JSON data"""
        try:
            if not card_file.exists():
                logger.error(f"❌ File not found: {card_file}")
                return None
            
            with open(card_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"✅ Successfully loaded card data from {card_file.name}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in {card_file}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error loading {card_file}: {e}")
            return None
    
    def _validate_card_data(self, card_data: Dict[str, Any], force: bool = False) -> bool:
        """Comprehensive validation of card data"""
        logger.info("🔍 Running comprehensive card validation...")
        
        # Structure validation
        structure_errors = self.validator.validate_structure(card_data)
        
        # Completeness check
        completeness = self.validator.check_completeness(card_data)
        
        # Consistency validation
        consistency_errors = self.validator.validate_consistency(card_data)
        
        # Count errors by severity
        critical_errors = [e for e in structure_errors if e.severity == 'critical']
        high_errors = [e for e in structure_errors if e.severity == 'high']
        
        self.stats['validation_errors'] = len(structure_errors) + len(consistency_errors)
        self.stats['warnings'] = len([e for e in structure_errors if e.severity in ['medium', 'low']])
        
        # Log validation results
        logger.info(f"📊 Validation Results:")
        logger.info(f"   Overall Score: {completeness.overall_score:.1f}%")
        logger.info(f"   Critical Fields: {completeness.critical_score:.1f}%")
        logger.info(f"   Structure Errors: {len(structure_errors)}")
        logger.info(f"   Consistency Issues: {len(consistency_errors)}")
        
        # Print detailed errors
        if structure_errors:
            logger.warning("⚠️ Structure Validation Issues:")
            for error in structure_errors[:10]:  # Limit to first 10
                icon = "🚨" if error.severity == 'critical' else "⚠️"
                logger.warning(f"   {icon} {error.field_path}: {error.message}")
        
        if consistency_errors:
            logger.warning("⚠️ Consistency Issues:")
            for error in consistency_errors[:5]:  # Limit to first 5
                logger.warning(f"   ⚠️ {error.field_path}: {error.message}")
        
        # Determine if validation passed
        validation_passed = (
            completeness.overall_score >= 85 and
            len(critical_errors) == 0 and
            completeness.critical_score == 100
        )
        
        if validation_passed:
            logger.info("✅ Card validation passed!")
        else:
            if not force:
                logger.error("❌ Card validation failed:")
                if completeness.overall_score < 85:
                    logger.error(f"   - Overall completeness too low: {completeness.overall_score:.1f}% (required: 85%)")
                if len(critical_errors) > 0:
                    logger.error(f"   - Critical errors found: {len(critical_errors)}")
                if completeness.critical_score < 100:
                    logger.error(f"   - Missing critical fields: {completeness.missing_critical}")
            else:
                logger.warning("⚠️ Validation failed but proceeding due to --force flag")
        
        return validation_passed or force
    
    def _check_duplicate_card(self, card_id: str, new_file: Path) -> bool:
        """Check if card already exists"""
        for existing_file in self.data_dir.glob("*.json"):
            if existing_file.name == new_file.name:
                continue  # Skip if it's the same file being updated
            
            try:
                with open(existing_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                
                existing_id = existing_data.get('card', {}).get('id')
                if existing_id == card_id:
                    logger.error(f"❌ Duplicate card ID '{card_id}' found in {existing_file.name}")
                    return True
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not read {existing_file}: {e}")
        
        return False
    
    def _create_backup(self) -> bool:
        """Create backup of current state"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_subdir = self.backup_dir / f"backup_{timestamp}"
            backup_subdir.mkdir(exist_ok=True)
            
            # Backup data directory
            if self.data_dir.exists():
                shutil.copytree(self.data_dir, backup_subdir / "data", dirs_exist_ok=True)
            
            # Backup JSONL file
            if self.output_file.exists():
                shutil.copy2(self.output_file, backup_subdir / self.output_file.name)
            
            logger.info(f"✅ Created backup: {backup_subdir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return False
    
    def _copy_card_file(self, source: Path, target: Path) -> bool:
        """Copy card file to data directory"""
        try:
            shutil.copy2(source, target)
            logger.info(f"✅ Copied card file to: {target}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to copy card file: {e}")
            return False
    
    def _add_card_to_jsonl(self, card_data: Dict[str, Any]) -> bool:
        """Add single card to existing JSONL"""
        try:
            # Import the transform logic
            sys.path.append(str(Path.cwd()))
            from transform_to_jsonl import create_chunks_from_node
            import base64
            
            card_name = card_data.get("card", {}).get("name", "Unknown Card")
            chunks = create_chunks_from_node(card_data["card"], "card", card_name)
            
            # Append to existing JSONL
            with open(self.output_file, 'a', encoding='utf-8') as f_out:
                for chunk in chunks:
                    # Encode content to Base64 (matching existing pipeline)
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
                    self.stats['total_chunks'] += 1
            
            logger.info(f"✅ Added {len(chunks)} chunks to {self.output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update JSONL: {e}")
            return False
    
    def _rebuild_all_jsonl(self) -> bool:
        """Rebuild entire JSONL from all cards"""
        try:
            # Run the existing transform script
            logger.info("🔄 Rebuilding entire JSONL from all cards...")
            
            sys.path.append(str(Path.cwd()))
            from transform_to_jsonl import transform_data
            
            # Backup existing JSONL
            if self.output_file.exists():
                backup_file = self.output_file.with_suffix('.jsonl.backup')
                shutil.copy2(self.output_file, backup_file)
            
            # Run transformation
            transform_data()
            
            logger.info("✅ Successfully rebuilt JSONL file")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to rebuild JSONL: {e}")
            return False
    
    def _validate_jsonl_integrity(self) -> bool:
        """Validate integrity of final JSONL file"""
        try:
            if not self.output_file.exists():
                logger.error("❌ JSONL file doesn't exist")
                return False
            
            line_count = 0
            card_names = set()
            
            with open(self.output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line_count += 1
                    try:
                        doc = json.loads(line.strip())
                        card_name = doc.get('struct_data', {}).get('cardName')
                        if card_name:
                            card_names.add(card_name)
                    except json.JSONDecodeError:
                        logger.error(f"❌ Invalid JSON at line {line_count}")
                        return False
            
            logger.info(f"✅ JSONL integrity check passed: {line_count} chunks, {len(card_names)} cards")
            return True
            
        except Exception as e:
            logger.error(f"❌ JSONL integrity check failed: {e}")
            return False
    
    def _rollback_changes(self, card_file: Path) -> None:
        """Rollback changes if something fails"""
        try:
            if card_file.exists():
                card_file.unlink()
                logger.info(f"✅ Removed card file: {card_file}")
            
            # Restore JSONL from backup if available
            backup_file = self.output_file.with_suffix('.jsonl.backup')
            if backup_file.exists():
                shutil.copy2(backup_file, self.output_file)
                logger.info(f"✅ Restored JSONL from backup")
                
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
    
    def _generate_addition_report(self, card_data: Dict[str, Any], source_file: Path) -> None:
        """Generate post-addition report"""
        try:
            card_name = card_data.get('card', {}).get('name', 'Unknown Card')
            card_id = card_data.get('card', {}).get('id', 'unknown_id')
            
            report_file = Path(f"reports/card_addition_report_{card_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
            report_file.parent.mkdir(exist_ok=True)
            
            # Generate validation report
            validation_report = self.validator.generate_validation_report(card_data)
            
            # Create comprehensive report
            report_content = f"""# Card Addition Report: {card_name}

## Summary
- **Card Name**: {card_name}
- **Card ID**: {card_id}
- **Source File**: {source_file}
- **Addition Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status**: ✅ Successfully Added

## Pipeline Statistics
- **Cards Processed**: {self.stats['cards_processed']}
- **Cards Added**: {self.stats['cards_added']}
- **Total Chunks Created**: {self.stats['total_chunks']}
- **Validation Errors**: {self.stats['validation_errors']}
- **Warnings**: {self.stats['warnings']}

## Validation Report
{validation_report}

## Next Steps
1. **Upload to Google Cloud**: Upload updated `card_data.jsonl` to your Google Cloud Storage bucket
2. **Update Vertex AI Search**: Refresh the data store with new JSONL content
3. **Test Queries**: Run test queries to verify the new card is searchable
4. **Update Documentation**: Add the new card to README.md if needed

## Test Queries
Test these queries to verify the card works correctly:

```
What are the annual fees for {card_name}?
Compare {card_name} vs Axis Atlas
What rewards do I get with {card_name}?
```

---
Generated by CardGPT Automated Pipeline
"""
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"📄 Generated addition report: {report_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not generate report: {e}")


def main():
    """CLI interface for the card addition pipeline"""
    parser = argparse.ArgumentParser(
        description="CardGPT Automated Card Addition Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python add_new_card.py data/hdfc_regalia.json --dry-run
  python add_new_card.py data/new_card.json --force --rebuild-all
  python add_new_card.py data/amex_platinum.json
        """
    )
    
    parser.add_argument('card_file', help='Path to the card JSON file')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Validate only, don\'t make changes')
    parser.add_argument('--force', action='store_true',
                       help='Proceed despite validation errors')
    parser.add_argument('--rebuild-all', action='store_true',
                       help='Rebuild entire JSONL from all cards')
    parser.add_argument('--data-dir', default='data',
                       help='Data directory (default: data)')
    parser.add_argument('--output', default='card_data.jsonl',
                       help='Output JSONL file (default: card_data.jsonl)')
    
    args = parser.parse_args()
    
    # Validate input file
    card_file = Path(args.card_file)
    if not card_file.exists():
        logger.error(f"❌ Card file not found: {card_file}")
        sys.exit(1)
    
    # Initialize pipeline
    pipeline = CardAdditionPipeline(
        data_dir=args.data_dir,
        output_file=args.output
    )
    
    # Run pipeline
    success = pipeline.add_card(
        card_file=card_file,
        dry_run=args.dry_run,
        force=args.force,
        rebuild_all=args.rebuild_all
    )
    
    if success:
        logger.info("🎉 Card addition pipeline completed successfully!")
        if not args.dry_run:
            logger.info("📋 Don't forget to:")
            logger.info("   1. Upload card_data.jsonl to Google Cloud Storage")
            logger.info("   2. Refresh Vertex AI Search data store")
            logger.info("   3. Test queries with the new card")
        sys.exit(0)
    else:
        logger.error("❌ Card addition pipeline failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()