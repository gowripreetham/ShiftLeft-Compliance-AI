import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# --- Configuration from your agent ---
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "CA")

url = f"{JIRA_BASE_URL}/rest/api/3/issue"
auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
headers = {"Accept": "application/json", "Content-Type": "application/json"}

data = {
    "fields": {
        "project": {"key": JIRA_PROJECT_KEY},
        "issuetype": {"id": "10005"},  # Task type
        "summary": "[HIGH] Test Agent Failure Debug",
        "description": "Attempting to debug why tickets are not being created in project CA.",
        "priority": {"name": "High"},
        "reporter": {"id": JIRA_USER_EMAIL},
    }
}

print("Attempting to create ticket...")
response = requests.post(url, auth=auth, headers=headers, json=data)

# --- Print the FULL Response Details ---
print("\n--- JIRA API RESPONSE ---")
print(f"Status Code: {response.status_code}")

if response.status_code in (200, 201):
    print("✅ SUCCESS! Ticket created. Check your CA project for 'Test Agent Failure Debug'")
    print(f"Response Body (Key): {response.json().get('key')}")
else:
    print("❌ FAILURE DETECTED.")
    print("\nResponse Headers:")
    print(response.headers)
    print("\nResponse Text (Full Error Body):")
    # This is the line that will show the specific Jira validation error
    print(response.text)