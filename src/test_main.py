"""
Test script for the main module.

This script tests the initialization of all components
but exits after initialization is complete without starting the menu.
"""

import os
import sys
import asyncio
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the main module
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from src.database.connection import create_db_engine, get_db_session
from src.database.operations import DatabaseOperations
from src.whatsapp.api_client import WhatsAppAPIClient
from src.whatsapp.bot import WhatsAppBot
from src.nlp.summarizer import OpenAISummarizer
from src.scheduler.scheduler import Scheduler

# For Windows compatibility, we'll import the correct menu class
import platform
if platform.system() == 'Windows':
    from src.menu.windows_menu import WindowsBotMenu as BotMenu
else:
    from src.menu.terminal_menu import BotMenu


def setup_logging():
    """Configure logging for the test script."""
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )


async def test_initialization():
    """Test initializing all components."""
    logger.info("Starting initialization test...")
    
    try:
        # Initialize database components
        logger.info("Initializing database components...")
        engine = create_db_engine()
        session = get_db_session(engine)
        db_operations = DatabaseOperations(session)
        
        # Initialize WhatsApp API client
        logger.info("Initializing WhatsApp API client...")
        api_client = WhatsAppAPIClient()
        
        # Check API client authentication
        auth_status = await api_client.check_auth()
        logger.info(f"WhatsApp API authentication: {auth_status}")
        
        # Initialize WhatsApp bot
        logger.info("Initializing WhatsApp bot...")
        whatsapp_bot = WhatsAppBot(db_operations)
        
        # Initialize scheduler
        logger.info("Initializing scheduler...")
        scheduler = Scheduler(whatsapp_bot, db_operations)
        
        # Initialize the terminal menu
        logger.info("Initializing terminal menu...")
        terminal_menu = BotMenu(whatsapp_bot, db_operations)
        
        logger.info("All components initialized successfully")
        return True
    
    except Exception as e:
        logger.exception(f"Error during initialization: {str(e)}")
        return False
    
    finally:
        # Clean up resources
        if 'session' in locals():
            session.close()
            logger.info("Database session closed")


async def main():
    """Main function."""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    
    logger.info("Starting main module test")
    
    # Test initialization
    result = await test_initialization()
    
    if result:
        logger.info("Main module test completed successfully")
    else:
        logger.error("Main module test failed")


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main()) 