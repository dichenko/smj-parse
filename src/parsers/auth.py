"""
Authentication module for Smart-J Data Collector.
"""
import requests
import logging
import urllib3
from src.config import BASE_URL, USERNAME, PASSWORD, HEADERS

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def login():
    """Log in to the website and return the session."""
    session = requests.Session()
    
    try:
        # Get main page
        logging.info("Getting main page...")
        response = session.get(BASE_URL, headers=HEADERS, verify=False, timeout=15)
        logging.info(f"Response status: {response.status_code}")
        
        # Prepare login data
        login_data = {
            'login': USERNAME,
            'passw': PASSWORD,
            'auth_mode': 'login'
        }
        
        # Submit login form
        logging.info("Submitting login data...")
        response = session.post(BASE_URL, data=login_data, headers=HEADERS, verify=False, timeout=15)
        logging.info(f"Response status after login: {response.status_code}")
        
        # Check if login was successful
        if "logout" in response.text.lower():
            logging.info("Login successful!")
            return session
        else:
            logging.error("Login failed. Check your credentials.")
            return None
        
    except Exception as e:
        logging.error(f"Error during login: {e}")
        return None
