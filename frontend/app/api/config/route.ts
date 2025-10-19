import { NextResponse } from 'next/server';
import { Config } from '@/lib/types';

export async function GET() {
  try {
    const config: Config = {
      JIRA_BASE_URL: process.env.JIRA_BASE_URL || '',
      JIRA_PROJECT_KEY: process.env.JIRA_PROJECT_KEY || '',
      GITHUB_REPO: process.env.GITHUB_REPO || '',
      SLACK_CHANNEL_ID: process.env.SLACK_CHANNEL_ID || '',
    };

    return NextResponse.json(config);
  } catch (error) {
    console.error('Error fetching config:', error);
    return NextResponse.json(
      { error: 'Failed to fetch config' },
      { status: 500 }
    );
  }
}

