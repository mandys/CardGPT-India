"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from models import HealthResponse
from datetime import datetime

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    
    # Check service availability by accessing app state
    from main import app_state
    service_status = {}
    
    try:
        # Check if services are initialized in app_state
        if "llm_service" in app_state and app_state["llm_service"] is not None:
            service_status["llm"] = True
        else:
            service_status["llm"] = False
            
        if "retriever_service" in app_state and app_state["retriever_service"] is not None:
            service_status["retriever"] = True
        else:
            service_status["retriever"] = False
            
        if "query_enhancer_service" in app_state and app_state["query_enhancer_service"] is not None:
            service_status["query_enhancer"] = True
        else:
            service_status["query_enhancer"] = False
            
        # Overall status
        overall_status = "healthy" if all(service_status.values()) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(),
            services=service_status,
            version="1.0.0"
        )
        
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            services=service_status,
            version="1.0.0"
        )