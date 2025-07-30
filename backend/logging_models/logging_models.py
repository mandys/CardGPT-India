"""
Pydantic models for query logging system
Privacy-first design with GDPR compliance
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class QueryLogData(BaseModel):
    """Data to log when a query is initiated"""
    # Core Query Data
    query_text: str = Field(..., description="Original user query")
    enhanced_query: Optional[str] = Field(None, description="Enhanced query with card names/keywords")
    
    # Request Configuration  
    selected_model: str = Field(..., description="AI model selected (gemini-1.5-flash, etc.)")
    query_mode: str = Field(..., description="Query mode (General Query, Specific Card, etc.)")
    card_filter: Optional[str] = Field(None, description="Card filter if specified")
    top_k: int = Field(10, description="Number of search results requested")
    
    # User Context (will be hashed for privacy)
    user_ip: Optional[str] = Field(None, description="User IP address (will be hashed)")
    user_agent: Optional[str] = Field(None, description="User agent string (will be hashed)")
    
    # Session Management
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), description="Session UUID")

class ResponseLogData(BaseModel):
    """Data to log when a response is completed"""
    response_status: int = Field(..., description="HTTP status code")
    execution_time_ms: int = Field(..., description="Total execution time in milliseconds")
    llm_tokens_used: int = Field(0, description="Tokens consumed by LLM")
    llm_cost: float = Field(0.0, description="Cost in USD for LLM usage")
    search_results_count: int = Field(0, description="Number of documents retrieved")

class QueryLogEntry(BaseModel):
    """Complete query log entry for database storage"""
    id: Optional[int] = Field(None, description="Database ID")
    session_id: str = Field(..., description="Session UUID")
    query_text: str = Field(..., description="Original user query")
    enhanced_query: Optional[str] = Field(None, description="Enhanced query")
    
    # Request Configuration
    selected_model: str = Field(..., description="AI model used")
    query_mode: str = Field(..., description="Query mode")
    card_filter: Optional[str] = Field(None, description="Card filter")
    top_k: int = Field(7, description="Search results requested")
    
    # Response Metrics
    response_status: int = Field(..., description="HTTP status code")
    execution_time_ms: Optional[int] = Field(None, description="Execution time")
    llm_tokens_used: Optional[int] = Field(None, description="LLM tokens used")
    llm_cost: Optional[float] = Field(None, description="LLM cost")
    search_results_count: Optional[int] = Field(None, description="Search results count")
    
    # Privacy-Protected Data
    user_ip_hash: Optional[str] = Field(None, description="Hashed IP address")
    user_agent_hash: Optional[str] = Field(None, description="Hashed user agent")
    
    # Temporal and Privacy Data
    timestamp: datetime = Field(default_factory=datetime.now, description="When query was made")
    retention_expires_at: datetime = Field(..., description="When to delete for GDPR compliance")
    is_anonymized: bool = Field(False, description="Whether PII has been removed")
    is_exported: bool = Field(False, description="Whether included in training exports")
    
    class Config:
        from_attributes = True

class QueryStatsEntry(BaseModel):
    """Daily aggregated statistics (privacy-safe)"""
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    total_queries: int = Field(0, description="Total queries")
    successful_queries: int = Field(0, description="Successful queries (status 200)")
    failed_queries: int = Field(0, description="Failed queries")
    
    # Model Usage
    gemini_flash_queries: int = Field(0, description="Gemini Flash usage")
    gemini_pro_queries: int = Field(0, description="Gemini Pro usage")
    
    # Query Types
    general_queries: int = Field(0, description="General queries")
    specific_card_queries: int = Field(0, description="Specific card queries")
    comparison_queries: int = Field(0, description="Comparison queries")
    
    # Performance Metrics
    avg_execution_time_ms: Optional[float] = Field(None, description="Average execution time")
    avg_tokens_used: Optional[float] = Field(None, description="Average tokens used")
    total_cost: Optional[float] = Field(0.0, description="Total cost for the day")
    
    class Config:
        from_attributes = True

class LoggingConfig(BaseModel):
    """Configuration for query logging system"""
    enabled: bool = Field(True, description="Whether logging is enabled")
    db_path: str = Field("logs/query_logs.db", description="SQLite database path")
    retention_days: int = Field(90, description="Days to retain logs (GDPR compliance)")
    anonymize_after_days: int = Field(30, description="Days after which to anonymize data")
    hash_salt: str = Field(..., description="Salt for hashing PII")
    gdpr_compliance_mode: bool = Field(True, description="Enable strict GDPR compliance")

class ExportRequest(BaseModel):
    """Request for exporting training data"""
    format: str = Field("json", description="Export format (json, csv)")
    anonymized_only: bool = Field(True, description="Export only anonymized data")
    start_date: Optional[str] = Field(None, description="Start date filter (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date filter (YYYY-MM-DD)")
    include_failed_queries: bool = Field(False, description="Include failed queries")

class ExportResponse(BaseModel):
    """Response for export request"""
    export_id: str = Field(..., description="Unique export identifier")
    record_count: int = Field(..., description="Number of records exported")
    file_path: Optional[str] = Field(None, description="Path to exported file")
    gist_url: Optional[str] = Field(None, description="GitHub Gist URL if enabled")
    created_at: datetime = Field(default_factory=datetime.now, description="Export timestamp")

class PrivacySettings(BaseModel):
    """Privacy configuration for individual users/sessions"""
    session_id: str = Field(..., description="Session identifier")
    consent_given: bool = Field(False, description="Whether user gave consent for logging")
    data_retention_override: Optional[int] = Field(None, description="Custom retention period in days")
    anonymize_immediately: bool = Field(False, description="Anonymize data immediately")
    opt_out_of_exports: bool = Field(False, description="Exclude from training data exports")