"""
Card Configuration Service

Centralized service for managing credit card configuration data.
Eliminates hardcoded card references throughout the application.
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CardConfigService:
    """Service for managing centralized card configuration"""
    
    def __init__(self):
        self._config = None
        self._cards_by_id = {}
        self._cards_by_display_name = {}
        self._cards_by_jsonl_name = {}
        self._alias_map = {}
        self._load_config()
    
    def _load_config(self):
        """Load card configuration from JSON file"""
        try:
            # Get the project root directory (go up from backend/services to project root)
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "available_cards.json"
            
            if not config_path.exists():
                logger.error(f"Card configuration file not found: {config_path}")
                self._config = {"supported_cards": []}
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            
            # Build lookup maps for efficient access
            self._build_lookup_maps()
            
            logger.info(f"✅ Loaded {len(self._config['supported_cards'])} cards from configuration")
            
        except Exception as e:
            logger.error(f"Failed to load card configuration: {e}")
            self._config = {"supported_cards": []}
    
    def _build_lookup_maps(self):
        """Build efficient lookup maps for different card identifiers"""
        self._cards_by_id.clear()
        self._cards_by_display_name.clear()
        self._cards_by_jsonl_name.clear()
        self._alias_map.clear()
        
        for card in self._config.get("supported_cards", []):
            if not card.get("active", True):
                continue
            
            card_id = card["id"]
            
            # Map by ID (primary key)
            self._cards_by_id[card_id] = card
            
            # Map by display name
            self._cards_by_display_name[card["display_name"]] = card
            
            # Map by JSONL name (for search results)
            self._cards_by_jsonl_name[card["jsonl_name"]] = card
            
            # Map all aliases to the card
            for alias in card.get("aliases", []):
                self._alias_map[alias.lower()] = card
            
            # Also map the display name as an alias
            self._alias_map[card["display_name"].lower()] = card
    
    def get_all_active_cards(self) -> List[Dict[str, Any]]:
        """Get all active cards"""
        return [card for card in self._config.get("supported_cards", []) if card.get("active", True)]
    
    def get_card_by_id(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get card by its ID"""
        return self._cards_by_id.get(card_id)
    
    def get_card_by_display_name(self, display_name: str) -> Optional[Dict[str, Any]]:
        """Get card by its display name"""
        return self._cards_by_display_name.get(display_name)
    
    def get_card_by_jsonl_name(self, jsonl_name: str) -> Optional[Dict[str, Any]]:
        """Get card by its JSONL name (used in search results)"""
        return self._cards_by_jsonl_name.get(jsonl_name)
    
    def get_card_by_alias(self, alias: str) -> Optional[Dict[str, Any]]:
        """Get card by any of its aliases"""
        return self._alias_map.get(alias.lower())
    
    def get_display_names(self) -> List[str]:
        """Get list of all active card display names"""
        return [card["display_name"] for card in self.get_all_active_cards()]
    
    def get_jsonl_names(self) -> List[str]:
        """Get list of all active card JSONL names"""
        return [card["jsonl_name"] for card in self.get_all_active_cards()]
    
    def get_aliases_for_card(self, card_id: str) -> List[str]:
        """Get all aliases for a specific card"""
        card = self.get_card_by_id(card_id)
        return card.get("aliases", []) if card else []
    
    def get_card_name_mapping(self) -> Dict[str, str]:
        """Get mapping from JSONL names to display names"""
        return {card["jsonl_name"]: card["display_name"] for card in self.get_all_active_cards()}
    
    def get_category_summary(self, category: str) -> Optional[str]:
        """Get category summary text"""
        return self._config.get("category_summaries", {}).get(category)
    
    def get_card_info_for_category(self, card_id: str, category: str) -> Optional[Dict[str, Any]]:
        """Get specific category information for a card"""
        card = self.get_card_by_id(card_id)
        if not card:
            return None
        return card.get("category_info", {}).get(category)
    
    def search_cards_by_text(self, search_text: str) -> List[Dict[str, Any]]:
        """Search cards by text (matches against names and aliases)"""
        search_lower = search_text.lower()
        matching_cards = []
        
        for card in self.get_all_active_cards():
            # Check display name
            if search_lower in card["display_name"].lower():
                matching_cards.append(card)
                continue
            
            # Check aliases
            for alias in card.get("aliases", []):
                if search_lower in alias.lower():
                    matching_cards.append(card)
                    break
        
        return matching_cards
    
    def get_config_version(self) -> str:
        """Get configuration version"""
        return self._config.get("version", "unknown")
    
    def reload_config(self):
        """Reload configuration from file (useful for development)"""
        self._load_config()

# Global instance
card_config = CardConfigService()

def get_card_config() -> CardConfigService:
    """Get the global card configuration service instance"""
    return card_config