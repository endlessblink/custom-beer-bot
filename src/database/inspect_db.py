#!/usr/bin/env python
"""
Database inspection script for WhatsApp Group Summarizer Bot.
This script connects to the database and verifies that all tables were created correctly.
"""

import os
import sys
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import models
from src.database.models import Base, WhatsAppMessage, MessageSummary, ScheduleConfig, BotStatus

def main():
    """Inspect database tables and their structure."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Check if NEON_DATABASE_URL exists
        db_url = os.getenv("NEON_DATABASE_URL")
        if not db_url:
            logger.error("NEON_DATABASE_URL not found in environment variables")
            return False
        
        logger.info("Connecting to database...")
        
        # Create engine and inspector
        engine = create_engine(db_url)
        inspector = inspect(engine)
        
        # Get list of tables
        tables = inspector.get_table_names()
        logger.info(f"Found {len(tables)} tables in the database:")
        for table in tables:
            logger.info(f"  - {table}")
            
            # Get columns for each table
            columns = inspector.get_columns(table)
            logger.info(f"    Columns:")
            for column in columns:
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                logger.info(f"      - {column['name']} ({str(column['type'])}): {nullable}")
            
            # Get primary keys
            pks = inspector.get_pk_constraint(table)
            if pks and pks.get('constrained_columns'):
                logger.info(f"    Primary Key: {', '.join(pks['constrained_columns'])}")
            
            # Get foreign keys
            fks = inspector.get_foreign_keys(table)
            if fks:
                for fk in fks:
                    logger.info(f"    Foreign Key: {', '.join(fk['constrained_columns'])} -> "
                                f"{fk['referred_table']}.{', '.join(fk['referred_columns'])}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error inspecting database: {str(e)}")
        return False

if __name__ == "__main__":
    # Configure logger
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    success = main()
    
    if not success:
        sys.exit(1) 