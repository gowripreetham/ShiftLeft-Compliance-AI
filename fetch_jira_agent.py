#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime
from uagents import Agent, Context, Model
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# ---------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------
load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "CA")
# 💡 REMOVED: JIRA_ACCOUNT_ID is no longer used in this version.

# ---------------------------------------------------------------------
# Jira helper: create new issue (Task or Bug)
# ---------------------------------------------------------------------
def create_jira_ticket(summary: str, description: str, risk: str) -> Optional[Dict[str, Any]]:
    """Create a new Jira Task or Bug in the specified project."""
    
    if not all([JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY]):
        print("❌ Jira credentials missing in .env (Check BASE_URL, EMAIL, TOKEN, PROJECT_KEY)")
        return None

    # Decide issue type dynamically based on summary content
    issue_type = "Bug" if "vulnerability" in summary.lower() else "Task"

    url = f"{JIRA_BASE_URL}/rest/api/3/issue"
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    # Create description using Atlassian Document Format (ADF) for robustness
    adf_description = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": description[:32000]}] # Max length for ADF
            }
        ]
    }

    # 💡 MODIFIED: This payload now omits the 'reporter' field.
    # If this fails, it's because Jira requires it to be explicitly set.
    data = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "issuetype": {"name": issue_type},
            "summary": f"[{risk.upper()}] {summary}",
            "description": adf_description,
            # 'priority' and 'reporter' are both omitted to rely on project defaults.
        }
    }

    response = requests.post(url, auth=auth, headers=headers, json=data)

    if response.status_code in (200, 201):
        issue_key = response.json().get("key", "Unknown Key")
        print(f"✅ Jira {issue_type} created successfully! Key: {issue_key}")
        return response.json()
    else:
        print(f"❌ Jira issue creation failed with status {response.status_code}:")
        print(response.text) # Print the full error for debugging
        return None

# ---------------------------------------------------------------------
# Jira helper: comment fallback (No changes needed)
# ---------------------------------------------------------------------
TARGET_ISSUE_KEY = "CA-1"

def create_jira_comment(summary: str, description: str, risk: str) -> Optional[Dict[str, Any]]:
    """Add a comment to an existing Jira issue for fallback/testing."""
    if not all([JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN]):
        print("❌ Jira credentials missing in .env")
        return None

    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{TARGET_ISSUE_KEY}/comment"
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    comment_body = f"""
--- Agent Action Log ---
Risk: {risk.upper()}
Issue Type: {summary}
Description: {description[:500]}

(Fallback action: This comment confirms the agent is active but failed to create a new issue.)
"""

    data = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": comment_body}]}
            ]
        }
    }

    response = requests.post(url, auth=auth, headers=headers, json=data)

    if response.status_code == 201:
        print(f"✅ Jira comment created successfully on {TARGET_ISSUE_KEY}!")
        return response.json()
    else:
        print(f"❌ Jira comment creation failed with status {response.status_code}:")
        print(response.text)
        return None

# ---------------------------------------------------------------------
# Agent definition (No changes needed)
# ---------------------------------------------------------------------
agent = Agent(name="fetch_jira_agent", port=8001)

class AnalysisRequest(Model):
    analysis_path: str

class ActionResponse(Model):
    ok: bool
    action: str
    error: Optional[str] = None

# ---------------------------------------------------------------------
# Main handler (No changes needed)
# ---------------------------------------------------------------------
@agent.on_rest_post("/act", AnalysisRequest, ActionResponse)
async def handle_analysis(ctx: Context, req: AnalysisRequest) -> Dict[str, Any]:
    """Handle incoming analysis JSON and take action."""
    analysis_path = req.analysis_path

    if not analysis_path:
        return {"ok": False, "action": "none", "error": "analysis_path missing."}
    if not os.path.exists(analysis_path):
        return {"ok": False, "action": "none", "error": f"File not found: {analysis_path}"}

    ctx.logger.info(f"\n🤖 Received analysis file: {analysis_path}")

    try:
        with open(analysis_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        return {"ok": False, "action": "none", "error": f"Failed to read analysis file: {e}"}

    gemini = data.get("gemini_analysis", {})
    risk = gemini.get("risk_level", "unknown")
    issues = gemini.get("issues", [])

    ctx.logger.info(f"🔍 Risk level: {risk}")

    if risk.lower() == "high" and issues:
        actions_taken = []
        for issue in issues:
            summary = issue.get("type", "Unknown issue")
            desc = issue.get("description", "No description")

            ticket = create_jira_ticket(summary, desc, risk)

            if not ticket:
                create_jira_comment(summary, desc, risk)
                actions_taken.append("commented")
            else:
                actions_taken.append("ticket_created")

            os.makedirs("captures/actions", exist_ok=True)
            log_path = f"captures/actions/{datetime.utcnow().isoformat()}Z_jira_action.json"
            with open(log_path, "w") as log:
                json.dump(
                    {
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "action": actions_taken[-1],
                        "issue_type": summary,
                        "risk_level": risk,
                    },
                    log,
                    indent=4,
                )
            ctx.logger.info(f"🪵 Logged → {log_path}")

        return {"ok": True, "action": ",".join(actions_taken), "error": None}

    ctx.logger.info("✅ No high-risk issues detected — no Jira action taken.")
    return {"ok": True, "action": "none", "error": None}

# ---------------------------------------------------------------------
# Run agent (No changes needed)
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Fetch.ai Jira Agent running on port 8001")
    agent.run()

