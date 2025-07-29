#!/usr/bin/env python3
"""
Database initialization script for Railway deployment
This runs automatically when the app starts to ensure PostgreSQL tables exist
"""

import os
import sys
import logging

# Add the backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.auth_service import AuthService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize PostgreSQL database tables"""
    try:
        logger.info("🚀 Starting database initialization...")
        
        # Check required environment variables
        required_vars = ["DATABASE_URL", "JWT_SECRET", "GOOGLE_CLIENT_ID"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            return False
        
        # Initialize auth service (this will create tables)
        auth_service = AuthService()
        
        # Test database connection
        if auth_service.test_database_connection():
            logger.info("✅ Database initialization completed successfully!")
            return True
        else:
            logger.error("❌ Database connection test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)