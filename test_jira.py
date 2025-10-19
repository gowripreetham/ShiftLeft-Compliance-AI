import os, requests
from dotenv import load_dotenv

load_dotenv()

# Use the environment variable set in .env
project_key = os.getenv("JIRA_PROJECT_KEY") 

# *** THE CORRECTED URL IS HERE ***
url = os.getenv("JIRA_BASE_URL") + "/rest/api/3/search/jql" 
auth = (os.getenv("JIRA_USER_EMAIL"), os.getenv("JIRA_API_TOKEN"))
# Change the JQL to search for the summary text, ignoring the project key
params = {"jql": "summary ~ \"SQL Injection Vulnerability\" ORDER BY created DESC"}

# Also, temporarily set the print statement to reflect the broad search
print("Searching across all projects for ticket summary text...")
r = requests.get(url, auth=auth, params=params)

if r.status_code == 200:
    data = r.json()
    issues = data.get("issues", [])
    print(f"\nStatus Code: {r.status_code} | Found {len(issues)} issues.")
    
    if issues:
        print("--- Issues Found ---")
        for issue in issues:
            print(issue["key"], "-", issue["fields"]["summary"])
        print("\n✅ ISSUES EXIST IN JIRA'S DATABASE.")
    else:
        print("\n❌ NO ISSUES FOUND. Check JIRA_PROJECT_KEY.")
else:
    # Print the status code and text for any new errors (like 401 or 404)
    print(f"\n❌ API SEARCH FAILED. Status: {r.status_code}")
    print(r.text)