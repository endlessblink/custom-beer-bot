#!/usr/bin/env python3
"""
Database connection test script.

This script tests the connection to the database and provides diagnostic information.
Run this script to verify your database configuration is working properly.
"""

import os
import sys
from dotenv import load_dotenv
from loguru import logger
import time

def setup_logging():
    """Set up logging configuration."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )
    logger.add(
        "logs/db_test_{time}.log",
        rotation="1 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )

def main():
    """Main entry point for the script."""
    # Set up logging
    setup_logging()
    
    # Load environment variables
    load_dotenv()
    
    logger.info("Database connection test started")
    
    # Print database URL (with password masked)
    db_url = os.getenv("NEON_DATABASE_URL", "")
    if db_url:
        # Basic masking of password in the URL for logging
        masked_url = db_url
        if ":" in db_url and "@" in db_url:
            parts = db_url.split(":")
            if len(parts) >= 3:
                user_part = parts[1].lstrip("/")
                host_part = parts[2].split("@", 1)[1] if len(parts[2].split("@", 1)) > 1 else ""
                masked_url = f"{parts[0]}://{user_part}:****@{host_part}"
        logger.info(f"Database URL: {masked_url}")
    else:
        logger.error("NEON_DATABASE_URL environment variable not found")
        print("Error: NEON_DATABASE_URL environment variable not found")
        return False
    
    # Try to import SQLAlchemy
    try:
        import sqlalchemy
        logger.info(f"SQLAlchemy version: {sqlalchemy.__version__}")
    except ImportError:
        logger.error("SQLAlchemy not installed")
        print("Error: SQLAlchemy not installed. Run: pip install sqlalchemy")
        return False
    
    # Try to import database connection modules
    try:
        from src.database.connection import test_connection, get_engine
        logger.info("Successfully imported database connection module")
    except ImportError as e:
        logger.error(f"Failed to import database connection module: {str(e)}")
        print(f"Error: Failed to import database connection module: {str(e)}")
        return False
    
    # Test connection
    try:
        logger.info("Testing database connection...")
        start_time = time.time()
        connection_success = test_connection()
        elapsed_time = time.time() - start_time
        
        if connection_success:
            logger.info(f"Connection successful! Time: {elapsed_time:.2f} seconds")
            print(f"✅ Database connection successful! Time: {elapsed_time:.2f} seconds")
            
            # Get more details about the connection
            engine = get_engine()
            with engine.connect() as conn:
                # Get database info
                try:
                    from sqlalchemy import text
                    version_result = conn.execute(text("SHOW server_version")).scalar()
                    logger.info(f"PostgreSQL version: {version_result}")
                    print(f"PostgreSQL version: {version_result}")
                    
                    # Test table query
                    try:
                        # Try to get the list of tables
                        table_result = conn.execute(text(
                            "SELECT table_name FROM information_schema.tables "
                            "WHERE table_schema = 'public'"
                        ))
                        tables = [row[0] for row in table_result]
                        logger.info(f"Tables found: {', '.join(tables) if tables else 'No tables found'}")
                        print(f"Tables in database: {', '.join(tables) if tables else 'No tables found'}")
                    except Exception as e:
                        logger.error(f"Error querying tables: {str(e)}")
                except Exception as e:
                    logger.error(f"Error getting database version: {str(e)}")
            
            return True
        else:
            logger.error("Connection failed")
            print("❌ Database connection failed")
            return False
    except Exception as e:
        logger.error(f"Error during connection test: {str(e)}")
        print(f"❌ Error during connection test: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 