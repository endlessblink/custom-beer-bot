"""
Database connection module for the WhatsApp Bot.

This module provides functions for establishing database connections and managing sessions
using SQLAlchemy's connection pooling features.
"""

import os
import time
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

# Load environment variables
load_dotenv()

# Initialize engine at module level
_engine = None
_Session = None


def get_database_url():
    """Get the database URL from environment variables."""
    db_url = os.getenv("NEON_DATABASE_URL")
    if not db_url:
        raise ValueError("NEON_DATABASE_URL not found in environment variables")
    return db_url


def create_db_engine(database_url=None, pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=1800):
    """
    Create a SQLAlchemy engine with connection pooling.
    
    Args:
        database_url: The database URL. If None, gets from environment variables.
        pool_size: The number of connections to keep open in the pool.
        max_overflow: The maximum number of connections to create beyond pool_size.
        pool_timeout: The number of seconds to wait for a connection.
        pool_recycle: The number of seconds after which a connection is recycled.
        
    Returns:
        SQLAlchemy engine instance.
    """
    if database_url is None:
        database_url = get_database_url()
    
    return create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        pool_pre_ping=True
    )


def get_engine():
    """Get or create the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


def get_session_factory():
    """Get or create the session factory."""
    global _Session
    if _Session is None:
        engine = get_engine()
        _Session = sessionmaker(bind=engine)
    return _Session


def get_db_session(engine=None):
    """
    Create a new database session.
    
    Args:
        engine: Optional SQLAlchemy engine. If None, uses the default engine.
        
    Returns:
        SQLAlchemy session.
    """
    if engine:
        Session = sessionmaker(bind=engine)
        return Session()
    else:
        Session = get_session_factory()
        return Session()


@contextmanager
def session_scope():
    """
    Context manager for database sessions.
    
    Usage:
        with session_scope() as session:
            # Use session here
    
    The session will be committed if no exceptions occur, 
    or rolled back if an exception is raised.
    """
    session = get_db_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        session.close()


def test_connection():
    """Test the database connection."""
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
                logger.info("Database connection successful")
                return True
        except Exception as e:
            logger.warning(f"Connection attempt {attempt+1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
    
    logger.error(f"Failed to connect to database after {max_retries} attempts")
    return False 