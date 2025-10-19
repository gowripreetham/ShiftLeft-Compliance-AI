# memory.py
import sqlite3
from datetime import datetime
from contextlib import contextmanager

DB_PATH = "compliance_memory.db"

# ---------------------------------------------------------------------
# Connection Helper
# ---------------------------------------------------------------------
@contextmanager
def get_connection():
    """Context manager for SQLite connections (auto-closes safely)."""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

# ---------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------
def init_db():
    """Initialize SQLite database and create table if not exists."""
    with get_connection() as conn:
        cursor = conn.cursor()
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
                control_id TEXT
            );
        """)
        conn.commit()
    print(f"🧠 SQLite memory initialized at {DB_PATH}")

# ---------------------------------------------------------------------
# Insert new finding
# ---------------------------------------------------------------------
def store_finding(summary: str, risk: str, jira_key: str = None, github_link: str = None, slack_link: str = None, control_id: str = None, source: str = 'code'):
    """Insert a new compliance finding into memory and update policy status."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_log (timestamp, summary, risk_level, jira_key, github_link, slack_link, control_id, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, summary, risk, jira_key, github_link, slack_link, control_id, source))
        
        # Update policy status to 'failing' if control_id is provided
        if control_id:
            cursor.execute("""
                UPDATE policies SET status = 'failing' WHERE control_id = ?
            """, (control_id,))
            print(f"🔴 Updated policy {control_id} to FAILING status")
        
        conn.commit()
    print(f"🧩 Stored finding in memory: {summary[:60]}... [{risk.upper()}] Control: {control_id or 'N/A'} Source: {source}")

# ---------------------------------------------------------------------
# Fetch latest findings
# ---------------------------------------------------------------------
def get_recent_findings(limit: int = 10):
    """Fetch the most recent compliance findings."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, summary, risk_level, jira_key, github_link, slack_link, resolved, control_id, source
            FROM audit_log ORDER BY id DESC LIMIT ?
        """, (limit,))
        results = cursor.fetchall()
    return results

# ---------------------------------------------------------------------
# Deduplication Check
# ---------------------------------------------------------------------
def finding_exists(summary: str, risk: str) -> bool:
    """Check if a similar finding (summary + risk) already exists and is unresolved."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM audit_log
            WHERE summary = ? AND risk_level = ? AND resolved = 0
        """, (summary, risk))
        result = cursor.fetchone()[0]
    if result > 0:
        print(f"⚠️ Duplicate finding detected — skipping new entry: {summary[:50]}...")
        return True
    return False

# ---------------------------------------------------------------------
# Mark Resolved
# ---------------------------------------------------------------------
def mark_resolved(jira_key: str):
    """Mark a finding as resolved using its Jira issue key and update policy status."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Get the control_id before marking as resolved
        cursor.execute("SELECT control_id FROM audit_log WHERE jira_key = ?", (jira_key,))
        result = cursor.fetchone()
        control_id = result[0] if result else None
        
        # Mark finding as resolved
        cursor.execute("""
            UPDATE audit_log SET resolved = 1 WHERE jira_key = ?
        """, (jira_key,))
        
        # Update policy status to 'passing' if no unresolved findings exist for this control
        if control_id:
            cursor.execute("""
                UPDATE policies
                SET status = 'passing'
                WHERE control_id = ?
                AND NOT EXISTS (
                    SELECT 1 FROM audit_log
                    WHERE control_id = ?
                    AND resolved = 0
                )
            """, (control_id, control_id))
            print(f"🟢 Updated policy {control_id} to PASSING status")
        
        conn.commit()
    print(f"✅ Marked finding resolved for Jira key: {jira_key}")

# ---------------------------------------------------------------------
# View unresolved items (for debugging)
# ---------------------------------------------------------------------
def list_unresolved():
    """List all unresolved findings."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, summary, risk_level, jira_key, control_id
            FROM audit_log WHERE resolved = 0
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
    if not rows:
        print("🎉 No unresolved findings in memory.")
    else:
        print("🧾 Unresolved findings:")
        for r in rows:
            print(f"  • [{r[3].upper()}] {r[2]} (Jira: {r[4] or 'N/A'}, Control: {r[5] or 'N/A'}) @ {r[1]}")
