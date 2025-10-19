# Unified Backend Architecture - Implementation Guide

## 🎯 Overview

The backend has been refactored to follow the **DRY (Don't Repeat Yourself)** principle by creating a shared `actions.py` module that handles all external API integrations (Jira, Slack, GitHub). Both the code analysis agent and screenshot analysis service now use the same unified action workflow.

## ✅ Refactoring Complete

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│                  http://localhost:3001                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
┌─────────────────┐   ┌──────────────────────────┐
│  Code Analysis  │   │  Screenshot Analysis     │
│  Agent (8001)   │   │  Service (8002)          │
└────────┬────────┘   └──────────┬───────────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Shared Modules      │
         ├───────────────────────┤
         │  • actions.py         │  ← Jira, Slack, GitHub
         │  • memory.py          │  ← Database operations
         └───────────────────────┘
```

## 📁 File Structure

### New Files

#### `actions.py` (NEW)
**Purpose:** Centralized external API integration module

**Functions:**
- `create_jira_ticket()` - Create Jira issues
- `create_jira_comment()` - Fallback Jira comments
- `send_slack_message()` - Send Slack notifications
- `handle_github_action()` - Create GitHub issues/comments
- `take_actions()` - Unified action handler for all services

**Environment Variables:**
- `JIRA_BASE_URL`, `JIRA_USER_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`
- `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`
- `GITHUB_TOKEN`, `GITHUB_REPO`

### Modified Files

#### `fetch_jira_agent.py` (REFACTORED)
**Changes:**
- ✅ Removed all external API functions (moved to `actions.py`)
- ✅ Added import: `import actions`
- ✅ Updated `handle_analysis()` to use `actions.take_actions()`
- ✅ Explicitly sets `source='code'` when storing findings
- ✅ Simplified from ~280 lines to ~100 lines

**Before:**
```python
# Old way - functions defined locally
ticket = create_jira_ticket(summary, desc, risk)
send_slack_message(slack_text)
gh_resp = handle_github_action(summary, desc, risk)
```

**After:**
```python
# New way - using shared module
action_results = actions.take_actions(
    summary=summary,
    description=desc,
    risk=risk,
    control_id=control_id,
    pr_number=pr_number
)
```

#### `screenshot_vision_service.py` (ENHANCED)
**Changes:**
- ✅ Added imports: `import memory`, `import actions`
- ✅ Integrated unified action workflow in `/analyze-image` endpoint
- ✅ Performs deduplication check using `memory.finding_exists()`
- ✅ Calls `actions.take_actions()` for medium/high risk findings
- ✅ Saves findings with `source='screenshot'`

**New Workflow:**
```python
# 1. Gemini analyzes screenshot
analysis = gemini_vision_analyze(image)

# 2. Vector search for control_id
control_id = search_policy(analysis['summary'])

# 3. Check for duplicates
if not memory.finding_exists(summary, risk):
    # 4. Take actions (Jira, Slack, GitHub)
    action_results = actions.take_actions(...)
    
    # 5. Save to database
    memory.store_finding(..., source='screenshot')
```

#### `memory.py` (UPDATED)
**Changes:**
- ✅ Added `source` parameter to `store_finding()` with default `'code'`
- ✅ Updated `get_recent_findings()` to include `source` column
- ✅ Updated `list_unresolved()` to include `source` column

## 🔄 Unified Action Workflow

### `actions.take_actions()` Function

**Purpose:** Single entry point for all external API calls

**Parameters:**
```python
def take_actions(
    summary: str,           # Brief description of issue
    description: str,       # Detailed description
    risk: str,             # Risk level (high, medium, low)
    control_id: str,       # Associated compliance control
    pr_number: int = None  # Optional PR number for GitHub
) -> Dict:
```

**Returns:**
```python
{
    "jira_key": "CA-123",           # Jira issue key
    "github_link": "https://...",   # GitHub issue URL
    "action_result": "ticket_created" # Result summary
}
```

**Logic:**
1. Only takes actions for **medium** or **high** risk findings
2. Creates Jira ticket (or comment if ticket creation fails)
3. Creates GitHub issue (high risk) or PR comment (medium/low risk)
4. Sends Slack notification
5. Returns all results for database storage

## 🎯 Service Comparison

| Feature | Code Analysis (8001) | Screenshot Analysis (8002) |
|---------|---------------------|---------------------------|
| **Trigger** | Code commit analysis | Screenshot upload |
| **Analysis** | Gemini text analysis | Gemini Vision API |
| **Deduplication** | ✅ Yes | ✅ Yes |
| **Jira Integration** | ✅ Yes | ✅ Yes |
| **Slack Integration** | ✅ Yes | ✅ Yes |
| **GitHub Integration** | ✅ Yes | ✅ Yes |
| **Control Mapping** | ✅ Yes (vector search) | ✅ Yes (vector search) |
| **Database Save** | ✅ Yes (`source='code'`) | ✅ Yes (`source='screenshot'`) |
| **Policy Update** | ✅ Yes | ✅ Yes |

## 🔧 How It Works

### Code Analysis Flow (Port 8001)

```
1. Developer commits code
2. analyze_with_gemini.py analyzes code
3. Vector search finds control_id
4. fetch_jira_agent.py receives analysis
5. Checks memory.finding_exists()
6. If new → actions.take_actions()
   - Create Jira ticket
   - Send Slack message
   - Create GitHub issue
7. memory.store_finding(source='code')
8. Update policies table
```

### Screenshot Analysis Flow (Port 8002)

```
1. User uploads screenshot
2. Next.js API sends to Python service
3. Gemini Vision analyzes image
4. Vector search finds control_id
5. Checks memory.finding_exists()
6. If new → actions.take_actions()
   - Create Jira ticket
   - Send Slack message
   - Create GitHub issue
7. memory.store_finding(source='screenshot')
8. Update policies table
```

## 📊 Database Schema

### `audit_log` Table

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    summary TEXT,
    risk_level TEXT,
    jira_key TEXT,
    github_link TEXT,
    slack_link TEXT,
    resolved INTEGER DEFAULT 0,
    control_id TEXT,
    source TEXT DEFAULT 'code'  -- NEW: 'code' or 'screenshot'
);
```

### Source Tracking

- **`source='code'`** - Findings from code analysis
- **`source='screenshot'`** - Findings from screenshot analysis

## 🚀 Setup & Usage

### 1. Start Code Analysis Agent (Port 8001)

```bash
source venv/bin/activate
python fetch_jira_agent.py
```

### 2. Start Screenshot Analysis Service (Port 8002)

```bash
source venv/bin/activate
python screenshot_vision_service.py
```

### 3. Both Services Share

- ✅ Same `actions.py` module
- ✅ Same `memory.py` module
- ✅ Same database (`compliance_memory.db`)
- ✅ Same environment variables
- ✅ Same policy controls

## 🔍 Testing

### Test Code Analysis

```bash
# Trigger code analysis
curl -X POST http://localhost:8001/act \
  -H "Content-Type: application/json" \
  -d '{"analysis_path": "path/to/analysis.json"}'
```

### Test Screenshot Analysis

```bash
# Upload screenshot
curl -X POST http://localhost:8002/analyze-image \
  -H "Content-Type: application/json" \
  -d '{"image": "data:image/png;base64,..."}'
```

### Verify Unified Actions

1. Check both services use same Jira credentials
2. Verify Slack messages from both sources
3. Confirm GitHub issues created by both
4. Check database has both `source='code'` and `source='screenshot'`

## ✨ Benefits of Refactoring

### 1. **DRY Principle**
- No code duplication
- Single source of truth for API integrations
- Easier to maintain and update

### 2. **Consistency**
- Same action workflow for all analysis types
- Uniform error handling
- Consistent Slack/Jira/GitHub formatting

### 3. **Extensibility**
- Easy to add new analysis types (e.g., API logs, config files)
- Just import `actions` and `memory`
- No need to rewrite API integration code

### 4. **Testability**
- Test `actions.py` independently
- Mock actions in tests
- Verify workflow without external APIs

### 5. **Maintainability**
- Update API logic in one place
- Fix bugs once, works everywhere
- Clear separation of concerns

## 🎯 Future Enhancements

### Easy to Add New Analysis Types:

```python
# Example: API Log Analysis Service (Port 8003)
import memory
import actions

def analyze_api_logs(log_data):
    # Analyze logs with Gemini
    analysis = gemini_analyze(log_data)
    
    # Check duplicates
    if not memory.finding_exists(analysis['summary'], analysis['risk']):
        # Take unified actions
        actions.take_actions(
            summary=analysis['summary'],
            description=analysis['description'],
            risk=analysis['risk'],
            control_id=analysis['control_id']
        )
        
        # Save with new source
        memory.store_finding(..., source='api_logs')
```

## 📝 Summary

### What Changed

1. **Created** `actions.py` - Shared external API module
2. **Refactored** `fetch_jira_agent.py` - Uses shared actions
3. **Enhanced** `screenshot_vision_service.py` - Uses shared actions
4. **Updated** `memory.py` - Supports `source` parameter
5. **Added** `source` column to database

### What Stayed the Same

- ✅ Frontend code (no changes needed)
- ✅ Database structure (only added `source` column)
- ✅ API endpoints (same URLs)
- ✅ User experience (same workflow)

### Key Achievement

**Both code analysis and screenshot analysis now use the exact same action workflow, ensuring consistency and maintainability across the entire system.**

---

**Status:** ✅ Fully Refactored and Unified  
**Date:** October 19, 2025  
**Principle:** DRY (Don't Repeat Yourself)  
**Services:** Code Analysis (8001) + Screenshot Analysis (8002)

