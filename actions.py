#!/usr/bin/env python3
"""
Shared Actions Module for External API Integrations

This module contains all external API calls (Jira, Slack, GitHub)
that can be used by both the code analysis agent and screenshot analysis service.
"""

import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# ---------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------
load_dotenv()

# Jira Configuration
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "CA")
TARGET_ISSUE_KEY = "CA-1"

# Slack Configuration
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

# GitHub Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")  # format: owner/repo

# ---------------------------------------------------------------------
# Jira Actions
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
# Slack Actions
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
# GitHub Actions
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
        f"**Risk Level:** {risk.upper()}\n"
        f"**Summary:** {issue_summary}\n\n"
        f"**Description:**\n{description}\n\n"
        f"---\n"
        f"*This issue was automatically created by the Shift-Left Compliance Dashboard.*"
    )

    # HIGH risk → Create GitHub Issue
    if risk.lower() == "high":
        url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
        data = {
            "title": f"[{risk.upper()}] {issue_summary}",
            "body": body_text,
            "labels": ["security", "compliance", risk.lower()]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            issue_data = response.json()
            print(f"✅ GitHub Issue created: {issue_data.get('html_url')}")
            return issue_data
        else:
            print(f"❌ GitHub Issue creation failed: {response.text}")
            return None

    # MEDIUM/LOW risk → Comment on PR (if pr_number provided)
    elif pr_number:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/pulls/{pr_number}/comments"
        data = {
            "body": body_text,
            "commit_id": "HEAD",
            "path": "compliance-finding.md",
            "position": 1
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            comment_data = response.json()
            print(f"✅ GitHub PR comment created: {comment_data.get('html_url')}")
            return comment_data
        else:
            print(f"❌ GitHub PR comment failed: {response.text}")
            return None

    return None


# ---------------------------------------------------------------------
# Unified Action Handler
# ---------------------------------------------------------------------

def take_actions(summary: str, description: str, risk: str, control_id: Optional[str] = None, pr_number: Optional[int] = None):
    """
    Unified function to take all actions (Jira, Slack, GitHub) for a finding.
    
    Args:
        summary: Brief description of the issue
        description: Detailed description
        risk: Risk level (high, medium, low)
        control_id: Associated compliance control ID
        pr_number: Optional PR number for GitHub comments
    
    Returns:
        Dict with action results (jira_key, github_link, etc.)
    """
    jira_key = None
    github_link = None
    action_result = "none"
    
    # Take actions only for medium/high risk
    if risk.lower() in ('high', 'medium'):
        # Create Jira ticket
        ticket = create_jira_ticket(summary, description, risk)
        if not ticket:
            create_jira_comment(summary, description, risk)
            action_result = "commented"
        else:
            jira_key = ticket.get("key")
            action_result = "ticket_created"
        
        # Create GitHub issue/comment
        gh_response = handle_github_action(summary, description, risk, pr_number)
        if gh_response:
            github_link = gh_response.get("html_url")
        
        # Send Slack notification
        slack_text = (
            f"🚨 *[{risk.upper()}]-Risk Finding Detected!*\n"
            f"• *Summary:* {summary}\n"
            f"• *Risk:* {risk.upper()}\n"
            f"• *Control:* {control_id or 'N/A'}\n"
            f"• *Action Taken:* {action_result}\n"
        )
        send_slack_message(slack_text)
    
    return {
        "jira_key": jira_key,
        "github_link": github_link,
        "action_result": action_result
    }

