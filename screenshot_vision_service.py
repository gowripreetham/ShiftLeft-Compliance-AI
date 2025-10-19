#!/usr/bin/env python3
"""
Python Gemini Vision Service for Screenshot Compliance Analysis

This service receives screenshot images from the Next.js frontend,
analyzes them using Gemini Vision API, and returns structured compliance findings.

Run this service on port 8002:
    python screenshot_vision_service.py
"""

import os
import json
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js frontend

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("❌ Missing GEMINI_API_KEY in .env")

genai.configure(api_key=GEMINI_API_KEY)

# Import shared modules
import memory
import actions

# Import vector search function from populate_policies.py
from pathlib import Path
import chromadb

CHROMA_DB_PATH = Path(__file__).parent / 'chroma_db'

def search_policy(issue_description: str, top_k: int = 1):
    """Search for the most relevant policy control for a given issue."""
    try:
        client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
        collection = client.get_collection(name="policies")
        
        results = collection.query(
            query_texts=[issue_description],
            n_results=top_k
        )
        
        if results['ids'] and len(results['ids'][0]) > 0:
            return results['ids'][0]
        return []
    except Exception as e:
        print(f"⚠️ Error searching policies: {e}")
        return []

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Analyze a screenshot for compliance issues using Gemini Vision."""
    try:
        # Parse JSON request
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        image_data = data['image']
        filename = data.get('filename', 'screenshot')
        
        # Extract base64 data if it's a data URL
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Prepare prompt for Gemini Vision
        prompt = """
You are a security and compliance auditor AI analyzing a screenshot.

Analyze this image for:
1. Security vulnerabilities (e.g., hardcoded credentials, exposed secrets, sensitive data)
2. Compliance violations (e.g., improper access controls, data handling issues)
3. Privacy concerns (e.g., exposed personal information, unsecured data)

Provide your analysis in this JSON format:
{
  "risk_level": "low|medium|high",
  "summary": "Brief one-line summary of the issue",
  "description": "Detailed description of what you found",
  "issues": [
    {
      "type": "Issue type (e.g., 'Hardcoded Credentials', 'Exposed Secrets')",
      "description": "Detailed explanation",
      "recommendation": "How to fix this issue"
    }
  ]
}

Be thorough and specific. If no issues are found, set risk_level to "low" and provide a positive summary.
"""
        
        # Call Gemini Vision API
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Create image part
        import PIL.Image
        from io import BytesIO
        image = PIL.Image.open(BytesIO(image_bytes))
        
        # Generate content
        response = model.generate_content([prompt, image])
        
        # Parse response
        response_text = response.text.strip()
        
        # Extract JSON from response (handle markdown code blocks)
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        try:
            analysis = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            analysis = {
                "risk_level": "medium",
                "summary": "Screenshot analyzed",
                "description": response_text[:500],
                "issues": []
            }
        
        # Perform vector search to find matching control
        control_id = None
        if analysis.get('summary'):
            matches = search_policy(analysis['summary'], top_k=1)
            if matches:
                control_id = matches[0]
                print(f"🔍 Mapped to control: {control_id}")
        
        # Add control_id to analysis
        analysis['control_id'] = control_id
        
        print(f"✅ Analysis complete for {filename}: {analysis['risk_level']} risk")
        
        # ============================================
        # UNIFIED ACTION WORKFLOW (Same as code analysis)
        # ============================================
        
        # Extract analysis results
        summary = analysis.get('summary', 'Screenshot analysis completed')
        desc = analysis.get('description', 'No description available')
        risk = analysis.get('risk_level', 'unknown')
        control_id = analysis.get('control_id')
        
        # Check for duplicates
        if memory.finding_exists(summary, risk):
            print(f"⚠️ Duplicate finding: {summary}. Skipping actions.")
            return jsonify({
                'ok': True,
                'action_taken': 'duplicate',
                'analysis': analysis
            })
        
        # Take actions for medium/high risk findings
        action_results = actions.take_actions(
            summary=summary,
            description=desc,
            risk=risk,
            control_id=control_id,
            pr_number=None  # Screenshots don't have PR numbers
        )
        
        # Save to memory with source='screenshot'
        memory.store_finding(
            summary=summary,
            risk=risk,
            jira_key=action_results.get('jira_key'),
            github_link=action_results.get('github_link'),
            slack_link=None,
            control_id=control_id,
            source='screenshot'  # CRITICAL: Mark as screenshot source
        )
        
        print(f"✅ Finding saved to database with source='screenshot'")
        
        # Return full analysis with action results
        return jsonify({
            'ok': True,
            'action_taken': action_results.get('action_result'),
            'analysis': analysis
        })
        
    except Exception as e:
        print(f"❌ Error analyzing image: {e}")
        return jsonify({
            'error': 'Failed to analyze image',
            'details': str(e)
        }), 500

@app.route('/generate-fix', methods=['POST'])
def generate_fix():
    """Generate AI-powered code fix for a compliance violation."""
    try:
        data = request.get_json()
        violation_summary = data.get('violation_summary', '')
        code_snippet = data.get('code_snippet', '')

        if not violation_summary:
            return jsonify({
                'error': 'Missing violation_summary'
            }), 400

        # Create a prompt for Gemini to generate the fix
        prompt = f"""You are an expert DevSecOps engineer specializing in security and compliance.

Given the following compliance violation:
{violation_summary}

And this code snippet:
```python
{code_snippet[:2000] if len(code_snippet) > 2000 else code_snippet}
```

Your task:
1. Identify the security/compliance issue in the code
2. Generate a secure, compliant version of the code
3. Provide a brief, one-sentence explanation of what was fixed

Respond in the following JSON format:
{{
    "explanation": "Brief explanation of the fix",
    "fixed_code": "The complete fixed code block"
}}

Important:
- Only return valid JSON
- The fixed_code should be the complete, working solution
- Keep the explanation concise (one sentence)
- Ensure the fix addresses the specific compliance violation mentioned
"""

        # Use Gemini to generate the fix
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = model.generate_content(prompt)
        
        # Parse the response
        response_text = response.text.strip()
        
        # Try to extract JSON from the response
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        try:
            result = json.loads(response_text)
            return jsonify({
                'explanation': result.get('explanation', 'Code fix generated'),
                'fixed_code': result.get('fixed_code', ''),
            })
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response
            return jsonify({
                'explanation': 'AI-generated fix',
                'fixed_code': response_text,
            })

    except Exception as e:
        print(f"❌ Error generating fix: {e}")
        return jsonify({
            'error': 'Failed to generate fix',
            'details': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Gemini Vision Analysis Service',
        'port': 8002
    })

if __name__ == '__main__':
    print("🚀 Gemini Vision Service starting on port 8002...")
    print("📸 Ready to analyze screenshots for compliance!")
    print("\n⚠️  Make sure to install required dependencies:")
    print("   pip install flask flask-cors pillow google-generativeai chromadb")
    print("\n")
    
    app.run(host='0.0.0.0', port=8002, debug=True)

