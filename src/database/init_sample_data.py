#!/usr/bin/env python
"""
Database sample data initialization script for WhatsApp Group Summarizer Bot.
This script inserts sample data for testing purposes.
"""

import os
import sys
from dotenv import load_dotenv
from loguru import logger
from datetime import datetime, time, date

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import models and database
from src.database.models import (
    WhatsAppMessage, 
    MessageSummary, 
    ScheduleConfig, 
    BotStatus,
    setup_database
)

def init_schedule_configs(session):
    """Initialize schedule configuration data."""
    # Check if data already exists
    existing = session.query(ScheduleConfig).first()
    if existing:
        logger.info("Schedule configurations already exist, skipping...")
        return
    
    # Get WhatsApp group ID from environment
    load_dotenv()
    group_id = os.getenv("WHATSAPP_GROUP_IDS", "").split(",")[0].strip()
    
    if not group_id:
        logger.warning("No WhatsApp group ID found in environment variables")
        group_id = "120363271484974874@g.us"  # Use default group ID
    
    # Create schedule configuration
    schedule = ScheduleConfig(
        source_group_id=group_id,
        target_group_id=group_id,  # Same group for both source and target
        schedule_time="20:00",     # Schedule summary at 8 PM
        is_active=True,
        test_mode=False,
        last_run_date=date.today()
    )
    
    session.add(schedule)
    session.commit()
    logger.info(f"Created schedule configuration: {schedule}")

def init_bot_status(session):
    """Initialize bot status data."""
    # Check if data already exists
    existing = session.query(BotStatus).first()
    if existing:
        logger.info("Bot status already exists, updating...")
        existing.database_connected = True
        existing.last_connected = datetime.now()
        session.commit()
        logger.info(f"Updated bot status: {existing}")
        return
    
    # Create bot status
    status = BotStatus(
        is_running=False,
        is_background_mode=False,
        last_connected=datetime.now(),
        whatsapp_connected=False,
        discord_connected=False,
        database_connected=True
    )
    
    session.add(status)
    session.commit()
    logger.info(f"Created bot status: {status}")

def main():
    """Initialize sample data in the database."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Check if NEON_DATABASE_URL exists
        db_url = os.getenv("NEON_DATABASE_URL")
        if not db_url:
            logger.error("NEON_DATABASE_URL not found in environment variables")
            return False
        
        logger.info("Connecting to database...")
        
        # Setup database session
        session = setup_database()
        
        # Initialize sample data
        init_schedule_configs(session)
        init_bot_status(session)
        
        # Close the session
        session.close()
        
        logger.info("Sample data initialization completed")
        return True
    
    except Exception as e:
        logger.error(f"Error initializing sample data: {str(e)}")
        return False

if __name__ == "__main__":
    # Configure logger
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    success = main()
    
    if not success:
        sys.exit(1) 