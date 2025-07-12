"""
OpenAI LLM Service
Handles text generation using OpenAI's chat models (GPT-4, GPT-3.5-turbo)
"""

import openai
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating answers using OpenAI's chat models"""
    
    def __init__(self, api_key: str):
        """Initialize the LLM service with OpenAI API key"""
        self.client = openai.OpenAI(api_key=api_key)
        
        # Model pricing (per 1K tokens)
        self.model_pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
        }
    
    def generate_answer(
        self, 
        question: str, 
        context_documents: List[Dict], 
        card_name: str = None, 
        use_gpt4: bool = True,
        max_tokens: int = 500,  # Reduced from 1000 to 500
        temperature: float = 0.1
    ) -> tuple[str, Dict[str, Any]]:
        """
        Generate an answer using OpenAI's chat models
        
        Args:
            question: User's question
            context_documents: Relevant documents for context
            card_name: Specific card to focus on (optional)
            use_gpt4: Whether to use GPT-4 (True) or GPT-3.5-turbo (False)
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
        
        # Select model and pricing
        model = "gpt-4" if use_gpt4 else "gpt-3.5-turbo"
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
    
    def _build_context(self, documents: List[Dict]) -> str:
        """Build concise context string from relevant documents"""
        return "\n\n".join([
            f"{doc['cardName']} {doc['section']}: {doc['content'][:400]}{'...' if len(doc['content']) > 400 else ''}"
            for doc in documents
        ])
    
    def _create_system_prompt(self, card_name: str = None) -> str:
        """Create a concise system prompt for the LLM"""
        prompt = """You are a credit card expert. Be concise and accurate.

CRITICAL: For each ₹ spent, apply ONLY ONE earning rate (base OR category, never both).

CALCULATION RULES:
1. Check exclusions first (government, rent, fuel, utilities may be excluded)
2. Use exact earning rates: "X points per ₹Y" → (spend ÷ Y) × X  
3. Category rates: Hotels/flights use accelerated rates, everything else uses base rate
4. Milestones: Only apply if spend meets threshold (cumulative)

RATES:
- Axis Atlas: 2 miles/₹100 (base), 5 miles/₹100 (hotels/flights only)
- ICICI EPM: 6 points/₹200 (all categories, with caps)

EXCLUSIONS: 
- Both: Government, rent, fuel
- Axis only: Utilities, insurance, wallet, jewellery
- Education: ICICI (capped 1K points), Axis (no exclusion)

EXAMPLE:
₹7.5L general spend on Atlas → (750000 ÷ 100) × 2 = 15,000 miles
Milestones: ₹3L (2,500) + ₹7.5L (2,500) = +5,000 miles  
✅ Total: 20,000 miles

Show calculations step-by-step. For comparisons, discuss both cards."""
        
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
2. Use ONE rate per spend: base OR category (never add both)
3. Apply milestones only if total spend ≥ threshold
4. Show step-by-step: (amount ÷ Y) × X = result

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