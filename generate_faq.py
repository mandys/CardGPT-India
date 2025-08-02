#!/usr/bin/env python3
"""
FAQ System Generator for Credit Card Comparison Queries
Creates pre-built answers for complex comparison questions to reduce RAG complexity

Usage:
    python generate_faq.py                    # Generate FAQ JSONL file
    python generate_faq.py --validate         # Validate FAQ entries
"""

import json
import base64
import argparse
from pathlib import Path
from datetime import datetime, timezone
import logging
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FAQGenerator:
    def __init__(self):
        self.output_file = Path("faq-common-questions.jsonl")
        
    def get_faq_entries(self) -> list:
        """Define common comparison FAQ entries"""
        current_time = datetime.now(timezone.utc).isoformat()
        
        faqs = [
            {
                "id": "faq_infinia_vs_atlas_education",
                "question": "Is HDFC Infinia better than Axis Atlas for education payments?",
                "answer": "For education payments, HDFC Infinia is significantly better than Axis Atlas. Infinia earns 5 points per ₹150 (3.33% return) on direct education payments, while Atlas earns 2 EDGE Miles per ₹100 (2% return). However, both cards charge 1% surcharge via third-party apps. For ₹1L education spend: Infinia = 3,333 points (₹3,333 value), Atlas = 2,000 miles (₹2,000 value).",
                "keywords": ["infinia", "atlas", "education", "comparison", "hdfc", "axis"],
                "confidence": 0.95,
                "categories": ["education", "comparison"],
                "cards": ["HDFC Infinia", "Axis Atlas"]
            },
            {
                "id": "faq_gold_purchase_best_card",
                "question": "Which card is best for gold and jewellery purchases?",
                "answer": "HDFC Infinia is the best for gold/jewellery purchases, earning 5 points per ₹150 (3.33% return). ICICI EPM earns 6 points per ₹200 (3% return). HSBC Premier earns 3 points per ₹100 but has ₹1L monthly cap. Axis Atlas excludes gold/jewellery completely (0% return). For ₹2L gold purchase: Infinia = ₹6,667 value, ICICI EPM = ₹6,000 value, HSBC Premier = ₹6,000 value (if within cap), Atlas = ₹0.",
                "keywords": ["gold", "jewellery", "jewelry", "best card", "comparison", "purchase"],
                "confidence": 0.92,
                "categories": ["gold_jewellery", "comparison"],
                "cards": ["HDFC Infinia", "ICICI EPM", "HSBC Premier", "Axis Atlas"]
            },
            {
                "id": "faq_fuel_surcharge_comparison",
                "question": "Which cards have fuel surcharge and waiver policies?",
                "answer": "All cards exclude fuel from rewards but have different surcharge policies. Axis Atlas: 1% surcharge beyond ₹50K monthly, waiver on ₹400-₹4K transactions (₹400 monthly cap). HDFC Infinia: 1% surcharge beyond ₹15K, waiver on ₹400-₹1L (₹1K monthly cap). ICICI EPM: 1% surcharge beyond ₹10K, waiver up to ₹4K at HPCL. HSBC Premier: 1% surcharge above ₹4K, waiver on ₹400-₹4K.",
                "keywords": ["fuel", "surcharge", "waiver", "comparison", "petrol"],
                "confidence": 0.88,
                "categories": ["fuel", "comparison"],
                "cards": ["All Cards"]
            },
            {
                "id": "faq_government_tax_payments",
                "question": "Which cards allow earning points on government and tax payments?",
                "answer": "Only HSBC Premier earns points on government/tax payments - 3 points per ₹100 up to ₹1L monthly spend limit. All other cards exclude government transactions: HDFC Infinia excludes 'government transactions for consumer cards', Axis Atlas excludes 'government institution' transactions, and ICICI EPM excludes 'government services' and 'tax' payments. For ₹50K tax payment: HSBC Premier = 1,500 points, others = 0 points.",
                "keywords": ["government", "tax", "payments", "income tax", "gst", "comparison"],
                "confidence": 0.93,
                "categories": ["government_tax", "comparison"],
                "cards": ["HSBC Premier", "HDFC Infinia", "Axis Atlas", "ICICI EPM"]
            },
            {
                "id": "faq_utility_payments_caps",
                "question": "What are the utility payment earning caps across cards?",
                "answer": "HDFC Infinia: Earns 5 points per ₹150, capped at 2,000 points monthly (₹60K spend). HSBC Premier: Earns 3 points per ₹100, capped at ₹1L monthly spend. ICICI EPM: Earns 6 points per ₹200, capped at 1,000 points per statement cycle (₹33.3K spend). Axis Atlas: Excludes utility completely (0 points). Surcharges apply beyond certain limits on most cards.",
                "keywords": ["utility", "cap", "limit", "electricity", "water", "comparison"],
                "confidence": 0.90,
                "categories": ["utility", "comparison"],
                "cards": ["HDFC Infinia", "HSBC Premier", "ICICI EPM", "Axis Atlas"]
            },
            {
                "id": "faq_rent_payment_options",
                "question": "Which cards are good for rent payments?",
                "answer": "Rent payments are generally unfavorable across all cards. HSBC Premier is the only card that earns points on rent (3 points per ₹100) but charges 1% processing fee. All other cards exclude rent from rewards: HDFC Infinia charges 1% surcharge from 2nd transaction monthly (July 2025), ICICI EPM charges 1% surcharge on all rent transactions, and Axis Atlas charges 1% surcharge on all rent transactions. Consider direct payment methods for rent.",
                "keywords": ["rent", "payment", "surcharge", "comparison", "housing"],
                "confidence": 0.87,
                "categories": ["rent", "comparison"],
                "cards": ["HSBC Premier", "HDFC Infinia", "ICICI EPM", "Axis Atlas"]
            },
            {
                "id": "faq_overall_best_card",
                "question": "Which is the overall best credit card among these four?",
                "answer": "There's no single 'best' card - it depends on spending patterns. HDFC Infinia: Best for gold/jewellery, travel (10X-5X via SmartBuy), general spending (3.33%). HSBC Premier: Best for government/tax payments, international travel, comprehensive benefits. ICICI EPM: Balanced earning (3%), good for general retail, luxury benefits. Axis Atlas: Best for direct travel bookings (5X), tier-based benefits, but many exclusions. Choose based on your primary spending categories.",
                "keywords": ["best card", "overall", "recommendation", "comparison", "choose"],
                "confidence": 0.85,
                "categories": ["comparison", "general"],
                "cards": ["HDFC Infinia", "HSBC Premier", "ICICI EPM", "Axis Atlas"]
            },
            {
                "id": "faq_annual_fee_value",
                "question": "Which card provides the best value for annual fees?",
                "answer": "Fee-to-value analysis: HDFC Infinia (₹10K fee): Excellent if you use SmartBuy, golf benefits, unlimited lounge. HSBC Premier (₹20K fee): Great for Premier customers, comprehensive travel benefits, golf league. ICICI EPM (₹12.5K from 2nd year): Good milestone benefits, golf access, balanced rewards. Axis Atlas (₹5K fee): Lowest fee, good for travel-focused spenders, tier upgrades. Consider spending patterns and benefit usage for value assessment.",
                "keywords": ["annual fee", "value", "worth", "cost", "comparison", "fees"],
                "confidence": 0.82,
                "categories": ["fees", "comparison"],
                "cards": ["HDFC Infinia", "HSBC Premier", "ICICI EPM", "Axis Atlas"]
            },
            {
                "id": "faq_insurance_premium_earning",
                "question": "Which cards earn points on insurance premium payments?",
                "answer": "Three cards earn points on insurance premiums: HDFC Infinia earns 5 points per ₹150 (3.33% return) with daily cap of 5,000 points. HSBC Premier earns 3 points per ₹100 (3% return) up to ₹1L monthly spend. ICICI EPM earns 6 points per ₹200 (3% return) with 5,000 points cap per statement cycle. Axis Atlas excludes insurance premiums completely (0% return). For ₹50K annual premium: Infinia = 1,667 points (₹1,667 value), HSBC = 1,500 points, ICICI EPM = 1,500 points, Atlas = 0 points.",
                "keywords": ["insurance", "premium", "earning", "comparison", "life insurance", "health insurance"],
                "confidence": 0.91,
                "categories": ["insurance", "comparison"],
                "cards": ["HDFC Infinia", "HSBC Premier", "ICICI EPM", "Axis Atlas"]
            }
        ]
        
        # Add metadata to each FAQ entry
        for faq in faqs:
            faq["metadata"] = {
                "created_at": current_time,
                "version": "v1.0",
                "content_hash": self.generate_content_hash(faq["answer"]),
                "faq_type": "comparison_query"
            }
            
        return faqs
    
    def generate_content_hash(self, content: str) -> str:
        """Generate a consistent hash for content tracking"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def generate_faq_jsonl(self) -> int:
        """Generate FAQ JSONL file with Vertex AI Search format"""
        faqs = self.get_faq_entries()
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for faq in faqs:
                # Create comprehensive searchable content
                searchable_content = f"""Question: {faq['question']}

