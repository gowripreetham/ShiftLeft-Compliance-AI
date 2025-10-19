import { NextRequest, NextResponse } from 'next/server';

// Python Gemini Vision Service URL
const PYTHON_VISION_SERVICE_URL = process.env.PYTHON_VISION_SERVICE_URL || 'http://localhost:8002/analyze-image';

export async function POST(request: NextRequest) {
  try {
    // Parse FormData
    const formData = await request.formData();
    const imageFile = formData.get('image') as File;

    if (!imageFile) {
      return NextResponse.json(
        { error: 'No image file provided' },
        { status: 400 }
      );
    }

    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif'];
    if (!allowedTypes.includes(imageFile.type)) {
      return NextResponse.json(
        { error: 'Invalid file type. Only PNG, JPEG, JPG, and GIF are allowed.' },
        { status: 400 }
      );
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (imageFile.size > maxSize) {
      return NextResponse.json(
        { error: 'Image size too large. Maximum size is 10MB.' },
        { status: 400 }
      );
    }

    // Convert image to base64
    const arrayBuffer = await imageFile.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    const base64Image = buffer.toString('base64');
    const dataUrl = `data:${imageFile.type};base64,${base64Image}`;

    // Call Python Vision Service
    let pythonResponse;
    try {
      pythonResponse = await fetch(PYTHON_VISION_SERVICE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: dataUrl,
          filename: imageFile.name,
        }),
      });

      if (!pythonResponse.ok) {
        throw new Error(`Python service returned ${pythonResponse.status}`);
      }
    } catch (error) {
      console.error('Error calling Python Vision Service:', error);
      return NextResponse.json(
        { 
          error: 'Failed to connect to analysis service. Please ensure the Python Vision Service is running on port 8002.',
          details: error instanceof Error ? error.message : 'Unknown error'
        },
        { status: 503 }
      );
    }

    // Parse Python service response
    const pythonData = await pythonResponse.json();
    
    // The Python service already:
    // 1. Analyzed the image with Gemini Vision
    // 2. Performed vector search for control_id
    // 3. Checked for duplicates
    // 4. Took actions (Jira, Slack, GitHub)
    // 5. Saved to database with source='screenshot'
    
    // Just pass through the Python service response to the frontend
    return NextResponse.json({
      success: true,
      ok: pythonData.ok,
      action_taken: pythonData.action_taken,
      analysis: pythonData.analysis,
    });

  } catch (error) {
    console.error('Error analyzing screenshot:', error);
    return NextResponse.json(
      { 
        error: 'Failed to analyze screenshot',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

