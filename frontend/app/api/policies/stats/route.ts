import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET() {
  try {
    // Get counts by status
    const statusStats = db.prepare(
      'SELECT status, COUNT(*) as count FROM policies GROUP BY status'
    ).all() as Array<{ status: string; count: number }>;

    // Get total count
    const totalCount = db.prepare(
      'SELECT COUNT(*) as count FROM policies'
    ).get() as { count: number };

    // Calculate compliance score
    const passingCount = statusStats.find(s => s.status === 'passing')?.count || 0;
    const failingCount = statusStats.find(s => s.status === 'failing')?.count || 0;
    const complianceScore = totalCount.count > 0 
      ? ((passingCount / totalCount.count) * 100).toFixed(1)
      : '0.0';

    return NextResponse.json({
      statusStats,
      totalCount: totalCount.count,
      passingCount,
      failingCount,
      complianceScore: parseFloat(complianceScore),
    });
  } catch (error) {
    console.error('Error fetching policy stats:', error);
    return NextResponse.json(
      { error: 'Failed to fetch policy stats' },
      { status: 500 }
    );
  }
}

