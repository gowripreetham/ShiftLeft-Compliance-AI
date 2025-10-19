import { NextRequest, NextResponse } from 'next/server'
import Database from 'better-sqlite3'

const db = new Database('compliance_memory.db')

export async function GET(request: NextRequest) {
  try {
    // For now, using a mock user ID. In production, get from NextAuth session
    const mockUserId = 'user-123' // TODO: Replace with actual user ID from session
    
    const findings = db.prepare(`
      SELECT id, summary, risk_level, timestamp
      FROM audit_log
      WHERE status = 'open'
      AND assignee_id = ?
      ORDER BY 
        CASE risk_level
          WHEN 'high' THEN 1
          WHEN 'medium' THEN 2
          WHEN 'low' THEN 3
          ELSE 4
        END,
        timestamp DESC
      LIMIT 5
    `).all(mockUserId)
    
    return NextResponse.json({ findings })
  } catch (error) {
    console.error('Error fetching my findings:', error)
    return NextResponse.json(
      { error: 'Failed to fetch findings' },
      { status: 500 }
    )
  }
}

