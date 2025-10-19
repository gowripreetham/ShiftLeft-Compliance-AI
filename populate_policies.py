#!/usr/bin/env python3
"""
Populate policies table and create vector embeddings for semantic search.
Uses ChromaDB for vector storage and sentence-transformers for embeddings.
"""

import sqlite3
import csv
from pathlib import Path
import chromadb
from chromadb.config import Settings

# Database path
DB_PATH = Path(__file__).parent / 'compliance_memory.db'
CHROMA_DB_PATH = Path(__file__).parent / 'chroma_db'

def populate_policies():
    """Populate policies from CSV and create vector embeddings."""
    
    # Initialize ChromaDB
    print("🔧 Initializing ChromaDB...")
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    
    # Create or get collection
    collection = client.get_or_create_collection(
        name="policies",
        metadata={"description": "Compliance policy controls for semantic search"}
    )
    
    # Connect to SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Read policies from CSV
        policies_csv = Path(__file__).parent / 'policies.csv'
        if not policies_csv.exists():
            print(f"❌ policies.csv not found at {policies_csv}")
            return
        
        with open(policies_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            policies = list(reader)
        
        print(f"📖 Found {len(policies)} policies in CSV")
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for policy in policies:
            control_id = policy['control_id']
            framework = policy['framework']
            title = policy['title']
            description = policy['description']
            
            # Create document for embedding (title + description)
            doc = f"{title}. {description}"
            documents.append(doc)
            metadatas.append({
                "control_id": control_id,
                "framework": framework,
                "title": title
            })
            ids.append(control_id)
            
            # Insert into SQLite
            cursor.execute("""
                INSERT OR REPLACE INTO policies (control_id, framework, title, description, status)
                VALUES (?, ?, ?, ?, 'passing')
            """, (control_id, framework, title, description))
        
        # Add to ChromaDB
        print("🔄 Creating vector embeddings...")
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        conn.commit()
        print(f"✅ Inserted {len(policies)} policies into database")
        print(f"✅ Created {len(policies)} vector embeddings in ChromaDB")
        
        # Print summary
        cursor.execute("SELECT COUNT(*) FROM policies")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total policies in database: {count}")
        
        cursor.execute("SELECT framework, COUNT(*) FROM policies GROUP BY framework")
        frameworks = cursor.fetchall()
        print("\n📋 Policies by framework:")
        for framework, count in frameworks:
            print(f"   - {framework}: {count}")
        
        print("\n✅ Policy & Knowledge Layer initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

def search_policy(issue_description: str, top_k: int = 1):
    """
    Search for the most relevant policy control for a given issue.
    
    Args:
        issue_description: Description of the security issue
        top_k: Number of top results to return
    
    Returns:
        List of matching control IDs
    """
    try:
        client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
        collection = client.get_collection(name="policies")
        
        results = collection.query(
            query_texts=[issue_description],
            n_results=top_k
        )
        
        if results['ids'] and len(results['ids'][0]) > 0:
            return results['ids'][0]  # Return list of control IDs
        return []
    except Exception as e:
        print(f"❌ Error searching policies: {e}")
        return []

if __name__ == '__main__':
    print("🚀 Populating Policy & Knowledge Layer...\n")
    populate_policies()
    
    # Test search
    print("\n🔍 Testing semantic search...")
    test_query = "Hardcoded AWS credentials found in source code"
    matches = search_policy(test_query)
    if matches:
        print(f"   Query: '{test_query}'")
        print(f"   Best match: {matches[0]}")
    else:
        print("   No matches found")

