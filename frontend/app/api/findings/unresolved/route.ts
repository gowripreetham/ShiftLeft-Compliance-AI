import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { AuditLog } from '@/lib/types';

export async function GET() {
  try {
    const findings = db.prepare(
      'SELECT * FROM audit_log WHERE resolved = 0 ORDER BY timestamp DESC'
    ).all() as AuditLog[];

    return NextResponse.json(findings);
  } catch (error) {
    console.error('Error fetching unresolved findings:', error);
    return NextResponse.json(
      { error: 'Failed to fetch unresolved findings' },
      { status: 500 }
    );
  }
}

