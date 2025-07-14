"""
OpenAI LLM Service
Handles text generation using OpenAI's chat models (GPT-4, GPT-3.5-turbo)
"""

import openai
import google.generativeai as genai
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating answers using OpenAI's chat models"""
    
    def __init__(self, api_key: str, gemini_api_key: str = None):
        """Initialize the LLM service with API keys"""
        self.client = openai.OpenAI(api_key=api_key)
        
        # Initialize Gemini if API key provided
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
        
        # Model pricing (per 1K tokens)
        self.model_pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},  # Much cheaper!
            "gemini-1.5-pro": {"input": 0.00125, "output": 0.005}
        }
    
    def generate_answer(
        self, 
        question: str, 
        context_documents: List[Dict], 
        card_name: str = None, 
        model_choice: str = "gpt-3.5-turbo",  # Changed from use_gpt4 bool
        max_tokens: int = 500,
        temperature: float = 0.1
    ) -> tuple[str, Dict[str, Any]]:
        """
        Generate an answer using selected LLM
        
        Args:
            question: User's question
            context_documents: Relevant documents for context
            card_name: Specific card to focus on (optional)
            model_choice: Model to use (gpt-4, gpt-3.5-turbo, gemini-1.5-flash, gemini-1.5-pro)
            max_tokens: Maximum tokens in response
            temperature: Creativity parameter (0.0 to 1.0)
            
        Returns:
            tuple: (answer_text, usage_info)
        """
        if not context_documents:
            return self._no_context_response(), {"tokens": 0, "cost": 0, "model": "none"}
        
        # Build context from documents
        context = self._build_context(context_documents)
        
        # Create prompts
        system_prompt = self._create_system_prompt(card_name)
        user_prompt = self._create_user_prompt(question, context)
        
        # Route to appropriate model
        if model_choice.startswith("gemini"):
            return self._generate_gemini_answer(system_prompt, user_prompt, model_choice, max_tokens, temperature)
        else:
            return self._generate_openai_answer(system_prompt, user_prompt, model_choice, max_tokens, temperature)
    
    def _generate_openai_answer(self, system_prompt: str, user_prompt: str, model: str, max_tokens: int, temperature: float):
        """Generate answer using OpenAI models"""
        pricing = self.model_pricing[model]
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Calculate costs
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_cost = (input_tokens * pricing["input"] / 1000) + (output_tokens * pricing["output"] / 1000)
            
            usage_info = {
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": response.usage.total_tokens,
                "cost": total_cost,
                "pricing": pricing
            }
            
            answer = response.choices[0].message.content or "Sorry, I couldn't generate a response."
            logger.info(f"Generated answer using {model}: {input_tokens} input + {output_tokens} output tokens")
            
            return answer, usage_info
            
        except Exception as e:
            logger.error(f"Error generating answer with {model}: {str(e)}")
            return f"Error generating answer: {str(e)}", {"tokens": 0, "cost": 0, "model": model}
    
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
            
            response = gemini_model.generate_content(combined_prompt)
            
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
        """Build context string from relevant documents with smart truncation"""
        context_parts = []
        for doc in documents:
            # Give full content for renewal benefits, welcome benefits, and important sections
            important_sections = ['renewal_benefits', 'welcome_benefits', 'milestones', 'tier_structure']
            
            if any(section in doc['section'] for section in important_sections):
                # Full content for important sections
                content = doc['content']
            else:
                # Truncate other sections to 400 chars
                content = doc['content'][:400]
                if len(doc['content']) > 400:
                    content += '...'
            
            context_parts.append(f"{doc['cardName']} {doc['section']}: {content}")
        
        return "\n\n".join(context_parts)
    
    def _create_system_prompt(self, card_name: str = None) -> str:
        """Create a concise system prompt for the LLM"""
        prompt = """You are a credit card expert. Be concise and accurate.

CRITICAL: For each ₹ spent, apply ONLY ONE earning rate (base OR category, never both).
CRITICAL: If question asks about ONE specific card, answer ONLY about that card. Don't compare unnecessarily.

CALCULATION RULES:
1. Check exclusions first (government, rent, fuel, utilities may be excluded)
2. Use exact earning rates: "X points per ₹Y" → (spend ÷ Y) × X  
3. Category rates: Hotels/flights may have accelerated rates, everything else uses base rate
4. **CHECK CAPS**: Always check monthly/annual caps for accelerated rates
5. **MILESTONES ARE ANNUAL**: Earned once per year based on total yearly spend (NOT monthly)
6. **MILESTONE LOGIC**: Add milestones ONLY if the spend amount in the question ≥ milestone threshold
7. **CAPPING vs EXCLUSION**: "Capped" means rewards earned but limited; "Excluded" means 0 rewards

KNOWN CARD PATTERNS (use context to verify):
- Axis Atlas: 2 miles/₹100 (base), 5 miles/₹100 (hotels/flights share ₹2L/month cap)
- ICICI EPM: 6 points/₹200 (all categories, with caps per cycle)
- HSBC Premier: 3 points/₹100 (general rate with category caps)

CRITICAL: Hotels and flights often SHARE monthly caps (not separate caps!)

EXCLUSIONS (check context to verify): 
- Common exclusions: Government, rent, fuel
- Axis Atlas additional: Utilities, insurance, wallet, jewellery
- ICICI EPM: Fewer exclusions but has caps instead
- HSBC Premier: Check context for specific exclusions

EARNING CAPS (earns rewards but capped per cycle):
- Look for "capped at X points per cycle/month" in context
- Calculate normally, then apply the cap limit

SURCHARGES (calculate if spend exceeds threshold):
- Look for surcharge rules in context (typically 1% above thresholds)

MILESTONE EXAMPLES (ANNUAL - verify thresholds in context):
₹7.5L yearly spend on Atlas → Base: (750000 ÷ 100) × 2 = 15,000 miles
Annual milestones: Add milestone bonuses from context
✅ Total: Base + milestone bonuses

₹3L yearly spend → Check if ≥ milestone threshold, add bonus if applicable

Show calculations step-by-step. For comparisons, discuss relevant cards from context."""
        
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
    
    def get_model_info(self, model: str = "gpt-4") -> Dict[str, Any]:
        """Get information about a specific model"""
        if model not in self.model_pricing:
            raise ValueError(f"Unknown model: {model}")
        
        return {
            "model": model,
            "pricing": self.model_pricing[model],
            "context_window": 128000 if model == "gpt-4" else 16385,
            "max_output_tokens": 4096
        }