# test_vulnerabilities_part2.py
# More vulnerabilities for testing the compliance scanner.

import os
import hashlib # For weak crypto example
import subprocess # For command execution example
import logging

# Configure basic logging (potential log injection)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# --- Vulnerabilities ---

# 1. MEDIUM-RISK: Use of Weak Cryptography (MD5)
# MD5 is known to be insecure against collisions.
password = "mysecretpassword"
hashed_password = hashlib.md5(password.encode()).hexdigest()
logging.info(f"Storing MD5 hash: {hashed_password}") # Also logs sensitive data type

# 2. HIGH-RISK: Potential Command Injection (using subprocess with variable)
# Using shell=True with unvalidated input is dangerous.
def list_directory_contents(directory_name):
    # In a real app, directory_name might come from user input.
    # Gemini might flag this as risky even without direct user input shown.
    command = f"ls -la {directory_name}"
    logging.info(f"Executing command: {command}")
    try:
        # Using shell=True is the risky part Gemini should catch
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print("Directory Contents:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e}")
        print(f"Error executing command: {e.stderr}")

# Simulate calling with potentially risky input (even if hardcoded here)
list_directory_contents("/tmp; ls /") # Example of injection attempt

# 3. MEDIUM-RISK: Potential Log Injection / Sensitive Data in Logs
# If user_input contained newline characters, it could forge log entries.
user_input = "User login attempt: username=admin\nInjecting fake log entry here"
logging.warning(f"Processing user input: {user_input}")

# 4. LOW-RISK: Insufficient Input Validation (Example)
# A function that doesn't properly check input types or ranges.
def process_payment(amount_str):
    try:
        amount = int(amount_str) # What if amount_str isn't an int? Or negative?
        if amount <= 0:
             print("Payment amount must be positive.")
             return False
        print(f"Processing payment of ${amount}")
        # ... payment logic ...
        return True
    except ValueError:
        print("Invalid amount format.")
        return False

# Simulate potentially bad input
process_payment("one hundred dollars")
process_payment("-50")

print("Vulnerability test script finished.")