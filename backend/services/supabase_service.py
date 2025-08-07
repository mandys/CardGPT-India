"""
Supabase Service - Unified database operations for CardGPT
Handles all database operations using Supabase PostgreSQL
Supports automatic environment detection (dev/prod)
"""

import os
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize Supabase client with environment-based configuration
        
        Args:
            supabase_url: Override URL (if not provided, uses env vars)
            supabase_key: Override API key (if not provided, uses env vars)
        """
        # Get Supabase configuration from environment
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be provided via environment variables or parameters")
        
        try:
            # Create Supabase client
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            self.database_type = "supabase"
            
            logger.info(f"✅ Supabase client initialized for {self.environment} environment")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            # Simple query to test connection
            result = self.client.table('user_preferences').select('count', count='exact').execute()
            logger.info(f"🔗 Supabase connection test successful ({self.environment})")
            return True
        except Exception as e:
            logger.error(f"❌ Supabase connection test failed: {e}")
            return False
    
    # User Preferences Operations
    def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Save or update user preferences"""
        try:
            now = datetime.utcnow().isoformat()
            
            preference_data = {
                'user_id': user_id,
                'travel_type': preferences.get('travel_type'),
                'lounge_access': preferences.get('lounge_access'),
                'fee_willingness': preferences.get('fee_willingness'),
                'current_cards': preferences.get('current_cards', []),
                'preferred_banks': preferences.get('preferred_banks', []),
                'spend_categories': preferences.get('spend_categories', []),
                'updated_at': now
            }
            
            # Upsert user preferences
            result = self.client.table('user_preferences').upsert(
                preference_data,
                on_conflict='user_id'
            ).execute()
            
            if result.data:
                logger.info(f"✅ User preferences saved for user {user_id}")
                return result.data[0]
            else:
                raise Exception("No data returned from upsert operation")
                
        except Exception as e:
            logger.error(f"❌ Error saving user preferences: {e}")
            raise
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences by user_id"""
        try:
            result = self.client.table('user_preferences').select('*').eq('user_id', user_id).execute()
            
            if result.data:
                logger.info(f"✅ User preferences retrieved for user {user_id}")
                return result.data[0]
            else:
                logger.info(f"ℹ️ No preferences found for user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting user preferences: {e}")
            raise
    
    # Session Preferences Operations
    def save_session_preferences(self, session_id: str, preferences: Dict[str, Any], expires_at: datetime = None) -> str:
        """Save preferences for anonymous session"""
        try:
            if not expires_at:
                from datetime import timedelta
                expires_at = datetime.utcnow() + timedelta(days=30)
            
            session_data = {
                'session_id': session_id,
                'preferences': preferences,
                'expires_at': expires_at.isoformat(),
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.client.table('session_preferences').upsert(
                session_data,
                on_conflict='session_id'
            ).execute()
            
            if result.data:
                logger.info(f"✅ Session preferences saved for session {session_id}")
                return session_id
            else:
                raise Exception("No data returned from session preferences upsert")
                
        except Exception as e:
            logger.error(f"❌ Error saving session preferences: {e}")
            raise
    
    def get_session_preferences(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get preferences for anonymous session"""
        try:
            now = datetime.utcnow().isoformat()
            
            result = self.client.table('session_preferences').select('preferences').eq('session_id', session_id).gt('expires_at', now).execute()
            
            if result.data:
                logger.info(f"✅ Session preferences retrieved for session {session_id}")
                return result.data[0]['preferences']
            else:
                logger.info(f"ℹ️ No active session preferences found for {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting session preferences: {e}")
            raise
    
    # Query Limits Operations
    def get_user_query_count(self, user_id: str) -> tuple[int, datetime]:
        """Get user's current query count and last reset date"""
        try:
            today = datetime.utcnow().date().isoformat()
            
            result = self.client.table('user_query_counts').select('*').eq('user_id', user_id).execute()
            
            if result.data:
                record = result.data[0]
                query_count = record['query_count']
                last_reset_str = record.get('last_reset_date')
                
                if last_reset_str:
                    last_reset = datetime.fromisoformat(last_reset_str).date()
                    # Reset count if it's a new day
                    if last_reset.isoformat() < today:
                        query_count = 0
                        # Update the record with reset count
                        self.client.table('user_query_counts').update({
                            'query_count': 0,
                            'last_reset_date': today,
                            'updated_at': datetime.utcnow().isoformat()
                        }).eq('user_id', user_id).execute()
                        
                    return query_count, last_reset
                else:
                    return query_count, datetime.utcnow().date()
            else:
                return 0, datetime.utcnow().date()
                
        except Exception as e:
            logger.error(f"❌ Error getting user query count: {e}")
            return 0, datetime.utcnow().date()
    
    def increment_user_query_count(self, user_id: str, user_email: Optional[str] = None) -> int:
        """Increment user's query count and return new count"""
        try:
            today = datetime.utcnow().date().isoformat()
            now = datetime.utcnow().isoformat()
            
            # Get current count
            current_count, last_reset = self.get_user_query_count(user_id)
            
            # Reset if new day
            if last_reset.isoformat() < today:
                current_count = 0
            
            new_count = current_count + 1
            
            # Upsert user query count record
            query_data = {
                'user_id': user_id,
                'user_email': user_email,
                'query_count': new_count,
                'last_reset_date': today,
                'updated_at': now
            }
            
            result = self.client.table('user_query_counts').upsert(
                query_data,
                on_conflict='user_id'
            ).execute()
            
            if result.data:
                logger.info(f"✅ User query count incremented to {new_count} for user {user_id}")
                return new_count
            else:
                raise Exception("No data returned from query count upsert")
                
        except Exception as e:
            logger.error(f"❌ Error incrementing user query count: {e}")
            raise
    
    # Query Logging Operations
    def log_query(self, log_data: Dict[str, Any]) -> str:
        """Log a query with all metadata"""
        try:
            log_data['created_at'] = datetime.utcnow().isoformat()
            
            result = self.client.table('query_logs').insert(log_data).execute()
            
            if result.data:
                log_id = result.data[0]['id']
                logger.info(f"✅ Query logged with ID {log_id}")
                return log_id
            else:
                raise Exception("No data returned from query log insert")
                
        except Exception as e:
            logger.error(f"❌ Error logging query: {e}")
            raise
    
    def get_query_logs(self, user_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get query logs with optional filtering"""
        try:
            query = self.client.table('query_logs').select('*')
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            result = query.order('created_at', desc=True).limit(limit).execute()
            
            if result.data:
                logger.info(f"✅ Retrieved {len(result.data)} query logs")
                return result.data
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting query logs: {e}")
            raise
    
    # Analytics Operations
    def log_analytics_event(self, event_type: str, user_id: str = None, session_id: str = None, 
                           event_data: Dict[str, Any] = None) -> str:
        """Log analytics event"""
        try:
            analytics_data = {
                'event_type': event_type,
                'user_id': user_id,
                'session_id': session_id,
                'event_data': event_data,
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.client.table('analytics_events').insert(analytics_data).execute()
            
            if result.data:
                event_id = result.data[0]['id']
                logger.info(f"✅ Analytics event logged: {event_type}")
                return event_id
            else:
                raise Exception("No data returned from analytics insert")
                
        except Exception as e:
            logger.error(f"❌ Error logging analytics event: {e}")
            # Don't raise exception for analytics failures
            return None
    
    # Cleanup Operations
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired session preferences"""
        try:
            now = datetime.utcnow().isoformat()
            
            result = self.client.table('session_preferences').delete().lt('expires_at', now).execute()
            
            deleted_count = len(result.data) if result.data else 0
            
            if deleted_count > 0:
                logger.info(f"🧹 Cleaned up {deleted_count} expired session preferences")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up expired sessions: {e}")
            return 0