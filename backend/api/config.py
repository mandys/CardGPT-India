"""
Configuration endpoints
"""

from fastapi import APIRouter, Depends
from models import ConfigResponse, ModelInfo
from typing import List

router = APIRouter()

@router.get("/config", response_model=ConfigResponse)
async def get_config(services=Depends(lambda: {})):
    """Get API configuration including available models and supported cards"""
    
    try:
        # Google-only model selection (ultra-low cost architecture)
        available_models = [
            ModelInfo(
                name="gemini-2.5-flash-lite",
                provider="Google",
                cost_per_1k_input=0.1,    # $0.0001 - NEW: Lowest cost!
                cost_per_1k_output=0.4,   # $0.0004
                available=True,
                description="🚀 NEW: Lowest latency & cost in Gemini 2.5 family"
            ),
            ModelInfo(
                name="gemini-1.5-flash",
                provider="Google",
                cost_per_1k_input=0.075,  # $0.000075
                cost_per_1k_output=0.3,   # $0.0003
                available=True,
                description="Ultra-fast model, great for simple queries"
            ),
            ModelInfo(
                name="gemini-1.5-pro",
                provider="Google",
                cost_per_1k_input=1.25,   # $0.00125
                cost_per_1k_output=5.0,   # $0.005
                available=True,
                description="Balanced model, good for complex queries"
            )
        ]
        
        # Check if Gemini is actually available
        if "llm_service" in services:
            gemini_available = services["llm_service"].gemini_available
            for model in available_models:
                if model.name.startswith("gemini"):
                    model.available = gemini_available
        
        # Supported credit cards
        supported_cards = [
            "Axis Atlas",
            "ICICI EPM", 
            "HSBC Premier",
            "HDFC Infinia"
        ]
        
        return ConfigResponse(
            available_models=available_models,
            supported_cards=supported_cards,
            default_model="gemini-2.5-flash-lite",  # NEW: Lowest latency & cost!
            max_top_k=15
        )
        
    except Exception as e:
        # Return default configuration if there's an error
        return ConfigResponse(
            available_models=[],
            supported_cards=["Axis Atlas", "ICICI EPM", "HSBC Premier"],
            default_model="gemini-2.5-flash-lite",
            max_top_k=15
        )

@router.get("/models", response_model=List[ModelInfo])
async def get_models(services=Depends(lambda: {})):
    """Get available AI models"""
    config = await get_config(services)
    return config.available_models

@router.get("/cards")
async def get_cards():
    """Get supported credit cards"""
    return {
        "cards": [
            "Axis Atlas",
            "ICICI EPM",
            "HSBC Premier",
            "HDFC Infinia"
        ]
    }