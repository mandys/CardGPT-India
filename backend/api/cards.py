"""
Card Configuration API

Provides endpoints for accessing centralized card configuration data.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import logging

from services.card_config import get_card_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["cards"])

@router.get("/cards")
async def get_all_cards() -> Dict[str, Any]:
    """
    Get all active cards with their configuration
    
    Returns:
        Dictionary containing all active card configurations
    """
    try:
        card_config = get_card_config()
        cards = card_config.get_all_active_cards()
        
        return {
            "cards": cards,
            "total_count": len(cards),
            "version": card_config.get_config_version()
        }
    except Exception as e:
        logger.error(f"Failed to get cards: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve card configuration")

@router.get("/cards/display-names")
async def get_card_display_names() -> Dict[str, List[str]]:
    """
    Get list of card display names for frontend components
    
    Returns:
        List of display names for all active cards
    """
    try:
        card_config = get_card_config()
        display_names = card_config.get_display_names()
        
        # Add 'None' option for frontend filters
        filter_options = ['None'] + display_names
        
        return {
            "display_names": display_names,
            "filter_options": filter_options
        }
    except Exception as e:
        logger.error(f"Failed to get card display names: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve card names")

@router.get("/cards/{card_id}")
async def get_card_by_id(card_id: str) -> Dict[str, Any]:
    """
    Get specific card by ID
    
    Args:
        card_id: Card identifier
        
    Returns:
        Card configuration data
    """
    try:
        card_config = get_card_config()
        card = card_config.get_card_by_id(card_id)
        
        if not card:
            raise HTTPException(status_code=404, detail=f"Card not found: {card_id}")
        
        return {"card": card}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get card {card_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve card")

@router.get("/cards/search/{search_text}")
async def search_cards(search_text: str) -> Dict[str, Any]:
    """
    Search cards by text (names and aliases)
    
    Args:
        search_text: Text to search for
        
    Returns:
        Matching cards
    """
    try:
        card_config = get_card_config()
        matching_cards = card_config.search_cards_by_text(search_text)
        
        return {
            "cards": matching_cards,
            "search_text": search_text,
            "matches_found": len(matching_cards)
        }
    except Exception as e:
        logger.error(f"Failed to search cards for '{search_text}': {e}")
        raise HTTPException(status_code=500, detail="Failed to search cards")

@router.get("/cards/category/{category}")
async def get_category_info(category: str) -> Dict[str, Any]:
    """
    Get category information across all cards
    
    Args:
        category: Category name (e.g., 'insurance', 'education')
        
    Returns:
        Category information for all cards
    """
    try:
        card_config = get_card_config()
        cards = card_config.get_all_active_cards()
        
        category_info = {}
        for card in cards:
            card_category_info = card.get("category_info", {}).get(category)
            if card_category_info:
                category_info[card["display_name"]] = card_category_info
        
        category_summary = card_config.get_category_summary(category)
        
        return {
            "category": category,
            "summary": category_summary,
            "cards": category_info
        }
    except Exception as e:
        logger.error(f"Failed to get category info for '{category}': {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve category information")

@router.post("/cards/reload")
async def reload_card_config() -> Dict[str, str]:
    """
    Reload card configuration from file (development endpoint)
    
    Returns:
        Status message
    """
    try:
        card_config = get_card_config()
        card_config.reload_config()
        
        return {
            "status": "success",
            "message": "Card configuration reloaded successfully"
        }
    except Exception as e:
        logger.error(f"Failed to reload card config: {e}")
        raise HTTPException(status_code=500, detail="Failed to reload configuration")