import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { TrendData } from '@/lib/types';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const riskLevel = searchParams.get('risk_level');

    let query = 'SELECT substr(timestamp, 1, 10) as day, COUNT(*) as count FROM audit_log';
    
    if (riskLevel) {
      query += ` WHERE risk_level = '${riskLevel}'`;
    }
    
    query += ' GROUP BY day ORDER BY day';

    const trends = db.prepare(query).all() as TrendData[];

    return NextResponse.json(trends);
  } catch (error) {
    console.error('Error fetching trends:', error);
    return NextResponse.json(
      { error: 'Failed to fetch trends' },
      { status: 500 }
    );
  }
}

