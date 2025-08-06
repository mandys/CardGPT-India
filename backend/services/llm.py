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
from services.card_config import get_card_config

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating answers using Google Gemini models"""
    
    def __init__(self, gemini_api_key: str):
        """Initialize the LLM service with Gemini API key"""
        # Get card configuration service
        self.card_config = get_card_config()
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
        temperature: float = 0.1,
        user_preferences: Dict = None
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
        
        # Special optimizations for Gemini 2.5 Flash-Lite
        if model_choice == "gemini-2.5-flash-lite":
            # Increase token limits for travel and generic recommendation queries to ensure all cards are covered
            travel_keywords = ["travel", "trip", "vacation", "holiday", "journey", "lot of travel", "upcoming travel"]
            generic_rec_keywords = ["which card should i", "best card for", "recommend", "suggest", "better card"]
            
            if any(keyword in question.lower() for keyword in travel_keywords):
                max_tokens = min(max_tokens + 800, 2000)  # Extra tokens for comprehensive travel analysis
            elif any(keyword in question.lower() for keyword in generic_rec_keywords):
                max_tokens = min(max_tokens + 600, 1800)  # Extra tokens for complete card comparison
            
            # For Flash-Lite, we need more tokens for comparisons to ensure all cards are analyzed
            if any(keyword in question.lower() for keyword in ['compare', 'comparison', 'vs', 'versus']):
                max_tokens = min(max_tokens + 400, 1600)  # Additional boost for Flash-Lite comparisons
                
        # Create prompts with calculation enhancement
        system_prompt = self._create_system_prompt(card_name, is_calculation, user_preferences)
        user_prompt = self._create_user_prompt(question, context, is_calculation)
        
        # Google Gemini only architecture
        if not model_choice.startswith("gemini"):
            raise ValueError(f"Only Gemini models are supported. Requested: {model_choice}")
        
        # Generate answer using hybrid approach
        answer, usage_info = self._generate_gemini_answer(system_prompt, user_prompt, model_choice, max_tokens, temperature)
        
        # Add hybrid metadata
        usage_info["hybrid_intelligence"] = True
        usage_info["cardgpt_version"] = "2.0"
        logger.info(f"🔗 Hybrid CardGPT: Generated response with RAG + Gemini intelligence")
        
        return answer, usage_info
    
    def generate_answer_stream(
        self, 
        question: str, 
        context_documents: List[Dict], 
        card_name: str = None, 
        model_choice: str = "gemini-1.5-pro",
        max_tokens: int = 1200,
        temperature: float = 0.1,
        user_preferences: Dict = None
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
        system_prompt = self._create_system_prompt(card_name, is_calculation, user_preferences)
        user_prompt = self._create_user_prompt(question, context, is_calculation)
        
        # Google Gemini only architecture
        if not model_choice.startswith("gemini"):
            yield (f"Error: Only Gemini models are supported. Requested: {model_choice}", True, {"tokens": 0, "cost": 0, "model": model_choice})
            return
            
        yield from self._generate_gemini_answer_stream(system_prompt, user_prompt, model_choice, max_tokens, temperature, question)
    

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
    
    def _generate_gemini_answer_stream(self, system_prompt: str, user_prompt: str, model: str, max_tokens: int, temperature: float, question: str = ""):
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
            
            # Add hybrid metadata
            usage_info["hybrid_intelligence"] = True
            usage_info["cardgpt_version"] = "2.0"
            logger.info(f"🔗 Hybrid CardGPT: Generated streaming response with RAG + Gemini intelligence")
            
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
    
    def _create_system_prompt(self, card_name: str = None, is_calculation: bool = False, user_preferences: Dict = None) -> str:
        """Create an optimized hybrid system prompt for CardGPT"""
        
        # Use hybrid CardGPT approach
        prompt = """You are CardGPT, a knowledgeable assistant about Indian credit cards.

