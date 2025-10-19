import { NextRequest, NextResponse } from 'next/server'
import Database from 'better-sqlite3'
import fs from 'fs'
import path from 'path'

const dbPath = path.join(process.cwd(), '..', 'compliance_memory.db')
const db = new Database(dbPath)

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const findingId = params.id

    // Fetch the finding from the database
    const finding = db.prepare(`
      SELECT id, summary, risk_level, timestamp, source
      FROM audit_log
      WHERE id = ?
    `).get(findingId)

    if (!finding) {
      return NextResponse.json(
        { error: 'Finding not found' },
        { status: 404 }
      )
    }

    // For code-based findings, try to get the original code from the last commit diff
    let originalCode = ''
    let fixedCode = ''
    let explanation = ''

    if (finding.source === 'code') {
      // Read the last commit diff
      const diffPath = path.join(process.cwd(), '..', 'last_commit.diff')
      console.log('Looking for diff file at:', diffPath)
      
      if (fs.existsSync(diffPath)) {
        originalCode = fs.readFileSync(diffPath, 'utf-8')
        console.log('Read diff file, length:', originalCode.length)
      } else {
        console.log('Diff file not found, using summary as context')
        // If no diff file, use the summary as context
        originalCode = `Issue: ${finding.summary}\n\nNo code diff available. Please provide context about the code that needs to be fixed.`
      }

      // Call Python service to generate the fix
      const pythonServiceUrl = 'http://localhost:8002/generate-fix'
      console.log('Calling Python service:', pythonServiceUrl)
      
      const response = await fetch(pythonServiceUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          violation_summary: finding.summary,
          code_snippet: originalCode,
        }),
      })

      console.log('Python service response status:', response.status)

      if (response.ok) {
        const result = await response.json()
        console.log('Python service result:', result)
        fixedCode = result.fixed_code || ''
        explanation = result.explanation || ''
      } else {
        const errorText = await response.text()
        console.error('Python service error:', errorText)
        throw new Error(`Python service returned ${response.status}: ${errorText}`)
      }
    } else {
      return NextResponse.json(
        { error: 'Fix suggestions are only available for code-based findings' },
        { status: 400 }
      )
    }

    return NextResponse.json({
      explanation,
      original_code: originalCode,
      fixed_code: fixedCode,
    })
  } catch (error) {
    console.error('Error generating fix:', error)
    return NextResponse.json(
      { error: 'Failed to generate fix' },
      { status: 500 }
    )
  }
}

