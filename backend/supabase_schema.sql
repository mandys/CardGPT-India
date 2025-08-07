-- CardGPT Supabase Database Schema
-- Run this SQL script in both your dev and production Supabase projects
-- Navigate to SQL Editor in Supabase Dashboard and execute this script

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User Preferences Table
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    travel_type VARCHAR(50),
    lounge_access VARCHAR(50),
    fee_willingness VARCHAR(50),
    current_cards TEXT[] DEFAULT '{}',
    preferred_banks TEXT[] DEFAULT '{}',
    spend_categories TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Session Preferences Table (for anonymous users)
CREATE TABLE IF NOT EXISTS session_preferences (
    session_id VARCHAR(255) PRIMARY KEY,
    preferences JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days')
);

-- User Query Counts Table (for rate limiting)
CREATE TABLE IF NOT EXISTS user_query_counts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    user_email VARCHAR(255),
    query_count INTEGER DEFAULT 0,
    last_reset_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Query Logs Table (for analytics and debugging)
CREATE TABLE IF NOT EXISTS query_logs (
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

-- Analytics Events Table (for tracking user behavior)
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    event_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Daily Query Statistics Table (for analytics dashboards)
CREATE TABLE IF NOT EXISTS daily_query_stats (
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
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_session_preferences_expires ON session_preferences(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_query_counts_user_id ON user_query_counts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_query_counts_reset_date ON user_query_counts(last_reset_date);
CREATE INDEX IF NOT EXISTS idx_query_logs_user_id ON query_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_session_id ON query_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_created_at ON query_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_query_logs_retention ON query_logs(retention_expires_at);
CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at ON analytics_events(created_at);
CREATE INDEX IF NOT EXISTS idx_daily_query_stats_date ON daily_query_stats(date);

-- Create updated_at trigger function for user preferences
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic updated_at
CREATE TRIGGER update_user_preferences_updated_at 
    BEFORE UPDATE ON user_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_query_counts_updated_at 
    BEFORE UPDATE ON user_query_counts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_query_counts ENABLE ROW LEVEL SECURITY;
ALTER TABLE query_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_query_stats ENABLE ROW LEVEL SECURITY;

-- Policies for service role access (allows full access for backend)
CREATE POLICY "Service role access" ON user_preferences 
    FOR ALL 
    TO service_role 
    USING (true) 
    WITH CHECK (true);

CREATE POLICY "Service role access" ON session_preferences 
    FOR ALL 
    TO service_role 
    USING (true) 
    WITH CHECK (true);

CREATE POLICY "Service role access" ON user_query_counts 
    FOR ALL 
    TO service_role 
    USING (true) 
    WITH CHECK (true);

CREATE POLICY "Service role access" ON query_logs 
    FOR ALL 
    TO service_role 
    USING (true) 
    WITH CHECK (true);

CREATE POLICY "Service role access" ON analytics_events 
    FOR ALL 
    TO service_role 
    USING (true) 
    WITH CHECK (true);

CREATE POLICY "Service role access" ON daily_query_stats 
    FOR ALL 
    TO service_role 
    USING (true) 
    WITH CHECK (true);

-- Optional: Add policies for authenticated users if needed
-- (Currently all access is through service role for backend operations)

-- Comments for documentation
COMMENT ON TABLE user_preferences IS 'User personalization settings and card preferences';
COMMENT ON TABLE session_preferences IS 'Anonymous session preferences with auto-expiry';
COMMENT ON TABLE user_query_counts IS 'Daily query count tracking for rate limiting';
COMMENT ON TABLE query_logs IS 'Complete query history with GDPR compliance and privacy features';
COMMENT ON TABLE analytics_events IS 'User behavior and system events tracking';
COMMENT ON TABLE daily_query_stats IS 'Aggregated daily query statistics for analytics dashboards';

-- Sample data verification (optional - remove if not needed)
-- SELECT 'Schema creation completed successfully' as status;
-- SELECT table_name, table_type FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;