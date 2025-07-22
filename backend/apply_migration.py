#!/usr/bin/env python3
"""
Apply database migration to add Gemini 2.5 Flash-Lite tracking
"""
import sqlite3
import os

def apply_migration():
    db_path = os.path.join(os.path.dirname(__file__), "data", "query_logs.db")
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Check if column already exists
            cursor = conn.execute("PRAGMA table_info(query_stats)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'gemini_flash_lite_queries' not in columns:
                print("Adding gemini_flash_lite_queries column...")
                conn.execute("ALTER TABLE query_stats ADD COLUMN gemini_flash_lite_queries INTEGER DEFAULT 0")
                print("✅ Migration applied successfully")
            else:
                print("✅ Column already exists, skipping migration")
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    apply_migration()