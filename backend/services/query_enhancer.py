"""
Query Enhancement Service
Preprocesses user queries to detect categories and ensure correct earning rates are applied
"""

import re
from typing import Dict, Tuple, Optional
import logging
from services.card_config import get_card_config

logger = logging.getLogger(__name__)

class QueryEnhancer:
    """Enhances user queries to improve LLM accuracy for credit card calculations"""
    
    def __init__(self):
        # Get card configuration service
        self.card_config = get_card_config()
        
        # Build card patterns and mappings from configuration
        self._build_card_patterns()
        
        # Initialize other patterns
        self._initialize_patterns()
    
    def _build_card_patterns(self):
        """Build card patterns and mappings from centralized configuration"""
        self.card_patterns = {}
        self.card_name_mapping = {}
        
        for card in self.card_config.get_all_active_cards():
            display_name = card["display_name"]
            aliases = card.get("aliases", [])
            jsonl_name = card["jsonl_name"]
            
            # Build pattern mapping (display_name -> aliases)
            self.card_patterns[display_name] = aliases
            
            # Build name mapping (display_name -> jsonl_name)
            self.card_name_mapping[display_name] = jsonl_name
    
    def _initialize_patterns(self):
        
        # Simplified category detection patterns - basic keywords only
        self.category_patterns = {
            'hotel': ['hotel', 'hotels', 'accommodation', 'stay'],
            'flight': ['flight', 'flights', 'airline', 'airlines'],
            'travel': ['travel', 'vacation', 'trip', 'journey'],
            'dining': ['dining', 'restaurant', 'food', 'meal'],
            'fuel': ['fuel', 'petrol', 'diesel'],
            'utility': ['utility', 'utilities', 'electricity', 'mobile bill'],
            'insurance': ['insurance', 'policy'],
            'education': ['education', 'school fee', 'tuition'],
            'government': ['government', 'tax', 'municipal'],
            'rent': ['rent', 'rental'],
            'milestone': ['milestone', 'milestones']
        }
        
        # Spend amount patterns for Indian currency
        self.amount_patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|l\b)',
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:crore|cr\b)',
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:thousand|k\b)',
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)', # Corrected: Added missing newline character here
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|l\b)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:crore|cr\b)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:thousand|k\b)',
        ]
        
        # Simplified comparison patterns
        self.comparison_patterns = [
            'which card', 'best card', 'compare', 'vs', 'versus', 'better'
        ]
    
    def detect_card_name(self, query: str) -> Optional[str]:
        """Detect credit card name from the query."""
        query_lower = query.lower()
        for card_name, keywords in self.card_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                return card_name
        return None
    
    def detect_category(self, query: str) -> Optional[str]:
        """Detect spending category from query"""
        query_lower = query.lower()
        
        # Check each category
        for category, keywords in self.category_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return None
    
    def detect_spend_amount(self, query: str) -> Optional[str]:
        """Extract spending amount from query"""
        for pattern in self.amount_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).replace(',', '')
        return None
    
    def is_comparison_query(self, query: str) -> bool:
        """Detect if this is a comparison query"""
        query_lower = query.lower()
        return any(pattern in query_lower for pattern in self.comparison_patterns)
    
    def detect_direct_comparison(self, query: str) -> Optional[tuple]:
        """Detect direct card-to-card comparison queries"""
        import re
        
        direct_comparison_patterns = [
            r'\bbetween\s+(\w+).*?and\s+(\w+)', 
            r'(\w+)\s+vs\s+(\w+)', 
            r'(\w+)\s+versus\s+(\w+)',
            r'compare\s+(\w+).*?and\s+(\w+)',
            r'(\w+)\s+or\s+(\w+)',
            r'(\w+)\s+better\s+than\s+(\w+)'
        ]
        
        for pattern in direct_comparison_patterns:
            match = re.search(pattern, query.lower())
            if match:
                logger.info(f"Direct comparison detected: {match.groups()}")
                return match.groups()
        
        return None

    def enhance_search_query(self, query: str) -> Tuple[str, Dict[str, any]]:
        """
        Simplified query enhancement - minimal processing, let Vertex AI Search do the heavy lifting
        
        Returns:
            Tuple of (enhanced_search_query, metadata)
        """
        card_detected = self.detect_card_name(query)
        category = self.detect_category(query)
        spend_amount = self.detect_spend_amount(query)
        is_comparison = self.is_comparison_query(query)
        direct_comparison = self.detect_direct_comparison(query)
        
        metadata = {
            'card_detected': card_detected,
            'category_detected': category,
            'spend_amount': spend_amount,
            'is_calculation_query': bool(spend_amount),
            'is_comparison': is_comparison,
            'direct_comparison': direct_comparison
        }
        
        # Start with the original query - minimal enhancement approach
        enhanced_query = query
        
        # Only add card names for direct comparisons to ensure balanced retrieval
        if direct_comparison:
            card1, card2 = direct_comparison
            enhanced_query += f" {card1} {card2}"
            logger.info(f"Enhanced for direct comparison: {direct_comparison}")
        
        # Add basic category context only if spending amount is mentioned (calculation queries)
        if category and spend_amount:
            enhanced_query += f" {category} spending rates"
        
        # Fix insurance ambiguity: distinguish between spending on insurance vs insurance benefits
        if category == 'insurance':
            if any(word in query.lower() for word in ['spend', 'spending', 'spends', 'rewards', 'points', 'earn', 'rate']):
                # This is about earning rewards when paying insurance premiums
                enhanced_query += " insurance spending rewards caps monthly limit premium"
                logger.info("Enhanced for insurance spending rewards (not benefits)")
            elif any(word in query.lower() for word in ['coverage', 'benefit', 'travel insurance', 'accident', 'protection']):
                # This is about insurance coverage provided by the card
                enhanced_query += " insurance coverage benefits travel accident protection"
                logger.info("Enhanced for insurance benefits/coverage (not spending)")
        
        logger.info(f"Enhanced query: '{enhanced_query}', metadata: {metadata}")
        return enhanced_query, metadata
    
    
