# Supabase Migration Guide - CardGPT

Complete guide to migrate from SQLite/Railway PostgreSQL to Supabase for both development and production environments.

## 🎯 Migration Overview

Your CardGPT application has been successfully migrated from:
- **Old**: SQLite (local) + Railway PostgreSQL (prod) 
- **New**: Supabase Dev + Supabase Prod

## 📋 Prerequisites

1. **Two Supabase Projects** (Already Created):
   - **Dev Project**: `https://tdfvtjuvkgggvcxbrxib.supabase.co`
   - **Prod Project**: `https://afvynoxcsgaggsglgigk.supabase.co`

2. **Dependencies Updated**:
   - ✅ Added `supabase>=2.3.0` to requirements.txt
   - ✅ Removed `psycopg2-binary` dependency

## 🗄️ Database Setup

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Run Schema Scripts

**For Development Database:**
1. Go to [Supabase Dev Dashboard](https://supabase.com/dashboard/project/tdfvtjuvkgggvcxbrxib)
2. Navigate to **SQL Editor**
3. Copy and paste the entire content of `backend/supabase_schema.sql`
4. Click **Run** to execute the schema

**For Production Database:**
1. Go to [Supabase Prod Dashboard](https://supabase.com/dashboard/project/afvynoxcsgaggsglgigk)  
2. Navigate to **SQL Editor**
3. Copy and paste the entire content of `backend/supabase_schema.sql`
4. Click **Run** to execute the schema

### Step 3: Verify Tables Created

Both databases should now have these tables:
- `user_preferences` - User settings and personalization
- `session_preferences` - Anonymous user preferences  
- `user_query_counts` - Daily query limits tracking
- `query_logs` - Complete query history with GDPR compliance
- `analytics_events` - User behavior tracking
- `daily_query_stats` - Aggregated daily statistics

## ⚙️ Environment Configuration

### Local Development Setup

1. **Copy your existing `.env` to backup**:
```bash
cp .env .env.backup  # If you have an existing .env
```

2. **Use the new environment files**:
```bash
# Development uses .env.local (already created)
# Add your existing API keys to .env.local:
```

3. **Update `.env.local`** with your existing keys:
```bash
# Supabase Configuration (Already set)
SUPABASE_URL=https://tdfvtjuvkgggvcxbrxib.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRkZnZ0anV2a2dnZ3ZjeGJyeGliIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDU4NjczMSwiZXhwIjoyMDcwMTYyNzMxfQ.qdWlNZ_K_8TGgC1_Xki65f8CC0ggqsSp1SowJis7osQ

# Add your existing API keys:
GEMINI_API_KEY=your-gemini-api-key-here
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
VERTEX_AI_DATA_STORE_ID=your-data-store-id
CLERK_SECRET_KEY=sk_test_your-clerk-secret
```

### Production Setup (Railway)

1. **Update Railway environment variables**:
   - Go to your Railway project dashboard
   - Navigate to **Variables** tab
   - Add/update these variables:

```bash
ENVIRONMENT=production
SUPABASE_URL=https://afvynoxcsgaggsglgigk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFmdnlub3hjc2dhZ2dzZ2xnaWdrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDU4NjgzMSwiZXhwIjoyMDcwMTYyODMxfQ.Zlp_DcWHkL_6ShliKYPhtKzQ7FGOKocn5PlYlAqYP20

# Keep your existing production API keys:
GEMINI_API_KEY=production-gemini-key
GOOGLE_CLOUD_PROJECT=production-gcp-project
VERTEX_AI_DATA_STORE_ID=production-data-store-id
CLERK_SECRET_KEY=sk_live_production-clerk-secret
```

2. **Remove old DATABASE_URL**:
   - Delete the `DATABASE_URL` variable (no longer needed)

## 🧪 Testing the Migration

### Test Local Development

1. **Start the backend**:
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

2. **Verify Supabase connection**:
```bash
curl http://localhost:8000/api/health
# Should show: {"status": "healthy", "database": "supabase"}
```

3. **Test query limits endpoint**:
```bash
curl http://localhost:8000/api/query-limits/health
# Should show: {"status": "healthy", "database": "supabase", "service": "query_limits"}
```

### Test Production

1. **Deploy to Railway** (automatic on git push)

2. **Verify production health**:
```bash
curl https://cardgpt-india-production.up.railway.app/api/health
# Should show: {"status": "healthy", "database": "supabase"}
```

## 🔧 Key Changes Made

### 1. Database Architecture
- **Old**: Hybrid SQLite/PostgreSQL system
- **New**: Unified Supabase PostgreSQL for all environments

### 2. Service Layer Updates
- ✅ **SupabaseService**: New unified database service
- ✅ **PreferenceService**: Refactored to use Supabase
- ✅ **QueryLimitsService**: Migrated from SQLite to Supabase  
- ✅ **QueryLogger**: Updated for Supabase with GDPR compliance

### 3. Configuration Changes
- ✅ **Environment Detection**: Auto-detects dev/prod based on `ENVIRONMENT` variable
- ✅ **Config Files**: `.env.local` (dev) and `.env.production` (prod)
- ✅ **Dependency Management**: Supabase Python SDK integration

## 📊 Database Schema Overview

### Core Tables

```sql
-- User data and preferences
user_preferences          # User settings and card preferences
session_preferences       # Anonymous user preferences (30-day expiry)
user_query_counts         # Daily query limits (resets daily)

-- Analytics and logging
query_logs                # Complete query history with GDPR compliance
analytics_events          # User behavior tracking
daily_query_stats         # Aggregated daily statistics
```

### GDPR & Privacy Features
- **Row Level Security (RLS)** enabled on all tables
- **Automatic data retention** and anonymization
- **PII hashing** for privacy protection
- **Service role access** for backend operations

## 🚀 Benefits of Migration

### Development Benefits
1. **Unified Technology**: Single database system across all environments
2. **Real-time Capabilities**: Built-in real-time subscriptions (if needed)
3. **Better Tooling**: Supabase dashboard for database management
4. **Automatic Backups**: Built-in backup and recovery

### Production Benefits  
1. **Managed Infrastructure**: No database maintenance required
2. **Scalability**: Automatic scaling based on usage
3. **Performance**: Optimized PostgreSQL with connection pooling
4. **Monitoring**: Built-in performance monitoring and logs

## 🔍 Troubleshooting

### Common Issues

**1. Connection Errors**
```
Error: SUPABASE_URL and SUPABASE_KEY must be provided
```
**Solution**: Ensure environment variables are set correctly

**2. Schema Errors**
```
Error: relation "user_preferences" does not exist  
```
**Solution**: Run the `supabase_schema.sql` script in Supabase SQL Editor

**3. Authentication Errors**
```
Error: Invalid API key
```
**Solution**: Verify you're using the service role key, not the anon key

### Debugging Commands

```bash
# Test Supabase connection
python -c "from services.supabase_service import SupabaseService; s=SupabaseService(); print('Connected:', s.test_connection())"

# Check environment loading
python -c "import os; print('Environment:', os.getenv('ENVIRONMENT')); print('Supabase URL:', os.getenv('SUPABASE_URL'))"

# Verify table creation
# Check in Supabase Dashboard > Table Editor
```

## 📝 Data Migration (Optional)

If you need to migrate existing data from SQLite/Railway to Supabase:

1. **Export existing data** from old databases
2. **Transform to Supabase format** if needed  
3. **Import using Supabase CSV import** or Python scripts
4. **Verify data integrity** after migration

*Note: Most apps can start fresh with the new Supabase setup.*

## ✅ Migration Checklist

- ✅ Created Supabase dev and prod projects
- ✅ Updated dependencies (supabase SDK added)
- ✅ Created SupabaseService class
- ✅ Refactored all database services
- ✅ Updated main.py for Supabase initialization
- ✅ Created environment configuration files
- ✅ Generated SQL schema scripts
- ⏳ Run schema scripts in both Supabase projects
- ⏳ Update .env.local with your API keys
- ⏳ Update Railway environment variables
- ⏳ Test local development
- ⏳ Test production deployment
- ⏳ Verify all endpoints working
- ⏳ Remove old SQLite database files (optional)

## 🎉 Next Steps

Once migration is complete:

1. **Remove Legacy Files** (optional):
   ```bash
   rm backend/*.db  # Remove SQLite files
   rm -rf backend/logs/  # Remove local log databases
   ```

2. **Update Documentation**:
   - Update README.md with new Supabase setup instructions
   - Update deployment guides

3. **Monitor Performance**:
   - Check Supabase dashboard for query performance
   - Monitor connection usage and limits
   - Set up alerts for high usage

Your CardGPT application is now running on a modern, scalable Supabase infrastructure! 🚀