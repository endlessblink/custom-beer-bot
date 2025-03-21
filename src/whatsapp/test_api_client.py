#!/usr/bin/env python
"""
Test script for WhatsApp API client.
This script tests the functionality of the WhatsApp API client.
"""

import os
import sys
from dotenv import load_dotenv
from loguru import logger

# Add parent directory to path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import WhatsApp API client
from src.whatsapp.api_client import WhatsAppAPIClient

def main():
    """Test the WhatsApp API client."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Configure logger
        logger.remove()
        logger.add(sys.stderr, level="INFO")
        
        logger.info("Testing WhatsApp API client...")
        
        # Initialize client
        client = WhatsAppAPIClient()
        
        # Test authentication
        logger.info("Testing authentication...")
        if not client.check_auth():
            logger.error("Authentication test failed")
            return False
        
        # Get test group ID from environment
        test_group_id = os.getenv("TEST_GROUP_ID")
        
        if not test_group_id:
            logger.warning("TEST_GROUP_ID not found in environment variables")
            test_group_id = os.getenv("WHATSAPP_GROUP_IDS", "").split(",")[0].strip()
            
            if not test_group_id:
                logger.error("No test group ID found. Cannot continue tests.")
                return False
            
            logger.info(f"Using WhatsApp group ID: {test_group_id}")
        
        # Test group data
        logger.info("Testing getting group data...")
        group_data = client.get_group_data(test_group_id)
        
        if group_data:
            group_name = group_data.get("groupData", {}).get("name", "Unknown Group")
            logger.info(f"Group Name: {group_name}")
            participants_count = len(group_data.get("groupData", {}).get("participants", []))
            logger.info(f"Participants Count: {participants_count}")
        else:
            logger.warning("Failed to get group data")
        
        # Only run the following tests if BOT_DRY_RUN is not set to true
        dry_run = os.getenv("BOT_DRY_RUN", "false").lower() == "true"
        
        if not dry_run:
            # Test sending a message
            logger.info("Testing sending a message...")
            message = "🤖 This is a test message from the WhatsApp Bot. Please ignore."
            message_id = client.send_message(test_group_id, message)
            
            if message_id:
                logger.info(f"Message sent successfully with ID: {message_id}")
            else:
                logger.error("Failed to send test message")
                return False
                
            # Test getting chat history
            logger.info("Testing getting chat history...")
            history = client.get_chat_history(test_group_id, count=5)
            
            if history:
                logger.info(f"Retrieved {len(history)} messages from chat history")
                
                # Display the last few messages
                for i, msg in enumerate(history[:3]):
                    sender = msg.get("senderName", "Unknown")
                    text = msg.get("textMessage", "No text")
                    timestamp = msg.get("timestamp", "Unknown time")
                    logger.info(f"Message {i+1}: From {sender} at {timestamp}: {text}")
            else:
                logger.warning("Failed to get chat history")
        else:
            logger.info("Skipping message sending and chat history tests due to BOT_DRY_RUN=true")
        
        logger.info("WhatsApp API client tests completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error testing WhatsApp API client: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        sys.exit(1) 