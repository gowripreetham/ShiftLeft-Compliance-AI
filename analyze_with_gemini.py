#!/usr/bin/env python3
# --- START NOISE SUPPRESSION (MUST BE FIRST) ---
import os
import warnings

# 1. Suppress the 'NotOpenSSLWarning' from urllib3
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")

# 2. Suppress the gRPC/ALTS warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'

# 3. Suppress the TensorFlow/ABSL warnings (1 = ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
# --- END NOISE SUPPRESSION ---

# Now import everything else
import json
import re
import textwrap
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init
import google.generativeai as genai
from dotenv import load_dotenv
import chromadb

# Initialize colorama
init(autoreset=True)

# ---------------------------------------------------------------------
# Setup Gemini API
# ---------------------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise EnvironmentError("❌ Missing GEMINI_API_KEY in .env")

genai.configure(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------------------
# Vector Search for Policy Controls
# ---------------------------------------------------------------------
CHROMA_DB_PATH = Path(__file__).parent / 'chroma_db'

def search_policy(issue_description: str, top_k: int = 1):
    """
    Search for the most relevant policy control for a given issue.
    
    Args:
        issue_description: Description of the security issue
        top_k: Number of top results to return
    
    Returns:
        List of matching control IDs
    """
    try:
        client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
        collection = client.get_collection(name="policies")
        
        results = collection.query(
            query_texts=[issue_description],
            n_results=top_k
        )
        
        if results['ids'] and len(results['ids'][0]) > 0:
            return results['ids'][0]  # Return list of control IDs
        return []
    except Exception as e:
        print(f"⚠️ Error searching policies: {e}")
        return []

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

    # ---------------------------------------------------------------------
    # Improved JSON parsing (handles ```json ... ``` wrappers)
    # ---------------------------------------------------------------------
    raw_text = response.text.strip()
    cleaned_text = re.sub(r"^```(?:json)?|```$", "", raw_text, flags=re.MULTILINE).strip()

    try:
        gemini_output = json.loads(cleaned_text)
    except Exception:
        gemini_output = {"raw_text": cleaned_text}

    # ---------------------------------------------------------------------
    # Vector search for control_id mapping
    # ---------------------------------------------------------------------
    issues = gemini_output.get("issues", [])
    control_id = None
    
    if issues and isinstance(issues, list):
        # Use the first issue's description for vector search
        issue_desc = f"{issues[0].get('type', '')} {issues[0].get('description', '')}"
        matches = search_policy(issue_desc, top_k=1)
        if matches:
            control_id = matches[0]
            print(f"{Fore.CYAN}🔍 Mapped to control: {Style.BRIGHT}{control_id}")
    
    # ---------------------------------------------------------------------
    # Save analysis output
    # ---------------------------------------------------------------------
    analysis = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source_capture": capture_path,
        "gemini_analysis": gemini_output,
        "control_id": control_id
    }

    base_dir = os.path.dirname(capture_path).replace("commits", "analysis")
    os.makedirs(base_dir, exist_ok=True)

    capture_name = os.path.basename(capture_path).replace(".json", "_analysis.json")
    out_path = os.path.join(base_dir, capture_name)

    with open(out_path, "w") as f:
        json.dump(analysis, f, indent=4)

    print(f"\n✅ Gemini analysis complete: {out_path}")

    # ---------------------------------------------------------------------
    # Display formatted summary in terminal
    # ---------------------------------------------------------------------
    risk_level = gemini_output.get("risk_level", "unknown")
    summary = gemini_output.get("summary", "No summary provided.")

    # --- 1. Print Risk Level Header ---
    if risk_level.lower() == 'high':
        print(Fore.RED + Style.BRIGHT + "\n==========================================")
        print(Fore.RED + Style.BRIGHT + "       🚨 HIGH RISK DETECTED 🚨")
        print(Fore.RED + Style.BRIGHT + "==========================================")
    elif risk_level.lower() == 'medium':
        print(Fore.YELLOW + Style.BRIGHT + "\n==========================================")
        print(Fore.YELLOW + Style.BRIGHT + "       ⚠️ MEDIUM RISK DETECTED ⚠️")
        print(Fore.YELLOW + Style.BRIGHT + "==========================================")
    elif risk_level.lower() == 'low':
        print(Fore.GREEN + "\n==========================================")
        print(Fore.GREEN + "        ✅ LOW RISK DETECTED")
        print(Fore.GREEN + "==========================================")
    else:
        print(Fore.WHITE + "\n==========================================")
        print(Fore.WHITE + "        ℹ️ INFO/UNKNOWN RISK")
        print(Fore.WHITE + "==========================================")

    # --- 2. Print Summary Info ---
    print(f"{Style.BRIGHT}Control ID:{Style.NORMAL} {control_id}")
    print(f"{Style.BRIGHT}Summary:   {Style.NORMAL} {summary}")

    # --- 3. Print Formatted Issues ---
    if issues and isinstance(issues, list):
        print(Fore.WHITE + Style.BRIGHT + "\n--- Top Issues Found ---")
        for i, issue in enumerate(issues[:2], start=1):
            issue_type = issue.get('type', 'Unknown Issue')
            description = issue.get('description', 'No description.')
            recommendation = issue.get('recommendation', 'No recommendation.')
            
            # Print the Issue Type
            print(f"\n{Style.BRIGHT}{i}. {issue_type}")
            
            # Print the indented, wrapped description
            desc_lines = textwrap.wrap(description, width=80)
            if desc_lines:
                print(Fore.CYAN + "   ├─ Finding:  " + desc_lines[0])
                for line in desc_lines[1:]:
                    print(Fore.CYAN + "   │            " + line)
            
            # Print the indented, wrapped recommendation
            rec_lines = textwrap.wrap(recommendation, width=80)
            if rec_lines:
                print(Fore.YELLOW + "   ╰─ 💡 Rec:    " + rec_lines[0])
                for line in rec_lines[1:]:
                    print(Fore.YELLOW + "                " + line)

    print("\n---------------------------------------------")
    return analysis


# ---------------------------------------------------------------------
# Auto-run for latest capture
# ---------------------------------------------------------------------
if __name__ == "__main__":
    import glob

    paths = sorted(glob.glob("captures/commits/**/*.json", recursive=True))
    if not paths:
        print("⚠️ No capture files found. Commit something first.")
    else:
        latest = paths[-1]
        print(f"🧠 Sending latest capture to Gemini: {latest}")
        analyze_capture_with_gemini(latest)
