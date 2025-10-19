#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime
from uagents import Agent, Context, Model
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# 🧠 Memory module (SQLite)
from memory import init_db, store_finding, finding_exists

# ---------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------
load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "CA")

# 🧩 SLACK INTEGRATION CONFIG
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

# 🧩 GITHUB INTEGRATION CONFIG
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")  # format: owner/repo

# ---------------------------------------------------------------------
# Jira helper: create new issue (Task or Bug)
# ---------------------------------------------------------------------
def create_jira_ticket(summary: str, description: str, risk: str) -> Optional[Dict[str, Any]]:
    """Create a new Jira Task or Bug in the specified project."""
    if not all([JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY]):
        print("❌ Jira credentials missing in .env (Check BASE_URL, EMAIL, TOKEN, PROJECT_KEY)")
        return None

    issue_type = "Bug" if "vulnerability" in summary.lower() else "Task"
    url = f"{JIRA_BASE_URL}/rest/api/3/issue"
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    adf_description = {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": description[:32000]}]}
        ]
    }

    data = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "issuetype": {"name": issue_type},
            "summary": f"[{risk.upper()}] {summary}",
            "description": adf_description,
        }
    }

    response = requests.post(url, auth=auth, headers=headers, json=data)
    if response.status_code in (200, 201):
        issue_key = response.json().get("key", "Unknown Key")
        print(f"✅ Jira {issue_type} created successfully! Key: {issue_key}")
        return response.json()
    else:
        print(f"❌ Jira issue creation failed with status {response.status_code}:")
        print(response.text)
        return None

# ---------------------------------------------------------------------
# Jira helper: comment fallback
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
# 🧩 SLACK HELPER FUNCTION
# ---------------------------------------------------------------------
def send_slack_message(text: str):
    """Send a message to a Slack channel."""
    if not SLACK_BOT_TOKEN or not SLACK_CHANNEL_ID:
        print("⚠️ Slack credentials missing. Skipping Slack alert.")
        return

    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}", "Content-Type": "application/json"}
    payload = {"channel": SLACK_CHANNEL_ID, "text": text}

    response = requests.post(url, headers=headers, json=payload)
    print("🧩 Slack raw response:", response.text)
    if response.status_code != 200 or not response.json().get("ok"):
        print(f"❌ Failed to send Slack message: {response.text}")
    else:
        print("✅ Slack message sent successfully!")

# ---------------------------------------------------------------------
# 🧩 GITHUB HELPER FUNCTION (HYBRID MODE)
# ---------------------------------------------------------------------
def handle_github_action(issue_summary: str, description: str, risk: str, pr_number: Optional[int] = None):
    """Hybrid GitHub action: HIGH risk → Issue | MEDIUM/LOW risk → PR Comment."""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("⚠️ GitHub credentials missing. Skipping GitHub action.")
        return None

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    body_text = (
        f"🚨 **Compliance Finding Detected** 🚨\n\n"
        f"**Risk:** {risk.upper()}\n"
        f"**Summary:** {issue_summary}\n\n"
        f"**Details:**\n{description}\n\n"
        f"_Generated automatically by the Fetch.ai Compliance Agent._"
    )

    # 🟥 HIGH risk → Create GitHub Issue
    if risk.lower() == "high":
        url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
        payload = {"title": f"[{risk.upper()}] {issue_summary}", "body": body_text, "labels": ["compliance", risk.lower()]}
        resp = requests.post(url, headers=headers, json=payload)
        print(f"🧩 GitHub Issue creation response: {resp.status_code} {resp.text}")
        if resp.status_code == 201:
            print("✅ GitHub Issue created successfully.")
            return resp.json()
        else:
            print("❌ Failed to create GitHub Issue.")
            return None

    # 🟨 MEDIUM/LOW risk → Comment on PR
    elif risk.lower() in ["medium", "low"]:
        if not pr_number:
            print("⚠️ No PR number provided — skipping GitHub comment.")
            return None
        url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{pr_number}/comments"
        payload = {"body": body_text}
        resp = requests.post(url, headers=headers, json=payload)
        print(f"🧩 GitHub PR comment response: {resp.status_code} {resp.text}")
        if resp.status_code == 201:
            print(f"✅ GitHub comment posted on PR #{pr_number}.")
            return resp.json()
        else:
            print(f"❌ Failed to post GitHub comment: {resp.status_code}")
            return None
    else:
        print(f"⚙️ Unknown risk level ({risk}) — no GitHub action taken.")
        return None

# ---------------------------------------------------------------------
# Agent definition
# ---------------------------------------------------------------------
agent = Agent(name="fetch_jira_agent", port=8001)

class AnalysisRequest(Model):
    analysis_path: str

class ActionResponse(Model):
    ok: bool
    action: str
    error: Optional[str] = None

# ---------------------------------------------------------------------
# Main handler
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

    if issues:
        actions_taken = []
        for issue in issues:
            summary = issue.get("type", "Unknown issue")
            desc = issue.get("description", "No description")
            pr_number = issue.get("pr_number")

            # 🧠 DEDUPLICATION CHECK
            if finding_exists(summary, risk):
                ctx.logger.info(f"⚠️ Duplicate finding skipped: {summary}")
                continue

            # 🪵 Jira
            ticket = create_jira_ticket(summary, desc, risk)
            action_result = "ticket_created" if ticket else "commented"
            if not ticket:
                create_jira_comment(summary, desc, risk)

            # 💬 Slack
            slack_text = (
                f"🚨 *{risk.upper()}-Risk Finding Detected!*\n"
                f"• *Summary:* {summary}\n"
                f"• *Risk:* {risk.upper()}\n"
                f"• *Action:* {action_result}\n"
                f"• *Source:* `{analysis_path}`\n"
            )
            if ticket and ticket.get("key"):
                slack_text += f"• *Jira:* {ticket.get('key')}\n"
            send_slack_message(slack_text)

            # 🧩 GitHub
            gh_resp = handle_github_action(summary, desc, risk, pr_number=pr_number)

            # 🧠 Store in memory
            store_finding(
                summary=summary,
                risk=risk,
                jira_key=ticket.get("key") if ticket else None,
                github_link=f"https://github.com/{GITHUB_REPO}" if GITHUB_REPO else None
            )

            actions_taken.append(action_result)

        return {"ok": True, "action": ",".join(actions_taken), "error": None}

    ctx.logger.info("✅ No issues detected — no Jira, Slack, or GitHub action taken.")
    return {"ok": True, "action": "none", "error": None}

# ---------------------------------------------------------------------
# Run agent
# ---------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    print("🚀 Fetch.ai Jira Agent (with Slack + GitHub + Memory) running on port 8001")
    agent.run()
