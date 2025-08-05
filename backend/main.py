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
from api import chat, config, health, admin, chat_stream, auth, preferences, cards

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
        # Initialize database first (for Railway PostgreSQL)
        logger.info("🗄️ Initializing database...")
        from services.auth_service import AuthService
        
        try:
            # Initialize auth service (this creates tables automatically)
            auth_service = AuthService()
            if auth_service.test_database_connection():
                logger.info("✅ Database initialized successfully")
            else:
                logger.warning("⚠️ Database connection test failed")
        except Exception as e:
            logger.error(f"❌ Database initialization error: {e}")
            # Continue startup anyway, so auth issues don't break the entire app
        
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
        
        if not gcp_project_id or not gcp_data_store_id:
            raise ValueError("Google Cloud project ID and data store ID are required")
        
        # Initialize services (Google-only)
        app_state["llm_service"] = LLMService(gemini_key)
        app_state["retriever_service"] = VertexRetriever(gcp_project_id, gcp_location, gcp_data_store_id)
        app_state["query_enhancer_service"] = QueryEnhancer()
        
        # Initialize query logger
        logging_config = LoggingConfig(
            enabled=os.getenv("ENABLE_QUERY_LOGGING", "true").lower() == "true",
            db_path=os.getenv("QUERY_LOG_DB_PATH", "logs/query_logs.db"),
            retention_days=int(os.getenv("LOG_RETENTION_DAYS", "90")),
            anonymize_after_days=int(os.getenv("ANONYMIZE_AFTER_DAYS", "30")),
            hash_salt=os.getenv("HASH_SALT_SECRET", "default-salt-change-in-production"),
            gdpr_compliance_mode=os.getenv("GDPR_COMPLIANCE_MODE", "true").lower() == "true"
        )
        app_state["query_logger"] = QueryLogger(logging_config)
        
        # Initialize auth service and database
        from services.auth_service import AuthService
        auth_service = AuthService()
        app_state["auth_service"] = auth_service
        
        # Initialize preference service
        from services.preference_service import PreferenceService
        preference_service = PreferenceService()
        app_state["preference_service"] = preference_service
        
        # Log appropriate database info based on type
        if auth_service.use_postgres:
            logger.info(f"🔑 Auth service initialized with PostgreSQL database")
            logger.info(f"🎯 Preference service initialized with PostgreSQL database")
        else:
            logger.info(f"🔑 Auth service initialized with SQLite database at: {auth_service.db_path}")
            logger.info(f"🎯 Preference service initialized with SQLite database")
        
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
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(chat_stream.router, prefix="/api", tags=["chat"])
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(preferences.router, prefix="/api", tags=["preferences"])
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