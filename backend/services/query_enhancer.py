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
                'income tax', 'gst', 'fine', 'government spend', 
                'government payment', 'government bills', 'tax payment',
                'municipal payment', 'government fees'
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

    def enhance_search_query(self, query: str) -> Tuple[str, Dict[str, any]]:
        """
        Enhance query for search retrieval only - focuses on search intent without user preferences
        
        Returns:
            Tuple of (enhanced_search_query, metadata)
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
        
        logger.info(f"Search query metadata: {metadata}")
        
        # Enhance the query with explicit category information for search
        enhanced_query = query
        
        # Handle direct card-to-card comparisons first (highest priority)
        if direct_comparison:
            card1, card2 = direct_comparison
            logger.info(f"=== SEARCH QUERY ENHANCEMENT DEBUG ===")
            logger.info(f"Direct comparison detected: {direct_comparison}")
            logger.info(f"Original enhanced_query: '{enhanced_query}'")
            
            # With document-level aliases, we can rely on natural search matching
            # The search engine will match aliases automatically, so we just need to
            # ensure both card terms are in the query for balanced retrieval
            enhanced_query += f" {card1} {card2}"
            logger.info(f"Enhanced search query after adding card names: '{enhanced_query}'")
            logger.info(f"=== END SEARCH QUERY ENHANCEMENT DEBUG ===")
        
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
        elif category and spend_amount:
            # Make category explicit in the query with simple guidance
            if category in ['hotel', 'flight']:
                enhanced_query += f" {category} spending rates caps milestones"
            elif category == 'utility':
                enhanced_query += f" utility spending rates surcharge"
            elif category == 'insurance':
                enhanced_query += f" insurance spending rewards rates caps exclusions policy premium benefits coverage"
            elif category == 'fuel':
                enhanced_query += f" fuel spending exclusions rates surcharge"
            elif category == 'rent':
                enhanced_query += f" rent rental spending exclusions rates"
            # elif category == 'government':
            #     enhanced_query += f" government tax municipal spending exclusions rates payment bills fees"
            elif category == 'education':
                enhanced_query += f" education spending rates surcharge"
        elif category in ['hotel', 'flight'] and not spend_amount:
            # Handle category queries without spend amounts (like comparisons)
            enhanced_query += f" {category} rewards comparison rates caps"
        elif category == 'education' and not spend_amount:
            # Handle education category comparisons - now using RAG retrieval instead of hardcoded responses
            enhanced_query += f" education spending rewards comparison rates caps surcharge"
        elif category == 'insurance' and not spend_amount:
            # Handle insurance category comparisons - use natural language terms
            enhanced_query += f" insurance spending rewards comparison rates caps exclusions policy premium benefits coverage"
        # elif category == 'government' and not spend_amount:
        #     # Handle government category comparisons - comprehensive government payment terms
        #     enhanced_query += f" government tax municipal spending exclusions rates payment bills fees comparison rewards"
        elif category in ['fuel', 'rent'] and not spend_amount:
            # Handle fuel and rent category comparisons
            enhanced_query += f" {category} spending exclusions rates comparison rewards"
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
        
        logger.info(f"=== FINAL SEARCH ENHANCEMENT RESULT ===")
        logger.info(f"Final enhanced search query: '{enhanced_query}'")
        logger.info(f"Final metadata: {metadata}")
        logger.info(f"=== END FINAL SEARCH ENHANCEMENT RESULT ===")
        
        return enhanced_query, metadata
    
    def build_preference_context(self, user_preferences: Dict = None) -> str:
        """
        Build user preference context for LLM personalization
        
        Returns:
            Formatted preference context string for LLM
        """
        if not user_preferences:
            logger.info("⚠️ [PREFERENCE_CONTEXT] No user preferences provided")
            return ""
            
        logger.info(f"🎯 [PREFERENCE_CONTEXT] Building context from preferences: {user_preferences}")
        context_parts = []

        # Travel preferences
        if user_preferences.travel_type:
            if user_preferences.travel_type == 'domestic':
                context_parts.append("travels domestically")
            elif user_preferences.travel_type == 'international':
                context_parts.append("travels internationally")
            elif user_preferences.travel_type == 'both':
                context_parts.append("travels both domestically and internationally")
            
        if user_preferences.lounge_access:
            if user_preferences.lounge_access == 'family':
                context_parts.append("travels with family")
            elif user_preferences.lounge_access == 'solo':
                context_parts.append("travels solo")
            elif user_preferences.lounge_access == 'with_guests':
                context_parts.append("travels with guests")

        # Fee willingness
        if user_preferences.fee_willingness:
            if user_preferences.fee_willingness in ['5000-10000', '10000+']:
                context_parts.append("can afford luxury cards")

        # Spending categories
        if user_preferences.spend_categories:
            context_parts.append(f"spends on {', '.join(user_preferences.spend_categories)}")

        # Current cards (when enabled)
        # if user_preferences.current_cards:
        #     context_parts.append(f"currently uses {', '.join(user_preferences.current_cards)}")

        # Preferred banks (when enabled)
        # if user_preferences.preferred_banks:
        #     context_parts.append(f"prefers banks like {', '.join(user_preferences.preferred_banks)}")

        if context_parts:
            preference_context = f"USER PREFERENCE CONTEXT: While answering the question, make sure you prioritize user preferences - like they {', '.join(context_parts)}."
            logger.info(f"✅ [PREFERENCE_CONTEXT] Built context: {preference_context}")
            return preference_context
        else:
            logger.info("⚠️ [PREFERENCE_CONTEXT] No valid preference context built")
            return ""

    def enhance_query(self, query: str, user_preferences: Dict = None) -> Tuple[str, Dict[str, any]]:
        """
        Legacy method for backward compatibility - combines search and preference enhancement
        
        Returns:
            Tuple of (enhanced_query_with_preferences, metadata)
        """
        logger.info(f"🔄 [LEGACY_ENHANCE] Using legacy enhance_query method")
        
        # Get search-focused enhancement
        enhanced_search_query, metadata = self.enhance_search_query(query)
        
        # Add preference context if provided
        preference_context = self.build_preference_context(user_preferences)
        
        if preference_context:
            enhanced_query = f"{enhanced_search_query}\n\n{preference_context}"
            logger.info(f"📝 [LEGACY_ENHANCE] Added preference context to search query")
        else:
            enhanced_query = enhanced_search_query
        
        logger.info(f"User preferences received: {user_preferences}")
        logger.info(f"Query metadata: {metadata}")
        
        return enhanced_query, metadata
    
    def get_category_guidance(self, category: str) -> str:
        """Get general guidance for specific spending categories"""
        # Load category summaries from centralized configuration
        guidance = {}
        
        # Load configured category summaries
        for category in ['insurance', 'education']:
            summary = self.card_config.get_category_summary(category)
            if summary:
                guidance[category] = summary
        
        # Add other generic guidance
        guidance.update({
            'hotel': 'Look for accelerated earning rates for hotel bookings. Check for monthly caps on accelerated rates.',
            'flight': 'Look for accelerated earning rates for flight bookings. Check for monthly caps on accelerated rates.',
            'fuel': 'Commonly excluded from earning rewards on most cards. Check exclusion lists.',
            'utility': 'May be excluded or have earning caps. Check for surcharge fees above spending thresholds.',
            'rent': 'Commonly excluded from earning rewards on most cards. Check exclusion lists.',
            'government': 'Commonly excluded from earning rewards on most cards. Check exclusion lists.',
            'grocery': 'May have earning caps or accelerated rates depending on the card.',
            'dining': 'Often treated as general spending, but some cards may have accelerated rates.'
        })
        
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
    
    # def get_available_cards(self) -> list[str]:
    #     """Get list of available cards from our data directory"""
    #     return list(self.card_patterns.keys())
    
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

        # Current cards
        current_cards = getattr(user_preferences, 'current_cards', None)
        if current_cards:
            context_parts.append(f"currently uses {', '.join(current_cards)}")

        # Preferred banks
        preferred_banks = getattr(user_preferences, 'preferred_banks', None)
        if preferred_banks:
            context_parts.append(f"prefers banks like {', '.join(preferred_banks)}")

        if not context_parts:
            return ""

        return f"USER PREFERENCE CONTEXT: While answering the question, make sure you prioritize user preferences - like they {', '.join(context_parts)}."