#!/usr/bin/env python
"""
Test script for database operations.

This script tests the database connection and performs basic CRUD operations
to verify that the database is correctly set up and functioning.
"""

import os
import sys
from dotenv import load_dotenv
from loguru import logger
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import database modules
from src.database.connection import session_scope, test_connection
from src.database.operations import DatabaseOperations
from src.database.models import WhatsAppMessage, MessageSummary, ScheduleConfig, BotStatus

def test_message_operations():
    """Test WhatsApp message operations."""
    with session_scope() as session:
        db_ops = DatabaseOperations(session)
        
        # Test saving a message
        test_message_id = f"test_message_{datetime.now().timestamp()}"
        test_chat_id = "120363271484974874@g.us"  # Use the group ID from .env
        
        logger.info("Testing message operations...")
        
        # Save a test message
        saved_message = db_ops.save_message(
            message_id=test_message_id,
            chat_id=test_chat_id,
            sender_id="test_sender",
            sender_name="Test User",
            message_text="This is a test message for database operations testing",
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Saved test message with ID: {saved_message.id}")
        
        # Retrieve unprocessed messages
        unprocessed = db_ops.get_unprocessed_messages(test_chat_id)
        logger.info(f"Found {len(unprocessed)} unprocessed messages")
        
        # Mark as processed
        if unprocessed:
            message_ids = [msg.id for msg in unprocessed]
            updated = db_ops.mark_messages_as_processed(message_ids)
            logger.info(f"Marked {updated} messages as processed")
        
        # Get message count
        count = db_ops.get_message_count(test_chat_id)
        logger.info(f"Total messages for test chat: {count}")
        
        return saved_message

def test_summary_operations():
    """Test summary operations."""
    with session_scope() as session:
        db_ops = DatabaseOperations(session)
        
        test_group_id = "120363271484974874@g.us"
        
        logger.info("Testing summary operations...")
        
        # Create a test summary
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=1)
        
        summary = db_ops.create_summary(
            group_id=test_group_id,
            summary_text="This is a test summary for database testing purposes.",
            start_date=start_date,
            end_date=end_date,
            message_count=10
        )
        
        logger.info(f"Created test summary with ID: {summary.id}")
        
        # Mark as sent
        updated_summary = db_ops.mark_summary_as_sent(summary.id)
        logger.info(f"Marked summary as sent at {updated_summary.sent_at}")
        
        # Get latest summary
        latest = db_ops.get_latest_summary(test_group_id)
        logger.info(f"Latest summary ID: {latest.id}")
        
        return summary

def test_schedule_operations():
    """Test schedule operations."""
    with session_scope() as session:
        db_ops = DatabaseOperations(session)
        
        logger.info("Testing schedule operations...")
        
        # Get current schedule
        config = db_ops.get_schedule_config()
        if config:
            logger.info(f"Current schedule: {config.schedule_time}, Active: {config.is_active}")
            
            # Update schedule status
            updated = db_ops.update_schedule_status(not config.is_active)
            logger.info(f"Updated schedule active status to: {updated.is_active}")
            
            # Revert back to original status
            reverted = db_ops.update_schedule_status(config.is_active)
            logger.info(f"Reverted schedule active status to: {reverted.is_active}")
        else:
            logger.warning("No schedule configuration found")

def test_bot_status_operations():
    """Test bot status operations."""
    with session_scope() as session:
        db_ops = DatabaseOperations(session)
        
        logger.info("Testing bot status operations...")
        
        # Get or create bot status
        status = db_ops.get_or_create_bot_status()
        logger.info(f"Bot status: Running: {status.is_running}, "
                   f"Background: {status.is_background_mode}, "
                   f"WhatsApp: {status.whatsapp_connected}")
        
        # Test updating bot status
        updated = db_ops.update_bot_status(
            is_running=True,
            whatsapp_connected=True
        )
        
        logger.info(f"Updated bot status: Running: {updated.is_running}, "
                   f"WhatsApp: {updated.whatsapp_connected}")
        
        # Revert changes
        reverted = db_ops.update_bot_status(
            is_running=status.is_running,
            whatsapp_connected=status.whatsapp_connected
        )
        
        logger.info("Reverted bot status changes")

def main():
    """Run database tests."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Configure logger
        logger.remove()
        logger.add(sys.stderr, level="INFO")
        
        logger.info("Starting database operations tests...")
        
        # Test connection
        if not test_connection():
            logger.error("Database connection test failed")
            return False
        
        # Run tests
        test_message_operations()
        test_summary_operations()
        test_schedule_operations()
        test_bot_status_operations()
        
        logger.info("All database tests completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error running database tests: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        sys.exit(1) 