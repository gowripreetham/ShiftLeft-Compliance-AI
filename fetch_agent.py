#!/usr/bin/env python3
import os
import json
import glob
from datetime import datetime

# ---------------------------------------------------------------------
# Placeholder functions for real-world actions
# ---------------------------------------------------------------------
def send_slack_alert(issue_summary, risk_level):
    """Simulate sending a Slack message (later replaced with real webhook)."""
    print(f"💬 [Slack Alert] Risk: {risk_level.upper()} | {issue_summary}")


def create_jira_ticket(issue_summary, description, risk_level):
    """Simulate creating a Jira ticket (later replaced with Jira API)."""
    print(f"🎟️ [Jira Ticket] Created for {risk_level.upper()} risk issue: {issue_summary}")
    print(f"   ➕ Description: {description[:100]}...")


def log_evidence(action, issue_type, risk_level):
    """Record actions taken for audit trail."""
    log_dir = "captures/actions"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{datetime.utcnow().isoformat()}Z_action_log.json")

    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "issue_type": issue_type,
        "risk_level": risk_level
    }

    with open(log_path, "w") as f:
        json.dump(record, f, indent=4)

    print(f"🪵 [Log] Action recorded in {log_path}")


# ---------------------------------------------------------------------
# Core Agent Logic
# ---------------------------------------------------------------------
def fetch_agent_decision(analysis_path):
    """Read Gemini analysis JSON and take appropriate actions."""
    with open(analysis_path, "r") as f:
        data = json.load(f)

    gemini_analysis = data.get("gemini_analysis", {})
    risk = gemini_analysis.get("risk_level", "unknown")
    issues = gemini_analysis.get("issues", [])

    print(f"\n🤖 Fetch Agent activated for {analysis_path}")
    print(f"🔍 Detected risk level: {risk}")

    if risk in ["high", "medium"] and isinstance(issues, list):
        for issue in issues:
            issue_type = issue.get("type", "Unknown")
            desc = issue.get("description", "")
            rec = issue.get("recommendation", "")

            # Decide actions
            if risk == "high":
                send_slack_alert(issue_type, risk)
                create_jira_ticket(issue_type, desc, risk)
                log_evidence("Slack + Jira", issue_type, risk)

            elif risk == "medium":
                send_slack_alert(issue_type, risk)
                log_evidence("Slack Only", issue_type, risk)

    else:
        print("✅ No significant risk detected — no action required.")


# ---------------------------------------------------------------------
# Auto-run on latest Gemini analysis file
# ---------------------------------------------------------------------
if __name__ == "__main__":
    paths = sorted(glob.glob("captures/analysis/**/*.json", recursive=True))
    if not paths:
        print("⚠️ No analysis files found. Run Gemini analysis first.")
    else:
        latest = paths[-1]
        fetch_agent_decision(latest)