HYBRID INTELLIGENCE INSTRUCTIONS:
- Your PRIMARY source is the provided context from our trusted internal database
- If the context fully answers the query, use only that information
- If the context is incomplete, you may supplement with your own knowledge of Indian credit cards
- CLEARLY indicate what comes from provided sources vs. your own knowledge
- Do not hallucinate - only supplement when genuinely helpful
- For current/latest queries, acknowledge your knowledge cutoff and suggest verification

RESPONSE FORMAT:
- Start with information from provided context
- If supplementing, clearly mark: "From my knowledge:" or "Based on general understanding:"
- End current/promotional queries with verification note"""

        # Card focus logic
        if card_name:
            prompt += f"\nFOCUS: Answer specifically about {card_name} unless comparison is explicitly requested."
        else:
            prompt += """
COMPARISON REQUIREMENTS:
- Equal treatment of all cards in context
- Comprehensive analysis for travel/benefit queries  
- Balanced recommendations based on user needs"""

        # Essential calculation logic (streamlined)
        prompt += """
EARNING RATES & CALCULATIONS:
- Base rates: "X points per ₹Y" → (spend ÷ Y) × X
- REWARD CURRENCIES: Atlas=EDGE Miles, EPM=Reward Points, Premier=Reward points, Infinia=Reward Points
- Apply milestone bonuses: ₹3L→2500, ₹7.5L→2500, ₹15L→5000 (Atlas)
- Show step-by-step math with milestone calculations

CRITICAL CATEGORIES:
- Travel: flight/hotel bookings, includes "Direct Airlines/Hotels"  
- Insurance: general rate applies WITH caps (not excluded unless stated)
- Education: 2 EDGE Miles/₹100 (Atlas), specific amounts in context (EPM)"""
        
        # User personalization (streamlined)
        logger.info(f"🔍 [LLM_PREFS] Checking user preferences: {user_preferences}")
        if user_preferences:
            prompt += "\n\nUSER CONTEXT: Tailor recommendations to user's profile:"
            
            travel_type = user_preferences.get('travel_type', None)
            if travel_type:
                prompt += f"\n- Travel: {travel_type} focus"
                
            fee_willingness = user_preferences.get('fee_willingness', None)
            if fee_willingness:
                prompt += f"\n- Fee tolerance: {fee_willingness}"
                
            spend_categories = user_preferences.get('spend_categories', None)
            if spend_categories:
                prompt += f"\n- Primary spend: {', '.join(spend_categories)}"
                
            current_cards = user_preferences.get('current_cards', None)
            if current_cards:
                prompt += f"\n- Current cards: {', '.join(current_cards)} - optimize across portfolio"
                
            logger.info("✅ [LLM_PREFS] Streamlined user preferences added")
        else:
            logger.info("⚠️ [LLM_PREFS] No user preferences provided - using generic recommendations")
        
        # Log the complete system prompt for debugging
        logger.info(f"🎯 [LLM_PROMPT] === COMPLETE SYSTEM PROMPT ===")
        logger.info(f"🎯 [LLM_PROMPT] System prompt length: {len(prompt)} characters")
        logger.info(f"🎯 [LLM_PROMPT] Full system prompt:\n{prompt}")
        logger.info(f"🎯 [LLM_PROMPT] === END SYSTEM PROMPT ===")
        
        return prompt
    
    def _create_user_prompt(self, question: str, context: str, is_calculation: bool = False) -> str:
        """Create a hybrid user prompt with clear source attribution"""
        base_prompt = f"""Below are documents retrieved from our trusted internal database:

{context}

Please answer the user's query using the content above. If the content above does not fully address the query, you may use your own trained knowledge to supplement the answer.
Clearly mark which parts are based on source data and which are from your own understanding.

User Query:
{question}"""

        if is_calculation:
            base_prompt += """

🧮 CALCULATION REQUIRED: Show step-by-step math with milestone bonuses applied correctly."""

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