"""
FastAPI Backend for Credit Card Assistant
Modern REST API with CORS support for React frontend
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# Import our models and API routes
from models import HealthResponse, ErrorResponse, ConfigResponse, ModelInfo
from api import chat, config, health

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services will be initialized on startup
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    logger.info("🚀 Starting Credit Card Assistant API...")
    
    try:
        # Initialize services here
        from services.llm import LLMService
        from services.vertex_retriever import VertexRetriever
        from services.query_enhancer import QueryEnhancer
        
        # Get API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if not openai_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Get Google Cloud config
        gcp_project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT_ID")
        gcp_location = os.getenv("VERTEX_AI_LOCATION") or os.getenv("GCP_LOCATION", "global")
        gcp_data_store_id = os.getenv("VERTEX_AI_DATA_STORE_ID") or os.getenv("GCP_DATA_STORE_ID")
        
        if not gcp_project_id or not gcp_data_store_id:
            raise ValueError("Google Cloud project ID and data store ID are required")
        
        # Initialize services
        app_state["llm_service"] = LLMService(openai_key, gemini_key)
        app_state["retriever_service"] = VertexRetriever(gcp_project_id, gcp_location, gcp_data_store_id)
        app_state["query_enhancer_service"] = QueryEnhancer()
        
        logger.info("✅ All services initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {str(e)}")
        raise
    finally:
        logger.info("🔄 Shutting down services...")

# Create FastAPI app
app = FastAPI(
    title="Credit Card Assistant API",
    description="Modern REST API for querying Indian credit card terms and conditions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            code=str(exc.status_code)
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc)
        ).model_dump()
    )

# Dependency to get services
def get_services():
    """Dependency to get initialized services"""
    return app_state

# Include API routes
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(health.router, prefix="/api", tags=["health"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Credit Card Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )