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
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "SCRUM")

# ---------------------------------------------------------------------
# Jira helper function
# ---------------------------------------------------------------------
def create_jira_ticket(summary: str, description: str, risk: str) -> Optional[Dict[str, Any]]:
    """Create a Jira ticket using REST API."""
    if not all([JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN]):
        print("❌ Jira credentials missing in .env")
        return None

    url = f"{JIRA_BASE_URL}/rest/api/3/issue"
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    data = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": f"[{risk.upper()}] {summary}",
            "description": description[:2500],
            "issuetype": {"name": "Task"},
            "priority": {"name": "High" if risk == "high" else "Medium"},
        }
    }

    response = requests.post(url, auth=auth, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print("✅ Jira ticket created successfully!")
        return response.json()
    else:
        print("❌ Jira ticket creation failed:", response.text)
        return None


# ---------------------------------------------------------------------
# Agent definition
# ---------------------------------------------------------------------
agent = Agent(name="fetch_jira_agent", port=8001)

## REST Endpoint Models
# Input Model for the POST request body
class AnalysisRequest(Model):
    analysis_path: str

# Output Model for the POST response
class ActionResponse(Model):
    ok: bool
    action: str
    error: Optional[str] = None


# ---------------------------------------------------------------------
# Agent Handler
# ---------------------------------------------------------------------
# 1. The decorator now includes the Request Model and the Response Model.
@agent.on_rest_post("/act", AnalysisRequest, ActionResponse)
# 2. The function signature now accepts the parsed Request Model object (req).
async def handle_analysis(ctx: Context, req: AnalysisRequest) -> Dict[str, Any]:
    """
    POST endpoint that receives analysis.json path from pre-commit pipeline.
    The payload is automatically parsed into the 'req' object.
    The response is returned as a dictionary, which is validated against ActionResponse.
    """
    analysis_path = req.analysis_path

    if not analysis_path:
        return {"ok": False, "action": "none", "error": "analysis_path missing in payload."}
    
    if not os.path.exists(analysis_path):
        return {"ok": False, "action": "none", "error": f"File not found at path: {analysis_path}"}

    ctx.logger.info(f"\n🤖 Agent received analysis request for: {analysis_path}")

    try:
        with open(analysis_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        return {"ok": False, "action": "none", "error": f"Failed to read/parse analysis file: {e}"}

    gemini = data.get("gemini_analysis", {})
    risk = gemini.get("risk_level", "unknown")
    issues = gemini.get("issues", [])

    ctx.logger.info(f"🔍 Risk level: {risk}")

    if risk.lower() == "high" and issues:
        for issue in issues:
            summary = issue.get("type", "Unknown issue")
            desc = issue.get("description", "No description")
            create_jira_ticket(summary, desc, risk)

            # Log evidence
            os.makedirs("captures/actions", exist_ok=True)
            log_path = f"captures/actions/{datetime.utcnow().isoformat()}Z_jira_action.json"
            with open(log_path, "w") as log:
                json.dump(
                    {
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "action": "Created Jira ticket",
                        "issue_type": summary,
                        "risk_level": risk,
                    },
                    log,
                    indent=4,
                )
            ctx.logger.info(f"🪵 Logged action → {log_path}")

        # Return the final response (the framework sends this as JSON)
        return {"ok": True, "action": "Jira tickets created", "error": None}
    else:
        ctx.logger.info("✅ No high-risk issues detected. No Jira action taken.")
        # Return the final response (the framework sends this as JSON)
        return {"ok": True, "action": "none", "error": None}

if __name__ == "__main__":
    print("🚀 Fetch.ai Jira Agent running on port 8001")
    # Note: The warning about Almanac Contract version 2.0.0 vs 2.3.0 is a strong suggestion
    # to update your uAgents library for the best compatibility.
    agent.run()