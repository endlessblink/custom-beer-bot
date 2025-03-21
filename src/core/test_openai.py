#!/usr/bin/env python
"""
Test script for OpenAI API connection.
This script verifies connectivity to the OpenAI API.
"""

import os
import sys
import requests
from dotenv import load_dotenv
from loguru import logger

# Add parent directory to path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_openai_api_connection():
    """Test the connection to OpenAI API using direct REST call."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            return False
        
        # Build the API request
        url = "https://api.openai.com/v1/models"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        logger.info("Testing connection to OpenAI API")
        
        # Make the request
        response = requests.get(url, headers=headers)
        
        # Check the response
        if response.status_code == 200:
            logger.info("Connection to OpenAI API successful")
            models = response.json().get('data', [])
            logger.info(f"Available models: {len(models)} models found")
            
            # Show a few models
            sample_models = models[:3] if len(models) > 3 else models
            for model in sample_models:
                logger.info(f"Model: {model.get('id')}")
            
            return True
        else:
            logger.error(f"Error connecting to OpenAI API. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Error testing OpenAI API connection: {str(e)}")
        return False

if __name__ == "__main__":
    # Configure logger
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    success = test_openai_api_connection()
    
    if success:
        logger.info("OpenAI API connection test completed successfully")
        sys.exit(0)
    else:
        logger.error("OpenAI API connection test failed")
        sys.exit(1) 