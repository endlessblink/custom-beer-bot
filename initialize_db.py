#!/usr/bin/env python3
"""
Database initialization script.

This script creates the initial database tables required by the application.
Run this script once before starting the application for the first time.
"""

import os
import sys
from dotenv import load_dotenv
from loguru import logger

def setup_logging():
    """Set up logging configuration."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )
    logger.add(
        "logs/db_init_{time}.log",
        rotation="1 MB", 
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )

def create_directories():
    """Create necessary directories."""
    os.makedirs("logs", exist_ok=True)

def initialize_database():
    """Initialize the database by creating tables."""
    try:
        # Import database models and setup
        from src.database.models import setup_database, Base
        from src.database.models import WhatsAppMessage, MessageSummary, ScheduleConfig, BotStatus
        
        logger.info("Setting up database tables...")
        
        # Create database session and tables
        session = setup_database()
        
        # Check if tables were created
        try:
            from sqlalchemy import inspect
            from src.database.connection import get_engine
            
            engine = get_engine()
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            logger.info(f"Tables in database: {', '.join(tables)}")
            print(f"Tables in database: {', '.join(tables)}")
            
            # Initialize BotStatus if it doesn't exist
            bot_status = session.query(BotStatus).first()
            if not bot_status:
                logger.info("Creating initial BotStatus record")
                bot_status = BotStatus(
                    is_running=False,
                    is_background_mode=False,
                    whatsapp_connected=False,
                    discord_connected=False,
                    database_connected=True
                )
                session.add(bot_status)
                session.commit()
                logger.info("Initial BotStatus record created")
            
            session.close()
            
            logger.info("Database initialization complete")
            print("✅ Database initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Error checking tables: {str(e)}")
            session.close()
            raise
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        print(f"❌ Error initializing database: {str(e)}")
        return False

def main():
    """Main entry point for the script."""
    # Create necessary directories
    create_directories()
    
    # Set up logging
    setup_logging()
    
    # Load environment variables
    load_dotenv()
    
    logger.info("Database initialization started")
    
    # Check database URL
    db_url = os.getenv("NEON_DATABASE_URL", "")
    if not db_url:
        logger.error("NEON_DATABASE_URL environment variable not found")
        print("Error: NEON_DATABASE_URL environment variable not found")
        return False
    
    # Check if SQLAlchemy is installed
    try:
        import sqlalchemy
        logger.info(f"SQLAlchemy version: {sqlalchemy.__version__}")
    except ImportError:
        logger.error("SQLAlchemy not installed")
        print("Error: SQLAlchemy not installed. Run: pip install sqlalchemy")
        return False
    
    # Initialize database
    success = initialize_database()
    
    if success:
        print("\nDatabase initialized successfully.")
        print("The application is now ready to use.")
        return True
    else:
        print("\nFailed to initialize database. Check the logs for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 