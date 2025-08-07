"""
User Preference Service for personalized credit card recommendations
Handles user preference storage, retrieval, and session management
Uses Supabase for all database operations
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from uuid import uuid4

from models import UserPreferences, UserPreferenceResponse
from .supabase_service import SupabaseService

logger = logging.getLogger(__name__)

class PreferenceService:
    def __init__(self, supabase_service: SupabaseService = None):
        """Initialize PreferenceService with SupabaseService"""
        if supabase_service:
            self.db = supabase_service
        else:
            # Create new SupabaseService instance
            self.db = SupabaseService()
        
        self.database_type = "supabase"
        logger.info("🎯 PreferenceService initialized with Supabase backend")
    
    def save_user_preferences(self, user_id: str, preferences: UserPreferences) -> UserPreferenceResponse:
        """Save or update user preferences"""
        try:
            # Convert Pydantic model to dict
            preferences_dict = preferences.model_dump()
            
            # Save to Supabase
            result = self.db.save_user_preferences(user_id, preferences_dict)
            
            # Log analytics event
            self.db.log_analytics_event("preference_updated", user_id=user_id, event_data=preferences_dict)
            
            # Format response
            return self._format_preference_response(result)
            
        except Exception as e:
            logger.error(f"❌ Error saving preferences for user {user_id}: {e}")
            raise
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferenceResponse]:
        """Get user preferences by user_id"""
        try:
            result = self.db.get_user_preferences(user_id)
            
            if result:
                return self._format_preference_response(result)
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting preferences for user {user_id}: {e}")
            return None
    
    def save_session_preferences(self, session_id: str, preferences: UserPreferences) -> str:
        """Save preferences for anonymous session"""
        try:
            expires_at = datetime.utcnow() + timedelta(days=30)
            preferences_dict = preferences.model_dump()
            
            result = self.db.save_session_preferences(session_id, preferences_dict, expires_at)
            
            # Log analytics event
            self.db.log_analytics_event("session_preference_saved", session_id=session_id, event_data=preferences_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error saving session preferences: {e}")
            raise
    
    def get_session_preferences(self, session_id: str) -> Optional[UserPreferences]:
        """Get preferences for anonymous session"""
        try:
            result = self.db.get_session_preferences(session_id)
            
            if result:
                return UserPreferences(**result)
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting session preferences: {e}")
            return None
    
    def _format_preference_response(self, result: Dict) -> UserPreferenceResponse:
        """Format database result into UserPreferenceResponse"""
        preferences = UserPreferences(
            travel_type=result.get('travel_type'),
            lounge_access=result.get('lounge_access'),
            fee_willingness=result.get('fee_willingness'),
            current_cards=result.get('current_cards', []),
            preferred_banks=result.get('preferred_banks', []),
            spend_categories=result.get('spend_categories', [])
        )
        
        # Calculate completion status
        completion_status = {
            "travel_preferences": bool(preferences.travel_type and preferences.lounge_access),
            "financial_preferences": bool(preferences.fee_willingness),
            "card_preferences": bool(preferences.current_cards or preferences.preferred_banks),
            "spending_preferences": bool(preferences.spend_categories)
        }
        
        return UserPreferenceResponse(
            user_id=result['user_id'],
            preferences=preferences,
            completion_status=completion_status,
            created_at=result['created_at'],
            updated_at=result['updated_at']
        )
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired session preferences"""
        try:
            deleted_count = self.db.cleanup_expired_sessions()
            
            if deleted_count > 0:
                logger.info(f"🧹 Cleaned up {deleted_count} expired session preferences")
                
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up expired sessions: {e}")
            return 0
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID for anonymous users"""
        return f"session_{uuid4().hex[:16]}"