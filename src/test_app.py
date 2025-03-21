"""
Test script for the WhatsApp Summarizer Bot application.

This script tests the basic functionality of the WhatsApp bot application
by initializing the core components and running a simple test.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from datetime import datetime, timedelta

# Add the parent directory to the path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

# Import application modules
from src.database.connection import create_db_engine, get_db_session
from src.database.operations import DatabaseOperations
from src.whatsapp.api_client import WhatsAppAPIClient
from src.whatsapp.bot import WhatsAppBot
from src.nlp.summarizer import OpenAISummarizer


def setup_logging():
    """Configure logging for the test script."""
    # Clear any existing handlers
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )


async def test_app_components():
    """Test the core application components."""
    logger.info("Starting application component test")
    
    try:
        # Test database connection
        logger.info("Testing database connection...")
        engine = create_db_engine()
        session = get_db_session(engine)
        db = DatabaseOperations(session)
        
        try:
            # Perform a simple database query to test connection
            # Just get the first record from a table, or count
            bot_status = db.get_or_create_bot_status()
            logger.info(f"Database connection successful. Bot status: {bot_status}")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False
        
        # Test WhatsApp API client
        logger.info("Testing WhatsApp API client...")
        api_client = WhatsAppAPIClient()
        
        try:
            auth_status = await api_client.check_auth()
            logger.info(f"WhatsApp API authentication: {auth_status}")
        except Exception as e:
            logger.error(f"WhatsApp API client test failed: {str(e)}")
            return False
        
        # Test summarizer
        logger.info("Testing OpenAI summarizer...")
        try:
            summarizer = OpenAISummarizer()
            
            # Create a simple test message
            now = datetime.now()
            yesterday = now - timedelta(days=1)
            
            test_messages = [
                {"sender_name": "User1", "message_text": "Hello everyone!", "timestamp": yesterday.strftime("%Y-%m-%d %H:%M:%S")},
                {"sender_name": "User2", "message_text": "Hi there! How is everyone doing?", "timestamp": yesterday.strftime("%Y-%m-%d %H:%M:%S")},
                {"sender_name": "User3", "message_text": "I'm good, thanks for asking!", "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")}
            ]
            
            # Test summarization with minimal messages
            logger.info("Generating test summary...")
            summary = summarizer.generate_summary(
                messages=test_messages, 
                start_date=yesterday,
                end_date=now
            )
            
            if summary:
                logger.info(f"Summary generated successfully ({len(summary)} characters)")
                logger.info(f"Summary: {summary[:100]}...")
            else:
                logger.error("Failed to generate summary")
                return False
                
        except Exception as e:
            logger.error(f"Summarizer test failed: {str(e)}")
            return False
        
        # Test WhatsApp bot initialization
        logger.info("Testing WhatsApp bot initialization...")
        try:
            # Note: According to bot.py, WhatsAppBot only takes db_operations as parameter
            bot = WhatsAppBot(db)
            logger.info("WhatsApp bot initialized successfully")
        except Exception as e:
            logger.error(f"WhatsApp bot initialization failed: {str(e)}")
            return False
        
        logger.info("All component tests completed successfully")
        return True
        
    except Exception as e:
        logger.exception(f"Unexpected error in application test: {str(e)}")
        return False
    finally:
        # Clean up resources
        if 'session' in locals():
            session.close()
            logger.info("Database session closed")


async def main():
    """Main function to run the test script."""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    
    logger.info("Starting WhatsApp Summarizer Bot application test")
    
    # Test the application components
    test_result = await test_app_components()
    
    if test_result:
        logger.info("Application test completed successfully")
    else:
        logger.error("Application test failed")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 