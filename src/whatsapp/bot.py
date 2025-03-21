import os
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
from loguru import logger
from dotenv import load_dotenv

from .green_api_client import GreenAPIClient
from ..database.operations import DatabaseOperations
from ..core.summarizer import OpenAISummarizer

# Load environment variables
load_dotenv()

class WhatsAppBot:
    """WhatsApp Bot for message processing and summarization."""
    
    def __init__(self, db_operations: DatabaseOperations):
        """Initialize the WhatsApp bot."""
        self.api_client = GreenAPIClient()
        self.db = db_operations
        self.summarizer = OpenAISummarizer()
        self.active_group_ids = self._parse_group_ids()
        self.running = False
        self.background_mode = False
        self.test_mode = False
        self.retry_delay = int(os.getenv("BOT_RETRY_DELAY", "60"))
        self.max_retries = int(os.getenv("BOT_MAX_RETRIES", "3"))
        
        # Safety mechanism: track authorized groups for sending
        self.authorized_target_group = None
        self.message_sending_authorized = False
        
        # Update bot status
        self.db.update_bot_status(is_running=False, whatsapp_connected=False)
        
        logger.info(f"WhatsApp Bot initialized with {len(self.active_group_ids)} active groups")
    
    def _parse_group_ids(self) -> List[str]:
        """Parse the comma-separated list of group IDs from environment variables."""
        group_ids_str = os.getenv("WHATSAPP_GROUP_IDS", "")
        if not group_ids_str:
            logger.warning("No group IDs specified in WHATSAPP_GROUP_IDS")
            return []
            
        return [gid.strip() for gid in group_ids_str.split(",") if gid.strip()]
    
    async def check_connection(self) -> bool:
        """Check if the WhatsApp API connection is active."""
        try:
            status = self.api_client.get_instance_status()
            is_connected = status.get('stateInstance') == 'authorized'
            
            # Update bot status
            self.db.update_bot_status(whatsapp_connected=is_connected)
            
            if not is_connected:
                logger.error(f"WhatsApp instance not authorized. Status: {status.get('stateInstance')}")
                
            return is_connected
            
        except Exception as e:
            logger.error(f"Error checking WhatsApp connection: {str(e)}")
            self.db.update_bot_status(whatsapp_connected=False)
            return False
    
    async def start(self, background_mode: bool = False) -> bool:
        """Start the WhatsApp bot."""
        try:
            if not await self.check_connection():
                logger.error("Failed to start WhatsApp bot: Not connected to WhatsApp")
                return False
                
            self.running = True
            self.background_mode = background_mode
            
            # Reset message sending authorization on start
            self.authorized_target_group = None
            self.message_sending_authorized = False
            
            # Update bot status
            self.db.update_bot_status(is_running=True, is_background_mode=background_mode)
            
            logger.info(f"WhatsApp bot started in {'background' if background_mode else 'foreground'} mode")
            return True
            
        except Exception as e:
            logger.error(f"Error starting WhatsApp bot: {str(e)}")
            self.db.update_bot_status(is_running=False)
            return False
    
    async def stop(self) -> bool:
        """Stop the WhatsApp bot."""
        try:
            self.running = False
            self.background_mode = False
            
            # Reset message authorization
            self.authorized_target_group = None
            self.message_sending_authorized = False
            
            # Update bot status
            self.db.update_bot_status(is_running=False, is_background_mode=False)
            
            logger.info("WhatsApp bot stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping WhatsApp bot: {str(e)}")
            return False
    
    # SAFETY METHODS: Authorization for sending messages
    
    def set_target_group(self, group_id: str) -> bool:
        """
        Set the authorized target group for sending messages.
        This is a safety mechanism to prevent sending to unintended groups.
        
        Args:
            group_id: The group ID to authorize for message sending
            
        Returns:
            True if set successfully, False otherwise
        """
        if not group_id:
            logger.error("Cannot set empty group ID as target")
            return False
            
        # Validate group ID format
        if not group_id.endswith('@g.us'):
            logger.warning(f"Group ID {group_id} doesn't match expected format (should end with @g.us)")
            
        self.authorized_target_group = group_id
        logger.info(f"Target group set to: {group_id}")
        return True
    
    def authorize_message_sending(self, authorized: bool = True) -> None:
        """
        Set the message sending authorization flag.
        Messages will only be sent if this flag is True.
        
        Args:
            authorized: Whether message sending is authorized
        """
        self.message_sending_authorized = authorized
        logger.info(f"Message sending authorization set to: {authorized}")
    
    async def process_messages_loop(self) -> None:
        """Main loop for processing incoming messages."""
        retry_count = 0
        
        while self.running:
            try:
                notification = self.api_client.receive_notification()
                
                if notification:
                    receipt_id = notification.get('receiptId')
                    
                    # Process the message
                    processed = await self.process_notification(notification)
                    
                    # Delete the notification from the queue
                    if receipt_id:
                        self.api_client.delete_notification(receipt_id)
                        
                    # Reset retry counter on successful operation
                    retry_count = 0
                    
                else:
                    # If no notifications, sleep for a short time
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error in message processing loop: {str(e)}")
                retry_count += 1
                
                if retry_count > self.max_retries:
                    logger.critical(f"Exceeded maximum retries ({self.max_retries}). Stopping bot.")
                    await self.stop()
                    break
                    
                # Wait before retry
                await asyncio.sleep(self.retry_delay)
    
    async def process_notification(self, notification: Dict) -> bool:
        """Process a single notification."""
        try:
            # Extract the message data
            message_data = self.api_client.process_incoming_message(notification)
            
            if not message_data:
                return False
                
            chat_id = message_data.get('chat_id')
            
            # Check if this is a message from one of our monitored groups
            if not chat_id or chat_id not in self.active_group_ids:
                logger.debug(f"Ignoring message from non-monitored chat: {chat_id}")
                return False
                
            # Save the message to the database
            self.db.save_message(
                message_id=message_data.get('message_id'),
                chat_id=chat_id,
                sender_id=message_data.get('sender_id'),
                sender_name=message_data.get('sender_name'),
                message_text=message_data.get('message_text'),
                timestamp=datetime.fromtimestamp(int(message_data.get('timestamp')))
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing notification: {str(e)}")
            return False
    
    async def generate_summary(self, group_id: str, days: int = 1) -> Optional[Dict]:
        """Generate a summary of messages for a specific group."""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get unprocessed messages for the group within the date range
            messages = self.db.get_unprocessed_messages(group_id)
            
            # Check if we have enough messages to generate a summary
            min_messages = int(os.getenv("BOT_MIN_MESSAGES_FOR_SUMMARY", "5"))
            if len(messages) < min_messages:
                logger.info(f"Not enough messages to generate summary. Found {len(messages)}, minimum {min_messages}")
                return None
                
            # Generate summary using OpenAI
            message_texts = [f"{msg.sender_name}: {msg.message_text}" for msg in messages]
            summary_text = await self.summarizer.generate_summary(message_texts, start_date, end_date)
            
            if not summary_text:
                logger.error("Failed to generate summary")
                return None
                
            # Save the summary to the database
            summary = self.db.create_summary(
                group_id=group_id,
                summary_text=summary_text,
                start_date=start_date,
                end_date=end_date,
                message_count=len(messages)
            )
            
            # Mark the messages as processed
            message_ids = [msg.id for msg in messages]
            self.db.mark_messages_as_processed(message_ids, summary.id)
            
            # Update the bot status with the latest summary
            self.db.update_bot_status(last_summary_id=summary.id)
            
            logger.info(f"Generated summary for group {group_id} with {len(messages)} messages")
            
            return {
                'summary_id': summary.id,
                'group_id': group_id,
                'summary_text': summary_text,
                'message_count': len(messages)
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return None
    
    async def send_summary(self, summary_id: Union[int, Dict], target_group_id: str = None) -> bool:
        """Send a summary to a WhatsApp group."""
        try:
            # Get the summary object
            summary = None
            if isinstance(summary_id, dict) and 'summary_id' in summary_id:
                summary_id = summary_id['summary_id']
                
            summary = self.db.session.query(self.db.session.get_bind().get_mapper().mapped_table.name).get(summary_id)
            
            if not summary:
                logger.error(f"Summary with ID {summary_id} not found")
                return False
            
            # If no target group is specified, use the authorized target group
            if not target_group_id:
                target_group_id = self.authorized_target_group
            
            # SAFETY CHECK 1: Verify a target group is specified
            if not target_group_id:
                logger.error("No target group specified and no authorized target group set")
                return False
                
            # SAFETY CHECK 2: Verify message sending is authorized
            if not self.message_sending_authorized:
                logger.warning("Message sending not authorized. Summary not sent.")
                logger.info(f"Would have sent summary {summary_id} to group {target_group_id}")
                return False
                
            # Check if message sending is disabled in environment
            if os.getenv("BOT_MESSAGE_SENDING_DISABLED", "false").lower() == "true":
                logger.warning("Message sending is disabled in environment. Summary not sent.")
                return False
                
            # Send the summary to the group
            logger.info(f"Sending summary {summary_id} to group {target_group_id}")
            self.api_client.send_message(target_group_id, summary.summary_text)
            
            # Mark the summary as sent
            self.db.mark_summary_as_sent(summary.id)
            
            # Reset authorization after sending (one-time authorization)
            self.message_sending_authorized = False
            
            logger.info(f"Summary {summary_id} sent successfully to group {target_group_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending summary: {str(e)}")
            return False
    
    async def generate_and_send_summary(self, source_group_id: str, target_group_id: str = None, send: bool = False) -> Optional[Dict]:
        """Generate a summary and optionally send it to a group."""
        summary_result = await self.generate_summary(source_group_id)
        
        if not summary_result:
            logger.warning("Failed to generate summary")
            return None
            
        # If send flag is true, send the summary
        if send and target_group_id:
            sent = await self.send_summary(summary_result['summary_id'], target_group_id)
            summary_result['sent'] = sent
            
        return summary_result
    
    def set_active_groups(self, group_ids: List[str]) -> None:
        """Set the active groups to monitor."""
        self.active_group_ids = group_ids
        
        # Update environment variable
        os.environ["WHATSAPP_GROUP_IDS"] = ",".join(group_ids)
        
        logger.info(f"Updated active groups: {group_ids}")
        
    def set_test_mode(self, enabled: bool) -> None:
        """Enable or disable test mode."""
        self.test_mode = enabled
        logger.info(f"Test mode {'enabled' if enabled else 'disabled'}")
        
    def get_status(self) -> Dict:
        """Get the current status of the WhatsApp bot."""
        status = self.db.get_or_create_bot_status()
        
        # Check connection status in real-time
        connection_status = self.api_client.get_instance_status()
        is_connected = connection_status.get('stateInstance') == 'authorized'
        
        return {
            'running': self.running,
            'background_mode': self.background_mode,
            'test_mode': self.test_mode,
            'whatsapp_connected': is_connected,
            'active_groups': self.active_group_ids,
            'last_connected': status.last_connected,
            'last_summary_id': status.last_summary_id
        } 