Answer: {faq['answer']}

Related Keywords: {', '.join(faq['keywords'])}
Categories: {', '.join(faq['categories'])}
Cards Covered: {', '.join(faq['cards'])}
Confidence Level: {faq['confidence']*100:.1f}%

FAQ Type: Pre-built comparison answer for complex queries"""
                
                # Encode content for Vertex AI Search
                content_bytes = searchable_content.encode('utf-8')
                content_base64 = base64.b64encode(content_bytes).decode('utf-8')
                
                # Create Vertex AI Search document
                vertex_doc = {
                    "id": faq["id"],
                    "struct_data": {
                        "question": faq["question"],
                        "categories": faq["categories"],
                        "cards": faq["cards"],
                        "keywords": faq["keywords"],
                        "confidence": faq["confidence"],
                        "created_at": faq["metadata"]["created_at"],
                        "version": faq["metadata"]["version"],
                        "content_hash": faq["metadata"]["content_hash"],
                        "document_type": "faq",
                        "faq_type": faq["metadata"]["faq_type"]
                    },
                    "content": {
                        "mime_type": "text/plain",
                        "raw_bytes": content_base64
                    }
                }
                
                f.write(json.dumps(vertex_doc) + '\n')
        
        return len(faqs)
    
    def validate_faqs(self) -> bool:
        """Validate FAQ entries for completeness and accuracy"""
        faqs = self.get_faq_entries()
        
        required_fields = ["id", "question", "answer", "keywords", "confidence", "categories", "cards"]
        issues = []
        
        for i, faq in enumerate(faqs):
            # Check required fields
            for field in required_fields:
                if field not in faq or not faq[field]:
                    issues.append(f"FAQ {i+1}: Missing or empty field '{field}'")
            
            # Check confidence range
            if "confidence" in faq and not (0 <= faq["confidence"] <= 1):
                issues.append(f"FAQ {i+1}: Confidence should be between 0 and 1")
            
            # Check answer length
            if "answer" in faq and len(faq["answer"]) < 50:
                issues.append(f"FAQ {i+1}: Answer too short (< 50 characters)")
            
            # Check for duplicate IDs
            ids = [f["id"] for f in faqs]
            if len(set(ids)) != len(ids):
                issues.append("Duplicate FAQ IDs found")
        
        if issues:
            logger.error("❌ FAQ validation failed:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        else:
            logger.info(f"✅ All {len(faqs)} FAQ entries validated successfully")
            return True

def main():
    parser = argparse.ArgumentParser(description="Generate FAQ system for credit card comparisons")
    parser.add_argument("--validate", action="store_true", help="Validate FAQ entries only")
    
    args = parser.parse_args()
    generator = FAQGenerator()
    
    try:
        if args.validate:
            success = generator.validate_faqs()
            if not success:
                exit(1)
        else:
            # Validate first, then generate
            if not generator.validate_faqs():
                logger.error("❌ FAQ validation failed - aborting generation")
                exit(1)
            
            faq_count = generator.generate_faq_jsonl()
            logger.info(f"✅ Generated {generator.output_file.name} with {faq_count} FAQ entries")
            logger.info(f"📄 FAQ file ready for upload: {generator.output_file.name}")
            
    except Exception as e:
        logger.error(f"❌ FAQ generation failed: {e}")
        raise

if __name__ == "__main__":
    main()