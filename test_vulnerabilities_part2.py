# test_vulnerabilities_part3.py
# Yet more diverse vulnerabilities for testing the compliance scanner.

import os
import sqlite3 # For SQL injection example
import pickle # For insecure deserialization example
import xml.etree.ElementTree as ET # For XXE placeholder
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# --- Vulnerabilities ---

# 1. HIGH-RISK: SQL Injection Vulnerability
# Directly formatting user input into SQL queries is extremely dangerous.
def get_user_data(username):
    conn = sqlite3.connect('example.db') # Assuming this DB exists for example
    cursor = conn.cursor()
    
    # !! VULNERABLE LINE !! Gemini should flag this.
    query = f"SELECT * FROM users WHERE username = '{username}'" 
    logging.info(f"Executing SQL query: {query}")
    try:
        cursor.execute(query) 
        user_data = cursor.fetchone()
        logging.info(f"User data fetched: {user_data}")
        return user_data
    except sqlite3.Error as e:
        logging.error(f"SQL error: {e}")
        return None
    finally:
        conn.close()

# Simulate potentially malicious input
get_user_data("admin' OR '1'='1") 


# 2. HIGH-RISK: Insecure Deserialization (pickle)
# Deserializing data from untrusted sources can lead to arbitrary code execution.
def deserialize_data(data_stream):
    try:
        # !! VULNERABLE LINE !! Using pickle is risky.
        data = pickle.loads(data_stream) 
        logging.info(f"Deserialized data: {data}")
        return data
    except Exception as e:
        logging.error(f"Deserialization failed: {e}")
        return None

# Simulate receiving potentially malicious pickled data
# (This is a benign example, but pickle can execute arbitrary code)
potentially_malicious_data = b'\x80\x04\x95\x13\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x04name\x94\x8c\x03Bob\x94\x8c\x03age\x94K\x1eu.'
deserialize_data(potentially_malicious_data)


# 3. MEDIUM-RISK: Placeholder for XML External Entity (XXE)