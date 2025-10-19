#!/usr/bin/env python3
"""
Add source column to audit_log table for screenshot analysis.
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / 'compliance_memory.db'

def add_source_column():
    """Add source column to audit_log table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Add source column to audit_log if it doesn't exist
        try:
            cursor.execute("ALTER TABLE audit_log ADD COLUMN source TEXT DEFAULT 'code'")
            print("✅ Added source column to audit_log")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️  source column already exists in audit_log")
            else:
                raise
        
        conn.commit()
        print("\n✅ Database schema updated successfully!")
        
        # Print summary
        cursor.execute("SELECT COUNT(*) FROM audit_log WHERE source = 'code'")
        code_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM audit_log WHERE source = 'screenshot'")
        screenshot_count = cursor.fetchone()[0]
        
        print(f"📊 Findings by source:")
        print(f"   - Code: {code_count}")
        print(f"   - Screenshot: {screenshot_count}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("🚀 Adding screenshot source support to database...\n")
    add_source_column()

