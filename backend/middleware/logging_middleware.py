"""
Query Logging Middleware for FastAPI
Automatically captures query and response data for training purposes
"""

import time
import logging
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
import json

logger = logging.getLogger(__name__)

class QueryLoggingMiddleware:
    """Middleware to automatically log query requests and responses"""
    
    def __init__(self, app, query_logger=None):
        self.app = app
        self.query_logger = query_logger
        
    async def __call__(self, scope, receive, send):
        """ASGI middleware implementation"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        request = Request(scope, receive)
        
        # Only log chat API endpoints
        if not request.url.path.startswith("/api/chat"):
            await self.app(scope, receive, send)
            return
            
        # Skip if logging is disabled or no logger available
        if not self.query_logger or not self.query_logger.config.enabled:
            await self.app(scope, receive, send)
            return
            
        # Start timing
        start_time = time.time()
        session_id = None
        
        # Capture request data
        try:
            body = await request.body()
            if body:
                request_data = json.loads(body.decode())
                session_id = await self._log_request(request, request_data)
        except Exception as e:
            logger.error(f"Failed to capture request data: {e}")
        
        # Create a new receive callable that can replay the body
        async def receive_wrapper():
            return {"type": "http.request", "body": body}
        
        # Capture response
        response_data = {}
        
        async def send_wrapper(message):
            """Capture response data"""
            if message["type"] == "http.response.start":
                response_data["status"] = message["status"]
            elif message["type"] == "http.response.body" and session_id:
                # Log response when body is complete
                execution_time = int((time.time() - start_time) * 1000)
                await self._log_response(session_id, response_data.get("status", 500), execution_time)
            
            await send(message)
        
        # Process request through the application
        await self.app(scope, receive_wrapper, send_wrapper)
    
    async def _log_request(self, request: Request, request_data: dict) -> Optional[str]:
        """Extract and log request data"""
        try:
            from models.logging_models import QueryLogData
            
            # Extract user context
            user_ip = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")
            
            # Create log data
            query_data = QueryLogData(
                query_text=request_data.get("message", ""),
                selected_model=request_data.get("model", "gemini-1.5-pro"),
                query_mode=request_data.get("query_mode", "General Query"),
                card_filter=request_data.get("card_filter"),
                top_k=request_data.get("top_k", 10),
                user_ip=user_ip,
                user_agent=user_agent
            )
            
            session_id = await self.query_logger.log_query(query_data)
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to log request: {e}")
            return None
    
    async def _log_response(self, session_id: str, status_code: int, execution_time_ms: int):
        """Log response data"""
        try:
            from models.logging_models import ResponseLogData
            
            response_data = ResponseLogData(
                response_status=status_code,
                execution_time_ms=execution_time_ms,
                llm_tokens_used=0,  # Will be updated by chat endpoint
                llm_cost=0.0,       # Will be updated by chat endpoint
                search_results_count=0  # Will be updated by chat endpoint
            )
            
            await self.query_logger.log_response(session_id, response_data)
            
        except Exception as e:
            logger.error(f"Failed to log response: {e}")
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers (for reverse proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        return request.client.host if request.client else "unknown"


# Standalone function for manual logging in endpoints
async def log_detailed_metrics(query_logger, session_id: str, metrics: dict):
    """
    Manually update query log with detailed metrics from chat endpoint
    Call this from the chat endpoint after getting LLM response
    """
    if not query_logger or not session_id:
        return
        
    try:
        from models.logging_models import ResponseLogData
        
        # Extract metrics from the response
        llm_usage = metrics.get("llm_usage", {})
        search_results = metrics.get("sources", [])
        
        response_data = ResponseLogData(
            response_status=200,  # Already successful if we got here
            execution_time_ms=metrics.get("execution_time_ms", 0),
            llm_tokens_used=llm_usage.get("total_tokens", 0),
            llm_cost=llm_usage.get("cost", 0.0),
            search_results_count=len(search_results)
        )
        
        await query_logger.log_response(session_id, response_data)
        
    except Exception as e:
        logger.error(f"Failed to log detailed metrics: {e}")