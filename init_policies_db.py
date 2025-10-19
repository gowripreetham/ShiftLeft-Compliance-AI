#!/usr/bin/env python3
"""
Initialize the policies table and modify audit_log table for Policy & Knowledge Layer.
"""

import sqlite3
import csv
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / 'compliance_memory.db'

def init_database():
    """Initialize the database with policies table and modify audit_log."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create policies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                control_id TEXT NOT NULL UNIQUE,
                framework TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'passing'
            )
        """)
        print("✅ Created policies table")
        
        # Add control_id column to audit_log if it doesn't exist
        try:
            cursor.execute("ALTER TABLE audit_log ADD COLUMN control_id TEXT")
            print("✅ Added control_id column to audit_log")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️  control_id column already exists in audit_log")
            else:
                raise
        
        # Populate policies table from CSV
        policies_csv = Path(__file__).parent / 'policies.csv'
        if policies_csv.exists():
            with open(policies_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                policies = list(reader)
            
            for policy in policies:
                cursor.execute("""
                    INSERT OR IGNORE INTO policies (control_id, framework, title, description, status)
                    VALUES (?, ?, ?, ?, 'passing')
                """, (
                    policy['control_id'],
                    policy['framework'],
                    policy['title'],
                    policy['description']
                ))
            
            print(f"✅ Inserted {len(policies)} policies from CSV")
        else:
            print(f"⚠️  policies.csv not found at {policies_csv}")
        
        conn.commit()
        print("\n✅ Database initialization complete!")
        
        # Print summary
        cursor.execute("SELECT COUNT(*) FROM policies")
        count = cursor.fetchone()[0]
        print(f"📊 Total policies in database: {count}")
        
        cursor.execute("SELECT framework, COUNT(*) FROM policies GROUP BY framework")
        frameworks = cursor.fetchall()
        print("\n📋 Policies by framework:")
        for framework, count in frameworks:
            print(f"   - {framework}: {count}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("🚀 Initializing Policy & Knowledge Layer database...\n")
    init_database()

