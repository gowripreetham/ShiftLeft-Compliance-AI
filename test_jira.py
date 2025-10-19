# Save this entire block and run it as a file, or paste all at once.
import os, requests
from dotenv import load_dotenv

# 1. This must be called AFTER you update the .env file!
load_dotenv()

# 2. This will now include 'https://' if step 1 was done correctly.
url = os.getenv("JIRA_BASE_URL") + "/rest/api/3/myself"
auth = (os.getenv("JIRA_USER_EMAIL"), os.getenv("JIRA_API_TOKEN"))

# 3. The request is made and the response variable is defined.
response = requests.get(url, auth=auth)

print("Status Code:", response.status_code)

if response.status_code == 200:
    print("✅ Jira credentials are valid!")
    print("Your account info:", response.json().get("displayName"))
else:
    print("❌ Jira authentication failed.")
    print("Response:", response.text)