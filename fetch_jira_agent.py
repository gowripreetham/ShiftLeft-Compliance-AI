#!/usr/bin/env python3
"""
Fetch.ai Jira Agent - Code Analysis Service

This agent receives code analysis results and triggers actions (Jira, Slack, GitHub).
It uses the shared actions module for external API calls.
"""

import os
import json
from uagents import Agent, Context, Model
from typing import Dict, Any, Optional

# 🧠 Memory module (SQLite)
from memory import init_db, store_finding, finding_exists

# 🎯 Shared actions module
import actions

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
    control_id = data.get("control_id")  # Get control_id from analysis
    ctx.logger.info(f"🔍 Risk level: {risk}")
    if control_id:
        ctx.logger.info(f"🔍 Control ID: {control_id}")

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

            # 🎯 UNIFIED ACTION WORKFLOW (using shared actions module)
            action_results = actions.take_actions(
                summary=summary,
                description=desc,
                risk=risk,
                control_id=control_id,
                pr_number=pr_number
            )

            # 🧠 Store in memory with source='code'
            store_finding(
                summary=summary,
                risk=risk,
                jira_key=action_results.get("jira_key"),
                github_link=action_results.get("github_link"),
                slack_link=None,
                control_id=control_id,
                source='code'  # CRITICAL: Mark as code source
            )

            actions_taken.append(action_results.get("action_result", "none"))

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
