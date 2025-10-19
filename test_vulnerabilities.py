# test_vulnerabilities.py
# This file contains intentional vulnerabilities for testing the compliance scanner.

import os
import requests

# 1. HIGH-RISK: Hardcoded AWS Credentials
# This is a classic 'High' risk finding.
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE" 
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# 2. HIGH-RISK: Hardcoded GitHub Personal Access Token (PAT)
# This token format is easily detectable.
GITHUB_TOKEN = "ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890"

# 3. HIGH-RISK: Private Key
# Committing any private key is a critical finding.
RSA_PRIVATE_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0R/N2qnN2gK0...
... (this is a fake truncated key for the example) ...
-----END RSA PRIVATE KEY-----
"""

class UserConfig:
    def __init__(self, user, email, api_url):
        self.user = user
        self.email = email # 4. MEDIUM-RISK: PII (Email)
        self.api_url = api_url # 5. LOW-RISK: Insecure URL (HTTP)

    def get_user_data(self):
        # This function processes user data
        print(f"Fetching data for {self.user} ({self.email})")
        
        try:
            # 5. LOW-RISK: Insecure API endpoint
            response = requests.get(f"{self.api_url}/users/{self.user}")
            return response.json()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

# 4. MEDIUM-RISK: Storing PII in plain text
admin = UserConfig(
    user="admin", 
    email="admin-support@example.com", 
    api_url="http://api.internal-service.com" # 5. Insecure URL
)

# 6. HIGH-RISK: Hardcoded GCP Service Account (JSON key)
# This is a very common and dangerous leak.
GCP_SA_KEY = {
  "type": "service_account",
  "project_id": "my-test-project",
  "private_key_id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMII... (fake key) ...\n-----END PRIVATE KEY-----",
  "client_email": "test-sa@my-test-project.iam.gserviceaccount.com",
  "client_id": "12345678901234567890",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test-sa%40my-test-project.iam.gserviceaccount.com"
}