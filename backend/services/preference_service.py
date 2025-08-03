"""
User Preference Service for personalized credit card recommendations
Handles user preference storage, retrieval, and session management
Integrates with the hybrid database system (SQLite/PostgreSQL)
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from uuid import uuid4

from models import UserPreferences, UserPreferenceResponse

# Try to import psycopg2 for PostgreSQL support (optional for local development)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2.pool import SimpleConnectionPool
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger(__name__)

class PreferenceService:
    def __init__(self, database_url: str = None):
        # Database configuration - auto-detect environment like AuthService
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.use_postgres = self.database_url and self.database_url.startswith('postgres') and POSTGRES_AVAILABLE
        
        if self.use_postgres:
            logger.info("🎯 Using PostgreSQL for user preferences")
            self._init_postgresql()
        else:
            logger.info("🎯 Using SQLite for user preferences")
            self._init_sqlite()
    
    def _init_postgresql(self):
        """Initialize PostgreSQL connection for production"""
        try:
            self.pg_pool = SimpleConnectionPool(1, 10, self.database_url)
            self._create_postgres_tables()
            self.database_type = "postgresql"
            logger.info("✅ PostgreSQL preference service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize PostgreSQL preference service: {e}")
            raise
    
    def _init_sqlite(self):
        """Initialize SQLite connection for local development"""
        try:
            # Use the same directory as auth.db for consistency
            self.db_path = os.path.join(os.path.dirname(__file__), "..", "preferences.db")
            self._create_sqlite_tables()
            self.database_type = "sqlite"
            logger.info("✅ SQLite preference service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize SQLite preference service: {e}")
            raise
    
    def _create_postgres_tables(self):
        """Create PostgreSQL tables for user preferences"""
        with self.pg_pool.getconn() as conn:
            with conn.cursor() as cursor:
                # User preferences table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) UNIQUE NOT NULL,
                        travel_type VARCHAR(50),
                        lounge_access VARCHAR(50),
                        fee_willingness VARCHAR(50),
                        current_cards TEXT[],
                        preferred_banks TEXT[],
                        spend_categories TEXT[],
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Session preferences table for anonymous users
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS session_preferences (
                        session_id VARCHAR(255) PRIMARY KEY,
                        preferences JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '30 days')
                    );
                """)
                
                # Preference analytics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS preference_analytics (
                        id SERIAL PRIMARY KEY,
                        event_type VARCHAR(100) NOT NULL,
                        user_id VARCHAR(255),
                        session_id VARCHAR(255),
                        preference_data JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Create indexes for performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_preferences_expires ON session_preferences(expires_at);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON preference_analytics(created_at);")
                
                conn.commit()
            self.pg_pool.putconn(conn)
        
        logger.info("✅ PostgreSQL preference tables created/verified")
    
    def _create_sqlite_tables(self):
        """Create SQLite tables for user preferences"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    travel_type TEXT,
                    lounge_access TEXT,
                    fee_willingness TEXT,
                    current_cards TEXT,  -- JSON string
                    preferred_banks TEXT,  -- JSON string
                    spend_categories TEXT,  -- JSON string
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Session preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_preferences (
                    session_id TEXT PRIMARY KEY,
                    preferences TEXT NOT NULL,  -- JSON string
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT
                );
            """)
            
            # Preference analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preference_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    preference_data TEXT,  -- JSON string
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_preferences_expires ON session_preferences(expires_at);")
            
            conn.commit()
        
        logger.info("✅ SQLite preference tables created/verified")
    
    def save_user_preferences(self, user_id: str, preferences: UserPreferences) -> UserPreferenceResponse:
        """Save or update user preferences"""
        try:
            if self.use_postgres:
                return self._save_postgres_preferences(user_id, preferences)
            else:
                return self._save_sqlite_preferences(user_id, preferences)
        except Exception as e:
            logger.error(f"❌ Error saving preferences for user {user_id}: {e}")
            raise
    
    def _save_postgres_preferences(self, user_id: str, preferences: UserPreferences) -> UserPreferenceResponse:
        """Save preferences to PostgreSQL"""
        with self.pg_pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Upsert user preferences
                cursor.execute("""
                    INSERT INTO user_preferences (
                        user_id, travel_type, lounge_access, fee_willingness,
                        current_cards, preferred_banks, spend_categories, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) 
                    DO UPDATE SET
                        travel_type = EXCLUDED.travel_type,
                        lounge_access = EXCLUDED.lounge_access,
                        fee_willingness = EXCLUDED.fee_willingness,
                        current_cards = EXCLUDED.current_cards,
                        preferred_banks = EXCLUDED.preferred_banks,
                        spend_categories = EXCLUDED.spend_categories,
                        updated_at = EXCLUDED.updated_at
                    RETURNING *;
                """, (
                    user_id,
                    preferences.travel_type,
                    preferences.lounge_access,
                    preferences.fee_willingness,
                    preferences.current_cards or [],
                    preferences.preferred_banks or [],
                    preferences.spend_categories or [],
                    datetime.now(timezone.utc)
                ))
                
                result = cursor.fetchone()
                conn.commit()
            self.pg_pool.putconn(conn)
        
        # Log analytics event
        self._log_analytics_event("preference_updated", user_id=user_id, preference_data=preferences.model_dump())
        
        return self._format_preference_response(dict(result))
    
    def _save_sqlite_preferences(self, user_id: str, preferences: UserPreferences) -> UserPreferenceResponse:
        """Save preferences to SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # Check if user preferences exist
            cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing preferences
                cursor.execute("""
                    UPDATE user_preferences SET
                        travel_type = ?, lounge_access = ?, fee_willingness = ?,
                        current_cards = ?, preferred_banks = ?, spend_categories = ?,
                        updated_at = ?
                    WHERE user_id = ?
                """, (
                    preferences.travel_type,
                    preferences.lounge_access,
                    preferences.fee_willingness,
                    json.dumps(preferences.current_cards or []),
                    json.dumps(preferences.preferred_banks or []),
                    json.dumps(preferences.spend_categories or []),
                    now,
                    user_id
                ))
            else:
                # Insert new preferences
                cursor.execute("""
                    INSERT INTO user_preferences (
                        user_id, travel_type, lounge_access, fee_willingness,
                        current_cards, preferred_banks, spend_categories,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    preferences.travel_type,
                    preferences.lounge_access,
                    preferences.fee_willingness,
                    json.dumps(preferences.current_cards or []),
                    json.dumps(preferences.preferred_banks or []),
                    json.dumps(preferences.spend_categories or []),
                    now,
                    now
                ))
            
            # Get the saved preferences
            cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.commit()
        
        # Log analytics event
        self._log_analytics_event("preference_updated", user_id=user_id, preference_data=preferences.model_dump())
        
        return self._format_preference_response(dict(result))
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferenceResponse]:
        """Get user preferences by user_id"""
        try:
            if self.use_postgres:
                return self._get_postgres_preferences(user_id)
            else:
                return self._get_sqlite_preferences(user_id)
        except Exception as e:
            logger.error(f"❌ Error getting preferences for user {user_id}: {e}")
            return None
    
    def _get_postgres_preferences(self, user_id: str) -> Optional[UserPreferenceResponse]:
        """Get preferences from PostgreSQL"""
        with self.pg_pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM user_preferences WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
            self.pg_pool.putconn(conn)
        
        return self._format_preference_response(dict(result)) if result else None
    
    def _get_sqlite_preferences(self, user_id: str) -> Optional[UserPreferenceResponse]:
        """Get preferences from SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
        
        return self._format_preference_response(dict(result)) if result else None
    
    def save_session_preferences(self, session_id: str, preferences: UserPreferences) -> str:
        """Save preferences for anonymous session"""
        try:
            expires_at = datetime.now() + timedelta(days=30)
            
            if self.use_postgres:
                with self.pg_pool.getconn() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO session_preferences (session_id, preferences, expires_at)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (session_id)
                            DO UPDATE SET preferences = EXCLUDED.preferences, expires_at = EXCLUDED.expires_at
                        """, (session_id, json.dumps(preferences.model_dump()), expires_at))
                        conn.commit()
                    self.pg_pool.putconn(conn)
            else:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO session_preferences (session_id, preferences, expires_at)
                        VALUES (?, ?, ?)
                    """, (session_id, json.dumps(preferences.model_dump()), expires_at.isoformat()))
                    conn.commit()
            
            # Log analytics event
            self._log_analytics_event("session_preference_saved", session_id=session_id, preference_data=preferences.model_dump())
            
            return session_id
        except Exception as e:
            logger.error(f"❌ Error saving session preferences: {e}")
            raise
    
    def get_session_preferences(self, session_id: str) -> Optional[UserPreferences]:
        """Get preferences for anonymous session"""
        try:
            if self.use_postgres:
                with self.pg_pool.getconn() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                        cursor.execute("""
                            SELECT preferences FROM session_preferences 
                            WHERE session_id = %s AND expires_at > %s
                        """, (session_id, datetime.now()))
                        result = cursor.fetchone()
                    self.pg_pool.putconn(conn)
            else:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT preferences FROM session_preferences 
                        WHERE session_id = ? AND expires_at > ?
                    """, (session_id, datetime.now().isoformat()))
                    result = cursor.fetchone()
            
            if result:
                if self.use_postgres:
                    preferences_data = result['preferences']
                else:
                    preferences_data = json.loads(result[0])
                return UserPreferences(**preferences_data)
            
            return None
        except Exception as e:
            logger.error(f"❌ Error getting session preferences: {e}")
            return None
    
    def _format_preference_response(self, result: Dict) -> UserPreferenceResponse:
        """Format database result into UserPreferenceResponse"""
        # Handle JSON fields for SQLite
        if not self.use_postgres:
            result['current_cards'] = json.loads(result.get('current_cards', '[]'))
            result['preferred_banks'] = json.loads(result.get('preferred_banks', '[]'))
            result['spend_categories'] = json.loads(result.get('spend_categories', '[]'))
        
        preferences = UserPreferences(
            travel_type=result.get('travel_type'),
            lounge_access=result.get('lounge_access'),
            fee_willingness=result.get('fee_willingness'),
            current_cards=result.get('current_cards', []),
            preferred_banks=result.get('preferred_banks', []),
            spend_categories=result.get('spend_categories', [])
        )
        
        # Calculate completion status
        completion_status = {
            "travel_preferences": bool(preferences.travel_type and preferences.lounge_access),
            "financial_preferences": bool(preferences.fee_willingness),
            "card_preferences": bool(preferences.current_cards or preferences.preferred_banks),
            "spending_preferences": bool(preferences.spend_categories)
        }
        
        return UserPreferenceResponse(
            user_id=result['user_id'],
            preferences=preferences,
            completion_status=completion_status,
            created_at=result['created_at'],
            updated_at=result['updated_at']
        )
    
    def _log_analytics_event(self, event_type: str, user_id: str = None, session_id: str = None, preference_data: Dict = None):
        """Log analytics event for preference usage"""
        try:
            now = datetime.now()
            
            if self.use_postgres:
                with self.pg_pool.getconn() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO preference_analytics (event_type, user_id, session_id, preference_data)
                            VALUES (%s, %s, %s, %s)
                        """, (event_type, user_id, session_id, json.dumps(preference_data) if preference_data else None))
                        conn.commit()
                    self.pg_pool.putconn(conn)
            else:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO preference_analytics (event_type, user_id, session_id, preference_data, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (event_type, user_id, session_id, json.dumps(preference_data) if preference_data else None, now.isoformat()))
                    conn.commit()
        except Exception as e:
            # Don't fail the main operation if analytics logging fails
            logger.warning(f"⚠️ Failed to log analytics event: {e}")
    
    def cleanup_expired_sessions(self):
        """Clean up expired session preferences"""
        try:
            if self.use_postgres:
                with self.pg_pool.getconn() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("DELETE FROM session_preferences WHERE expires_at < %s", (datetime.now(),))
                        deleted_count = cursor.rowcount
                        conn.commit()
                    self.pg_pool.putconn(conn)
            else:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM session_preferences WHERE expires_at < ?", (datetime.now().isoformat(),))
                    deleted_count = cursor.rowcount
                    conn.commit()
            
            if deleted_count > 0:
                logger.info(f"🧹 Cleaned up {deleted_count} expired session preferences")
        except Exception as e:
            logger.error(f"❌ Error cleaning up expired sessions: {e}")
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID for anonymous users"""
        return f"session_{uuid4().hex[:16]}"