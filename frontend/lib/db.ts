import Database from 'better-sqlite3';
import path from 'path';

// Connect to the SQLite database
const dbPath = path.join(process.cwd(), '..', 'compliance_memory.db');
const db = new Database(dbPath);

// Enable foreign keys
db.pragma('foreign_keys = ON');

export { db };

