import asyncio
import datetime
from typing import Dict, Any, Optional, Callable
from loguru import logger

from ..database.operations import DatabaseOperations
from ..whatsapp.bot import WhatsAppBot

class Scheduler:
    """Scheduler for managing automated summary generation."""
    
    def __init__(self, whatsapp_bot: WhatsAppBot, db_operations: DatabaseOperations):
        """Initialize the scheduler with a WhatsApp bot instance and database operations."""
        self.bot = whatsapp_bot
        self.db = db_operations
        self.running = False
        self.last_check = None
        self.check_interval = 30  # Check schedule every 30 seconds
    
    async def start(self):
        """Start the scheduler."""
        if self.running:
            logger.warning("Scheduler is already running")
            return False
        
        self.running = True
        logger.info("Scheduler started")
        
        # Run the scheduler loop
        asyncio.create_task(self.scheduler_loop())
        
        return True
    
    async def stop(self):
        """Stop the scheduler."""
        if not self.running:
            logger.warning("Scheduler is not running")
            return False
        
        self.running = False
        logger.info("Scheduler stopped")
        
        return True
    
    async def scheduler_loop(self):
        """Main scheduler loop that checks for scheduled tasks."""
        while self.running:
            try:
                schedule_config = self.db.get_schedule_config()
                
                if schedule_config and schedule_config.is_active:
                    current_time = datetime.datetime.now().time()
                    schedule_time_parts = schedule_config.schedule_time.split(":")
                    scheduled_time = datetime.time(
                        hour=int(schedule_time_parts[0]),
                        minute=int(schedule_time_parts[1])
                    )
                    
                    # Check if current time is close to the scheduled time
                    current_minutes = current_time.hour * 60 + current_time.minute
                    scheduled_minutes = scheduled_time.hour * 60 + scheduled_time.minute
                    
                    # Check if it's within the check interval window
                    if abs(current_minutes - scheduled_minutes) <= 1:
                        # Check if we already ran the task in this time window
                        current_date = datetime.datetime.now().date()
                        last_run_date = self.db.get_last_schedule_run_date()
                        
                        if not last_run_date or last_run_date < current_date:
                            logger.info(f"Running scheduled summary task at {current_time}")
                            
                            # Generate and send summary
                            await self._execute_scheduled_task(schedule_config)
                            
                            # Update last run date
                            self.db.update_last_schedule_run_date(current_date)
                            
                            # Sleep for 2 minutes to avoid running the task again in the same window
                            await asyncio.sleep(120)
            
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
            
            # Sleep for the check interval
            await asyncio.sleep(self.check_interval)
    
    async def _execute_scheduled_task(self, schedule_config):
        """Execute the scheduled task based on the configuration."""
        try:
            source_group_id = schedule_config.source_group_id
            target_group_id = schedule_config.target_group_id
            test_mode = schedule_config.test_mode
            
            logger.info(f"Generating scheduled summary for group {source_group_id}")
            
            # If in test mode, don't actually send the message
            send_summary = not test_mode
            
            result = await self.bot.generate_and_send_summary(
                source_group_id=source_group_id,
                target_group_id=target_group_id,
                send=send_summary
            )
            
            if result:
                if test_mode:
                    logger.info(f"Test mode - Summary generated but not sent: {result['summary_text'][:100]}...")
                else:
                    logger.info(f"Summary generated and sent: {result['summary_text'][:100]}...")
                    
                return True
            else:
                logger.warning("Failed to generate summary: Not enough messages or an error occurred")
                return False
        
        except Exception as e:
            logger.error(f"Error executing scheduled task: {e}")
            return False 