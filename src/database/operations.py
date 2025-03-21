from datetime import datetime, date
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_, func, desc
from loguru import logger
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from .models import WhatsAppMessage, MessageSummary, ScheduleConfig, BotStatus

class DatabaseOperations:
    """Class to handle common database operations."""
    
    def __init__(self, session: Session):
        """Initialize with a database session."""
        self.session = session
    
    # --- WhatsApp Message Operations ---
    
    def save_message(self, message_id, chat_id, sender_id, sender_name, message_text, timestamp=None):
        """Save a WhatsApp message to the database."""
        try:
            # Check if message already exists
            existing_message = self.session.query(WhatsAppMessage).filter_by(message_id=message_id).first()
            if existing_message:
                logger.debug(f"Message {message_id} already exists in database")
                return existing_message
            
            # Create new message
            message = WhatsAppMessage(
                message_id=message_id,
                chat_id=chat_id,
                sender_id=sender_id,
                sender_name=sender_name,
                message_text=message_text,
                timestamp=timestamp or datetime.utcnow()
            )
            
            self.session.add(message)
            self.session.commit()
            logger.debug(f"Saved new message from {sender_name}")
            return message
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving message: {str(e)}")
            raise
    
    def get_unprocessed_messages(self, chat_id, limit=None):
        """Get unprocessed messages for a specific chat."""
        query = self.session.query(WhatsAppMessage).filter(
            and_(
                WhatsAppMessage.chat_id == chat_id,
                WhatsAppMessage.is_processed == False
            )
        ).order_by(WhatsAppMessage.timestamp)
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def mark_messages_as_processed(self, message_ids, summary_id=None):
        """Mark messages as processed and link to a summary."""
        try:
            updates = {
                "is_processed": True
            }
            
            if summary_id is not None:
                updates["summary_id"] = summary_id
                
            updated = self.session.query(WhatsAppMessage).filter(
                WhatsAppMessage.id.in_(message_ids)
            ).update(updates, synchronize_session=False)
            
            self.session.commit()
            return updated
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error marking messages as processed: {str(e)}")
            raise
    
    def get_message_count(self, chat_id, from_date=None, to_date=None):
        """Get count of messages in a specific chat with optional date range."""
        query = self.session.query(func.count(WhatsAppMessage.id)).filter(
            WhatsAppMessage.chat_id == chat_id
        )
        
        if from_date:
            query = query.filter(WhatsAppMessage.timestamp >= from_date)
        
        if to_date:
            query = query.filter(WhatsAppMessage.timestamp <= to_date)
            
        return query.scalar()
    
    # --- Summary Operations ---
    
    def create_summary(self, group_id, summary_text, start_date, end_date, message_count):
        """Create a new summary record."""
        try:
            summary = MessageSummary(
                group_id=group_id,
                summary_text=summary_text,
                start_date=start_date,
                end_date=end_date,
                message_count=message_count,
                created_at=datetime.utcnow()
            )
            
            self.session.add(summary)
            self.session.commit()
            return summary
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating summary: {str(e)}")
            raise
    
    def mark_summary_as_sent(self, summary_id):
        """Mark a summary as sent to the group."""
        try:
            summary = self.session.query(MessageSummary).get(summary_id)
            if not summary:
                raise NoResultFound(f"Summary with ID {summary_id} not found")
            
            summary.sent_to_group = True
            summary.sent_at = datetime.utcnow()
            
            self.session.commit()
            return summary
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error marking summary as sent: {str(e)}")
            raise

    def get_latest_summary(self, group_id=None):
        """Get the latest summary, optionally filtered by group ID."""
        query = self.session.query(MessageSummary).order_by(MessageSummary.created_at.desc())
        
        if group_id:
            query = query.filter(MessageSummary.group_id == group_id)
            
        return query.first()
    
    def get_summaries_by_date_range(self, start_date, end_date):
        """Get summaries created within a date range."""
        return self.session.query(MessageSummary).filter(
            and_(
                MessageSummary.created_at >= start_date,
                MessageSummary.created_at <= end_date
            )
        ).order_by(MessageSummary.created_at).all()
    
    # --- Schedule Config Operations ---
    
    def save_schedule_config(self, source_group_id, target_group_id, schedule_time, is_active=False, test_mode=False):
        """Save a schedule configuration."""
        try:
            # First check if we already have a config, we'll update it instead of creating a new one
            existing_config = self.session.query(ScheduleConfig).first()
            
            if existing_config:
                existing_config.source_group_id = source_group_id
                existing_config.target_group_id = target_group_id
                existing_config.schedule_time = schedule_time
                existing_config.is_active = is_active
                existing_config.test_mode = test_mode
                existing_config.updated_at = datetime.utcnow()
            else:
                config = ScheduleConfig(
                    source_group_id=source_group_id,
                    target_group_id=target_group_id,
                    schedule_time=schedule_time,
                    is_active=is_active,
                    test_mode=test_mode
                )
                self.session.add(config)
                
            self.session.commit()
            return existing_config or config
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving schedule config: {str(e)}")
            raise
    
    def get_schedule_config(self):
        """Get the current schedule configuration."""
        return self.session.query(ScheduleConfig).first()
    
    def update_schedule_status(self, is_active):
        """Update the active status of the schedule."""
        try:
            config = self.session.query(ScheduleConfig).first()
            if not config:
                return None
                
            config.is_active = is_active
            config.updated_at = datetime.utcnow()
            
            self.session.commit()
            return config
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating schedule status: {str(e)}")
            raise
    
    def update_last_schedule_run_date(self, run_date: date) -> bool:
        """Update the last run date for the schedule."""
        try:
            config = self.session.query(ScheduleConfig).first()
            
            if not config:
                logger.warning("No schedule configuration found")
                return False
            
            config.last_run_date = run_date
            config.updated_at = datetime.now()
            
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating last schedule run date: {e}")
            return False
    
    def get_last_schedule_run_date(self) -> Optional[date]:
        """Get the last run date for the schedule."""
        config = self.session.query(ScheduleConfig).first()
        
        if not config:
            return None
            
        return config.last_run_date
    
    # --- Bot Status Operations ---
    
    def get_or_create_bot_status(self):
        """Get or create the bot status record."""
        status = self.session.query(BotStatus).first()
        
        if not status:
            status = BotStatus()
            self.session.add(status)
            self.session.commit()
            
        return status
    
    def update_bot_status(self, is_running=None, is_background_mode=None, 
                         whatsapp_connected=None, discord_connected=None, 
                         database_connected=None, last_summary_id=None):
        """Update the bot status with the provided values."""
        try:
            status = self.get_or_create_bot_status()
            
            if is_running is not None:
                status.is_running = is_running
                
            if is_background_mode is not None:
                status.is_background_mode = is_background_mode
                
            if whatsapp_connected is not None:
                status.whatsapp_connected = whatsapp_connected
                
            if discord_connected is not None:
                status.discord_connected = discord_connected
                
            if database_connected is not None:
                status.database_connected = database_connected
                
            if last_summary_id is not None:
                status.last_summary_id = last_summary_id
                
            status.last_connected = datetime.utcnow()
            
            self.session.commit()
            return status
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating bot status: {str(e)}")
            raise 