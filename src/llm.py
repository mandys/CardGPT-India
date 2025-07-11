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
2. Check for CATEGORY-SPECIFIC earning rates (travel, dining, etc.) vs base rates
3. Calculate base rewards using TWO SEPARATE STEPS:
   Step A: Calculate transactions = (spend amount ÷ Y)
   Step B: Calculate rewards = transactions × X points/miles
4. Add applicable milestone bonuses from spending thresholds
5. ALWAYS show both the division AND multiplication calculations separately

EXCLUSIONS AND EARNING RATES:
- FIRST: Check "accrual_exclusions" - if spending category is excluded, rewards = 0
- Common exclusions: rent, fuel, government services, tax, utilities, insurance, wallet, jewellery
- SECOND: DEFAULT to general spending unless category is explicitly mentioned
- Only use accelerated rates when question specifically mentions travel categories
- Hotels/Hotel bookings (when mentioned) = "Direct Hotels" category = accelerated travel rate
- Airlines/Flights (when mentioned) = "Direct Airlines" category = accelerated travel rate  
- General spending (default) = Use base rate (e.g., "2 miles per ₹100")
- Check for monthly caps on accelerated earning only if travel category is mentioned
- DO NOT assume travel spending unless explicitly stated
- ALWAYS verify exclusions before calculating any rewards

CRITICAL ARITHMETIC RULES:
- Show intermediate results for each step
- Double-check your multiplication (e.g., 1,000 × 6 = 6,000, not 1,000)
- Never round down in the middle of calculations
- If category-specific rate exists, USE IT instead of base rate

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
1. FIRST check for EXCLUSIONS - if spending category is excluded, rewards = 0
2. DEFAULT to general spending UNLESS specific category is mentioned
3. Only use category-specific rates if the question explicitly mentions:
   - "hotels", "hotel bookings", "accommodation"
   - "flights", "airlines", "air travel"  
   - "travel", "vacation", "trip"
4. Use the CORRECT earning rate based on what's explicitly mentioned:
   - Hotels/Hotel bookings (when mentioned): Use accelerated travel rate (e.g., "5 miles per ₹100")
   - Airlines/Flights (when mentioned): Use accelerated travel rate (e.g., "5 miles per ₹100") 
   - General spending (default): Use base rate (e.g., "2 miles per ₹100")
5. Calculate rewards using the CORRECT formula: (spend amount ÷ Y) × X 
   where "X points/miles per ₹Y" is the earning rate FOR THAT CATEGORY
6. Then identify applicable milestone bonuses from the spending amount
7. Add base rewards + milestone bonuses for the total
8. Show each step with the correct division calculation

CRITICAL: ALWAYS CHECK EXCLUSIONS FIRST!
- If context shows "accrual_exclusions" containing the spending category, rewards = 0
- Common exclusions: rent, fuel, government services, tax, utilities, insurance
- Example: "rent" in exclusions = 0 points/miles for rent spending

CALCULATION EXAMPLES WITH STEP-BY-STEP ARITHMETIC:

Example 1: General spending "6 points per ₹200" with ₹50,000 spend
Step 1: Check exclusions - general spending not excluded
Step 2: ₹50,000 ÷ ₹200 = 250 transactions
Step 3: 250 transactions × 6 points = 1,500 points

Example 2: Rent spending "6 points per ₹200" with ₹20,000 rent
Step 1: Check exclusions - "rent" found in accrual_exclusions
Step 2: Rent spending earns 0 points (excluded category)
Total: 0 points

Example 3: Hotel spending "5 miles per ₹100" with ₹1,00,000 hotels
Step 1: Check exclusions - hotels not excluded
Step 2: ₹1,00,000 ÷ ₹100 = 1,000 transactions  
Step 3: 1,000 transactions × 5 miles = 5,000 miles

Example 4: Fuel spending "2 miles per ₹100" with ₹10,000 fuel
Step 1: Check exclusions - "fuel" found in accrual_exclusions
Step 2: Fuel spending earns 0 miles (excluded category)
Total: 0 miles

Example 5: Mixed spending - ₹50,000 general + ₹20,000 rent
Step 1: General: ₹50,000 ÷ ₹200 = 250 × 6 = 1,500 points
Step 2: Rent: 0 points (excluded)
Total: 1,500 points

CRITICAL: ALWAYS check exclusions FIRST! If excluded, rewards = 0!

ALWAYS show both division AND multiplication steps separately!

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