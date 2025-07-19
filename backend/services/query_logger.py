"""
Privacy-first Query Logger Service
Handles all query logging with GDPR compliance and security features
"""

import sqlite3
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pathlib import Path
import json

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
    """Privacy-first query logging service with GDPR compliance"""
    
    def __init__(self, config: LoggingConfig):
        self.config = config
        self.db_path = config.db_path
        self._ensure_db_directory()
        self._init_database()
        
    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
    def _init_database(self):
        """Initialize SQLite database with schema"""
        try:
            # Read schema from file
            schema_path = Path(__file__).parent.parent / "database" / "schemas" / "query_logs.sql"
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            # Execute schema
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema_sql)
                conn.commit()
                
            logger.info(f"Query logging database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize query logging database: {e}")
            raise
    
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
        return datetime.now() + timedelta(days=days)
    
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
            
            # Insert query log entry
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO query_logs (
                        session_id, query_text, enhanced_query, selected_model, 
                        query_mode, card_filter, top_k, response_status,
                        user_ip_hash, user_agent_hash, retention_expires_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    query_data.session_id,
                    query_data.query_text,
                    query_data.enhanced_query,
                    query_data.selected_model,
                    query_data.query_mode,
                    query_data.card_filter,
                    query_data.top_k,
                    0,  # Will be updated when response is logged
                    user_ip_hash,
                    user_agent_hash,
                    retention_expires_at
                ))
                conn.commit()
                
            logger.info(f"Query logged for session {query_data.session_id}")
            return query_data.session_id
            
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
            return query_data.session_id  # Don't break the main flow
    
    async def log_response(self, session_id: str, response_data: ResponseLogData):
        """Update query log with response metrics"""
        if not self.config.enabled:
            return
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE query_logs 
                    SET response_status = ?, execution_time_ms = ?, 
                        llm_tokens_used = ?, llm_cost = ?, search_results_count = ?
                    WHERE session_id = ?
                """, (
                    response_data.response_status,
                    response_data.execution_time_ms,
                    response_data.llm_tokens_used,
                    response_data.llm_cost,
                    response_data.search_results_count,
                    session_id
                ))
                conn.commit()
                
            # Update daily statistics with complete query information
            await self._update_daily_stats(session_id, response_data)
            
            logger.debug(f"Response logged for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to log response: {e}")
    
    async def _update_daily_stats(self, session_id: str, response_data: ResponseLogData):
        """Update daily aggregated statistics with detailed metrics"""
        try:
            today = datetime.now().date().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Get the complete query information for detailed stats
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM query_logs WHERE session_id = ?", (session_id,)
                )
                query_log = cursor.fetchone()
                
                if not query_log:
                    logger.warning(f"No query log found for session {session_id}")
                    return
                
                # Get current day's stats
                cursor = conn.execute(
                    "SELECT * FROM query_stats WHERE date = ?", (today,)
                )
                existing = cursor.fetchone()
                
                # Categorize the query for detailed stats
                model_used = query_log['selected_model']
                query_mode = query_log['query_mode']
                is_successful = response_data.response_status == 200
                
                # Model usage counters
                gemini_flash_increment = 1 if model_used == "gemini-1.5-flash" else 0
                gemini_pro_increment = 1 if model_used == "gemini-1.5-pro" else 0
                
                # Query type counters
                general_increment = 1 if query_mode == "General Query" else 0
                specific_card_increment = 1 if query_mode == "Specific Card" else 0
                comparison_increment = 1 if "compare" in query_log['query_text'].lower() else 0
                
                if existing:
                    # Update existing record with detailed metrics
                    conn.execute("""
                        UPDATE query_stats 
                        SET total_queries = total_queries + 1,
                            successful_queries = successful_queries + ?,
                            failed_queries = failed_queries + ?,
                            gemini_flash_queries = gemini_flash_queries + ?,
                            gemini_pro_queries = gemini_pro_queries + ?,
                            general_queries = general_queries + ?,
                            specific_card_queries = specific_card_queries + ?,
                            comparison_queries = comparison_queries + ?,
                            avg_execution_time_ms = CASE 
                                WHEN successful_queries > 0 THEN 
                                    ROUND((COALESCE(avg_execution_time_ms, 0) * successful_queries + ?) / (successful_queries + ?), 2)
                                ELSE ? 
                            END,
                            avg_tokens_used = CASE 
                                WHEN successful_queries > 0 THEN 
                                    ROUND((COALESCE(avg_tokens_used, 0) * successful_queries + ?) / (successful_queries + ?), 2)
                                ELSE ? 
                            END,
                            total_cost = ROUND(total_cost + ?, 6)
                        WHERE date = ?
                    """, (
                        1 if is_successful else 0,
                        1 if not is_successful else 0,
                        gemini_flash_increment,
                        gemini_pro_increment,
                        general_increment,
                        specific_card_increment,
                        comparison_increment,
                        response_data.execution_time_ms,
                        1 if is_successful else 0,
                        response_data.execution_time_ms,
                        response_data.llm_tokens_used,
                        1 if is_successful else 0,
                        response_data.llm_tokens_used,
                        response_data.llm_cost,
                        today
                    ))
                else:
                    # Create new record with detailed metrics
                    conn.execute("""
                        INSERT INTO query_stats (
                            date, total_queries, successful_queries, failed_queries,
                            gemini_flash_queries, gemini_pro_queries,
                            general_queries, specific_card_queries, comparison_queries,
                            avg_execution_time_ms, avg_tokens_used, total_cost
                        ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        today,
                        1 if is_successful else 0,
                        1 if not is_successful else 0,
                        gemini_flash_increment,
                        gemini_pro_increment,
                        general_increment,
                        specific_card_increment,
                        comparison_increment,
                        response_data.execution_time_ms if is_successful else None,
                        response_data.llm_tokens_used if is_successful else None,
                        response_data.llm_cost
                    ))
                    
                conn.commit()
                logger.debug(f"Daily stats updated for {today}: model={model_used}, mode={query_mode}, cost={response_data.llm_cost}")
                
        except Exception as e:
            logger.error(f"Failed to update daily stats: {e}")
    
    async def cleanup_expired_logs(self) -> Dict[str, int]:
        """GDPR compliance - cleanup expired logs"""
        if not self.config.gdpr_compliance_mode:
            return {"deleted": 0, "anonymized": 0}
            
        try:
            now = datetime.now()
            deleted_count = 0
            anonymized_count = 0
            
            with sqlite3.connect(self.db_path) as conn:
                # Delete fully expired logs
                cursor = conn.execute(
                    "DELETE FROM query_logs WHERE retention_expires_at < ?", (now,)
                )
                deleted_count = cursor.rowcount
                
                # Anonymize logs that should be anonymized but not deleted
                anonymize_before = now - timedelta(days=self.config.anonymize_after_days)
                cursor = conn.execute("""
                    UPDATE query_logs 
                    SET query_text = '[ANONYMIZED]', enhanced_query = '[ANONYMIZED]',
                        user_ip_hash = NULL, user_agent_hash = NULL, is_anonymized = 1
                    WHERE timestamp < ? AND is_anonymized = 0 AND retention_expires_at > ?
                """, (anonymize_before, now))
                anonymized_count = cursor.rowcount
                
                conn.commit()
                
            logger.info(f"Cleanup completed: {deleted_count} deleted, {anonymized_count} anonymized")
            return {"deleted": deleted_count, "anonymized": anonymized_count}
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired logs: {e}")
            return {"deleted": 0, "anonymized": 0}
    
    async def get_query_stats(self, days: int = 30) -> List[QueryStatsEntry]:
        """Get daily query statistics for analytics"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM query_stats 
                    WHERE date >= ? 
                    ORDER BY date DESC
                """, (start_date,))
                
                rows = cursor.fetchall()
                return [QueryStatsEntry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get query stats: {e}")
            return []
    
    async def export_training_data(self, request: ExportRequest) -> ExportResponse:
        """Export anonymized query data for training purposes"""
        try:
            export_id = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Build query conditions
            conditions = ["1=1"]  # Base condition
            params = []
            
            if request.anonymized_only:
                conditions.append("(is_anonymized = 1 OR query_text = '[ANONYMIZED]')")
                
            if request.start_date:
                conditions.append("date(timestamp) >= ?")
                params.append(request.start_date)
                
            if request.end_date:
                conditions.append("date(timestamp) <= ?")
                params.append(request.end_date)
                
            if not request.include_failed_queries:
                conditions.append("response_status = 200")
            
            query = f"""
                SELECT session_id, query_text, enhanced_query, selected_model,
                       query_mode, card_filter, response_status, execution_time_ms,
                       llm_tokens_used, llm_cost, search_results_count, timestamp
                FROM query_logs 
                WHERE {' AND '.join(conditions)}
                ORDER BY timestamp DESC
            """
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to list of dicts
                data = [dict(row) for row in rows]
                
                # Export to file
                export_dir = Path("exports")
                export_dir.mkdir(exist_ok=True)
                
                if request.format == "json":
                    file_path = export_dir / f"{export_id}.json"
                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=2, default=str)
                else:  # CSV
                    import csv
                    file_path = export_dir / f"{export_id}.csv"
                    if data:
                        with open(file_path, 'w', newline='') as f:
                            writer = csv.DictWriter(f, fieldnames=data[0].keys())
                            writer.writeheader()
                            writer.writerows(data)
                
                # Mark records as exported
                session_ids = [row['session_id'] for row in rows]
                if session_ids:
                    placeholders = ','.join(['?' for _ in session_ids])
                    conn.execute(f"""
                        UPDATE query_logs 
                        SET is_exported = 1 
                        WHERE session_id IN ({placeholders})
                    """, session_ids)
                    conn.commit()
                
                return ExportResponse(
                    export_id=export_id,
                    record_count=len(data),
                    file_path=str(file_path),
                    gist_url=None  # TODO: Implement Gist upload
                )
                
        except Exception as e:
            logger.error(f"Failed to export training data: {e}")
            raise
    
    async def get_session_data(self, session_id: str) -> Optional[QueryLogEntry]:
        """Get data for a specific session (for user data requests)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM query_logs WHERE session_id = ?", (session_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return QueryLogEntry(**dict(row))
                return None
                
        except Exception as e:
            logger.error(f"Failed to get session data: {e}")
            return None
    
    async def delete_session_data(self, session_id: str) -> bool:
        """Delete all data for a specific session (right to be forgotten)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM query_logs WHERE session_id = ?", (session_id,)
                )
                conn.commit()
                
                deleted = cursor.rowcount > 0
                if deleted:
                    logger.info(f"Deleted data for session {session_id}")
                return deleted
                
        except Exception as e:
            logger.error(f"Failed to delete session data: {e}")
            return False