#!/usr/bin/env python3
"""
Modular Card Addition Pipeline for CardGPT
Creates separate JSONL files for each card - no automatic Google Cloud upload
"""

import json
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Import our validation and JSONL creation tools
try:
    from plans.data_validation import CardDataValidator
    from create_card_jsonl import create_card_jsonl
except ImportError as e:
    print(f"Error: Required modules not found: {e}")
    print("Ensure you're running from the project root directory.")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_card_modular(card_file: Path, dry_run: bool = False) -> bool:
    """
    Add a new credit card using modular approach
    
    Args:
        card_file: Path to the card JSON file
        dry_run: If True, only validate without creating files
        
    Returns:
        bool: True if successful
    """
    logger.info(f"🚀 Starting modular card addition for: {card_file.name}")
    
    try:
        # Step 1: Load and validate card data
        with open(card_file, 'r', encoding='utf-8') as f:
            card_data = json.load(f)
        
        card_name = card_data.get('card', {}).get('name', 'Unknown Card')
        card_id = card_data.get('card', {}).get('id', 'unknown_id')
        
        logger.info(f"📋 Processing: {card_name} (ID: {card_id})")
        
        # Step 2: Validate card data
        validator = CardDataValidator()
        
        # Structure validation
        structure_errors = validator.validate_structure(card_data)
        completeness = validator.check_completeness(card_data)
        consistency_errors = validator.validate_consistency(card_data)
        
        critical_errors = [e for e in structure_errors if e.severity == 'critical']
        
        logger.info(f"📊 Validation Results:")
        logger.info(f"   Overall Score: {completeness.overall_score:.1f}%")
        logger.info(f"   Critical Fields: {completeness.critical_score:.1f}%")
        logger.info(f"   Structure Errors: {len(structure_errors)}")
        
        # Check if validation passed
        validation_passed = (
            completeness.overall_score >= 85 and
            len(critical_errors) == 0 and
            completeness.critical_score == 100
        )
        
        if not validation_passed:
            logger.error("❌ Card validation failed:")
            if completeness.overall_score < 85:
                logger.error(f"   - Overall completeness too low: {completeness.overall_score:.1f}% (required: 85%)")
            if len(critical_errors) > 0:
                logger.error(f"   - Critical errors found: {len(critical_errors)}")
            if completeness.critical_score < 100:
                logger.error(f"   - Missing critical fields: {completeness.missing_critical}")
            return False
        
        logger.info("✅ Card validation passed!")
        
        if dry_run:
            logger.info("✅ DRY RUN: Card would be successfully added.")
            return True
        
        # Step 3: Create separate JSONL file
        base_name = card_file.stem  # e.g., hdfc-infinia
        output_file = Path(f"{base_name}-data.jsonl")
        
        success = create_card_jsonl(card_file, output_file)
        
        if not success:
            logger.error("❌ Failed to create JSONL file")
            return False
        
        # Step 4: Print upload instructions
        logger.info("\n🎉 Card successfully prepared for upload!")
        logger.info("=" * 60)
        logger.info(f"📋 Card: {card_name}")
        logger.info(f"📁 JSONL File: {output_file}")
        logger.info(f"📊 File Size: {output_file.stat().st_size:,} bytes")
        
        print(f"\n📤 UPLOAD INSTRUCTIONS:")
        print(f"1. Upload the JSONL file to Google Cloud Storage:")
        print(f"   gsutil cp {output_file} gs://your-bucket-name/cards/")
        print(f"")
        print(f"2. Trigger incremental import in Vertex AI Search console:")
        print(f"   - Select 'Incremental' import")
        print(f"   - Choose the uploaded {output_file} file")
        print(f"   - Click 'Import' (processing takes 2-5 minutes)")
        print(f"")
        print(f"3. Test queries after indexing completes:")
        print(f"   - What are the annual fees for {card_name}?")
        print(f"   - Compare {card_name} vs Axis Atlas")
        print(f"   - What rewards do I get with {card_name}?")
        print(f"")
        print(f"✅ Benefits of modular approach:")
        print(f"   - Faster upload ({output_file.stat().st_size:,} bytes vs full file)")
        print(f"   - No disruption to existing cards")
        print(f"   - Easy to manage individual cards")
        print(f"   - Quick incremental indexing")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed with error: {str(e)}")
        return False

def main():
    """CLI interface for modular card addition"""
    parser = argparse.ArgumentParser(
        description="Modular Card Addition Pipeline - Creates separate JSONL files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python add_card_modular.py data/hdfc-infinia.json --dry-run
  python add_card_modular.py data/hdfc-infinia.json
  python add_card_modular.py data/new-card.json
        """
    )
    
    parser.add_argument('card_file', help='Path to the card JSON file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Validate only, don\'t create files')
    
    args = parser.parse_args()
    
    # Validate input file
    card_file = Path(args.card_file)
    if not card_file.exists():
        logger.error(f"❌ Card file not found: {card_file}")
        return 1
    
    # Run modular addition
    success = add_card_modular(card_file, dry_run=args.dry_run)
    
    if success:
        if not args.dry_run:
            logger.info("🎉 Modular card addition completed successfully!")
        return 0
    else:
        logger.error("❌ Modular card addition failed!")
        return 1

if __name__ == "__main__":
    exit(main())