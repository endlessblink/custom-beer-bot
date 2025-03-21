from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, create_engine, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

Base = declarative_base()

class WhatsAppMessage(Base):
    """Model for storing WhatsApp messages from groups."""
    __tablename__ = 'whatsapp_messages'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(String(128), unique=True, index=True)
    chat_id = Column(String(128), index=True)
    sender_id = Column(String(128))
    sender_name = Column(String(255))
    message_text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)
    
    # Relationship with summaries
    summary_id = Column(Integer, ForeignKey('message_summaries.id', ondelete='SET NULL'), nullable=True)
    
    def __repr__(self):
        return f"<WhatsAppMessage(id={self.id}, sender='{self.sender_name}', timestamp='{self.timestamp}')>"


class MessageSummary(Base):
    """Model for storing generated summaries of WhatsApp messages."""
    __tablename__ = 'message_summaries'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(String(128), index=True)
    summary_text = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_to_group = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    
    # Relationship with messages
    messages = relationship("WhatsAppMessage", backref="summary")
    
    def __repr__(self):
        return f"<MessageSummary(id={self.id}, group='{self.group_id}', created='{self.created_at}')>"


class ScheduleConfig(Base):
    """Model for storing scheduling configurations."""
    __tablename__ = 'schedule_configs'
    
    id = Column(Integer, primary_key=True)
    source_group_id = Column(String(128))
    target_group_id = Column(String(128))
    schedule_time = Column(String(10))  # Format: "HH:MM"
    is_active = Column(Boolean, default=False)
    test_mode = Column(Boolean, default=False)
    last_run_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ScheduleConfig(id={self.id}, time='{self.schedule_time}', active={self.is_active})>"


class BotStatus(Base):
    """Model for storing bot status information."""
    __tablename__ = 'bot_status'
    
    id = Column(Integer, primary_key=True)
    is_running = Column(Boolean, default=False)
    is_background_mode = Column(Boolean, default=False)
    last_connected = Column(DateTime, nullable=True)
    last_summary_id = Column(Integer, ForeignKey('message_summaries.id', ondelete='SET NULL'), nullable=True)
    whatsapp_connected = Column(Boolean, default=False)
    discord_connected = Column(Boolean, default=False)
    database_connected = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<BotStatus(running={self.is_running}, background={self.is_background_mode})>"


# Database setup function
def setup_database():
    """Set up the database connection and create tables if they don't exist."""
    database_url = os.getenv("NEON_DATABASE_URL")
    
    if not database_url:
        raise ValueError("Database URL not found in environment variables")
    
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return Session() 