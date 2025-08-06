"""
Query Limits API - Hybrid system for guest and authenticated users
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import sqlite3
import os

router = APIRouter()

# Configuration
AUTHENTICATED_DAILY_LIMIT = 100  # Queries per day for authenticated users
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "query_limits.db")

class QueryLimitResponse(BaseModel):
    can_query: bool
    remaining: int
    total: int
    message: Optional[str] = None

class QueryIncrementRequest(BaseModel):
    user_id: str
    user_email: Optional[str] = None

def init_query_limits_db():
    """Initialize the query limits database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_query_counts (
            user_id TEXT PRIMARY KEY,
            user_email TEXT,
            query_count INTEGER DEFAULT 0,
            last_reset_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def get_user_query_count(user_id: str) -> tuple[int, datetime]:
    """Get user's current query count and last reset date"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().date()
    
    cursor.execute("""
        SELECT query_count, last_reset_date FROM user_query_counts 
        WHERE user_id = ?
    """, (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return 0, today
    
    query_count, last_reset_str = result
    last_reset = datetime.fromisoformat(last_reset_str).date() if last_reset_str else today
    
    # Reset count if it's a new day
    if last_reset < today:
        query_count = 0
    
    return query_count, last_reset

def increment_user_query_count(user_id: str, user_email: Optional[str] = None) -> int:
    """Increment user's query count and return new count"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().date()
    now = datetime.now()
    
    # Get current count
    current_count, last_reset = get_user_query_count(user_id)
    
    # Reset if new day
    if last_reset < today:
        current_count = 0
    
    new_count = current_count + 1
    
    # Upsert user record
    cursor.execute("""
        INSERT OR REPLACE INTO user_query_counts 
        (user_id, user_email, query_count, last_reset_date, created_at, updated_at)
        VALUES (?, ?, ?, ?, 
                COALESCE((SELECT created_at FROM user_query_counts WHERE user_id = ?), ?),
                ?)
    """, (user_id, user_email, new_count, today.isoformat(), user_id, now.isoformat(), now.isoformat()))
    
    conn.commit()
    conn.close()
    
    return new_count

@router.get("/query-limits")
async def get_query_limits(authorization: Optional[str] = Header(None)):
    """Get query limits for authenticated user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = authorization.split("Bearer ")[1]
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    try:
        current_count, _ = get_user_query_count(user_id)
        remaining = max(0, AUTHENTICATED_DAILY_LIMIT - current_count)
        
        return QueryLimitResponse(
            can_query=remaining > 0,
            remaining=remaining,
            total=AUTHENTICATED_DAILY_LIMIT,
            message=None if remaining > 0 else "Daily limit reached. Resets at midnight UTC."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/increment-query")
async def increment_query(
    request: QueryIncrementRequest,
    authorization: Optional[str] = Header(None)
):
    """Increment query count for authenticated user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = authorization.split("Bearer ")[1]
    if not user_id or user_id != request.user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    try:
        # Check current count before incrementing
        current_count, _ = get_user_query_count(user_id)
        
        if current_count >= AUTHENTICATED_DAILY_LIMIT:
            raise HTTPException(
                status_code=429, 
                detail=f"Daily limit of {AUTHENTICATED_DAILY_LIMIT} queries reached"
            )
        
        # Increment count
        new_count = increment_user_query_count(user_id, request.user_email)
        remaining = max(0, AUTHENTICATED_DAILY_LIMIT - new_count)
        
        return QueryLimitResponse(
            can_query=remaining > 0,
            remaining=remaining,
            total=AUTHENTICATED_DAILY_LIMIT,
            message=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Initialize database on module import
init_query_limits_db()