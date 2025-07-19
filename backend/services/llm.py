"""
Google Gemini LLM Service
Handles text generation using Google's Gemini models (Flash/Pro)
Ultra-low cost architecture with Google-only services
"""

import google.generativeai as genai
from typing import List, Dict, Any
import logging
import json
import re

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating answers using Google Gemini models"""
    
    def __init__(self, gemini_api_key: str):
        """Initialize the LLM service with Gemini API key"""
        # Initialize Gemini
        self.gemini_available = False
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                
                # Test with a simple model list to verify API works
                models = genai.list_models()
                available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
                logger.info(f"Available Gemini models: {available_models[:3]}...")  # Log first few
                
                self.gemini_available = True
                logger.info("Gemini API initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
        else:
            raise ValueError("GEMINI_API_KEY is required for Google-only architecture")
        
        # Google Gemini model pricing (per 1K tokens) - Ultra-low cost!
        self.model_pricing = {
            "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},   # Ultra fast & cheap
            "gemini-1.5-pro": {"input": 0.00125, "output": 0.005}       # Balanced performance
        }
    
    def generate_answer(
        self, 
        question: str, 
        context_documents: List[Dict], 
        card_name: str = None, 
        model_choice: str = "gemini-1.5-pro",  # Changed from Flash due to performance issues
        max_tokens: int = 800,  # Increased from 500 to allow comprehensive answers
        temperature: float = 0.1,
        use_calculator: bool = True
    ) -> tuple[str, Dict[str, Any]]:
        """
        Generate an answer using selected LLM
        
        Args:
            question: User's question
            context_documents: Relevant documents for context
            card_name: Specific card to focus on (optional)
            model_choice: Gemini model to use (gemini-1.5-flash, gemini-1.5-pro)
            max_tokens: Maximum tokens in response
            temperature: Creativity parameter (0.0 to 1.0)
            
        Returns:
            tuple: (answer_text, usage_info)
        """
        if not context_documents:
            return self._no_context_response(), {"tokens": 0, "cost": 0, "model": "none"}
        
        # Build context from documents
        context = self._build_context(context_documents)
        
        # Check if we should use calculator for calculation queries
        if use_calculator and self._is_calculation_query(question):
            calc_result = self._try_calculator(question, context)
            if calc_result:
                return calc_result, {"model": "calculator", "tokens": 0, "cost": 0}
        
        # Adjust max_tokens based on query type
        if any(keyword in question.lower() for keyword in ['transfer partners', 'partners', 'airlines', 'hotels', 'list', 'all', 'complete']):
            max_tokens = min(max_tokens * 2, 1500)  # Double for comprehensive lists
        elif any(keyword in question.lower() for keyword in ['benefits', 'features', 'insurance', 'lounge', 'details']):
            max_tokens = min(max_tokens + 300, 1200)  # Increase for detailed info
        
        # Create prompts
        system_prompt = self._create_system_prompt(card_name)
        user_prompt = self._create_user_prompt(question, context)
        
        # Google Gemini only architecture
        if not model_choice.startswith("gemini"):
            raise ValueError(f"Only Gemini models are supported. Requested: {model_choice}")
            
        return self._generate_gemini_answer(system_prompt, user_prompt, model_choice, max_tokens, temperature)
    
    def _generate_gemini_answer(self, system_prompt: str, user_prompt: str, model: str, max_tokens: int, temperature: float):
        """Generate answer using Gemini models"""
        if not self.gemini_available:
            return "Gemini not available. Please check API key.", {"tokens": 0, "cost": 0, "model": model}
        
        pricing = self.model_pricing[model]
        
        try:
            # Combine system and user prompts for Gemini
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Map our model names to actual Gemini model names
            model_mapping = {
                "gemini-1.5-flash": "models/gemini-1.5-flash",
                "gemini-1.5-pro": "models/gemini-1.5-pro"
            }
            
            actual_model_name = model_mapping.get(model, model)
            
            gemini_model = genai.GenerativeModel(
                model_name=actual_model_name,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature
                )
            )
            
            import time
            start_time = time.time()
            
            response = gemini_model.generate_content(combined_prompt)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Estimate token usage (Gemini doesn't provide exact counts)
            input_tokens = len(combined_prompt.split()) * 1.3  # Rough estimation
            output_tokens = len(response.text.split()) * 1.3 if response.text else 0
            total_cost = (input_tokens * pricing["input"] / 1000) + (output_tokens * pricing["output"] / 1000)
            
            usage_info = {
                "model": model,
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "total_tokens": int(input_tokens + output_tokens),
                "cost": total_cost,
                "pricing": pricing,
                "note": "Token counts estimated for Gemini"
            }
            
            answer = response.text or "Sorry, I couldn't generate a response."
            logger.info(f"Generated answer using {model}: ~{int(input_tokens)} input + ~{int(output_tokens)} output tokens")
            
            return answer, usage_info
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating answer with {model}: {error_msg}")
            
            # If it's a model not found error, try to list available models
            if "not found" in error_msg.lower():
                try:
                    models = genai.list_models()
                    available = [m.name for m in models if 'generateContent' in m.supported_generation_methods][:5]
                    error_msg += f"\n\nAvailable models: {', '.join(available)}"
                except:
                    pass
            
            return f"Error generating answer: {error_msg}", {"tokens": 0, "cost": 0, "model": model}
    
    def _build_context(self, documents: List[Dict]) -> str:
        """
        (Improved) Build context string from relevant documents without
        aggressive truncation.
        """
        context_parts = []
        
        # Limit total context to avoid excessive length, but be generous
        max_context_chars = 15000  # ~3.7k tokens, well within limits
        current_chars = 0
        
        for doc in documents:
            content = doc.get('content', '')
            
            # Stop adding documents if we exceed the character limit
            if current_chars + len(content) > max_context_chars:
                break
                
            # Use the full, untruncated content from the document
            context_part = f"Source Document for '{doc['cardName']}' (section: {doc['section']}):\n{content}"
            context_parts.append(context_part)
            current_chars += len(content)
        
        final_context = "\n\n---\n\n".join(context_parts)
        return final_context
    
    def _create_system_prompt(self, card_name: str = None) -> str:
        """Create a concise system prompt for the LLM"""
        prompt = """You are a helpful credit card expert. Answer questions clearly and accurately based on the provided context.

CRITICAL: If the context contains information relevant to the question, use it to provide a comprehensive answer. NEVER claim information is missing if it exists in the context.

CRITICAL FOR COMPARISONS: When comparing cards, look for ALL card names in the context. If documents exist for both cards (even with different section names), use information from BOTH cards. Look carefully at the "Source Document" headers to identify which card each section belongs to.

For earning rate comparisons:
- Look for "rate_general", "earning_rate", "travel", "hotel", "flight", "capping_per_statement_cycle", "reward_capping" sections in the context
- Base earning rates are expressed as "X points per ₹Y spent" OR "X EDGE Miles/₹Y" OR "X miles per ₹Y"
- REWARD TYPES BY CARD:
  * Axis Atlas: Uses "EDGE Miles" (e.g., "2 EDGE Miles/₹100", "5 EDGE Miles/₹100")
  * ICICI EPM: Uses "Reward Points" (e.g., "6 points per ₹200") 
  * HSBC Premier: Uses "Reward points" (e.g., "3 points per ₹100")
- Travel categories may include hotels, flights, and general travel
- For insurance spending: Check "capping_per_statement_cycle" or "reward_capping" for limits, NOT "insurance" benefits section
- Check for both general rates and category-specific rates
- If a card mentions travel/hotel categories but shows same rate as general, that's the actual rate
- CRITICAL: Insurance spending ≠ Insurance benefits/coverage. Look for earning caps, not coverage amounts.

For calculations:
- Use exact rates from context: "X points per ₹Y" → (spend ÷ Y) × X
- Check for exclusions and caps
- Apply milestones if spend meets threshold
- Show calculations step-by-step

For informational queries:
- Extract all relevant details from context
- Include specific numbers, dates, and conditions
- Don't truncate important information
- If you see earning information for one card but not another, carefully re-read the context as the information may be there but in a different format

