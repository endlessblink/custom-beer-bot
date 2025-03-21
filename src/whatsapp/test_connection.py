#!/usr/bin/env python
"""
Test script for WhatsApp API connection.
This script verifies connectivity to the Green API.
"""

import os
import sys
import requests
from dotenv import load_dotenv
from loguru import logger

# Add parent directory to path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_green_api_connection():
    """Test the connection to Green API."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get Green API credentials
        api_id = os.getenv("GREEN_API_ID_INSTANCE")
        api_token = os.getenv("GREEN_API_TOKEN")
        base_url = os.getenv("GREEN_API_BASE_URL", "https://api.greenapi.com")
        
        if not api_id or not api_token:
            logger.error("GREEN_API_ID_INSTANCE or GREEN_API_TOKEN not found in environment variables")
            return False
        
        # Build the API URL to check account status
        url = f"{base_url}/waInstance{api_id}/getStateInstance/{api_token}"
        
        logger.info(f"Testing connection to Green API with ID: {api_id}")
        
        # Make the request
        response = requests.get(url)
        
        # Check the response
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Connection successful. API response: {data}")
            
            # Check the state of the instance
            state_name = data.get("stateInstance")
            logger.info(f"WhatsApp instance state: {state_name}")
            
            if state_name == "authorized":
                logger.info("WhatsApp account is authorized and ready to use")
                return True
            else:
                logger.warning(f"WhatsApp account is not ready. Current state: {state_name}")
                return False
        else:
            logger.error(f"Error connecting to Green API. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Error testing Green API connection: {str(e)}")
        return False

if __name__ == "__main__":
    # Configure logger
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    success = test_green_api_connection()
    
    if success:
        logger.info("WhatsApp API connection test completed successfully")
        sys.exit(0)
    else:
        logger.error("WhatsApp API connection test failed")
        sys.exit(1) 