"""
User Preferences API endpoints
Handles user preference storage, retrieval, and session management for personalized recommendations
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

# NOTE: Auth service disabled - using Clerk for authentication now
# Authenticated preferences are temporarily disabled until Clerk integration is complete

def get_session_id(request: Request) -> str:
    """Get or create session ID for guest users"""
    session_id = request.headers.get("x-session-id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

# DISABLED: Old JWT auth system removed, Clerk handles authentication now

# DISABLED: Authenticated preferences temporarily disabled until Clerk integration
# @router.post("/preferences", response_model=UserPreferenceResponse)
# async def create_or_update_preferences(...):
        
        user_id = str(user_info['user_id'])
        
        # Save preferences
        result = preference_service.save_user_preferences(user_id, request.preferences)
        
        logger.info(f"✅ Preferences updated for user: {user_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")

@router.get("/preferences", response_model=UserPreferenceResponse)
async def get_user_preferences(
    authorization: Optional[str] = Header(None),
    preference_service: PreferenceService = Depends(get_preference_service),
    auth_service = Depends(get_auth_service)
):
    """Get current user preferences for authenticated users"""
    logger.info("🔍 [GET_PREFS] Get user preferences endpoint called")
    try:
        # Get user info from JWT token
        user_info = get_user_from_auth(authorization, auth_service)
        logger.info(f"🔍 [GET_PREFS] User info: {user_info}")
        
        if not user_info:
            logger.warning("⚠️ [GET_PREFS] No authentication provided")
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(user_info['user_id'])
        logger.info(f"🔍 [GET_PREFS] Getting preferences for user: {user_id}")
        
        # Get preferences
        result = preference_service.get_user_preferences(user_id)
        logger.info(f"🔍 [GET_PREFS] Retrieved preferences: {result}")
        
        if not result:
            logger.warning(f"⚠️ [GET_PREFS] No preferences found for user: {user_id}")
            raise HTTPException(status_code=404, detail="No preferences found")
        
        logger.info(f"✅ [GET_PREFS] Returning preferences for user: {user_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get preferences")

@router.delete("/preferences")
async def delete_user_preferences(
    authorization: Optional[str] = Header(None),
    preference_service: PreferenceService = Depends(get_preference_service),
    auth_service = Depends(get_auth_service)
):
    """Clear user preferences for authenticated users"""
    try:
        # Get user info from JWT token
        user_info = get_user_from_auth(authorization, auth_service)
        
        if not user_info:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(user_info['user_id'])
        
        # Create empty preferences to clear existing ones
        empty_preferences = UserPreferences()
        preference_service.save_user_preferences(user_id, empty_preferences)
        
        logger.info(f"✅ Preferences cleared for user: {user_id}")
        return {"success": True, "message": "Preferences cleared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error clearing preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear preferences")

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

@router.get("/preferences/session/{session_id}", response_model=UserPreferences)
async def get_session_preferences(
    session_id: str,
    preference_service: PreferenceService = Depends(get_preference_service)
):
    """Get preferences for anonymous session"""
    try:
        result = preference_service.get_session_preferences(session_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="No session preferences found or session expired")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting session preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get session preferences")

# REMOVED: Complex ambiguity detection endpoint - using simplified post-response approach

@router.post("/preferences/cleanup-sessions")
async def cleanup_expired_sessions(
    preference_service: PreferenceService = Depends(get_preference_service)
):
    """Clean up expired session preferences (admin endpoint)"""
    try:
        preference_service.cleanup_expired_sessions()
        return {"success": True, "message": "Expired sessions cleaned up"}
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cleanup sessions")