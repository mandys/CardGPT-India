-- Query Logs Schema Update - Run this in Supabase SQL Editor
-- This adds the missing columns to fix query logging issues

-- Drop existing query_logs table if it exists (to recreate with proper schema)
DROP TABLE IF EXISTS query_logs CASCADE;
DROP TABLE IF EXISTS daily_query_stats CASCADE;

-- Recreate Query Logs Table with complete schema
CREATE TABLE query_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255),
    session_id VARCHAR(255) NOT NULL,
    query_text TEXT NOT NULL,
    enhanced_query TEXT,
    selected_model VARCHAR(100),
    query_mode VARCHAR(100),
    card_filter VARCHAR(255),
    top_k INTEGER,
    response_status INTEGER DEFAULT 0,
    execution_time_ms INTEGER,
    llm_tokens_used INTEGER,
    llm_cost DECIMAL(10, 6),
    search_results_count INTEGER,
    user_ip_hash VARCHAR(255),
    user_agent_hash VARCHAR(255),
    retention_expires_at TIMESTAMP WITH TIME ZONE,
    is_anonymized BOOLEAN DEFAULT FALSE,
    is_exported BOOLEAN DEFAULT FALSE,
    query_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Daily Query Statistics Table
CREATE TABLE daily_query_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_queries INTEGER DEFAULT 0,
    successful_queries INTEGER DEFAULT 0,
    failed_queries INTEGER DEFAULT 0,
    gemini_flash_lite_queries INTEGER DEFAULT 0,
    gemini_flash_queries INTEGER DEFAULT 0,
    gemini_pro_queries INTEGER DEFAULT 0,
    general_queries INTEGER DEFAULT 0,
    specific_card_queries INTEGER DEFAULT 0,
    comparison_queries INTEGER DEFAULT 0,
    avg_execution_time_ms DECIMAL(10, 2),
    avg_tokens_used DECIMAL(10, 2),
    total_cost DECIMAL(10, 6) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_query_logs_session_id ON query_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_created_at ON query_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_query_logs_retention ON query_logs(retention_expires_at);
CREATE INDEX IF NOT EXISTS idx_daily_query_stats_date ON daily_query_stats(date);

-- Enable Row Level Security
ALTER TABLE query_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_query_stats ENABLE ROW LEVEL SECURITY;

-- Service role access policies
CREATE POLICY "Service role access" ON query_logs 
    FOR ALL 
    TO service_role 
    USING (true) 
    WITH CHECK (true);

CREATE POLICY "Service role access" ON daily_query_stats 
    FOR ALL 
    TO service_role 
    USING (true) 
    WITH CHECK (true);

-- Add comments
COMMENT ON TABLE query_logs IS 'Complete query history with GDPR compliance and privacy features';
COMMENT ON TABLE daily_query_stats IS 'Aggregated daily query statistics for analytics dashboards';

SELECT 'Query logging tables updated successfully' as status;