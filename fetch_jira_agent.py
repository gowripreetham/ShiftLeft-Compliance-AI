#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime
from uagents import Agent, Context
from dotenv import load_dotenv

# ---------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------
load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "SEC")

# ---------------------------------------------------------------------
# Jira helper function
# ---------------------------------------------------------------------
def create_jira_ticket(summary, description, risk):
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

@agent.on_rest_post("/act")
async def handle_analysis(ctx: Context, request: dict):
    """
    POST endpoint that receives analysis.json path from pre-commit pipeline.
    Example payload: {"analysis_path": "captures/analysis/master/..._analysis.json"}
    """
    analysis_path = request.get("analysis_path")
    if not analysis_path or not os.path.exists(analysis_path):
        return {"ok": False, "error": "analysis_path missing or invalid"}

    with open(analysis_path, "r") as f:
        data = json.load(f)

    gemini = data.get("gemini_analysis", {})
    risk = gemini.get("risk_level", "unknown")
    issues = gemini.get("issues", [])

    print(f"\n🤖 Agent received analysis: {analysis_path}")
    print(f"🔍 Risk level: {risk}")

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
            print(f"🪵 Logged action → {log_path}")

        return {"ok": True, "action": "Jira tickets created"}
    else:
        print("✅ No high-risk issues detected. No Jira action taken.")
        return {"ok": True, "action": "none"}

if __name__ == "__main__":
    print("🚀 Fetch.ai Jira Agent running on port 8001")
    agent.run()
