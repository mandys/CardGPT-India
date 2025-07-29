#!/usr/bin/env python3
"""
Migration script to move data from SQLite to PostgreSQL
Run this script to migrate existing user data from auth.db to PostgreSQL
"""

import os
import sqlite3
import sys
from datetime import datetime
from urllib.parse import urlparse

import psycopg2
from psycopg2.extras import RealDictCursor

def get_database_config():
    """Get database configuration from environment"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable is required")
        sys.exit(1)
    
    url = urlparse(database_url)
    return {
        'host': url.hostname,
        'port': url.port or 5432,
        'database': url.path[1:],  # Remove leading '/'
        'user': url.username,
        'password': url.password,
    }

def connect_sqlite(db_path="auth.db"):
    """Connect to SQLite database"""
    if not os.path.exists(db_path):
        print(f"❌ SQLite database not found at: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        print(f"✅ Connected to SQLite: {db_path}")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to SQLite: {e}")
        return None

def connect_postgresql(db_config):
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**db_config)
        print(f"✅ Connected to PostgreSQL: {db_config['host']}")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return None

def migrate_users(sqlite_conn, postgres_conn):
    """Migrate users table"""
    print("\n🚀 Migrating users...")
    
    sqlite_cursor = sqlite_conn.cursor()
    postgres_cursor = postgres_conn.cursor(cursor_factory=RealDictCursor)
    
    # Get users from SQLite
    sqlite_cursor.execute("SELECT * FROM users")
    users = sqlite_cursor.fetchall()
    
    migrated_count = 0
    skipped_count = 0
    
    for user in users:
        try:
            # Check if user already exists in PostgreSQL
            postgres_cursor.execute(
                "SELECT id FROM users WHERE google_id = %s",
                (user['google_id'],)
            )
            existing = postgres_cursor.fetchone()
            
            if existing:
                print(f"⏭️  User already exists: {user['email']}")
                skipped_count += 1
                continue
            
            # Insert user into PostgreSQL
            postgres_cursor.execute("""
                INSERT INTO users (google_id, email, name, picture, created_at, last_login)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user['google_id'],
                user['email'],
                user['name'],
                user['picture'],
                user['created_at'],
                user['last_login']
            ))
            
            migrated_count += 1
            print(f"✅ Migrated user: {user['email']}")
            
        except Exception as e:
            print(f"❌ Failed to migrate user {user['email']}: {e}")
    
    postgres_conn.commit()
    print(f"\n📊 Users migration complete: {migrated_count} migrated, {skipped_count} skipped")
    return migrated_count

def migrate_daily_queries(sqlite_conn, postgres_conn):
    """Migrate daily_queries table"""
    print("\n🚀 Migrating daily queries...")
    
    sqlite_cursor = sqlite_conn.cursor()
    postgres_cursor = postgres_conn.cursor(cursor_factory=RealDictCursor)
    
    # Get daily queries from SQLite
    sqlite_cursor.execute("SELECT * FROM daily_queries")
    queries = sqlite_cursor.fetchall()
    
    migrated_count = 0
    skipped_count = 0
    
    for query in queries:
        try:
            # Check if query record already exists
            if query['user_id']:
                postgres_cursor.execute(
                    "SELECT id FROM daily_queries WHERE user_id = %s AND query_date = %s",
                    (query['user_id'], query['query_date'])
                )
            else:
                postgres_cursor.execute(
                    "SELECT id FROM daily_queries WHERE session_id = %s AND query_date = %s",
                    (query['session_id'], query['query_date'])
                )
            
            existing = postgres_cursor.fetchone()
            
            if existing:
                skipped_count += 1
                continue
            
            # Insert query record into PostgreSQL
            postgres_cursor.execute("""
                INSERT INTO daily_queries (user_id, session_id, query_date, count, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                query['user_id'],
                query['session_id'],
                query['query_date'],
                query['count'],
                query['created_at']
            ))
            
            migrated_count += 1
            
        except Exception as e:
            print(f"❌ Failed to migrate query record: {e}")
    
    postgres_conn.commit()
    print(f"📊 Daily queries migration complete: {migrated_count} migrated, {skipped_count} skipped")
    return migrated_count

def create_tables(postgres_conn):
    """Create PostgreSQL tables if they don't exist"""
    print("\n🏗️  Creating PostgreSQL tables...")
    
    cursor = postgres_conn.cursor()
    
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
    
    # Daily queries table
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
                WHEN duplicate_table THEN NULL;
            END;
            
            BEGIN
                ALTER TABLE daily_queries ADD CONSTRAINT unique_session_date 
                UNIQUE (session_id, query_date);
            EXCEPTION
                WHEN duplicate_table THEN NULL;
            END;
        END $$;
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_user_date ON daily_queries(user_id, query_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_session_date ON daily_queries(session_id, query_date)")
    
    postgres_conn.commit()
    print("✅ PostgreSQL tables created successfully")

def main():
    """Main migration function"""
    print("🔄 Starting SQLite to PostgreSQL migration...")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get database connections
    db_config = get_database_config()
    sqlite_conn = connect_sqlite()
    
    if not sqlite_conn:
        print("❌ Cannot proceed without SQLite connection")
        sys.exit(1)
    
    postgres_conn = connect_postgresql(db_config)
    if not postgres_conn:
        print("❌ Cannot proceed without PostgreSQL connection")
        sys.exit(1)
    
    try:
        # Create PostgreSQL tables
        create_tables(postgres_conn)
        
        # Migrate data
        users_migrated = migrate_users(sqlite_conn, postgres_conn)
        queries_migrated = migrate_daily_queries(sqlite_conn, postgres_conn)
        
        print("\n" + "=" * 50)
        print("✅ Migration completed successfully!")
        print(f"📊 Summary:")
        print(f"   • Users migrated: {users_migrated}")
        print(f"   • Query records migrated: {queries_migrated}")
        print("\n🔒 Security Recommendations:")
        print("   • Remove auth.db from your repository")
        print("   • Update .gitignore to exclude *.db files")
        print("   • Set secure JWT_SECRET in production")
        print("   • Configure GOOGLE_CLIENT_ID in environment")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
    
    finally:
        # Close connections
        if sqlite_conn:
            sqlite_conn.close()
        if postgres_conn:
            postgres_conn.close()
        print("\n🔌 Database connections closed")

if __name__ == "__main__":
    main()