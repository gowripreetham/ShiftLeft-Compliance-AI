import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { AuditLog } from '@/lib/types';

export async function GET() {
  try {
    const findings = db.prepare(
      'SELECT id, timestamp, summary, risk_level, jira_key, github_link, slack_link, resolved, control_id, source FROM audit_log ORDER BY id DESC'
    ).all() as AuditLog[];

    return NextResponse.json(findings);
  } catch (error) {
    console.error('Error fetching findings:', error);
    return NextResponse.json(
      { error: 'Failed to fetch findings' },
      { status: 500 }
    );
  }
}

