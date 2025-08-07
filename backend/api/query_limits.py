"""
Query Limits API - Supabase-based system for authenticated users
Handles rate limiting and query count tracking using Supabase
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional
import logging

from services.supabase_service import SupabaseService

router = APIRouter()
logger = logging.getLogger(__name__)

# Configuration
AUTHENTICATED_DAILY_LIMIT = 100  # Queries per day for authenticated users

class QueryLimitResponse(BaseModel):
    can_query: bool
    remaining: int
    total: int
    message: Optional[str] = None

class QueryIncrementRequest(BaseModel):
    user_id: str
    user_email: Optional[str] = None

# Dependency to get SupabaseService
def get_supabase_service() -> SupabaseService:
    """Dependency to get SupabaseService instance"""
    return SupabaseService()

@router.get("/query-limits")
async def get_query_limits(
    authorization: Optional[str] = Header(None),
    db: SupabaseService = Depends(get_supabase_service)
):
    """Get query limits for authenticated user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = authorization.split("Bearer ")[1]
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    try:
        current_count, _ = db.get_user_query_count(user_id)
        remaining = max(0, AUTHENTICATED_DAILY_LIMIT - current_count)
        
        logger.info(f"✅ Query limits retrieved for user {user_id}: {remaining} remaining")
        
        return QueryLimitResponse(
            can_query=remaining > 0,
            remaining=remaining,
            total=AUTHENTICATED_DAILY_LIMIT,
            message=None if remaining > 0 else "Daily limit reached. Resets at midnight UTC."
        )
    except Exception as e:
        logger.error(f"❌ Database error getting query limits: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/increment-query")
async def increment_query(
    request: QueryIncrementRequest,
    authorization: Optional[str] = Header(None),
    db: SupabaseService = Depends(get_supabase_service)
):
    """Increment query count for authenticated user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = authorization.split("Bearer ")[1]
    if not user_id or user_id != request.user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    try:
        # Check current count before incrementing
        current_count, _ = db.get_user_query_count(user_id)
        
        if current_count >= AUTHENTICATED_DAILY_LIMIT:
            logger.warning(f"⚠️ Daily limit reached for user {user_id}")
            raise HTTPException(
                status_code=429, 
                detail=f"Daily limit of {AUTHENTICATED_DAILY_LIMIT} queries reached"
            )
        
        # Increment count
        new_count = db.increment_user_query_count(user_id, request.user_email)
        remaining = max(0, AUTHENTICATED_DAILY_LIMIT - new_count)
        
        logger.info(f"✅ Query count incremented for user {user_id}: {new_count}/{AUTHENTICATED_DAILY_LIMIT}")
        
        return QueryLimitResponse(
            can_query=remaining > 0,
            remaining=remaining,
            total=AUTHENTICATED_DAILY_LIMIT,
            message=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Database error incrementing query count: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Health check endpoint for query limits
@router.get("/query-limits/health")
async def query_limits_health(db: SupabaseService = Depends(get_supabase_service)):
    """Health check for query limits service"""
    try:
        # Test database connection
        connection_ok = db.test_connection()
        
        if connection_ok:
            return {"status": "healthy", "database": "supabase", "service": "query_limits"}
        else:
            raise HTTPException(status_code=503, detail="Database connection failed")
            
    except Exception as e:
        logger.error(f"❌ Query limits health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")