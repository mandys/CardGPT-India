"""
Privacy-first Query Logger Service - Supabase Version
Handles all query logging with GDPR compliance and security features using Supabase
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import json

from .supabase_service import SupabaseService

try:
    from logging_models.logging_models import (
        QueryLogData, ResponseLogData, QueryLogEntry, QueryStatsEntry,
        LoggingConfig, ExportRequest, ExportResponse
    )
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from logging_models.logging_models import (
        QueryLogData, ResponseLogData, QueryLogEntry, QueryStatsEntry,
        LoggingConfig, ExportRequest, ExportResponse
    )

logger = logging.getLogger(__name__)

class QueryLogger:
    """Privacy-first query logging service with GDPR compliance using Supabase"""
    
    def __init__(self, config: LoggingConfig, supabase_service: SupabaseService = None):
        self.config = config
        
        if supabase_service:
            self.db = supabase_service
        else:
            self.db = SupabaseService()
        
        logger.info("✅ QueryLogger initialized with Supabase backend")
        
    def _hash_pii(self, data: str) -> str:
        """Hash PII data with salt for privacy protection"""
        if not data:
            return ""
        
        # Combine data with salt and hash
        salted_data = f"{data}{self.config.hash_salt}"
        return hashlib.sha256(salted_data.encode()).hexdigest()
    
    def _calculate_retention_expiry(self, custom_days: Optional[int] = None) -> datetime:
        """Calculate when data should be deleted for GDPR compliance"""
        days = custom_days or self.config.retention_days
        return datetime.utcnow() + timedelta(days=days)
    
    async def log_query(self, query_data: QueryLogData) -> str:
        """
        Log a user query with privacy protections
        Returns the session_id for tracking the response
        """
        if not self.config.enabled:
            return query_data.session_id
            
        try:
            # Hash PII data for privacy
            user_ip_hash = self._hash_pii(query_data.user_ip) if query_data.user_ip else None
            user_agent_hash = self._hash_pii(query_data.user_agent) if query_data.user_agent else None
            
            # Calculate retention expiry
            retention_expires_at = self._calculate_retention_expiry()
            
            # Prepare log data
            log_data = {
                'session_id': query_data.session_id,
                'query_text': query_data.query_text,
                'enhanced_query': query_data.enhanced_query,
                'selected_model': query_data.selected_model,
                'query_mode': query_data.query_mode,
                'card_filter': query_data.card_filter,
                'top_k': query_data.top_k,
                'response_status': 0,  # Will be updated when response is logged
                'user_ip_hash': user_ip_hash,
                'user_agent_hash': user_agent_hash,
                'retention_expires_at': retention_expires_at.isoformat(),
                'query_metadata': {
                    'logged_at': datetime.utcnow().isoformat(),
                    'gdpr_compliant': self.config.gdpr_compliance_mode
                }
            }
            
            # Log to Supabase
            log_id = self.db.log_query(log_data)
            logger.info(f"Query logged for session {query_data.session_id} with ID {log_id}")
            
            return query_data.session_id
            
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
            return query_data.session_id  # Don't break the main flow
    
    async def log_response(self, session_id: str, response_data: ResponseLogData):
        """Update query log with response metrics"""
        if not self.config.enabled:
            return
            
        try:
            # Get existing query logs for this session
            query_logs = self.db.get_query_logs(limit=1)  # This will need to be filtered by session_id
            
            # For now, let's create a method to update query logs by session_id
            await self._update_query_response(session_id, response_data)
            
            # Update daily statistics with complete query information
            await self._update_daily_stats(session_id, response_data)
            
            logger.debug(f"Response logged for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to log response: {e}")
    
    async def _update_query_response(self, session_id: str, response_data: ResponseLogData):
        """Update the query log with response data using direct Supabase operations"""
        try:
            # We'll need to create a method in SupabaseService to update by session_id
            update_data = {
                'response_status': response_data.response_status,
                'execution_time_ms': response_data.execution_time_ms,
                'llm_tokens_used': response_data.llm_tokens_used,
                'llm_cost': float(response_data.llm_cost),
                'search_results_count': response_data.search_results_count
            }
            
            # Update query logs table where session_id matches
            result = self.db.client.table('query_logs').update(update_data).eq('session_id', session_id).execute()
            
            if result.data:
                logger.debug(f"Query response updated for session {session_id}")
            else:
                logger.warning(f"No query log found for session {session_id}")
                
        except Exception as e:
            logger.error(f"Failed to update query response: {e}")
    
    async def _update_daily_stats(self, session_id: str, response_data: ResponseLogData):
        """Update daily aggregated statistics with detailed metrics"""
        try:
            today = datetime.utcnow().date().isoformat()
            
            # Get the complete query information for detailed stats
            query_logs = self.db.client.table('query_logs').select('*').eq('session_id', session_id).execute()
            
            if not query_logs.data:
                logger.warning(f"No query log found for session {session_id}")
                return
                
            query_log = query_logs.data[0]
            
            # Categorize the query for detailed stats
            model_used = query_log.get('selected_model')
            query_mode = query_log.get('query_mode')
            is_successful = response_data.response_status == 200
            
            # Model usage counters
            gemini_flash_lite_increment = 1 if model_used == "gemini-2.5-flash-lite" else 0
            gemini_flash_increment = 1 if model_used == "gemini-1.5-flash" else 0
            gemini_pro_increment = 1 if model_used == "gemini-1.5-pro" else 0
            
            # Query type counters
            general_increment = 1 if query_mode == "General Query" else 0
            specific_card_increment = 1 if query_mode == "Specific Card" else 0
            comparison_increment = 1 if "compare" in query_log.get('query_text', '').lower() else 0
            
            # Check if stats exist for today
            existing_stats = self.db.client.table('daily_query_stats').select('*').eq('date', today).execute()
            
            if existing_stats.data:
                # Update existing record with detailed metrics
                existing = existing_stats.data[0]
                
                total_queries = existing['total_queries'] + 1
                successful_queries = existing['successful_queries'] + (1 if is_successful else 0)
                failed_queries = existing['failed_queries'] + (1 if not is_successful else 0)
                
                # Calculate new averages
                new_avg_execution_time = None
                new_avg_tokens = None
                
                if is_successful and successful_queries > 0:
                    current_avg_time = existing.get('avg_execution_time_ms', 0) or 0
                    new_avg_execution_time = round(
                        (current_avg_time * (successful_queries - 1) + response_data.execution_time_ms) / successful_queries, 2
                    )
                    
                    current_avg_tokens = existing.get('avg_tokens_used', 0) or 0
                    new_avg_tokens = round(
                        (current_avg_tokens * (successful_queries - 1) + response_data.llm_tokens_used) / successful_queries, 2
                    )
                else:
                    new_avg_execution_time = existing.get('avg_execution_time_ms')
                    new_avg_tokens = existing.get('avg_tokens_used')
                
                update_data = {
                    'total_queries': total_queries,
                    'successful_queries': successful_queries,
                    'failed_queries': failed_queries,
                    'gemini_flash_lite_queries': existing['gemini_flash_lite_queries'] + gemini_flash_lite_increment,
                    'gemini_flash_queries': existing['gemini_flash_queries'] + gemini_flash_increment,
                    'gemini_pro_queries': existing['gemini_pro_queries'] + gemini_pro_increment,
                    'general_queries': existing['general_queries'] + general_increment,
                    'specific_card_queries': existing['specific_card_queries'] + specific_card_increment,
                    'comparison_queries': existing['comparison_queries'] + comparison_increment,
                    'avg_execution_time_ms': new_avg_execution_time,
                    'avg_tokens_used': new_avg_tokens,
                    'total_cost': round(existing['total_cost'] + float(response_data.llm_cost), 6)
                }
                
                self.db.client.table('daily_query_stats').update(update_data).eq('date', today).execute()
                
            else:
                # Create new record with detailed metrics
                insert_data = {
                    'date': today,
                    'total_queries': 1,
                    'successful_queries': 1 if is_successful else 0,
                    'failed_queries': 1 if not is_successful else 0,
                    'gemini_flash_lite_queries': gemini_flash_lite_increment,
                    'gemini_flash_queries': gemini_flash_increment,
                    'gemini_pro_queries': gemini_pro_increment,
                    'general_queries': general_increment,
                    'specific_card_queries': specific_card_increment,
                    'comparison_queries': comparison_increment,
                    'avg_execution_time_ms': response_data.execution_time_ms if is_successful else None,
                    'avg_tokens_used': response_data.llm_tokens_used if is_successful else None,
                    'total_cost': float(response_data.llm_cost)
                }
                
                self.db.client.table('daily_query_stats').insert(insert_data).execute()
                    
            logger.debug(f"Daily stats updated for {today}: model={model_used}, mode={query_mode}, cost={response_data.llm_cost}")
                
        except Exception as e:
            logger.error(f"Failed to update daily stats: {e}")
    
    async def cleanup_expired_logs(self) -> Dict[str, int]:
        """GDPR compliance - cleanup expired logs"""
        if not self.config.gdpr_compliance_mode:
            return {"deleted": 0, "anonymized": 0}
            
        try:
            now = datetime.utcnow().isoformat()
            deleted_count = 0
            anonymized_count = 0
            
            # Delete fully expired logs
            deleted_result = self.db.client.table('query_logs').delete().lt('retention_expires_at', now).execute()
            deleted_count = len(deleted_result.data) if deleted_result.data else 0
            
            # Anonymize logs that should be anonymized but not deleted
            anonymize_before = (datetime.utcnow() - timedelta(days=self.config.anonymize_after_days)).isoformat()
            
            anonymize_data = {
                'query_text': '[ANONYMIZED]',
                'enhanced_query': '[ANONYMIZED]',
                'user_ip_hash': None,
                'user_agent_hash': None,
                'is_anonymized': True
            }
            
            anonymized_result = self.db.client.table('query_logs').update(anonymize_data).lt('created_at', anonymize_before).eq('is_anonymized', False).gt('retention_expires_at', now).execute()
            anonymized_count = len(anonymized_result.data) if anonymized_result.data else 0
            
            logger.info(f"Cleanup completed: {deleted_count} deleted, {anonymized_count} anonymized")
            return {"deleted": deleted_count, "anonymized": anonymized_count}
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired logs: {e}")
            return {"deleted": 0, "anonymized": 0}
    
    async def get_query_stats(self, days: int = 30) -> List[QueryStatsEntry]:
        """Get daily query statistics for analytics"""
        try:
            start_date = (datetime.utcnow() - timedelta(days=days)).date().isoformat()
            
            result = self.db.client.table('daily_query_stats').select('*').gte('date', start_date).order('date', desc=True).execute()
            
            if result.data:
                return [QueryStatsEntry(**row) for row in result.data]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get query stats: {e}")
            return []
    
    async def get_session_data(self, session_id: str) -> Optional[QueryLogEntry]:
        """Get data for a specific session (for user data requests)"""
        try:
            result = self.db.client.table('query_logs').select('*').eq('session_id', session_id).execute()
            
            if result.data:
                return QueryLogEntry(**result.data[0])
            return None
                
        except Exception as e:
            logger.error(f"Failed to get session data: {e}")
            return None
    
    async def delete_session_data(self, session_id: str) -> bool:
        """Delete all data for a specific session (right to be forgotten)"""
        try:
            result = self.db.client.table('query_logs').delete().eq('session_id', session_id).execute()
            
            deleted = len(result.data) > 0 if result.data else False
            if deleted:
                logger.info(f"Deleted data for session {session_id}")
            return deleted
                
        except Exception as e:
            logger.error(f"Failed to delete session data: {e}")
            return False
    
    async def export_training_data(self, request: ExportRequest) -> ExportResponse:
        """Export anonymized query data for training purposes"""
        try:
            export_id = f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Build query for Supabase
            query = self.db.client.table('query_logs').select(
                'id, session_id, query_text, enhanced_query, selected_model, query_mode, '
                'card_filter, response_status, execution_time_ms, llm_tokens_used, '
                'llm_cost, search_results_count, created_at'
            )
            
            # Apply filters
            if request.anonymized_only:
                query = query.eq('is_anonymized', True)
                
            if request.start_date:
                query = query.gte('created_at', f"{request.start_date}T00:00:00.000Z")
                
            if request.end_date:
                query = query.lte('created_at', f"{request.end_date}T23:59:59.999Z")
                
            if not request.include_failed_queries:
                query = query.eq('response_status', 200)
            
            result = query.order('created_at', desc=True).execute()
            data = result.data if result.data else []
            
            # Export to file (simplified - in production you might want to store in cloud storage)
            import tempfile
            import csv
            
            if request.format == "json":
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                json.dump(data, temp_file, indent=2, default=str)
                temp_file.close()
                file_path = temp_file.name
            else:  # CSV
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='')
                if data:
                    writer = csv.DictWriter(temp_file, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                temp_file.close()
                file_path = temp_file.name
            
            # Mark records as exported (optional)
            if data:
                session_ids = [row['session_id'] for row in data]
                self.db.client.table('query_logs').update({'is_exported': True}).in_('session_id', session_ids).execute()
            
            return ExportResponse(
                export_id=export_id,
                record_count=len(data),
                file_path=file_path,
                gist_url=None  # TODO: Implement cloud storage upload
            )
                
        except Exception as e:
            logger.error(f"Failed to export training data: {e}")
            raise