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
        self.connection_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            **self.db_config
        )
        
        # JWT configuration
        self.jwt_secret = jwt_secret or os.getenv("JWT_SECRET")
        if not self.jwt_secret or self.jwt_secret == "fallback-secret-change-in-production":
            raise ValueError("JWT_SECRET environment variable must be set to a secure value")
        
        # Google OAuth configuration
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        if not self.google_client_id:
            raise ValueError("GOOGLE_CLIENT_ID environment variable is required")
        
        self.init_database()
    
    def get_connection(self):
        """Get connection from pool"""
        return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        """Return connection to pool"""
        self.connection_pool.putconn(conn)
    
    def init_database(self):
        """Initialize PostgreSQL database with required tables"""
        try:
            logger.info(f"🗄️ Initializing PostgreSQL database")
            
            conn = self.get_connection()
            try:
                with conn.cursor() as cursor:
                    # Users table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            google_id VARCHAR(255) UNIQUE NOT NULL,
                            email VARCHAR(255) NOT NULL,
                            name VARCHAR(255),
                            picture TEXT,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            last_login TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # User sessions table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS user_sessions (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER NOT NULL,
                            token TEXT UNIQUE NOT NULL,
                            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                        )
                    """)
                    
                    # Daily query counts table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS daily_queries (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER,
                            session_id VARCHAR(255),
                            query_date DATE NOT NULL,
                            count INTEGER DEFAULT 0,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                        )
                    """)
                    
                    # Create unique constraints
                    cursor.execute("""
                        DO $$ BEGIN
                            BEGIN
                                ALTER TABLE daily_queries ADD CONSTRAINT unique_user_date 
                                UNIQUE (user_id, query_date);
                            EXCEPTION
                                WHEN duplicate_table THEN -- Constraint already exists
                            END;
                            
                            BEGIN
                                ALTER TABLE daily_queries ADD CONSTRAINT unique_session_date 
                                UNIQUE (session_id, query_date);
                            EXCEPTION
                                WHEN duplicate_table THEN -- Constraint already exists
                            END;
                        END $$;
                    """)
                    
                    # Create indexes for better performance
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_user_date ON daily_queries(user_id, query_date)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_session_date ON daily_queries(session_id, query_date)")
                    
                    conn.commit()
                    logger.info("✅ PostgreSQL database tables created successfully")
                    
            finally:
                self.return_connection(conn)
                
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            raise
    
    def test_database_connection(self) -> bool:
        """Test if database is accessible and tables exist"""
        try:
            conn = self.get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_name IN ('users', 'user_sessions', 'daily_queries')
                    """)
                    table_count = cursor.fetchone()[0]
                    logger.info(f"🗄️ Database connection test: {table_count} tables found")
                    return table_count >= 3
            finally:
                self.return_connection(conn)
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
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Check if user exists
                cursor.execute("SELECT * FROM users WHERE google_id = %s", (google_user_info['google_id'],))
                user = cursor.fetchone()
                
                if user:
                    # Update last login
                    cursor.execute(
                        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE google_id = %s",
                        (google_user_info['google_id'],)
                    )
                    conn.commit()
                    
                    return {
                        'id': user['id'],
                        'google_id': user['google_id'],
                        'email': user['email'],
                        'name': user['name'],
                        'picture': user['picture'],
                        'created_at': user['created_at'].isoformat(),
                        'last_login': datetime.now(timezone.utc).isoformat()
                    }
                else:
                    # Create new user
                    cursor.execute("""
                        INSERT INTO users (google_id, email, name, picture)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id, created_at
                    """, (
                        google_user_info['google_id'],
                        google_user_info['email'],
                        google_user_info['name'],
                        google_user_info['picture']
                    ))
                    
                    result = cursor.fetchone()
                    conn.commit()
                    
                    return {
                        'id': result['id'],
                        'google_id': google_user_info['google_id'],
                        'email': google_user_info['email'],
                        'name': google_user_info['name'],
                        'picture': google_user_info['picture'],
                        'created_at': result['created_at'].isoformat(),
                        'last_login': datetime.now(timezone.utc).isoformat()
                    }
        finally:
            self.return_connection(conn)
    
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
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                if user_id:
                    cursor.execute(
                        "SELECT count FROM daily_queries WHERE user_id = %s AND query_date = %s",
                        (user_id, today)
                    )
                else:
                    cursor.execute(
                        "SELECT count FROM daily_queries WHERE session_id = %s AND query_date = %s",
                        (session_id, today)
                    )
                
                result = cursor.fetchone()
                return result[0] if result else 0
        finally:
            self.return_connection(conn)
    
    async def increment_query_count(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> int:
        """Increment daily query count and return new count"""
        today = datetime.now().date()
        logger.info(f"🚀 Incrementing query count for user_id={user_id}, session_id={session_id}, date={today}")
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                if user_id:
                    # For authenticated users
                    cursor.execute("""
                        INSERT INTO daily_queries (user_id, query_date, count)
                        VALUES (%s, %s, 1)
                        ON CONFLICT (user_id, query_date)
                        DO UPDATE SET count = daily_queries.count + 1
                        RETURNING count
                    """, (user_id, today))
                else:
                    # For guest users (session-based)
                    cursor.execute("""
                        INSERT INTO daily_queries (session_id, query_date, count)
                        VALUES (%s, %s, 1)
                        ON CONFLICT (session_id, query_date)
                        DO UPDATE SET count = daily_queries.count + 1
                        RETURNING count
                    """, (session_id, today))
                
                result = cursor.fetchone()
                conn.commit()
                final_count = result[0] if result else 1
                logger.info(f"✅ Query count updated to: {final_count}")
                return final_count
        finally:
            self.return_connection(conn)
    
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
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get user info
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                
                if not user:
                    return {}
                
                # Get total queries
                cursor.execute(
                    "SELECT SUM(count) FROM daily_queries WHERE user_id = %s",
                    (user_id,)
                )
                total_queries = cursor.fetchone()[0] or 0
                
                # Get today's queries
                today = datetime.now().date()
                cursor.execute(
                    "SELECT count FROM daily_queries WHERE user_id = %s AND query_date = %s",
                    (user_id, today)
                )
                today_result = cursor.fetchone()
                today_queries = today_result[0] if today_result else 0
                
                return {
                    'user': {
                        'id': user['id'],
                        'google_id': user['google_id'],
                        'email': user['email'],
                        'name': user['name'],
                        'picture': user['picture'],
                        'created_at': user['created_at'].isoformat(),
                        'last_login': user['last_login'].isoformat()
                    },
                    'stats': {
                        'total_queries': total_queries,
                        'today_queries': today_queries,
                        'is_unlimited': True
                    }
                }
        finally:
            self.return_connection(conn)
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions (can be called periodically)"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP"
                )
                deleted_count = cursor.rowcount
                conn.commit()
                logger.info(f"🧹 Cleaned up {deleted_count} expired sessions")
                return deleted_count
        finally:
            self.return_connection(conn)
    
    def __del__(self):
        """Clean up connection pool on destruction"""
        if hasattr(self, 'connection_pool'):
            self.connection_pool.closeall()