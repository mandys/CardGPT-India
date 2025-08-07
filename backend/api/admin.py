"""
Admin API endpoints for query logging management
Provides access to logs, stats, and data exports
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging
import sys
sys.path.append('..')
from logging_models.logging_models import QueryStatsEntry, ExportRequest, ExportResponse

logger = logging.getLogger(__name__)

router = APIRouter()

def get_services():
    """Get services from app state"""
    from main import app_state
    return app_state

@router.get("/logs/stats", response_model=List[QueryStatsEntry])
async def get_query_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    services=Depends(get_services)
):
    """Get daily query statistics for analytics"""
    
    try:
        query_logger = services.get("query_logger")
        
        if not query_logger:
            raise HTTPException(status_code=503, detail="Query logger service not available")
        
        stats = await query_logger.get_query_stats(days=days)
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get query stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logs/export", response_model=ExportResponse)
async def export_training_data(
    request: ExportRequest,
    services=Depends(get_services)
):
    """Export query logs for training data analysis"""
    
    try:
        query_logger = services.get("query_logger")
        
        if not query_logger:
            raise HTTPException(status_code=503, detail="Query logger service not available")
        
        export_result = await query_logger.export_training_data(request)
        return export_result
        
    except Exception as e:
        logger.error(f"Failed to export training data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logs/cleanup")
async def cleanup_expired_logs(services=Depends(get_services)):
    """Manually trigger GDPR compliance cleanup"""
    
    try:
        query_logger = services.get("query_logger")
        
        if not query_logger:
            raise HTTPException(status_code=503, detail="Query logger service not available")
        
        if not query_logger.config.gdpr_compliance_mode:
            raise HTTPException(status_code=400, detail="GDPR compliance mode is disabled")
        
        cleanup_result = await query_logger.cleanup_expired_logs()
        
        return {
            "status": "success",
            "deleted_logs": cleanup_result["deleted"],
            "anonymized_logs": cleanup_result["anonymized"],
            "message": f"Cleanup completed: {cleanup_result['deleted']} deleted, {cleanup_result['anonymized']} anonymized"
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/session/{session_id}")
async def get_session_data(
    session_id: str,
    services=Depends(get_services)
):
    """Get data for a specific session (for user data requests)"""
    
    try:
        query_logger = services.get("query_logger")
        
        if not query_logger:
            raise HTTPException(status_code=503, detail="Query logger service not available")
        
        session_data = await query_logger.get_session_data(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/logs/session/{session_id}")
async def delete_session_data(
    session_id: str,
    services=Depends(get_services)
):
    """Delete all data for a specific session (right to be forgotten)"""
    
    try:
        query_logger = services.get("query_logger")
        
        if not query_logger:
            raise HTTPException(status_code=503, detail="Query logger service not available")
        
        deleted = await query_logger.delete_session_data(session_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "status": "success",
            "message": f"All data for session {session_id} has been deleted",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/config")
async def get_logging_config(services=Depends(get_services)):
    """Get current logging configuration"""
    
    try:
        query_logger = services.get("query_logger")
        
        if not query_logger:
            raise HTTPException(status_code=503, detail="Query logger service not available")
        
        config = query_logger.config
        
        # Return sanitized config (hide sensitive data)
        return {
            "enabled": config.enabled,
            "retention_days": config.retention_days,
            "anonymize_after_days": config.anonymize_after_days,
            "gdpr_compliance_mode": config.gdpr_compliance_mode,
            "database_type": "Supabase PostgreSQL"
        }
        
    except Exception as e:
        logger.error(f"Failed to get logging config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/recent")
async def get_recent_logs(
    limit: int = Query(10, ge=1, le=100, description="Number of recent logs to retrieve"),
    services=Depends(get_services)
):
    """Get recent query logs for quick viewing (GET endpoint for convenience)"""
    
    try:
        query_logger = services.get("query_logger")
        
        if not query_logger:
            raise HTTPException(status_code=503, detail="Query logger service not available")
        
        # Export recent logs
        from logging_models.logging_models import ExportRequest
        export_request = ExportRequest(
            format="json",
            anonymized_only=False,
            include_failed_queries=True
        )
        
        export_result = await query_logger.export_training_data(export_request)
        
        # Read the exported file and return the data directly
        import json
        with open(export_result.file_path, 'r') as f:
            all_data = json.load(f)
        
        # Return only the most recent entries
        recent_data = all_data[:limit]
        
        return {
            "logs": recent_data,
            "total_available": len(all_data),
            "showing": len(recent_data)
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/health")
async def check_logging_health(services=Depends(get_services)):
    """Check health status of logging system"""
    
    try:
        query_logger = services.get("query_logger")
        
        if not query_logger:
            return {
                "status": "unavailable",
                "enabled": False,
                "message": "Query logger service not available"
            }
        
        # Test database connection
        stats = await query_logger.get_query_stats(days=1)
        
        return {
            "status": "healthy",
            "enabled": query_logger.config.enabled,
            "gdpr_compliance": query_logger.config.gdpr_compliance_mode,
            "db_accessible": True,
            "recent_queries": len(stats),
            "message": "Logging system is operational"
        }
        
    except Exception as e:
        logger.error(f"Logging health check failed: {e}")
        return {
            "status": "error",
            "enabled": False,
            "db_accessible": False,
            "error": str(e),
            "message": "Logging system has issues"
        }