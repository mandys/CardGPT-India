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
from api import config, health, admin, chat_stream, preferences, cards, query_limits

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables based on environment
environment = os.getenv("ENVIRONMENT", "development")
if environment == "production":
    load_dotenv(".env.production")
    logger.info("🌐 Loaded production environment configuration")
else:
    load_dotenv(".env.local")
    logger.info("🔧 Loaded local development environment configuration")

# Global services will be initialized on startup
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    logger.info("🚀 Starting Credit Card Assistant API...")
    
    try:
        # Initialize Supabase database service
        logger.info("🗄️ Initializing Supabase database service...")
        from services.supabase_service import SupabaseService
        try:
            supabase_service = SupabaseService()
            # Test connection
            if supabase_service.test_connection():
                app_state["supabase_service"] = supabase_service
                logger.info("✅ Supabase service initialized successfully")
            else:
                raise Exception("Supabase connection test failed")
        except Exception as e:
            logger.error(f"❌ Supabase service initialization error: {e}")
            # Continue startup anyway, so database issues don't break the entire app
        
        # Initialize other services
        from services.llm import LLMService
        from services.vertex_retriever import VertexRetriever
        from services.query_enhancer import QueryEnhancer
        from services.query_logger import QueryLogger
        from logging_models.logging_models import LoggingConfig
        
        # Get Google API keys (Google-only architecture)
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Get Google Cloud config
        gcp_project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT_ID")
        gcp_location = os.getenv("VERTEX_AI_LOCATION") or os.getenv("GCP_LOCATION", "global")
        gcp_data_store_id = os.getenv("VERTEX_AI_DATA_STORE_ID") or os.getenv("GCP_DATA_STORE_ID")
        
        logger.info(f"🔧 Environment check - Supabase URL: {os.getenv('SUPABASE_URL')[:50]}..." if os.getenv('SUPABASE_URL') else "🔧 No SUPABASE_URL found")
        logger.info(f"🔧 Environment check - Supabase Key: {os.getenv('SUPABASE_KEY')[:20]}..." if os.getenv('SUPABASE_KEY') else "🔧 No SUPABASE_KEY found")
        
        if not gcp_project_id or not gcp_data_store_id:
            raise ValueError("Google Cloud project ID and data store ID are required")
        
        # Initialize services (Google-only)
        app_state["llm_service"] = LLMService(gemini_key)
        app_state["retriever_service"] = VertexRetriever(gcp_project_id, gcp_location, gcp_data_store_id)
        app_state["query_enhancer_service"] = QueryEnhancer()
        
        # Initialize query logger with Supabase
        logging_config = LoggingConfig(
            enabled=os.getenv("ENABLE_QUERY_LOGGING", "true").lower() == "true",
            db_path=os.getenv("QUERY_LOG_DB_PATH", "logs/query_logs.db"),  # Not used with Supabase
            retention_days=int(os.getenv("LOG_RETENTION_DAYS", "90")),
            anonymize_after_days=int(os.getenv("ANONYMIZE_AFTER_DAYS", "30")),
            hash_salt=os.getenv("HASH_SALT_SECRET", "default-salt-change-in-production"),
            gdpr_compliance_mode=os.getenv("GDPR_COMPLIANCE_MODE", "true").lower() == "true"
        )
        app_state["query_logger"] = QueryLogger(logging_config, app_state.get("supabase_service"))
        
        # Initialize preference service with Supabase
        from services.preference_service import PreferenceService
        preference_service = PreferenceService(app_state.get("supabase_service"))
        app_state["preference_service"] = preference_service
        
        logger.info(f"🎯 Preference service initialized with Supabase database")
        
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
# Allow production Vercel domains and local development
allowed_origins = [
    "http://localhost:3000", 
    "http://localhost:3001", 
    "http://localhost:5173",  # React dev servers
    "https://card-gpt-india.vercel.app",  # Correct Vercel domain (with hyphen)
    "https://cardgpt-india.vercel.app",   # Alternative domain
    "https://cardgpt-india-git-main-mandys.vercel.app",  # Git-specific domain
    "*"  # Allow all origins for now (can restrict later)
]

# Add environment-specific origins
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
# Chat router removed - using chat_stream.router instead
app.include_router(chat_stream.router, prefix="/api", tags=["chat"])
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(preferences.router, prefix="/api", tags=["preferences"])
app.include_router(query_limits.router, prefix="/api", tags=["query_limits"])
app.include_router(cards.router, tags=["cards"])

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