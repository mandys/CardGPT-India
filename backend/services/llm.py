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
            "gemini-2.5-flash-lite": {"input": 0.0001, "output": 0.0004},  # NEW: Lowest latency & cost
            "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},   # Ultra fast & cheap
            "gemini-1.5-pro": {"input": 0.00125, "output": 0.005}       # Balanced performance
        }
    
    def generate_answer(
        self, 
        question: str, 
        context_documents: List[Dict], 
        card_name: str = None, 
        model_choice: str = "gemini-1.5-pro",  # Changed from Flash due to performance issues
        max_tokens: int = 1200,  # Increased from 800 for Gemini 2.5 Flash-Lite detailed responses
        temperature: float = 0.1
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
        
        # Enhance prompts for calculation queries
        is_calculation = self._is_calculation_query(question)
        if is_calculation:
            max_tokens = min(max_tokens + 400, 1600)  # More tokens for detailed calculations
        
        # Adjust max_tokens based on query type
        if any(keyword in question.lower() for keyword in ['transfer partners', 'partners', 'airlines', 'hotels', 'list', 'all', 'complete']):
            max_tokens = min(max_tokens * 2, 2000)  # Double for comprehensive lists
        elif any(keyword in question.lower() for keyword in ['benefits', 'features', 'insurance', 'lounge', 'details']):
            max_tokens = min(max_tokens + 400, 1600)  # Increase for detailed info
        elif any(keyword in question.lower() for keyword in ['compare', 'comparison', 'split', 'spending', 'distribution']):
            max_tokens = min(max_tokens + 600, 1800)  # Extra tokens for complex comparisons
        
        # Create prompts with calculation enhancement
        system_prompt = self._create_system_prompt(card_name, is_calculation)
        user_prompt = self._create_user_prompt(question, context, is_calculation)
        
        # Google Gemini only architecture
        if not model_choice.startswith("gemini"):
            raise ValueError(f"Only Gemini models are supported. Requested: {model_choice}")
            
        return self._generate_gemini_answer(system_prompt, user_prompt, model_choice, max_tokens, temperature)
    
    def generate_answer_stream(
        self, 
        question: str, 
        context_documents: List[Dict], 
        card_name: str = None, 
        model_choice: str = "gemini-1.5-pro",
        max_tokens: int = 1200,
        temperature: float = 0.1
    ):
        """
        Generate a streaming answer using selected LLM
        
        Args:
            question: User's question
            context_documents: Relevant documents for context
            card_name: Specific card to focus on (optional)
            model_choice: Gemini model to use (gemini-1.5-flash, gemini-1.5-pro)
            max_tokens: Maximum tokens in response
            temperature: Creativity parameter (0.0 to 1.0)
            
        Yields:
            tuple: (chunk_text, is_final, usage_info)
        """
        if not context_documents:
            yield ("I couldn't find relevant information to answer your question. Please try rephrasing your query or asking about specific credit card features.", True, {"tokens": 0, "cost": 0, "model": "none"})
            return
        
        # Build context from documents
        context = self._build_context(context_documents)
        
        # Enhance prompts for calculation queries
        is_calculation = self._is_calculation_query(question)
        if is_calculation:
            max_tokens = min(max_tokens + 400, 1600)  # More tokens for detailed calculations
        
        # Adjust max_tokens based on query type
        if any(keyword in question.lower() for keyword in ['transfer partners', 'partners', 'airlines', 'hotels', 'list', 'all', 'complete']):
            max_tokens = min(max_tokens * 2, 2000)  # Double for comprehensive lists
        elif any(keyword in question.lower() for keyword in ['benefits', 'features', 'insurance', 'lounge', 'details']):
            max_tokens = min(max_tokens + 400, 1600)  # Increase for detailed info
        elif any(keyword in question.lower() for keyword in ['compare', 'comparison', 'split', 'spending', 'distribution']):
            max_tokens = min(max_tokens + 600, 1800)  # Extra tokens for complex comparisons
        
        # Create prompts with calculation enhancement
        system_prompt = self._create_system_prompt(card_name, is_calculation)
        user_prompt = self._create_user_prompt(question, context, is_calculation)
        
        # Google Gemini only architecture
        if not model_choice.startswith("gemini"):
            yield (f"Error: Only Gemini models are supported. Requested: {model_choice}", True, {"tokens": 0, "cost": 0, "model": model_choice})
            return
            
        yield from self._generate_gemini_answer_stream(system_prompt, user_prompt, model_choice, max_tokens, temperature)
    
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
                "gemini-2.5-flash-lite": "models/gemini-2.5-flash-lite",  # New 2.5 Flash-Lite (CORRECT)
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
    
    def _generate_gemini_answer_stream(self, system_prompt: str, user_prompt: str, model: str, max_tokens: int, temperature: float):
        """Generate streaming answer using Gemini models"""
        if not self.gemini_available:
            yield ("Gemini not available. Please check API key.", True, {"tokens": 0, "cost": 0, "model": model})
            return
        
        pricing = self.model_pricing[model]
        
        try:
            # Combine system and user prompts for Gemini
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Map our model names to actual Gemini model names
            model_mapping = {
                "gemini-2.5-flash-lite": "models/gemini-2.5-flash-lite",  # New 2.5 Flash-Lite (CORRECT)
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
            
            # Generate streaming response
            response = gemini_model.generate_content(combined_prompt, stream=True)
            
            full_text = ""
            chunk_count = 0
            
            for chunk in response:
                if chunk.text:
                    chunk_count += 1
                    full_text += chunk.text
                    # Yield each chunk as it arrives
                    yield (chunk.text, False, None)  # False = not final
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Calculate final usage information
            input_tokens = len(combined_prompt.split()) * 1.3  # Rough estimation
            output_tokens = len(full_text.split()) * 1.3 if full_text else 0
            total_cost = (input_tokens * pricing["input"] / 1000) + (output_tokens * pricing["output"] / 1000)
            
            usage_info = {
                "model": model,
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "total_tokens": int(input_tokens + output_tokens),
                "cost": total_cost,
                "pricing": pricing,
                "response_time": response_time,
                "note": "Token counts estimated for Gemini"
            }
            
            logger.info(f"Generated streaming answer using {model}: ~{int(input_tokens)} input + ~{int(output_tokens)} output tokens, {chunk_count} chunks")
            
            # Yield final usage information
            yield ("", True, usage_info)  # True = final
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating streaming answer with {model}: {error_msg}")
            
            # If it's a model not found error, try to list available models
            if "not found" in error_msg.lower():
                try:
                    models = genai.list_models()
                    available = [m.name for m in models if 'generateContent' in m.supported_generation_methods][:5]
                    error_msg += f"\n\nAvailable models: {', '.join(available)}"
                except:
                    pass
            
            yield (f"Error generating answer: {error_msg}", True, {"tokens": 0, "cost": 0, "model": model})
    
    def _build_context(self, documents: List[Dict]) -> str:
        """
        (Improved) Build context string from relevant documents with
        balanced representation for comparison queries.
        """
        context_parts = []
        
        # For comparison queries, ensure balanced representation
        card_names = set(doc.get('cardName', '') for doc in documents)
        is_comparison = len(card_names) > 1
        
        if is_comparison:
            # Group documents by card name for balanced representation
            card_docs = {}
            for doc in documents:
                card_name = doc.get('cardName', '')
                if card_name not in card_docs:
                    card_docs[card_name] = []
                card_docs[card_name].append(doc)
            
            # Limit per card to ensure all cards are represented
            max_context_chars = 15000
            chars_per_card = max_context_chars // len(card_names)
            
            for card_name, docs in card_docs.items():
                current_card_chars = 0
                for doc in docs:
                    content = doc.get('content', '')
                    if current_card_chars + len(content) > chars_per_card:
                        # Truncate this document to fit within the card's allocation
                        remaining_chars = chars_per_card - current_card_chars
                        if remaining_chars > 500:  # Only include if we have reasonable space
                            content = content[:remaining_chars] + "..."
                        else:
                            break
                    
                    context_part = f"Source Document for '{doc['cardName']}' (section: {doc['section']}):\n{content}"
                    context_parts.append(context_part)
                    current_card_chars += len(content)
        else:
            # Single card or general query - use original logic
            max_context_chars = 15000
            current_chars = 0
            
            for doc in documents:
                content = doc.get('content', '')
                
                if current_chars + len(content) > max_context_chars:
                    break
                    
                context_part = f"Source Document for '{doc['cardName']}' (section: {doc['section']}):\n{content}"
                context_parts.append(context_part)
                current_chars += len(content)
        
        final_context = "\n\n---\n\n".join(context_parts)
        return final_context
    
    def _create_system_prompt(self, card_name: str = None, is_calculation: bool = False) -> str:
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
- CRITICAL CATEGORY MAPPINGS:
  * Flight/airline spending = "Direct Airlines", "Airlines", "Air Travel", "Flight" categories
  * Hotel spending = "Direct Hotels", "Hotels", "Hotel Booking" categories  
  * Travel = encompasses flights, hotels, and general travel bookings
- When user asks about "flight spend" or "airline spend", look for travel earning rates that include "Direct Airlines"
- For insurance spending: Check "capping_per_statement_cycle", "reward_capping", OR "others" section for limits, NOT "insurance" benefits section
- CRITICAL INSURANCE LOGIC: If you see insurance caps (like "5,000 RP/day"), this means the card DOES earn rewards at the general rate UP TO that cap
- Check for both general rates and category-specific rates
- If a card mentions travel/hotel categories but shows same rate as general, that's the actual rate
- CRITICAL: Insurance spending ≠ Insurance benefits/coverage. Look for earning caps, not coverage amounts.

For calculations:
- Apply earning rates: "X points per ₹Y" → (spend ÷ Y) × X
- Check caps and exclusions
- **CRITICAL**: Look for spending thresholds (₹4L, ₹8L, etc.) in context - apply ALL benefits where user spend ≥ threshold
- Show step-by-step math with milestone bonuses

For informational queries:
- Extract all relevant details from context
- Include specific numbers, dates, and conditions
- Don't truncate important information
- If you see earning information for one card but not another, carefully re-read the context as the information may be there but in a different format

CARD NAME RECOGNITION:
- "Axis Bank Atlas Credit Card" = "Axis Atlas" (uses EDGE Miles as reward currency)
- "ICICI Bank Emeralde Private Metal Credit Card" = "ICICI EPM" (uses Reward Points)
- "HSBC Premier Credit Card" = "HSBC Premier" (uses Reward points)
- "HDFC Infinia Credit Card" = "HDFC Infinia" (uses Reward Points)
- When users ask about "Axis Atlas", look for documents labeled "Axis Bank Atlas Credit Card" and search for "EDGE Miles" rates
- When users ask about "ICICI EPM", look for documents labeled "ICICI Bank Emeralde Private Metal Credit Card" 
- NEVER claim a card's information is missing if there are documents for that card in the context
- PAY SPECIAL ATTENTION: Axis Atlas reward information uses "EDGE Miles" terminology, not "points"

INSURANCE SPENDING SPECIFIC GUIDANCE:
- HDFC Infinia: Earns general rate (5 points per ₹150) with daily cap of 5,000 RP
- HSBC Premier: Earns 3 points per ₹100 with monthly cap of ₹1,00,000 spending
- ICICI EPM: Earns general rate (6 points per ₹200) with monthly cap of 5,000 points
- Axis Atlas: EXCLUDES insurance completely (0 rewards)

CRITICAL MILESTONE IDENTIFICATION FOR AXIS ATLAS:
- **Annual Spend Milestones**: Look for "Milestones:" section with spend thresholds (₹3L=2500 miles, ₹7.5L=2500 miles, ₹15L=5000 miles)
- **Tier-based Milestone Miles**: These are different - found in tier structure sections (Silver/Gold/Platinum milestone miles)
- For calculations, use ANNUAL SPEND MILESTONES only: ₹3L→2500, ₹7.5L→2500, ₹15L→5000
- Do NOT confuse tier "Milestone Miles" with annual spending milestone bonuses

CALCULATION REQUIREMENTS:
- Show step-by-step math with milestone bonuses
- Double-check arithmetic
- Include currency in results"""
        
        if card_name:
            prompt += f"\nFocus on information about the {card_name} card."
        
        return prompt
    
    def _create_user_prompt(self, question: str, context: str, is_calculation: bool = False) -> str:
        """Create a user prompt with enhanced calculation guidance"""
        base_prompt = f"""Answer this question: "{question}"

Context:
{context}"""

        if is_calculation:
            base_prompt += """

🧮 **CALCULATION MODE:**

STEPS:
1. **Amount**: Convert to actual numbers (₹1L = ₹1,00,000, ₹3L = ₹3,00,000, ₹7.5L = ₹7,50,000, ₹15L = ₹15,00,000)
2. **Base Calculation**: Apply earning rate from context
3. **Apply Caps**: Check monthly/cycle limits if any
4. **Find Milestones**: CRITICAL - Step-by-step milestone validation
   - **SEARCH FOR**: Look for "Milestones:" in context (format: {'spend': '₹3L', 'miles': 2500})
   - **FOR AXIS ATLAS**: Annual milestones are ₹3L=2500, ₹7.5L=2500, ₹15L=5000 miles
   - Convert user spend to numbers: ₹3,00,000 = 300000
   - Convert each milestone to numbers: ₹3L = 300000, ₹7.5L = 750000, ₹15L = 1500000
   - Check EACH milestone individually:
     * IF 300000 ≥ 300000 (₹3L) → YES, apply ₹3L milestone bonus (+2500 miles)
     * IF 300000 ≥ 750000 (₹7.5L) → NO, do not apply ₹7.5L milestone bonus
     * IF 300000 ≥ 1500000 (₹15L) → NO, do not apply ₹15L milestone bonus
   - NEVER assume spend exceeds higher milestones without explicit number comparison
5. **Final Total**: Base + applicable milestones + any fees

KEY RULES:
- MATHEMATICAL VALIDATION: Before applying any milestone, verify the numbers
  * ₹3,00,000 spend can ONLY qualify for ₹3L milestone (300000 ≥ 300000 ✅)
  * ₹3,00,000 spend CANNOT qualify for ₹7.5L milestone (300000 < 750000 ❌)
- Compare actual numbers, not shorthand (₹3L = ₹3,00,000 = 300000)  
- If you apply ₹7.5L bonus to ₹3L spend, that's a mathematical ERROR
- Show math: (spend ÷ rate) × multiplier = result

FORMAT: "🧮 **Detailed Calculation:**" with clear steps

AXIS ATLAS MILESTONE EXAMPLE:
For ₹3L hotel spend:
1. Base calculation: ₹2L at 5 EDGE Miles/₹100 = 10,000 miles
2. Excess: ₹1L at 2 EDGE Miles/₹100 = 2,000 miles 
3. Milestone check: ₹3,00,000 ≥ ₹3L threshold → +2,500 milestone bonus
4. Total: 10,000 + 2,000 + 2,500 = 14,500 EDGE Miles"""
        else:
            base_prompt += """

For informational queries:
- Extract all relevant details from context
- Include specific numbers, dates, and conditions
- Be comprehensive but concise"""

        return base_prompt
    
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
            r'\d+l.*spend',  # Matches "3l spend" (lowercase)
            r'spend.*\d+l',  # Matches "spend 3l" (lowercase)
            r'\d+l.*hotel',  # Matches "3l hotel" (lowercase)
            r'\d+l.*flight', # Matches "3l flight" (lowercase)  
            r'milestone',
            r'surcharge'
        ]
        
        question_lower = question.lower()
        return any(re.search(pattern, question_lower) for pattern in calculation_indicators)
    
    
    def get_model_info(self, model: str = "gemini-1.5-flash") -> Dict[str, Any]:
        """Get information about a specific Gemini model"""
        if model not in self.model_pricing:
            raise ValueError(f"Unknown model: {model}")
        
        # Gemini model specifications
        model_specs = {
            "gemini-2.5-flash-lite": {"context_window": 1048576, "max_output_tokens": 8192},  # 1M context - NEW
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