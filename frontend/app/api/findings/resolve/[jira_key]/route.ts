import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function POST(
  request: Request,
  { params }: { params: { jira_key: string } }
) {
  try {
    const result = db.prepare(
      'UPDATE audit_log SET resolved = 1 WHERE jira_key = ?'
    ).run(params.jira_key);

    if (result.changes === 0) {
      return NextResponse.json(
        { error: 'Finding not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({ 
      success: true, 
      message: 'Finding marked as resolved' 
    });
  } catch (error) {
    console.error('Error resolving finding:', error);
    return NextResponse.json(
      { error: 'Failed to resolve finding' },
      { status: 500 }
    );
  }
}

