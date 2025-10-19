#!/usr/bin/env python3
"""
Test file for demo - Contains intentional vulnerabilities
"""

# HIGH RISK: Hardcoded AWS credentials
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# MEDIUM RISK: Hardcoded API key
API_KEY = "sk_live_51Habc123xyz789"

# LOW RISK: Weak password
password = "admin123"

print("This is a test file for the demo")

# Test vulnerability
