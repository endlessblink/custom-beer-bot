import requests
import json
import time
import os
from loguru import logger
from typing import Dict, List, Union, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GreenAPIClient:
    """Client for interacting with the Green API for WhatsApp."""
    
    def __init__(self):
        """Initialize the Green API client with credentials from environment variables."""
        self.id_instance = os.getenv("GREEN_API_ID_INSTANCE")
        self.api_token = os.getenv("GREEN_API_TOKEN")
        self.base_url = os.getenv("GREEN_API_BASE_URL", "https://api.greenapi.com")
        self.delay = int(os.getenv("GREEN_API_DELAY", "1000")) / 1000  # Convert to seconds
        
        if not self.id_instance or not self.api_token:
            raise ValueError("GREEN_API_ID_INSTANCE and GREEN_API_TOKEN environment variables must be set")
        
        logger.debug(f"Green API client initialized with instance ID: {self.id_instance}")
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make a request to the Green API."""
        url = f"{self.base_url}/waInstance{self.id_instance}/{endpoint}/{self.api_token}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            time.sleep(self.delay)  # Respect rate limits
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            raise
    
    def get_instance_status(self) -> Dict:
        """Get the status of the WhatsApp instance."""
        return self._make_request('GET', 'getStateInstance')
    
    def receive_notification(self) -> Optional[Dict]:
        """Receive the next notification from the queue."""
        response = self._make_request('GET', 'receiveNotification')
        if response and response.get('receiptId'):
            return response
        return None
    
    def delete_notification(self, receipt_id: int) -> Dict:
        """Delete a notification from the queue after processing."""
        return self._make_request('DELETE', f'deleteNotification/{receipt_id}')
    
    def send_message(self, chat_id: str, message: str) -> Dict:
        """Send a text message to a specific chat."""
        data = {
            'chatId': chat_id,
            'message': message
        }
        return self._make_request('POST', 'sendMessage', data)
    
    def get_chat_history(self, chat_id: str, count: int = 100) -> List[Dict]:
        """Get the chat history for a specific chat."""
        data = {
            'chatId': chat_id,
            'count': count
        }
        return self._make_request('POST', 'getChatHistory', data)
    
    def create_group(self, group_name: str, participants: List[str]) -> Dict:
        """Create a new WhatsApp group."""
        data = {
            'groupName': group_name,
            'participants': participants
        }
        return self._make_request('POST', 'createGroup', data)
    
    def get_group_data(self, group_id: str) -> Dict:
        """Get information about a WhatsApp group."""
        data = {
            'groupId': group_id
        }
        return self._make_request('POST', 'getGroupData', data)
    
    def send_file_by_url(self, chat_id: str, file_url: str, caption: str = "", filename: str = "") -> Dict:
        """Send a file from a URL to a specific chat."""
        data = {
            'chatId': chat_id,
            'urlFile': file_url,
            'caption': caption,
            'fileName': filename
        }
        return self._make_request('POST', 'sendFileByUrl', data)
    
    def mark_as_read(self, chat_id: str) -> Dict:
        """Mark all messages in a chat as read."""
        data = {
            'chatId': chat_id
        }
        return self._make_request('POST', 'readChat', data)
    
    def process_incoming_message(self, notification: Dict) -> Optional[Dict]:
        """Process an incoming message notification and extract relevant data."""
        if not notification or not notification.get('body'):
            return None
            
        body = notification.get('body', {})
        
        # Check if it's a message notification
        if body.get('typeWebhook') != 'incomingMessageReceived':
            return None
            
        message_data = body.get('messageData', {})
        
        # Currently we only process text messages
        if message_data.get('typeMessage') != 'textMessage':
            logger.debug(f"Skipping non-text message of type: {message_data.get('typeMessage')}")
            return None
            
        sender_data = body.get('senderData', {})
        
        processed_message = {
            'message_id': body.get('idMessage'),
            'chat_id': sender_data.get('chatId'),
            'sender_id': sender_data.get('sender'),
            'sender_name': sender_data.get('senderName', 'Unknown'),
            'message_text': message_data.get('textMessageData', {}).get('textMessage', ''),
            'timestamp': body.get('timestamp')
        }
        
        return processed_message

    def get_contacts(self) -> List[Dict]:
        """Get all contacts including users and group chats."""
        try:
            contacts = self._make_request('GET', 'getContacts')
            logger.info(f"Retrieved {len(contacts)} contacts from WhatsApp")
            return contacts
        except Exception as e:
            logger.error(f"Error getting contacts: {str(e)}")
            return []
    
    def is_group_message(self, chat_id: str) -> bool:
        """Check if a chat ID corresponds to a group."""
        return chat_id and chat_id.endswith('@g.us')
        
    def extract_group_id(self, chat_id: str) -> Optional[str]:
        """Extract the group ID from a chat ID if it's a group chat."""
        if self.is_group_message(chat_id):
            return chat_id
        return None 