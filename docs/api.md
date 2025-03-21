# API Integration  
  
## Overview  
  
The WhatsApp Bot integrates with multiple external APIs to provide its functionality. This document outlines the API integration points and implementation details.  
  
## Green API  
  
The WhatsApp Bot uses Green API to send and receive WhatsApp messages.  
  
### Configuration  
  
```python  
# green_api_client.py  
import os  
import requests  
import logging  
from urllib.parse import urljoin  
  
  
class GreenAPIClient:  
    def __init__(self, instance_id=None, token=None):  
        """Initialize the Green API client >> api.md && echo. >> api.md && echo         Args: >> api.md && echo             instance_id (str, optional): Green API instance ID. Defaults to environment variable. >> api.md && echo             token (str, optional): Green API token. Defaults to environment variable. >> api.md && echo         """  
        self.instance_id = instance_id or os.getenv("GREEN_API_INSTANCE_ID")  
        self.token = token or os.getenv("GREEN_API_TOKEN")  
        self.base_url = f"https://api.green-api.com/waInstance{self.instance_id}/"  
  
        if not self.instance_id or not self.token:  
            raise ValueError("GREEN_API_INSTANCE_ID and GREEN_API_TOKEN must be set")  
```  
  
### Sending Messages  
  
```python  
def send_message(self, chat_id, message):  
    """Send a message to a WhatsApp chat >> api.md && echo. >> api.md && echo     Args: >> api.md && echo         chat_id (str): Chat ID in format '123456789@c.us' or '123456789-123456789@g.us' >> api.md && echo         message (str): Message text to send >> api.md && echo. >> api.md && echo     Returns: >> api.md && echo         dict: API response >> api.md && echo     """  
    endpoint = f"sendMessage/{self.token}"  
    url = urljoin(self.base_url, endpoint)  
  
    payload = {  
        "chatId": chat_id,  
        "message": message  
    }  
  
    try:  
        response = requests.post(url, json=payload)  
        response.raise_for_status()  
        result = response.json()  
        logging.info(f"Message sent to {chat_id} with ID: {result.get('idMessage')}")  
        return result  
    except requests.exceptions.RequestException as e:  
        logging.error(f"Failed to send message: {str(e)}")  
        raise  
```  
  
### Receiving Messages  
  
```python  
def receive_notification(self):  
    """Receive notification from the Green API queue >> api.md && echo. >> api.md && echo     Returns: >> api.md && echo         dict: Notification data or None if queue is empty >> api.md && echo     """  
    endpoint = f"receiveNotification/{self.token}"  
    url = urljoin(self.base_url, endpoint)  
  
    try:  
        response = requests.get(url)  
        response.raise_for_status()  
        result = response.json()  
  
        if result is None:  
            return None  # Queue is empty  
  
        return result  
    except requests.exceptions.RequestException as e:  
        logging.error(f"Failed to receive notification: {str(e)}")  
        return None  
```  
  
## OpenAI API  
  
The WhatsApp Bot uses OpenAI API to generate summaries of WhatsApp group messages.  
  
### Configuration  
  
```python  
# openai_client.py  
import os  
import time  
import logging  
import openai  
from datetime import datetime  
  
  
class OpenAIClient:  
    def __init__(self, api_key=None):  
        """Initialize the OpenAI client >> api.md && echo. >> api.md && echo         Args: >> api.md && echo             api_key (str, optional): OpenAI API key. Defaults to environment variable. >> api.md && echo         """  
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")  
        openai.api_key = self.api_key  
  
        if not self.api_key:  
            raise ValueError("OPENAI_API_KEY must be set")  
  
        # Validate API key format  
        if not self.api_key.startswith("sk-"):  
            logging.warning("OpenAI API key format appears to be invalid")  
```  
  
### Generating Summaries  
  
```python  
def generate_summary(self, messages, target_language="hebrew", progress_callback=None):  
    """Generate a summary of WhatsApp messages >> api.md && echo. >> api.md && echo     Args: >> api.md && echo         messages (list): List of message dictionaries >> api.md && echo         target_language (str): Language for the summary >> api.md && echo         progress_callback (function, optional): Callback for progress updates >> api.md && echo. >> api.md && echo     Returns: >> api.md && echo         str: Generated summary >> api.md && echo     """  
    start_time = time.time()  
    messages_text = self._prepare_messages(messages)  
  
    prompt = f""" >> api.md && echo     You are an assistant that summarizes WhatsApp group conversations. >> api.md && echo     Please create a concise summary of the following WhatsApp messages in {target_language}. >> api.md && echo     Focus on the main topics, important information, and key decisions. >> api.md && echo     Organize the summary by topics rather than by time. >> api.md && echo. >> api.md && echo     Messages: >> api.md && echo     {messages_text} >> api.md && echo     """  
  
    try:  
        response = openai.ChatCompletion.create(  
            model="gpt-3.5-turbo",  
            messages=[{"role": "system", "content": prompt}],  
            temperature=0.7,  
            max_tokens=1000,  
        )  
  
        summary = response.choices[0].message.content.strip()  
        duration = time.time() - start_time  
        logging.info(f"Summary generated in {duration:.2f} seconds")  
  
        return summary  
    except openai.error.OpenAIError as e:  
        logging.error(f"OpenAI API error: {str(e)}")  
        raise  
``` 
