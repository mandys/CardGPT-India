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
        max_tokens: int = 1000,
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
        """Build context string from relevant documents"""
        return "\n\n---\n\n".join([
            f"Card: {doc['cardName']}\nSection: {doc['section']}\nContent: {doc['content']}"
            for doc in documents
        ])
    
    def _create_system_prompt(self, card_name: str = None) -> str:
        """Create the system prompt for the LLM"""
        prompt = """You are an expert assistant helping users understand Indian credit card terms and conditions.
    
IMPORTANT: When calculating total rewards/miles for a spend amount, you MUST:
1. Identify the correct earning rate format from the context (e.g., "6 points per ₹200" or "2 miles per ₹100")
2. Calculate base rewards using the EXACT formula:
   - If "X points per ₹Y": (spend amount ÷ Y) × X points
   - Example: "6 points per ₹200" means (₹50,000 ÷ 200) × 6 = 1,500 points
   - Example: "2 miles per ₹100" means (₹50,000 ÷ 100) × 2 = 1,000 miles
3. Add applicable milestone bonuses from spending thresholds
4. Always show the correct division in your calculations

CRITICAL: Never assume "per ₹100" - use the exact amount specified in the earning rate!

Please provide accurate, helpful answers based on the provided context. If the context doesn't contain enough information to answer the question, say so clearly.

Format your response in a clear, easy-to-understand way. Use bullet points or numbered lists when appropriate.
Include specific details like fees, interest rates, and conditions when relevant."""
        
        if card_name:
            prompt += f"\nFocus on information about the {card_name} card."
        
        return prompt
    
    def _create_user_prompt(self, question: str, context: str) -> str:
        """Create the user prompt with question and context"""
        return f"""Based on the following credit card information, please answer this question: "{question}"

Context:
{context}

IMPORTANT: If the question involves calculating total rewards/miles for a spending amount:
1. First identify the exact earning rate format from context (e.g., "6 points per ₹200", "2 miles per ₹100")
2. Calculate base rewards using the CORRECT formula: (spend amount ÷ Y) × X 
   where "X points/miles per ₹Y" is the earning rate
3. Then identify applicable milestone bonuses from the spending amount
4. Add base rewards + milestone bonuses for the total
5. Show each step with the correct division calculation

EXAMPLE: If earning rate is "6 points per ₹200" and spend is ₹50,000:
Base rewards = (₹50,000 ÷ ₹200) × 6 = 250 × 6 = 1,500 points

Please provide a comprehensive answer based on the information provided."""
    
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