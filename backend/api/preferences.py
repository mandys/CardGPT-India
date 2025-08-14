"""
User Preferences API endpoints
Session-based preferences only (Clerk handles authentication separately)
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from typing import Optional
import uuid
import logging

from models import (
    UserPreferenceRequest, 
    UserPreferenceResponse, 
    UserPreferences
)
from services.preference_service import PreferenceService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/preferences/test")
async def test_preferences_api():
    """Test endpoint to verify preferences API is reachable"""
    logger.info("🧪 [TEST] Preferences test endpoint called")
    return {
        "status": "success",
        "message": "Preferences API is working",
        "timestamp": "2025-01-13T12:00:00Z"
    }

def get_preference_service():
    """Dependency to get preference service"""
    logger.info("🔧 [DEPS] Getting preference service")
    from main import app_state
    if "preference_service" in app_state:
        logger.info("✅ [DEPS] Found preference service in app_state")
        return app_state["preference_service"]
    else:
        # Fallback: create a new instance
        logger.warning("⚠️ [DEPS] Preference service not in app_state, creating fallback instance")
        return PreferenceService()

def get_session_id(request: Request) -> str:
    """Get or create session ID for guest users"""
    session_id = request.headers.get("x-session-id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

# Authenticated preferences for Clerk users

def get_clerk_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Extract Clerk user ID from Authorization header using proper JWT validation"""
    from services.clerk_auth import clerk_auth
    return clerk_auth.extract_user_id_from_request(authorization)

# Authenticated endpoints for Clerk users

@router.get("/preferences")
async def get_user_preferences(
    user_id: str = Depends(get_clerk_user_id),
    preference_service: PreferenceService = Depends(get_preference_service)
):
    """Get preferences for authenticated Clerk user"""
    try:
        prefs_response = preference_service.get_user_preferences(user_id)
        
        if not prefs_response:
            logger.warning(f"⚠️ No preferences found for user: {user_id}")
            # Return default preferences instead of 404
            default_prefs = UserPreferences()
            return UserPreferenceResponse(preferences=default_prefs)
        
        logger.info(f"✅ Retrieved user preferences for: {user_id}")
        return prefs_response
        
    except Exception as e:
        logger.error(f"❌ Error getting user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user preferences")

@router.post("/preferences")
async def save_user_preferences(
    request: UserPreferenceRequest,
    user_id: str = Depends(get_clerk_user_id),
    preference_service: PreferenceService = Depends(get_preference_service)
):
    """Save preferences for authenticated Clerk user"""
    try:
        # Save user preferences
        response = preference_service.save_user_preferences(user_id, request.preferences)
        
        logger.info(f"✅ User preferences saved: {user_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error saving user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save user preferences")

@router.delete("/preferences")
async def clear_user_preferences(
    user_id: str = Depends(get_clerk_user_id),
    preference_service: PreferenceService = Depends(get_preference_service)
):
    """Clear preferences for authenticated Clerk user"""
    try:
        # Create empty preferences to clear existing ones
        empty_preferences = UserPreferences()
        preference_service.save_user_preferences(user_id, empty_preferences)
        
        logger.info(f"✅ User preferences cleared for: {user_id}")
        return {"success": True, "message": "User preferences cleared successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error clearing user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear user preferences")

# Session-based endpoints for anonymous users

@router.post("/preferences/session")
async def save_session_preferences(
    request: UserPreferenceRequest,
    preference_service: PreferenceService = Depends(get_preference_service)
):
    """Store preferences for anonymous session"""
    try:
        # Use provided session_id or generate new one
        session_id = request.session_id or preference_service.generate_session_id()
        
        # Save session preferences
        result_session_id = preference_service.save_session_preferences(session_id, request.preferences)
        
        logger.info(f"✅ Session preferences saved: {result_session_id}")
        return {
            "success": True,
            "session_id": result_session_id,
            "message": "Session preferences saved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error saving session preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save session preferences")

@router.get("/preferences/session/{session_id}")
async def get_session_preferences(
    session_id: str,
    preference_service: PreferenceService = Depends(get_preference_service)
):
    """Get preferences for a specific session"""
    try:
        prefs = preference_service.get_session_preferences(session_id)
        
        if not prefs:
            logger.warning(f"⚠️ No preferences found for session: {session_id}")
            # Return default preferences instead of 404
            return UserPreferences().model_dump()
        
        logger.info(f"✅ Retrieved session preferences for: {session_id}")
        return prefs
        
    except Exception as e:
        logger.error(f"❌ Error getting session preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get session preferences")

@router.delete("/preferences/session/{session_id}")
async def clear_session_preferences(
    session_id: str,
    preference_service: PreferenceService = Depends(get_preference_service)
):
    """Clear preferences for a specific session"""
    try:
        # Create empty preferences to clear existing ones
        empty_preferences = UserPreferences()
        preference_service.save_session_preferences(session_id, empty_preferences)
        
        logger.info(f"✅ Session preferences cleared for: {session_id}")
        return {"success": True, "message": "Session preferences cleared successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error clearing session preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear session preferences")