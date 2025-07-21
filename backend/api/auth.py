"""
Authentication API endpoints
Handles Google OAuth login, JWT tokens, and query limits
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from typing import Optional
import uuid
import logging
from datetime import datetime, timezone

from models import GoogleAuthRequest, AuthResponse, UserStatsResponse, QueryLimitResponse
from services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter()

def get_auth_service():
    """Dependency to get auth service"""
    from main import app_state
    if "auth_service" in app_state:
        return app_state["auth_service"]
    else:
        # Fallback: create a new instance
        return AuthService()

def get_session_id(request: Request) -> str:
    """Get or create session ID for guest users"""
    session_id = request.headers.get("x-session-id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

@router.post("/auth/google", response_model=AuthResponse)
async def google_auth(
    request: GoogleAuthRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user with Google OAuth token"""
    try:
        # Verify Google token
        google_user_info = await auth_service.verify_google_token(request.token)
        
        if not google_user_info:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        
        # Create or get user
        user = await auth_service.create_or_get_user(google_user_info)
        
        # Create JWT token
        jwt_token = auth_service.create_jwt_token(user)
        
        logger.info(f"User authenticated: {user['email']}")
        
        return AuthResponse(
            success=True,
            jwt_token=jwt_token,
            user=user,
            message="Authentication successful"
        )
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@router.get("/auth/verify")
async def verify_token(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No valid authorization header")
    
    token = authorization.split(" ")[1]
    user_info = auth_service.verify_jwt_token(token)
    
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {"valid": True, "user": user_info}

@router.get("/auth/stats", response_model=UserStatsResponse)
async def get_user_stats(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get user statistics (requires authentication)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = authorization.split(" ")[1]
    user_info = auth_service.verify_jwt_token(token)
    
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    stats = await auth_service.get_user_stats(user_info['user_id'])
    
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserStatsResponse(
        user=stats['user'],
        stats=stats['stats']
    )

@router.get("/auth/query-limit", response_model=QueryLimitResponse)
async def check_query_limit(
    request: Request,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Check query limit for current user/session"""
    user_id = None
    session_id = None
    
    # Check if user is authenticated
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        user_info = auth_service.verify_jwt_token(token)
        if user_info:
            user_id = user_info['user_id']
    
    # If not authenticated, use session ID
    if not user_id:
        session_id = get_session_id(request)
    
    # Check query limits
    can_query, current_count, limit = await auth_service.can_make_query(user_id, session_id)
    
    remaining = None
    if limit > 0:  # Guest users have limits
        remaining = max(0, limit - current_count)
    
    return QueryLimitResponse(
        can_query=can_query,
        current_count=current_count,
        limit=limit,
        remaining=remaining
    )

@router.post("/auth/increment-query")
async def increment_query_count(
    request: Request,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Increment query count for current user/session"""
    user_id = None
    session_id = None
    
    logger.info(f"🚀 Increment query endpoint called")
    
    # Check if user is authenticated
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        user_info = auth_service.verify_jwt_token(token)
        if user_info:
            user_id = user_info['user_id']
            logger.info(f"🔑 Authenticated user: {user_id}")
    
    # If not authenticated, use session ID
    if not user_id:
        session_id = get_session_id(request)
        logger.info(f"👤 Guest session: {session_id}")
        
        # Check if guest user has exceeded limit
        can_query, current_count, limit = await auth_service.can_make_query(None, session_id)
        logger.info(f"📊 Guest query status: can_query={can_query}, current={current_count}, limit={limit}")
        if not can_query:
            logger.warning(f"❌ Guest limit exceeded: {current_count}/{limit}")
            raise HTTPException(
                status_code=429, 
                detail=f"Daily query limit exceeded ({limit} queries per day). Please sign in for unlimited queries."
            )
    
    # Increment query count
    new_count = await auth_service.increment_query_count(user_id, session_id)
    logger.info(f"✅ Query incremented successfully: new_count={new_count}")
    
    return {
        "success": True,
        "new_count": new_count,
        "is_authenticated": user_id is not None
    }

@router.post("/auth/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {
        "success": True,
        "message": "Logout successful. Please remove the JWT token from client storage."
    }