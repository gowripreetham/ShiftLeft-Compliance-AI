import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET() {
  try {
    // Risk Distribution
    const riskDistribution = db.prepare(`
      SELECT 
        risk_level,
        COUNT(*) as count
      FROM audit_log
      GROUP BY risk_level
    `).all();

    // Findings by Source
    const sourceDistribution = db.prepare(`
      SELECT 
        COALESCE(source, 'code') as source,
        COUNT(*) as count
      FROM audit_log
      GROUP BY source
    `).all();

    // Top Violating Controls
    const topControls = db.prepare(`
      SELECT 
        control_id,
        COUNT(*) as count,
        risk_level
      FROM audit_log
      WHERE control_id IS NOT NULL AND resolved = 0
      GROUP BY control_id, risk_level
      ORDER BY count DESC
      LIMIT 10
    `).all();

    // Resolution Rate
    const resolutionStats = db.prepare(`
      SELECT 
        resolved,
        COUNT(*) as count
      FROM audit_log
      GROUP BY resolved
    `).all();

    const totalFindings = resolutionStats.reduce((sum, stat) => sum + stat.count, 0);
    const resolvedFindings = resolutionStats.find(stat => stat.resolved === 1)?.count || 0;
    const resolutionRate = totalFindings > 0 ? Math.round((resolvedFindings / totalFindings) * 100) : 0;

    return NextResponse.json({
      riskDistribution,
      sourceDistribution,
      topControls,
      resolutionRate,
      totalFindings,
      resolvedFindings,
    });
  } catch (error) {
    console.error('Error fetching analytics:', error);
    return NextResponse.json(
      { error: 'Failed to fetch analytics' },
      { status: 500 }
    );
  }
}

