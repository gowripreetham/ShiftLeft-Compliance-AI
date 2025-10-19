import { NextRequest, NextResponse } from 'next/server'
import Database from 'better-sqlite3'

const db = new Database('compliance_memory.db')

export async function GET(request: NextRequest) {
  try {
    const findings = db.prepare(`
      SELECT id, summary, risk_level, timestamp
      FROM audit_log
      WHERE status = 'open'
      AND assignee_id IS NULL
      ORDER BY 
        CASE risk_level
          WHEN 'high' THEN 1
          WHEN 'medium' THEN 2
          WHEN 'low' THEN 3
          ELSE 4
        END,
        timestamp DESC
      LIMIT 5
    `).all()
    
    return NextResponse.json({ findings })
  } catch (error) {
    console.error('Error fetching triage findings:', error)
    return NextResponse.json(
      { error: 'Failed to fetch triage findings' },
      { status: 500 }
    )
  }
}

