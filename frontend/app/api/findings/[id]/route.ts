import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { AuditLog } from '@/lib/types';

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const finding = db.prepare(
      'SELECT * FROM audit_log WHERE id = ?'
    ).get(params.id) as AuditLog | undefined;

    if (!finding) {
      return NextResponse.json(
        { error: 'Finding not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(finding);
  } catch (error) {
    console.error('Error fetching finding:', error);
    return NextResponse.json(
      { error: 'Failed to fetch finding' },
      { status: 500 }
    );
  }
}

