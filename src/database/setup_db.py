#!/usr/bin/env python
"""
Database setup script for WhatsApp Group Summarizer Bot.
This script creates all required tables in the Neon PostgreSQL database.
"""

import os
import sys
from dotenv import load_dotenv
from loguru import logger

# Add parent directory to path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import models
from src.database.models import Base, setup_database, WhatsAppMessage, MessageSummary, ScheduleConfig, BotStatus

def main():
    """Set up the database tables."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Check if NEON_DATABASE_URL exists
        db_url = os.getenv("NEON_DATABASE_URL")
        if not db_url:
            logger.error("NEON_DATABASE_URL not found in environment variables")
            return False
        
        logger.info("Setting up database tables...")
        
        # Setup database session
        session = setup_database()
        
        logger.info("Database tables created successfully")
        logger.info(f"Tables: {', '.join([c.__tablename__ for c in [WhatsAppMessage, MessageSummary, ScheduleConfig, BotStatus]])}")
        
        # Close the session
        session.close()
        
        return True
    
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        return False

if __name__ == "__main__":
    # Configure logger
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    success = main()
    
    if success:
        logger.info("Database setup completed successfully")
    else:
        logger.error("Database setup failed")
        sys.exit(1) 