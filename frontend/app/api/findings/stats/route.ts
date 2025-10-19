import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { FindingStats, DashboardStats } from '@/lib/types';

export async function GET() {
  try {
    // Get counts by risk level
    const riskStats = db.prepare(
      'SELECT risk_level, COUNT(*) as count FROM audit_log GROUP BY risk_level'
    ).all() as FindingStats[];

    // Get open and resolved counts
    const openCount = db.prepare(
      'SELECT COUNT(*) as count FROM audit_log WHERE resolved = 0'
    ).get() as { count: number };

    const resolvedCount = db.prepare(
      'SELECT COUNT(*) as count FROM audit_log WHERE resolved = 1'
    ).get() as { count: number };

    // Get high, medium, low risk counts
    const highRisk = db.prepare(
      "SELECT COUNT(*) as count FROM audit_log WHERE risk_level = 'high'"
    ).get() as { count: number };

    const mediumRisk = db.prepare(
      "SELECT COUNT(*) as count FROM audit_log WHERE risk_level = 'medium'"
    ).get() as { count: number };

    const lowRisk = db.prepare(
      "SELECT COUNT(*) as count FROM audit_log WHERE risk_level = 'low'"
    ).get() as { count: number };

    const stats: DashboardStats = {
      openFindings: openCount.count,
      resolvedFindings: resolvedCount.count,
      highRisk: highRisk.count,
      mediumRisk: mediumRisk.count,
      lowRisk: lowRisk.count,
    };

    return NextResponse.json({ stats, riskStats });
  } catch (error) {
    console.error('Error fetching stats:', error);
    return NextResponse.json(
      { error: 'Failed to fetch stats' },
      { status: 500 }
    );
  }
}

