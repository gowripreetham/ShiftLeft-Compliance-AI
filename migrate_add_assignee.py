#!/usr/bin/env python3
"""
Migration script to add assignee_id and status columns to audit_log table.
"""
import sqlite3

DB_PATH = "compliance_memory.db"

def migrate():
    """Add assignee_id and status columns to audit_log table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Add assignee_id column if it doesn't exist
        cursor.execute("""
            ALTER TABLE audit_log 
            ADD COLUMN assignee_id TEXT
        """)
        print("✅ Added assignee_id column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  assignee_id column already exists")
        else:
            raise
    
    try:
        # Add status column if it doesn't exist
        cursor.execute("""
            ALTER TABLE audit_log 
            ADD COLUMN status TEXT DEFAULT 'open'
        """)
        print("✅ Added status column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  status column already exists")
        else:
            raise
    
    # Update existing records: set status to 'open' if not set
    cursor.execute("""
        UPDATE audit_log 
        SET status = 'open' 
        WHERE status IS NULL
    """)
    
    # Update existing records: set status to 'resolved' if resolved = 1
    cursor.execute("""
        UPDATE audit_log 
        SET status = 'resolved' 
        WHERE resolved = 1 AND status = 'open'
    """)
    
    conn.commit()
    conn.close()
    print("✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate()

