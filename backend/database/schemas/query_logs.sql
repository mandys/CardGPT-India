-- Query Logs Database Schema
-- Privacy-first design with GDPR compliance

CREATE TABLE IF NOT EXISTS query_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Session and Query Data
    session_id VARCHAR(36) NOT NULL,         -- Anonymous session tracking (UUID4)
    query_text TEXT NOT NULL,               -- Original user query
    enhanced_query TEXT,                    -- Our enhanced version with card names/keywords
    
    -- Request Configuration
    selected_model VARCHAR(50) NOT NULL,    -- gemini-1.5-flash, gemini-1.5-pro, etc.
    query_mode VARCHAR(50) NOT NULL,        -- General Query, Specific Card, Compare Cards
    card_filter VARCHAR(100),               -- Card filter if specified
    top_k INTEGER DEFAULT 7,                -- Number of search results requested
    
    -- Response Metrics
    response_status INTEGER NOT NULL,        -- HTTP status code (200, 400, 500, etc.)
    execution_time_ms INTEGER,              -- Total request processing time
    llm_tokens_used INTEGER,                -- Tokens consumed by LLM
    llm_cost DECIMAL(10,6),                 -- Cost in USD for LLM usage
    search_results_count INTEGER,           -- Number of documents retrieved
    
    -- Privacy-Protected User Data (Hashed)
    user_ip_hash VARCHAR(64),               -- SHA-256 hash of IP address
    user_agent_hash VARCHAR(64),            -- SHA-256 hash of user agent
    
    -- Temporal Data
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    retention_expires_at DATETIME NOT NULL, -- GDPR compliance - auto-delete after this date
    
    -- Privacy Flags
    is_anonymized BOOLEAN DEFAULT 0,        -- Whether PII has been stripped
    is_exported BOOLEAN DEFAULT 0           -- Whether included in training data exports
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_query_logs_timestamp ON query_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_query_logs_session ON query_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_retention ON query_logs(retention_expires_at);
CREATE INDEX IF NOT EXISTS idx_query_logs_model ON query_logs(selected_model);
CREATE INDEX IF NOT EXISTS idx_query_logs_status ON query_logs(response_status);

-- Index for cleanup operations
CREATE INDEX IF NOT EXISTS idx_query_logs_cleanup ON query_logs(retention_expires_at, is_anonymized);

-- Statistics table for aggregated analytics (privacy-safe)
CREATE TABLE IF NOT EXISTS query_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    
    -- Daily Aggregates
    total_queries INTEGER DEFAULT 0,
    successful_queries INTEGER DEFAULT 0,
    failed_queries INTEGER DEFAULT 0,
    
    -- Model Usage
    gemini_flash_queries INTEGER DEFAULT 0,
    gemini_pro_queries INTEGER DEFAULT 0,
    
    -- Query Types
    general_queries INTEGER DEFAULT 0,
    specific_card_queries INTEGER DEFAULT 0,
    comparison_queries INTEGER DEFAULT 0,
    
    -- Performance Metrics
    avg_execution_time_ms REAL,
    avg_tokens_used REAL,
    total_cost DECIMAL(10,6),
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(date)  -- One record per day
);

CREATE INDEX IF NOT EXISTS idx_query_stats_date ON query_stats(date);