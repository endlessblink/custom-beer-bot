#!/usr/bin/env python3
"""
WhatsApp Bot Runner Script

This script connects the different components of the WhatsApp bot system to:
1. Retrieve messages from a group chat
2. Store those messages in the database
3. Generate a summary of the messages
4. Post the summary to a test group

Usage:
    python run_bot.py [--source GROUP_ID] [--target GROUP_ID] [--days DAYS] [--debug]
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from loguru import logger

# Import project modules
from src.database.connection import create_db_engine, get_db_session
from src.database.operations import DatabaseOperations
from src.whatsapp.bot import WhatsAppBot
from src.nlp.summarizer import OpenAISummarizer

def setup_logging(debug=False):
    """Configure logging for the script."""
    # Clear any existing handlers
    logger.remove()
    
    # Set log level based on debug flag
    log_level = "DEBUG" if debug else "INFO"
    
    # Add console handler
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    logger.info("Logging configured successfully")

async def run_bot(source_group_id, target_group_id, days, debug):
    """Run the WhatsApp bot with the specified parameters."""
    logger.info(f"Starting WhatsApp bot with source group {source_group_id}, target group {target_group_id}, {days} days")
    
    try:
        # Initialize database connection
        engine = create_db_engine()
        session = get_db_session(engine)
        db_operations = DatabaseOperations(session)
        logger.info("Database connection established")
        
        # Initialize WhatsApp bot
        whatsapp_bot = WhatsAppBot(db_operations)
        
        # Check WhatsApp connection
        if not await whatsapp_bot.check_connection():
            logger.error("Failed to connect to WhatsApp API. Please check your credentials.")
            return False
        
        logger.info("WhatsApp connection successful")
        
        # Start the bot
        if not await whatsapp_bot.start():
            logger.error("Failed to start WhatsApp bot")
            return False
        
        try:
            # 1. Process messages from the notification queue (get new messages)
            # This will run the message processing loop in the background briefly
            # to collect any new messages
            logger.info("Processing any pending notifications")
            notification_count = 0
            max_notifications = 50  # Process up to 50 notifications
            
            # Process notifications one by one
            while notification_count < max_notifications:
                notification = whatsapp_bot.api_client.receive_notification()
                if not notification:
                    logger.debug("No more notifications in queue")
                    break
                    
                receipt_id = notification.get('receiptId')
                processed = await whatsapp_bot.process_notification(notification)
                
                if processed:
                    notification_count += 1
                
                # Delete the notification from the queue
                if receipt_id:
                    whatsapp_bot.api_client.delete_notification(receipt_id)
            
            logger.info(f"Processed {notification_count} notifications")
            
            # 2. Get unprocessed messages for the group from the database
            unprocessed_messages = db_operations.get_unprocessed_messages(source_group_id)
            logger.info(f"Found {len(unprocessed_messages)} unprocessed messages in the database")
            
            # 3. Generate summary if we have enough messages
            if len(unprocessed_messages) > 0:
                logger.info("Generating summary of messages")
                summary_result = await whatsapp_bot.generate_summary(source_group_id, days)
                
                if not summary_result:
                    logger.error("Failed to generate summary")
                    return False
                
                logger.info(f"Summary generated with ID {summary_result['summary_id']}")
                
                # 4. Send the summary to the target group
                if target_group_id:
                    logger.info(f"Sending summary to target group {target_group_id}")
                    
                    # If message sending is disabled (for testing), don't actually send
                    if os.getenv("BOT_MESSAGE_SENDING_DISABLED", "false").lower() == "true":
                        logger.warning("Message sending is disabled. Summary not sent.")
                        logger.info(f"Summary content: {summary_result['summary_text']}")
                    else:
                        # Send the summary
                        send_result = await whatsapp_bot.send_summary(summary_result, target_group_id)
                        
                        if send_result:
                            logger.info("Summary sent successfully")
                        else:
                            logger.error("Failed to send summary")
                            return False
            else:
                logger.warning("Not enough messages to generate a summary")
            
            return True
            
        finally:
            # Stop the bot when done
            await whatsapp_bot.stop()
            session.close()
            
    except Exception as e:
        logger.error(f"Error running WhatsApp bot: {str(e)}")
        return False

def main():
    """Main entry point for the script."""
    # Load environment variables
    load_dotenv()
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="WhatsApp Bot Runner")
    parser.add_argument("--source", help="Source group ID to fetch messages from")
    parser.add_argument("--target", help="Target group ID to send summary to")
    parser.add_argument("--days", type=int, default=1, help="Number of days to include in summary")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.debug)
    
    # Get group IDs from arguments or environment variables
    source_group_id = args.source or os.getenv("WHATSAPP_SOURCE_GROUP_ID")
    target_group_id = args.target or os.getenv("WHATSAPP_TARGET_GROUP_ID")
    
    if not source_group_id:
        logger.error("Source group ID not provided. Use --source or set WHATSAPP_SOURCE_GROUP_ID")
        sys.exit(1)
    
    # Run the bot
    try:
        result = asyncio.run(run_bot(source_group_id, target_group_id, args.days, args.debug))
        
        if result:
            logger.info("WhatsApp bot completed successfully")
            sys.exit(0)
        else:
            logger.error("WhatsApp bot failed to complete")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Script terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 