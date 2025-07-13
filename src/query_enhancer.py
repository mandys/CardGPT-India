"""
Query Enhancement Service
Preprocesses user queries to detect categories and ensure correct earning rates are applied
"""

import re
from typing import Dict, Tuple, Optional


class QueryEnhancer:
    """Enhances user queries to improve LLM accuracy for credit card calculations"""
    
    def __init__(self):
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
        Enhance query with category detection and metadata
        
        Returns:
            Tuple of (enhanced_query, metadata)
        """
        category = self.detect_category(query)
        spend_amount = self.detect_spend_amount(query)
        
        metadata = {
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
            # Make category explicit in the query with specific card guidance
            if category in ['hotel', 'flight']:
                enhanced_query += f"\n\nIMPORTANT: This is specifically about {category} spending. Use the accelerated {category} earning rate (5x) for Axis Atlas. CHECK CAPS: 5x rate applies to spend UP TO ₹2L per month. Only split calculation if spend EXCEEDS ₹2L (above ₹2L use base 2x rate)."
            elif category == 'utility':
                enhanced_query += f"\n\nIMPORTANT: This is about utility spending. Check BOTH rewards AND surcharges: Axis Atlas EXCLUDES utilities (0 rewards) + 1% surcharge above ₹25K/month. ICICI EPM earns 6 points per ₹200 but CAPPED at MAX 1,000 points per cycle (regardless of spend amount) + 1% surcharge above ₹50K/month."
            elif category in ['fuel', 'rent', 'government', 'insurance']:
                enhanced_query += f"\n\nIMPORTANT: This is about {category} spending. Check exclusions first - this category may be excluded from earning rewards."
            elif category == 'education':
                enhanced_query += f"\n\nIMPORTANT: This is about education spending. ICICI EPM has a cap of 1,000 points per cycle for education. Axis Atlas has NO exclusions for education - use base rate (2 miles per ₹100)."
        elif category == 'milestone':
            # Handle milestone queries separately (they often don't have spend amounts)
            enhanced_query += f"\n\nIMPORTANT: This is about milestone benefits. Check both the dedicated 'milestones' section AND the 'renewal_benefits' section which contains milestone-related vouchers and benefits. ICICI EPM has EaseMyTrip vouchers at ₹4L and ₹8L spend milestones."
        elif category == 'utility' and any(keyword in query.lower() for keyword in ['surcharge', 'fee', 'charge', 'cost']):
            # Handle utility fee/surcharge queries separately
            enhanced_query += f"\n\nIMPORTANT: This is about utility fees/surcharges. Check the 'surcharge_fees' section for both cards: Axis Atlas has 1% surcharge above ₹25K/month, ICICI EPM has 1% surcharge above ₹50K/month."
        elif is_distribution_query:
            enhanced_query += f"\n\nIMPORTANT: This is a spend distribution query. For each category, calculate separately using the appropriate rate (base rate for most categories, accelerated for hotels/flights, zero for excluded categories). Do NOT add base + category rates."
        elif spend_amount and not category:
            enhanced_query += f"\n\nNote: No specific category mentioned, so use BASE RATE for calculation."
        
        return enhanced_query, metadata
    
    def get_category_hints(self, category: str) -> Dict[str, str]:
        """Get earning rate hints for specific categories"""
        hints = {
            'hotel': {
                'axis_atlas': '5 EDGE Miles per ₹100 for hotel bookings (accelerated rate)',
                'icici_epm': '6 points per ₹200 (same as general rate)'
            },
            'flight': {
                'axis_atlas': '5 EDGE Miles per ₹100 for flights (accelerated rate)', 
                'icici_epm': '6 points per ₹200 (same as general rate)'
            },
            'fuel': {
                'axis_atlas': 'Excluded from earning (0 rewards)',
                'icici_epm': 'Excluded from earning (0 rewards)'
            },
            'utility': {
                'axis_atlas': 'Excluded from earning (0 rewards)',
                'icici_epm': 'Earns rewards but capped at 1,000 points per cycle'
            },
            'rent': {
                'axis_atlas': 'Excluded from earning (0 rewards)',
                'icici_epm': 'Excluded from earning (0 rewards)'
            },
            'government': {
                'axis_atlas': 'Excluded from earning (0 rewards)',
                'icici_epm': 'Excluded from earning (0 rewards)'
            },
            'insurance': {
                'axis_atlas': 'Excluded from earning (0 rewards)',
                'icici_epm': 'Earns rewards but capped at 5,000 points per cycle'
            }
        }
        
        return hints.get(category, {})