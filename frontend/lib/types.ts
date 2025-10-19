// TypeScript types for the Shift-Left Compliance Dashboard

export type RiskLevel = 'low' | 'medium' | 'high';

export interface AuditLog {
  id: number;
  timestamp: string;
  summary: string;
  risk_level: RiskLevel;
  jira_key: string | null;
  github_link: string | null;
  slack_link: string | null;
  resolved: number; // 0 = open, 1 = resolved
  control_id: string | null;
  source: 'code' | 'screenshot';
}

export interface Policy {
  id: number;
  control_id: string;
  framework: string;
  title: string;
  description: string;
  status: 'passing' | 'failing';
}

export interface PolicyStats {
  statusStats: Array<{ status: string; count: number }>;
  totalCount: number;
  passingCount: number;
  failingCount: number;
  complianceScore: number;
}

export interface FindingStats {
  risk_level: RiskLevel;
  count: number;
}

export interface DashboardStats {
  openFindings: number;
  resolvedFindings: number;
  highRisk: number;
  mediumRisk: number;
  lowRisk: number;
}

export interface TrendData {
  day: string;
  count: number;
}

export interface Config {
  JIRA_BASE_URL: string;
  JIRA_PROJECT_KEY: string;
  GITHUB_REPO: string;
  SLACK_CHANNEL_ID: string;
}