CARD NAME RECOGNITION:
- "Axis Bank Atlas Credit Card" = "Axis Atlas" (uses EDGE Miles as reward currency)
- "ICICI Bank Emeralde Private Metal Credit Card" = "ICICI EPM" (uses Reward Points)
- "HSBC Premier Credit Card" = "HSBC Premier" (uses Reward points)
- When users ask about "Axis Atlas", look for documents labeled "Axis Bank Atlas Credit Card" and search for "EDGE Miles" rates
- When users ask about "ICICI EPM", look for documents labeled "ICICI Bank Emeralde Private Metal Credit Card" 
- NEVER claim a card's information is missing if there are documents for that card in the context
- PAY SPECIAL ATTENTION: Axis Atlas reward information uses "EDGE Miles" terminology, not "points"""
        
        if card_name:
            prompt += f"\nFocus on information about the {card_name} card."
        
        return prompt
    
    def _create_user_prompt(self, question: str, context: str) -> str:
        """Create a concise user prompt with question and context"""
        return f"""Answer this question: "{question}"

Context:
{context}

For calculations:
1. Check exclusions first (excluded = 0 rewards)
2. **CHECK CAPS**: For ICICI EPM, check EARNING CAPS (max points per cycle)
3. **CHECK SPEND CAPS**: For Axis Atlas, split spending above caps to different rates
4. **CHECK SURCHARGES**: Calculate 1% on amount above threshold if mentioned
5. Use ONE rate per spend: base OR category (never add both)
6. Apply milestones only if total spend ≥ threshold
7. Show step-by-step: (amount ÷ Y) × X = result, then apply caps, then calculate surcharges

CRITICAL: For Axis Atlas hotels/flights, 5x rate applies to spend UP TO ₹2L/month. Only split calculation if spend EXCEEDS ₹2L. If spend ≤ ₹2L, use 5x rate for entire amount.

Be precise with math. Double-check arithmetic."""
    
    def _no_context_response(self) -> str:
        """Response when no relevant context is found"""
        return "I couldn't find relevant information to answer your question. Please try rephrasing your query or asking about specific credit card features."
    
    def _is_calculation_query(self, question: str) -> bool:
        """Check if this is a calculation query that should use the calculator"""
        calculation_indicators = [
            r'spend.*₹\d+',
            r'₹\d+.*spend',
            r'how many.*points',
            r'how many.*miles',
            r'points.*earn',
            r'miles.*earn',
            r'earn.*points',
            r'earn.*miles',
            r'\d+.*lakh',
            r'₹\d+.*L',
            r'₹\d+K',
            r'milestone',
            r'surcharge'
        ]
        
        question_lower = question.lower()
        return any(re.search(pattern, question_lower) for pattern in calculation_indicators)
    
    def _try_calculator(self, question: str, context: str) -> str:
        """Try to use the calculator for precise calculations"""
        try:
            from src.calculator import calculate_rewards, parse_spend_string
            
            # Use the robust spend parser from calculator.py
            spend = parse_spend_string(question)
            
            if spend == 0:
                return None  # Exit if no valid spend amount is found
            
            # Extract card name
            card = None
            if 'atlas' in question.lower():
                card = 'Axis Atlas'
            elif 'icici' in question.lower() or 'epm' in question.lower():
                card = 'ICICI EPM'
            elif 'hsbc' in question.lower() or 'premier' in question.lower():
                card = 'HSBC Premier'
            
            if not card:
                return None
            
            # Extract category
            category = 'general'
            if any(word in question.lower() for word in ['hotel', 'hotels']):
                category = 'hotel'
            elif any(word in question.lower() for word in ['flight', 'flights', 'airline']):
                category = 'flight'
            elif any(word in question.lower() for word in ['utility', 'utilities']):
                category = 'utility'
            elif any(word in question.lower() for word in ['education', 'school', 'college']):
                category = 'education'
            elif any(word in question.lower() for word in ['insurance']):
                category = 'insurance'
            elif any(word in question.lower() for word in ['grocery', 'groceries']):
                category = 'grocery'
            
            # Determine period
            period = 'annual'
            if any(word in question.lower() for word in ['month', 'monthly']):
                period = 'monthly'
            elif any(word in question.lower() for word in ['year', 'yearly', 'annual']):
                period = 'annual'
            
            # Use calculator
            result = calculate_rewards(spend, card, category, period)
            return f"🧮 **Precise Calculation Using Advanced Calculator**\n\n{result}"
            
        except Exception as e:
            logger.error(f"Calculator failed: {e}")
            return None
    
    def get_model_info(self, model: str = "gemini-1.5-flash") -> Dict[str, Any]:
        """Get information about a specific Gemini model"""
        if model not in self.model_pricing:
            raise ValueError(f"Unknown model: {model}")
        
        # Gemini model specifications
        model_specs = {
            "gemini-1.5-flash": {"context_window": 1048576, "max_output_tokens": 8192},  # 1M context
            "gemini-1.5-pro": {"context_window": 2097152, "max_output_tokens": 8192}    # 2M context
        }
        
        specs = model_specs.get(model, {"context_window": 1048576, "max_output_tokens": 8192})
        
        return {
            "model": model,
            "pricing": self.model_pricing[model],
            "context_window": specs["context_window"],
            "max_output_tokens": specs["max_output_tokens"]
        }