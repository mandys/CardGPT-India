"""
Query Enhancement Service
Preprocesses user queries to detect categories and ensure correct earning rates are applied
"""

import re
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class QueryEnhancer:
    """Enhances user queries to improve LLM accuracy for credit card calculations"""
    
    def __init__(self):
        # Card name detection patterns
        self.card_patterns = {
            'Axis Atlas': ['axis atlas', 'atlas', 'axis', 'axis bank atlas'],
            'ICICI EPM': ['icici epm', 'epm', 'emeralde private', 'icici bank emeralde', 'icici', 'emeralde'],
            'HSBC Premier': ['hsbc premier', 'premier', 'hsbc'],
            'HDFC Infinia': ['hdfc infinia', 'infinia', 'hdfc bank infinia', 'hdfc']
        }
        
        # Mapping from user-friendly names to actual card names in data
        self.card_name_mapping = {
            'ICICI EPM': 'ICICI Bank Emeralde Private Metal Credit Card',
            'Axis Atlas': 'Axis Bank Atlas Credit Card',
            'HSBC Premier': 'HSBC Premier Credit Card',
            'HDFC Infinia': 'HDFC Infinia Credit Card'
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
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)', # Corrected: Added missing newline character here
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|l\b)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:crore|cr\b)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:thousand|k\b)',
        ]
        
        # Travel query patterns for enhanced handling
        self.travel_query_patterns = [
            'travel', 'trip', 'vacation', 'holiday', 'journey',
            'flight', 'hotel', 'booking', 'miles', 'points for travel',
            'best card for travel', 'travel benefits', 'travel rewards',
            'domestic travel', 'international travel', 'business travel',
            'frequent travel', 'upcoming travel', 'lot of travel'
        ]
        
        # Generic recommendation patterns
        self.generic_recommendation_patterns = [
            'which card should i', 'best card for', 'recommend',
            'suggest', 'better card', 'good card', 'right card',
            'should i get', 'which one', 'what card'
        ]
        
        # Generic comparison patterns (questions asking about ALL cards)
        self.generic_comparison_patterns = [
            'which card gives', 'which card earns', 'which card offers',
            'which card has', 'which card provides', 'which cards give',
            'which cards earn', 'which cards offer', 'which cards have',
            'what card gives', 'what card earns', 'what card offers'
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
    
    def is_travel_query(self, query: str) -> bool:
        """Detect if this is a travel-related query"""
        query_lower = query.lower()
        return any(pattern in query_lower for pattern in self.travel_query_patterns)
    
    def is_generic_recommendation_query(self, query: str) -> bool:
        """Detect if this is a generic recommendation query that might benefit from follow-up questions"""
        query_lower = query.lower()
        
        # Check for generic recommendation patterns
        has_generic_pattern = any(pattern in query_lower for pattern in self.generic_recommendation_patterns)
        
        # Check if no specific card is mentioned
        no_specific_card = self.detect_card_name(query) is None
        
        # Check if no specific category is mentioned
        no_specific_category = self.detect_category(query) is None
        
        return has_generic_pattern and no_specific_card and (no_specific_category or self.is_travel_query(query))
    
    def is_generic_comparison_query(self, query: str) -> bool:
        """Detect if this is a generic comparison query asking about ALL cards (like 'which card gives points for education')"""
        query_lower = query.lower()
        
        # Check for generic comparison patterns
        has_comparison_pattern = any(pattern in query_lower for pattern in self.generic_comparison_patterns)
        
        # Check if no specific card is mentioned
        no_specific_card = self.detect_card_name(query) is None
        
        return has_comparison_pattern and no_specific_card
    
    def detect_direct_comparison(self, query: str) -> Optional[tuple]:
        """Detect direct card-to-card comparison queries"""
        import re
        
        logger.info(f"=== DIRECT COMPARISON DEBUG ===")
        logger.info(f"Original query: '{query}'")
        
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
            logger.info(f"Pattern '{pattern}' -> Match: {match.groups() if match else 'No match'}")
            if match:
                logger.info(f"SUCCESS: Direct comparison detected: {match.groups()}")
                logger.info(f"=== END DIRECT COMPARISON DEBUG ===")
                return match.groups()
        
        logger.info(f"No direct comparison patterns matched")
        logger.info(f"=== END DIRECT COMPARISON DEBUG ===")
        return None

    def enhance_query(self, query: str, user_preferences: Dict = None) -> Tuple[str, Dict[str, any]]:
        """
        Enhance query with category and card detection, plus other metadata
        
        Returns:
            Tuple of (enhanced_query, metadata)
        """
        card_detected = self.detect_card_name(query)
        category = self.detect_category(query)
        spend_amount = self.detect_spend_amount(query)
        is_travel_query = self.is_travel_query(query)
        is_generic_recommendation = self.is_generic_recommendation_query(query)
        is_generic_comparison = self.is_generic_comparison_query(query)
        direct_comparison = self.detect_direct_comparison(query)
        
        metadata = {
            'card_detected': card_detected,
            'category_detected': category,
            'spend_amount': spend_amount,
            'is_calculation_query': bool(spend_amount),
            'requires_category_rate': category in ['hotel', 'flight', 'travel'],
            'is_travel_query': is_travel_query,
            'is_generic_recommendation': is_generic_recommendation,
            'is_generic_comparison': is_generic_comparison,
            'direct_comparison': direct_comparison,
            'suggest_followup': is_generic_recommendation and not spend_amount
        }
        
        logger.info(f"Query metadata: {metadata}")
        logger.info(f"User preferences received: {user_preferences}")
        
        # Enhance the query with explicit category information
        enhanced_query = query
        
        # Add preference-aware enhancement FIRST (highest priority)
        if user_preferences:
            preference_context = self._build_preference_context(user_preferences, query, is_travel_query, is_generic_recommendation)
            if preference_context:
                enhanced_query += f"\n\n{preference_context}"
                logger.info(f"Added preference context: {preference_context}")
        
        # Handle direct card-to-card comparisons first (highest priority)
        if direct_comparison:
            card1, card2 = direct_comparison
            logger.info(f"=== QUERY ENHANCEMENT DEBUG ===")
            logger.info(f"Direct comparison detected: {direct_comparison}")
            logger.info(f"Original enhanced_query: '{enhanced_query}'")
            
            # With document-level aliases, we can rely on natural search matching
            # The search engine will match aliases automatically, so we just need to
            # ensure both card terms are in the query for balanced retrieval
            enhanced_query += f" {card1} {card2}"
            logger.info(f"Enhanced query after adding card names: '{enhanced_query}'")
            logger.info(f"=== END QUERY ENHANCEMENT DEBUG ===")
        
        # Detect spend distribution queries
        is_distribution_query = any(word in query.lower() for word in ['split', 'distribution', 'monthly', 'breakdown', 'categories'])
        
        # Handle generic comparison queries first (higher priority than travel queries)
        if is_generic_comparison and not card_detected:
            if "travel insurance" in query.lower():
                if any(word in query.lower() for word in ["spend", "rewards", "points"]):
                    enhanced_query = f"Travel insurance spending rewards for {', '.join(self.card_patterns.keys())}"
                else:
                    enhanced_query = f"Travel insurance coverage benefits for {', '.join(self.card_patterns.keys())} including lost baggage, trip cancellation, and medical coverage"
            elif category == 'education':
                enhanced_query = f"Education spending rewards and fees for {', '.join(self.card_patterns.keys())}"
            else:
                enhanced_query += f" comparison all cards Atlas EPM Premier Infinia rewards rates"
        # Handle travel queries specially (lower priority than generic comparisons)
        elif is_travel_query and not card_detected:
            # Add specific card names and travel terms to ensure balanced retrieval
            enhanced_query += f" travel rewards miles points lounge access Atlas EPM Premier Infinia"
        # elif is_generic_recommendation and not card_detected:
        #     enhanced_query += f"\n\nIMPORTANT: This is a generic recommendation query. Analyze ALL available cards systematically and provide balanced comparison. Do not limit analysis to first few cards in context. Include key differentiators for each card."
        elif category and spend_amount:
            # Make category explicit in the query with simple guidance
            if category in ['hotel', 'flight']:
                enhanced_query += f" {category} spending rates caps milestones"
            elif category == 'utility':
                enhanced_query += f" utility spending rates surcharge"
            elif category == 'insurance':
                enhanced_query += f" insurance spending rewards rates caps exclusions"
            elif category in ['fuel', 'rent', 'government']:
                enhanced_query += f" {category} spending exclusions rates"
            elif category == 'education':
                enhanced_query += f" education spending rates surcharge"
        elif category in ['hotel', 'flight'] and not spend_amount:
            # Handle category queries without spend amounts (like comparisons)
            enhanced_query += f" {category} rewards comparison rates caps"
        elif category == 'education' and not spend_amount:
            # Handle education category comparisons - now using RAG retrieval instead of hardcoded responses
            enhanced_query += f" education spending rewards comparison rates caps surcharge"
        elif category == 'milestone':
            # Handle milestone queries separately (they often don't have spend amounts)
            enhanced_query += f" milestone benefits spending thresholds annual rewards"
        elif category == 'utility' and any(keyword in query.lower() for keyword in ['surcharge', 'fee', 'charge', 'cost']):
            # Handle utility fee/surcharge queries separately
            enhanced_query += f" utility fees surcharges calculation threshold"
        elif is_distribution_query:
            enhanced_query += f" spend distribution categories rates calculation separate"
        elif spend_amount and not category:
            enhanced_query += f" base rate calculation milestones spending threshold"
        
        logger.info(f"=== FINAL ENHANCEMENT RESULT ===")
        logger.info(f"Final enhanced query: '{enhanced_query}'")
        logger.info(f"Final metadata: {metadata}")
        logger.info(f"=== END FINAL ENHANCEMENT RESULT ===")
        
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
            'insurance': 'HSBC Premier and HDFC Infinia earn rewards on insurance spending, ICICI EPM has caps, Axis Atlas excludes insurance completely.',
            'education': 'HSBC Premier earns 3 points per ₹100, HDFC Infinia excludes education, ICICI EPM earns 6 points per ₹200 with caps, Axis Atlas earns 2 EDGE Miles per ₹100 with 1% surcharge via third-party apps.',
            'grocery': 'May have earning caps or accelerated rates depending on the card.',
            'dining': 'Often treated as general spending, but some cards may have accelerated rates.'
        }
        
        return guidance.get(category, 'Check the card-specific earning rates and exclusions for this category.')
    
    def needs_card_selector(self, query: str) -> bool:
        """
        Card selector permanently disabled for better user experience.
        Always returns False to allow open-ended searches.
        """
        return False
    
    def is_generic_comparison_query(self, query: str) -> bool:
        """
        DEPRECATED: Use needs_card_selector() instead.
        Kept for backward compatibility.
        """
        return self.needs_card_selector(query)
    
    def get_available_cards(self) -> list[str]:
        """Get list of available cards from our data directory"""
        return list(self.card_patterns.keys())
    
    def get_followup_questions(self, query: str) -> list[str]:
        """Generate contextual follow-up questions for generic queries"""
        followup_questions = []
        
        if self.is_travel_query(query):
            followup_questions = [
                "What type of travel do you do most? (Domestic flights, International flights, Hotels)",
                "What's your approximate monthly travel spending?",
                "Do you prefer earning miles/points or cashback for travel?",
                "Are lounge access and travel insurance important to you?"
            ]
        elif self.is_generic_recommendation_query(query):
            followup_questions = [
                "What's your primary spending category? (Travel, Dining, Shopping, General)",
                "What's your approximate monthly credit card spending?",
                "Do you prefer earning miles, points, or cashback?",
                "Are you looking for specific benefits like lounge access or insurance?"
            ]
        
        return followup_questions
    
    def _build_preference_context(self, user_preferences: Dict, query: str, is_travel_query: bool, is_generic_recommendation: bool) -> str:
        """Build intelligent and concise preference context for query enhancement."""
        if not user_preferences:
            return ""

        context_parts = []

        # Travel preferences
        if is_travel_query:
            if getattr(user_preferences, 'travel_type', None) == 'domestic':
                context_parts.append("travels domestically")
            elif getattr(user_preferences, 'travel_type', None) == 'international':
                context_parts.append("travels internationally")
            
            if getattr(user_preferences, 'lounge_access', None) == 'family':
                context_parts.append("travels with family")

        # Fee willingness
        if is_generic_recommendation:
            fee_willingness = getattr(user_preferences, 'fee_willingness', None)
            if fee_willingness == '5000-10000' or fee_willingness == '10000+':
                context_parts.append("can afford luxury cards")

        # Spending categories
        spend_categories = getattr(user_preferences, 'spend_categories', None)
        if spend_categories:
            context_parts.append(f"spends on {', '.join(spend_categories)}")

        if not context_parts:
            return ""

        return f"USER PREFERENCE CONTEXT: Prioritize recommendations for a user who {', '.join(context_parts)}."