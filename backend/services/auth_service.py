"""
Hybrid Authentication service for Google OAuth integration
Automatically detects environment and uses SQLite (local) or PostgreSQL (production)
Handles user sessions, JWT tokens, and query counting with persistent storage
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Union
from urllib.parse import urlparse

from jose import jwt
from google.auth.transport import requests
from google.oauth2 import id_token

# Try to import psycopg2 for PostgreSQL support (optional for local development)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2.pool import SimpleConnectionPool
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, database_url: str = None, jwt_secret: str = None):
        # Database configuration - auto-detect environment
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.use_postgres = self.database_url and self.database_url.startswith('postgres') and POSTGRES_AVAILABLE
        
        if self.use_postgres:
            logger.info("🗄️ Using PostgreSQL database for production environment")
            self._init_postgresql()
        else:
            logger.info("🗄️ Using SQLite database for local development")
            self._init_sqlite()
        
        # JWT configuration
        self.jwt_secret = jwt_secret or os.getenv("JWT_SECRET", "fallback-secret-change-in-production")
        if self.jwt_secret == "fallback-secret-change-in-production" and self.use_postgres:
            raise ValueError("JWT_SECRET environment variable must be set to a secure value in production")
        
        # Google OAuth configuration
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        if not self.google_client_id and self.use_postgres:
            raise ValueError("GOOGLE_CLIENT_ID environment variable is required in production")
        
        self.init_database()
    
    def _init_postgresql(self):
        """Initialize PostgreSQL configuration"""
        if not POSTGRES_AVAILABLE:
            raise ValueError("psycopg2 not installed - cannot use PostgreSQL")
        
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
    
    def _init_sqlite(self):
        """Initialize SQLite configuration"""
        self.db_path = os.getenv("AUTH_DB_PATH", "backend/auth.db")
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
    
    def get_connection(self):
        """Get database connection based on environment"""
        if self.use_postgres:
            return self.connection_pool.getconn()
        else:
            return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def return_connection(self, conn):
        """Return connection based on environment"""
        if self.use_postgres:
            self.connection_pool.putconn(conn)
        else:
            conn.close()
    
    def init_database(self):
        """Initialize database with required tables"""
        if self.use_postgres:
            self._init_postgresql_tables()
        else:
            self._init_sqlite_tables()
    
    def _init_postgresql_tables(self):
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
            logger.error(f"❌ PostgreSQL database initialization failed: {str(e)}")
            raise
    
    def _init_sqlite_tables(self):
        """Initialize SQLite database with required tables"""
        try:
            logger.info(f"🗄️ Initializing SQLite database at: {self.db_path}")
            
            conn = self.get_connection()
            try:
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
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
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
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                        UNIQUE(user_id, query_date),
                        UNIQUE(session_id, query_date)
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_user_date ON daily_queries(user_id, query_date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_session_date ON daily_queries(session_id, query_date)")
                
                conn.commit()
                logger.info("✅ SQLite database tables created successfully")
                
            finally:
                self.return_connection(conn)
                
        except Exception as e:
            logger.error(f"❌ SQLite database initialization failed: {str(e)}")
            raise
    
    def test_database_connection(self) -> bool:
        """Test if database is accessible and tables exist"""
        try:
            conn = self.get_connection()
            try:
                if self.use_postgres:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_name IN ('users', 'user_sessions', 'daily_queries')
                    """)
                    table_count = cursor.fetchone()[0]
                else:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT COUNT(*) FROM sqlite_master 
                        WHERE type='table' AND name IN ('users', 'user_sessions', 'daily_queries')
                    """)
                    table_count = cursor.fetchone()[0]
                
                logger.info(f"🗄️ Database connection test: {table_count} tables found ({self.database_type})")
                return table_count >= 3
            finally:
                self.return_connection(conn)
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {str(e)}")
            return False
    
    @property
    def database_type(self) -> str:
        """Get database type for logging"""
        return "PostgreSQL" if self.use_postgres else "SQLite"
    
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
            if self.use_postgres:
                return await self._create_or_get_user_postgres(conn, google_user_info)
            else:
                return await self._create_or_get_user_sqlite(conn, google_user_info)
        finally:
            self.return_connection(conn)
    
    async def _create_or_get_user_postgres(self, conn, google_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """PostgreSQL implementation of create_or_get_user"""
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
    
    async def _create_or_get_user_sqlite(self, conn, google_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """SQLite implementation of create_or_get_user"""
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
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if user_id:
                if self.use_postgres:
                    cursor.execute(
                        "SELECT count FROM daily_queries WHERE user_id = %s AND query_date = %s",
                        (user_id, today)
                    )
                else:
                    cursor.execute(
                        "SELECT count FROM daily_queries WHERE user_id = ? AND query_date = ?",
                        (user_id, today)
                    )
            else:
                if self.use_postgres:
                    cursor.execute(
                        "SELECT count FROM daily_queries WHERE session_id = %s AND query_date = %s",
                        (session_id, today)
                    )
                else:
                    cursor.execute(
                        "SELECT count FROM daily_queries WHERE session_id = ? AND query_date = ?",
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
            cursor = conn.cursor()
            if self.use_postgres:
                return await self._increment_query_count_postgres(conn, cursor, user_id, session_id, today)
            else:
                return await self._increment_query_count_sqlite(conn, cursor, user_id, session_id, today)
        finally:
            self.return_connection(conn)
    
    async def _increment_query_count_postgres(self, conn, cursor, user_id, session_id, today):
        """PostgreSQL implementation of increment_query_count"""
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
    
    async def _increment_query_count_sqlite(self, conn, cursor, user_id, session_id, today):
        """SQLite implementation of increment_query_count"""
        if user_id:
            # Check if record exists
            cursor.execute(
                "SELECT count FROM daily_queries WHERE user_id = ? AND query_date = ?",
                (user_id, today)
            )
            result = cursor.fetchone()
            
            if result:
                # Update existing record
                new_count = result[0] + 1
                cursor.execute(
                    "UPDATE daily_queries SET count = ? WHERE user_id = ? AND query_date = ?",
                    (new_count, user_id, today)
                )
            else:
                # Insert new record
                new_count = 1
                cursor.execute(
                    "INSERT INTO daily_queries (user_id, query_date, count) VALUES (?, ?, ?)",
                    (user_id, today, new_count)
                )
        else:
            # For guest users (session-based)
            cursor.execute(
                "SELECT count FROM daily_queries WHERE session_id = ? AND query_date = ?",
                (session_id, today)
            )
            result = cursor.fetchone()
            
            if result:
                # Update existing record
                new_count = result[0] + 1
                cursor.execute(
                    "UPDATE daily_queries SET count = ? WHERE session_id = ? AND query_date = ?",
                    (new_count, session_id, today)
                )
            else:
                # Insert new record
                new_count = 1
                cursor.execute(
                    "INSERT INTO daily_queries (session_id, query_date, count) VALUES (?, ?, ?)",
                    (session_id, today, new_count)
                )
        
        conn.commit()
        logger.info(f"✅ Query count updated to: {new_count}")
        return new_count
    
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
            if self.use_postgres:
                return await self._get_user_stats_postgres(conn, user_id)
            else:
                return await self._get_user_stats_sqlite(conn, user_id)
        finally:
            self.return_connection(conn)
    
    async def _get_user_stats_postgres(self, conn, user_id: int) -> Dict[str, Any]:
        """PostgreSQL implementation of get_user_stats"""
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
    
    async def _get_user_stats_sqlite(self, conn, user_id: int) -> Dict[str, Any]:
        """SQLite implementation of get_user_stats"""
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
        today_result = cursor.fetchone()
        today_queries = today_result[0] if today_result else 0
        
        # Handle datetime conversion for SQLite (stores as strings)
        def format_datetime(dt_value):
            if dt_value is None:
                return None
            if isinstance(dt_value, str):
                return dt_value  # Already a string
            return dt_value.isoformat()  # Convert datetime to string
        
        return {
            'user': {
                'id': user[0],
                'google_id': user[1],
                'email': user[2],
                'name': user[3],
                'picture': user[4],
                'created_at': format_datetime(user[5]),
                'last_login': format_datetime(user[6])
            },
            'stats': {
                'total_queries': total_queries,
                'today_queries': today_queries,
                'is_unlimited': True
            }
        }
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions (can be called periodically)"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if self.use_postgres:
                cursor.execute(
                    "DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP"
                )
            else:
                cursor.execute(
                    "DELETE FROM user_sessions WHERE expires_at < datetime('now')"
                )
            deleted_count = cursor.rowcount
            conn.commit()
            logger.info(f"🧹 Cleaned up {deleted_count} expired sessions")
            return deleted_count
        finally:
            self.return_connection(conn)
    
    def __del__(self):
        """Clean up connection pool on destruction"""
        if self.use_postgres and hasattr(self, 'connection_pool'):
            self.connection_pool.closeall()