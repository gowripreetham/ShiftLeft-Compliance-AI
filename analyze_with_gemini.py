#!/usr/bin/env python3
import os
import json
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# ---------------------------------------------------------------------
# Setup Gemini API
# ---------------------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise EnvironmentError("❌ Missing GEMINI_API_KEY in .env")

genai.configure(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------------------
# Core Analyzer (Gemini-based)
# ---------------------------------------------------------------------
def analyze_capture_with_gemini(capture_path):
    """Send the capture JSON to Gemini for compliance/security analysis."""
    with open(capture_path, "r", errors="ignore") as f:
        data = json.load(f)

    # Combine relevant content for Gemini context
    prompt_content = {
        "branch": data.get("branch"),
        "commit_message": data.get("commit_message"),
        "diff_content": data.get("diff_content", "")[:8000],  # truncate if too long
        "recent_terminal_history": "\n".join(data.get("recent_terminal_history", [])[-50:]),
        "config_snapshots": list(data.get("config_snapshots", {}).keys()),
        "log_snippets": {k: v[:2000] for k, v in data.get("log_snippets", {}).items()},
    }

    prompt = f"""
You are a security and compliance auditor AI.

Analyze the following developer activity for **security, compliance, and privacy risks**.
Provide:
1. Overall risk level (low, medium, high)
2. A list of specific issues found (with explanation)
3. Mapped SOC2 or NIST controls if applicable
4. Recommendations to the developer

Input data (JSON):
{json.dumps(prompt_content, indent=2)}

Respond in this JSON format:

{{
  "risk_level": "low|medium|high",
  "issues": [
    {{
      "type": "string",
      "description": "string",
      "recommendation": "string",
      "related_control": "string (optional)"
    }}
  ],
  "summary": "short summary of the analysis"
}}
    """

    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(prompt)

    try:
        # Try to parse JSON from Gemini output
        gemini_output = json.loads(response.text)
    except Exception:
        # If Gemini doesn’t return perfect JSON, store as raw text
        gemini_output = {"raw_text": response.text.strip()}

    analysis = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source_capture": capture_path,
        "gemini_analysis": gemini_output
    }

    # Save to /captures/analysis/
    base_dir = os.path.dirname(capture_path).replace("commits", "analysis")
    os.makedirs(base_dir, exist_ok=True)

    capture_name = os.path.basename(capture_path).replace(".json", "_analysis.json")
    out_path = os.path.join(base_dir, capture_name)

    with open(out_path, "w") as f:
        json.dump(analysis, f, indent=4)

    print(f"✅ Gemini analysis complete: {out_path}")
    print(f"🔍 Risk level: {gemini_output.get('risk_level', 'unknown')}")
    return analysis


if __name__ == "__main__":
    import glob

    # Automatically analyze the latest capture file
    paths = sorted(glob.glob("captures/commits/**/*.json", recursive=True))
    if not paths:
        print("⚠️ No capture files found. Commit something first.")
    else:
        latest = paths[-1]
        print(f"🧠 Sending latest capture to Gemini: {latest}")
        analyze_capture_with_gemini(latest)
