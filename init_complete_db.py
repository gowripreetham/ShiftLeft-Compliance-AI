#!/usr/bin/env python3
"""
Complete Database Initialization Script
Creates all tables with the correct schema for the full application.
"""

import sqlite3
from datetime import datetime

DB_PATH = "compliance_memory.db"

def init_complete_db():
    """Initialize the complete database with all required tables and columns."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create audit_log table with all columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                summary TEXT,
                risk_level TEXT,
                jira_key TEXT,
                github_link TEXT,
                slack_link TEXT,
                resolved INTEGER DEFAULT 0,
                control_id TEXT,
                source TEXT DEFAULT 'code',
                assignee_id TEXT,
                status TEXT DEFAULT 'open'
            );
        """)
        
        # Create policies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                control_id TEXT UNIQUE NOT NULL,
                framework TEXT,
                title TEXT,
                description TEXT,
                status TEXT DEFAULT 'passing'
            );
        """)
        
        conn.commit()
        print(f"✅ Database initialized successfully at {DB_PATH}")
        print(f"✅ Created tables: audit_log, policies")
        
        # Verify the schema
        cursor.execute("PRAGMA table_info(audit_log)")
        columns = cursor.fetchall()
        print(f"\n📋 audit_log columns:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        cursor.execute("PRAGMA table_info(policies)")
        columns = cursor.fetchall()
        print(f"\n📋 policies columns:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Initializing complete database schema...")
    init_complete_db()
    print("\n✅ Database initialization complete!")

