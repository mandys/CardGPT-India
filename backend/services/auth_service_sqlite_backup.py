"""
PostgreSQL-based Authentication service for Google OAuth integration
Handles user sessions, JWT tokens, and query counting with persistent storage
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from jose import jwt
from google.auth.transport import requests
from google.oauth2 import id_token

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, database_url: str = None, jwt_secret: str = None):
        # Database configuration
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Parse database URL for connection pool
        url = urlparse(self.database_url)
        self.db_config = {
            'host': url.hostname,
            'port': url.port or 5432,
            'database': url.path[1:],  # Remove leading '/'
            'user': url.username,
            'password': url.password,
        }
        
        # Connection pool for better performance
        try:
            self.connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **self.db_config
            )
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            # Fallback to direct connections if pool fails
            self.connection_pool = None
        
        # JWT configuration
        self.jwt_secret = jwt_secret or os.getenv("JWT_SECRET")
        if not self.jwt_secret or self.jwt_secret == "fallback-secret-change-in-production":
            raise ValueError("JWT_SECRET environment variable must be set to a secure value")
        
        # Google OAuth configuration
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID", "910315304252-im8oclg36n7dun7hjs2atkv8p2ln7ng7.apps.googleusercontent.com")
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            # Ensure directory exists for database file
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            logger.info(f"🗄️ Initializing database at: {self.db_path}")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    google_id TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    name TEXT,
                    picture TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Daily query counts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_id TEXT,
                    query_date DATE NOT NULL,
                    count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, query_date),
                    UNIQUE(session_id, query_date),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.commit()
            logger.info("✅ Database tables created successfully")
                
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            raise
    
    def test_database_connection(self) -> bool:
        """Test if database is accessible and tables exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                logger.info(f"🗄️ Database connection test: {table_count} tables found")
                return table_count >= 3  # We expect 3 tables: users, user_sessions, daily_queries
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {str(e)}")
            return False
    
    async def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth token and return user info"""
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                self.google_client_id
            )
            
            # Check if token is valid
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', '')
            }
            
        except ValueError as e:
            logger.error(f"Invalid Google token: {e}")
            return None
    
    async def create_or_get_user(self, google_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create user if doesn't exist, or update existing user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE google_id = ?", (google_user_info['google_id'],))
            user = cursor.fetchone()
            
            if user:
                # Update last login
                cursor.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE google_id = ?",
                    (google_user_info['google_id'],)
                )
                conn.commit()
                
                return {
                    'id': user[0],
                    'google_id': user[1],
                    'email': user[2],
                    'name': user[3],
                    'picture': user[4],
                    'created_at': user[5],
                    'last_login': datetime.now(timezone.utc).isoformat()
                }
            else:
                # Create new user
                cursor.execute("""
                    INSERT INTO users (google_id, email, name, picture)
                    VALUES (?, ?, ?, ?)
                """, (
                    google_user_info['google_id'],
                    google_user_info['email'],
                    google_user_info['name'],
                    google_user_info['picture']
                ))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                return {
                    'id': user_id,
                    'google_id': google_user_info['google_id'],
                    'email': google_user_info['email'],
                    'name': google_user_info['name'],
                    'picture': google_user_info['picture'],
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'last_login': datetime.now(timezone.utc).isoformat()
                }
    
    def create_jwt_token(self, user: Dict[str, Any]) -> str:
        """Create JWT token for authenticated user"""
        payload = {
            'user_id': user['id'],
            'google_id': user['google_id'],
            'email': user['email'],
            'exp': datetime.now(timezone.utc) + timedelta(days=30)  # 30 day expiry
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user info"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    async def get_daily_query_count(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> int:
        """Get today's query count for user or session"""
        today = datetime.now().date()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute(
                    "SELECT count FROM daily_queries WHERE user_id = ? AND query_date = ?",
                    (user_id, today)
                )
            else:
                cursor.execute(
                    "SELECT count FROM daily_queries WHERE session_id = ? AND query_date = ?",
                    (session_id, today)
                )
            
            result = cursor.fetchone()
            return result[0] if result else 0
    
    async def increment_query_count(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> int:
        """Increment daily query count and return new count"""
        today = datetime.now().date()
        logger.info(f"🚀 Incrementing query count for user_id={user_id}, session_id={session_id}, date={today}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if user_id:
                # For authenticated users
                cursor.execute("""
                    INSERT OR REPLACE INTO daily_queries (user_id, query_date, count)
                    VALUES (?, ?, COALESCE((SELECT count FROM daily_queries WHERE user_id = ? AND query_date = ?), 0) + 1)
                """, (user_id, today, user_id, today))
                
                cursor.execute(
                    "SELECT count FROM daily_queries WHERE user_id = ? AND query_date = ?",
                    (user_id, today)
                )
            else:
                # For guest users (session-based)
                cursor.execute("""
                    INSERT OR REPLACE INTO daily_queries (session_id, query_date, count)
                    VALUES (?, ?, COALESCE((SELECT count FROM daily_queries WHERE session_id = ? AND query_date = ?), 0) + 1)
                """, (session_id, today, session_id, today))
                
                cursor.execute(
                    "SELECT count FROM daily_queries WHERE session_id = ? AND query_date = ?",
                    (session_id, today)
                )
            
            conn.commit()
            result = cursor.fetchone()
            final_count = result[0] if result else 1
            logger.info(f"✅ Query count updated to: {final_count}")
            return final_count
    
    async def can_make_query(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> tuple[bool, int, int]:
        """
        Check if user/session can make a query
        Returns: (can_query, current_count, limit)
        """
        current_count = await self.get_daily_query_count(user_id, session_id)
        
        if user_id:
            # Authenticated users have unlimited queries
            return True, current_count, -1  # -1 means unlimited
        else:
            # Guest users have configurable query limit (default 5)
            limit = int(os.getenv('GUEST_DAILY_QUERY_LIMIT', '5'))
            return current_count < limit, current_count, limit
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get user info
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return {}
            
            # Get total queries
            cursor.execute(
                "SELECT SUM(count) FROM daily_queries WHERE user_id = ?",
                (user_id,)
            )
            total_queries = cursor.fetchone()[0] or 0
            
            # Get today's queries
            today = datetime.now().date()
            cursor.execute(
                "SELECT count FROM daily_queries WHERE user_id = ? AND query_date = ?",
                (user_id, today)
            )
            today_queries = cursor.fetchone()
            today_queries = today_queries[0] if today_queries else 0
            
            return {
                'user': {
                    'id': user[0],
                    'google_id': user[1],
                    'email': user[2],
                    'name': user[3],
                    'picture': user[4],
                    'created_at': user[5],
                    'last_login': user[6]
                },
                'stats': {
                    'total_queries': total_queries,
                    'today_queries': today_queries,
                    'is_unlimited': True
                }
            }