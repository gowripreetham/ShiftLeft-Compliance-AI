import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET(
  request: Request,
  { params }: { params: { control_id: string } }
) {
  try {
    const policy = db.prepare(
      'SELECT * FROM policies WHERE control_id = ?'
    ).get(params.control_id);

    if (!policy) {
      return NextResponse.json(
        { error: 'Policy not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(policy);
  } catch (error) {
    console.error('Error fetching policy:', error);
    return NextResponse.json(
      { error: 'Failed to fetch policy' },
      { status: 500 }
    );
  }
}

