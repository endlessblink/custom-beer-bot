"""
WhatsApp API Client for Green API.

This module provides a client to interact with the Green API for WhatsApp communication.
"""

import requests
import json
import os
import time
import asyncio
from dotenv import load_dotenv
from loguru import logger

class WhatsAppAPIClient:
    """Client for interacting with Green API for WhatsApp."""
    
    def __init__(self, api_id=None, api_token=None, base_url=None):
        """
        Initialize the WhatsApp API client.
        
        Args:
            api_id: Green API ID instance. If None, gets from environment.
            api_token: Green API token. If None, gets from environment.
            base_url: Green API base URL. If None, gets from environment.
        """
        # Load environment variables if needed
        load_dotenv()
        
        # Set credentials
        self.api_id = api_id or os.getenv("GREEN_API_ID_INSTANCE")
        self.api_token = api_token or os.getenv("GREEN_API_TOKEN")
        self.base_url = base_url or os.getenv("GREEN_API_BASE_URL", "https://api.greenapi.com")
        
        # Check credentials
        if not self.api_id or not self.api_token:
            raise ValueError("GREEN_API_ID_INSTANCE and GREEN_API_TOKEN must be provided")
        
        # API delay to avoid rate limiting
        self.api_delay = int(os.getenv("GREEN_API_DELAY", "1000")) / 1000  # Convert to seconds
        
        logger.debug(f"WhatsApp API client initialized with ID: {self.api_id}")
    
    def _make_request(self, endpoint, method="GET", data=None, params=None):
        """
        Make a request to the Green API.
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method (GET, POST, DELETE)
            data: Request data for POST requests
            params: URL parameters for GET requests
            
        Returns:
            Response JSON data or None if failed
        """
        url = f"{self.base_url}/waInstance{self.api_id}/{endpoint}/{self.api_token}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method == "POST":
                response = requests.post(url, data=json.dumps(data), headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, params=params, headers=headers)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            # Add delay to avoid rate limiting
            time.sleep(self.api_delay)
            
            # Check response
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API request failed. Status code: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error making API request: {str(e)}")
            return None
    
    async def check_auth(self):
        """
        Check if the WhatsApp instance is authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        logger.debug("Checking authentication status...")
        
        # Create an executor task to run the synchronous API call in a separate thread
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: self._make_request("getStateInstance")
        )
        
        if response and response.get("stateInstance") == "authorized":
            logger.info("WhatsApp instance is authorized")
            return True
        else:
            logger.warning("WhatsApp instance is not authorized or connection failed")
            if response:
                logger.warning(f"State: {response.get('stateInstance')}")
            return False
    
    def send_message(self, chat_id, message):
        """
        Send a message to a specific chat.
        
        Args:
            chat_id: Chat ID to send the message to
            message: Message text to send
            
        Returns:
            Message ID if sent successfully, None otherwise
        """
        logger.debug(f"Sending message to {chat_id}")
        
        data = {
            "chatId": chat_id,
            "message": message
        }
        
        response = self._make_request("sendMessage", method="POST", data=data)
        
        if response and response.get("idMessage"):
            logger.info(f"Message sent successfully. ID: {response.get('idMessage')}")
            return response.get("idMessage")
        else:
            logger.error("Failed to send message")
            return None
    
    def receive_notification(self):
        """
        Receive a notification from the Green API.
        
        Returns:
            Notification data if received, None otherwise
        """
        logger.debug("Receiving notification...")
        
        response = self._make_request("receiveNotification")
        
        if response and response.get("receiptId"):
            logger.info(f"Notification received. ID: {response.get('receiptId')}")
            return response
        else:
            logger.debug("No notifications available")
            return None
    
    def delete_notification(self, receipt_id):
        """
        Delete a notification from the queue after processing.
        
        Args:
            receipt_id: Receipt ID of the notification to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        logger.debug(f"Deleting notification with ID: {receipt_id}")
        
        response = self._make_request("deleteNotification", method="DELETE", params={"receiptId": receipt_id})
        
        if response and response.get("result"):
            logger.info(f"Notification {receipt_id} deleted successfully")
            return True
        else:
            logger.error(f"Failed to delete notification {receipt_id}")
            return False
    
    def get_group_data(self, group_id):
        """
        Get data about a specific WhatsApp group.
        
        Args:
            group_id: Group ID to get data for
            
        Returns:
            Group data if retrieved successfully, None otherwise
        """
        logger.debug(f"Getting data for group: {group_id}")
        
        data = {
            "groupId": group_id
        }
        
        response = self._make_request("getGroupData", method="POST", data=data)
        
        if response:
            logger.info(f"Group data retrieved successfully for: {group_id}")
            return response
        else:
            logger.error(f"Failed to retrieve group data for: {group_id}")
            return None
    
    def get_chat_history(self, chat_id, count=100):
        """
        Get chat history for a specific chat.
        
        Args:
            chat_id: Chat ID to get history for
            count: Number of messages to retrieve (max 100)
            
        Returns:
            List of messages if retrieved successfully, None otherwise
        """
        logger.debug(f"Getting chat history for: {chat_id}")
        
        data = {
            "chatId": chat_id,
            "count": min(count, 100)  # Maximum 100 messages per request
        }
        
        response = self._make_request("getChatHistory", method="POST", data=data)
        
        if response:
            logger.info(f"Chat history retrieved successfully. {len(response)} messages found")
            return response
        else:
            logger.error(f"Failed to retrieve chat history for: {chat_id}")
            return None 