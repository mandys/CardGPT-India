"""
Query Enhancement Service
Preprocesses user queries to detect categories and ensure correct earning rates are applied
"""

import re
from typing import Dict, Tuple, Optional


class QueryEnhancer:
    """Enhances user queries to improve LLM accuracy for credit card calculations"""
    
    def __init__(self):
        # Card name detection patterns
        self.card_patterns = {
            'Axis Atlas': ['axis atlas', 'atlas'],
            'ICICI EPM': ['icici epm', 'epm', 'emeralde private'],
            'HSBC Premier': ['hsbc premier', 'premier']
        }
        
        # Category detection patterns
        self.category_patterns = {
            'hotel': [
                'hotel', 'hotels', 'hotel booking', 'hotel bookings', 
                'accommodation', 'stay', 'lodging', 'resort'
            ],
            'flight': [
                'flight', 'flights', 'airline', 'airlines', 'air travel',
                'airfare', 'ticket', 'aviation'
            ],
            'travel': [
                'travel', 'vacation', 'trip', 'tour', 'journey'
            ],
            'dining': [
                'dining', 'restaurant', 'food', 'meal', 'cafe', 
                'zomato', 'swiggy'
            ],
            'fuel': [
                'fuel', 'petrol', 'diesel', 'gas', 'gasoline',
                'gas station', 'petrol pump'
            ],
            'utility': [
                'utility', 'utilities', 'electricity', 'electric bill',
                'water bill', 'mobile bill', 'internet', 'broadband',
                'utility payment', 'utility payments'
            ],
            'grocery': [
                'grocery', 'groceries', 'supermarket', 'vegetables',
                'provisions', 'shopping'
            ],
            'insurance': [
                'insurance', 'insurance premium', 'insurance payment',
                'policy', 'health insurance'
            ],
            'education': [
                'education', 'school fee', 'college fee', 'university',
                'tuition', 'course fee'
            ],
            'government': [
                'government', 'tax', 'municipal', 'challan',
                'income tax', 'gst', 'fine'
            ],
            'rent': [
                'rent', 'rental', 'house rent', 'apartment rent'
            ],
            'milestone': [
                'milestone', 'milestones', 'milestone benefit', 'milestone benefits',
                'spending milestone', 'spending milestones', 'milestone reward',
                'milestone rewards', 'spend milestone', 'annual milestone'
            ]
        }
        
        # Spend amount patterns for Indian currency
        self.amount_patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|l\b)',
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:crore|cr\b)',
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:thousand|k\b)',
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|l\b)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:crore|cr\b)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:thousand|k\b)',
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
    
    def enhance_query(self, query: str) -> Tuple[str, Dict[str, any]]:
        """
        Enhance query with category and card detection, plus other metadata
        
        Returns:
            Tuple of (enhanced_query, metadata)
        """
        card_detected = self.detect_card_name(query)  # Call the new method
        category = self.detect_category(query)
        spend_amount = self.detect_spend_amount(query)
        
        metadata = {
            'card_detected': card_detected,  # Add the detected card to metadata
            'category_detected': category,
            'spend_amount': spend_amount,
            'is_calculation_query': bool(spend_amount),
            'requires_category_rate': category in ['hotel', 'flight', 'travel']
        }
        
        # Enhance the query with explicit category information
        enhanced_query = query
        
        # Detect spend distribution queries
        is_distribution_query = any(word in query.lower() for word in ['split', 'distribution', 'monthly', 'breakdown', 'categories'])
        
        if category and spend_amount:
            # Make category explicit in the query with generic guidance
            if category in ['hotel', 'flight']:
                enhanced_query += f"\n\nIMPORTANT: This is specifically about {category} spending. Check for accelerated earning rates for {category} category. Look for any monthly caps on accelerated rates - if spend exceeds cap, use base rate for excess amount."
            elif category == 'utility':
                enhanced_query += f"\n\nIMPORTANT: This is about utility spending. Check BOTH rewards AND surcharges: Some cards exclude utilities (0 rewards), others have caps. Check for surcharge fees on amounts above monthly thresholds. Calculate: 1% × (spend - threshold) if spend exceeds threshold."
            elif category in ['fuel', 'rent', 'government', 'insurance']:
                enhanced_query += f"\n\nIMPORTANT: This is about {category} spending. Check exclusions first - this category may be excluded from earning rewards on some cards."
            elif category == 'education':
                enhanced_query += f"\n\nIMPORTANT: This is about education spending. Check for earning caps or exclusions for education category. Some cards may have monthly/cycle caps."
        elif category == 'milestone':
            # Handle milestone queries separately (they often don't have spend amounts)
            enhanced_query += f"\n\nIMPORTANT: This is about milestone benefits. Check both the dedicated 'milestones' section AND the 'renewal_benefits' section which may contain milestone-related vouchers and benefits."
        elif category == 'utility' and any(keyword in query.lower() for keyword in ['surcharge', 'fee', 'charge', 'cost']):
            # Handle utility fee/surcharge queries separately
            enhanced_query += f"\n\nIMPORTANT: This is about utility fees/surcharges. Calculate surcharges on amount ABOVE threshold if mentioned. Show surcharge calculation: percentage × (spend - threshold)."
        elif is_distribution_query:
            enhanced_query += f"\n\nIMPORTANT: This is a spend distribution query. For each category, calculate separately using the appropriate rate (base rate for most categories, accelerated for hotels/flights, zero for excluded categories). Do NOT add base + category rates."
        elif spend_amount and not category:
            enhanced_query += f"\n\nNote: No specific category mentioned, so use BASE RATE for calculation."
        
        return enhanced_query, metadata
    
    def get_category_guidance(self, category: str) -> str:
        """Get general guidance for specific spending categories"""
        guidance = {
            'hotel': 'Look for accelerated earning rates for hotel bookings. Check for monthly caps on accelerated rates.',
            'flight': 'Look for accelerated earning rates for flight bookings. Check for monthly caps on accelerated rates.',
            'fuel': 'Commonly excluded from earning rewards on most cards. Check exclusion lists.',
            'utility': 'May be excluded or have earning caps. Check for surcharge fees above spending thresholds.',
            'rent': 'Commonly excluded from earning rewards on most cards. Check exclusion lists.',
            'government': 'Commonly excluded from earning rewards on most cards. Check exclusion lists.',
            'insurance': 'May be excluded or have earning caps depending on the card.',
            'education': 'May have earning caps or be treated as general spending depending on the card.',
            'grocery': 'May have earning caps or accelerated rates depending on the card.',
            'dining': 'Often treated as general spending, but some cards may have accelerated rates.'
        }
        
        return guidance.get(category, 'Check the card-specific earning rates and exclusions for this category.')