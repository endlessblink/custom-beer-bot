"""
Module for generating summaries using OpenAI.
"""

import os
import requests
import json
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime

class OpenAISummarizer:
    """Class to generate summaries using OpenAI API."""
    
    def __init__(self):
        """Initialize the summarizer with API key from environment."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "4000"))
        
        if not self.api_key:
            logger.warning("OpenAI API key not found in environment variables")
    
    def generate_summary(self, messages: List[Dict[str, Any]], 
                         start_date: datetime, 
                         end_date: datetime,
                         summary_prompt: Optional[str] = None) -> str:
        """
        Generate a summary of messages using OpenAI.
        
        Args:
            messages: List of message dictionaries with keys 'sender_name', 'message_text', 'timestamp'
            start_date: Start date of the summary period
            end_date: End date of the summary period
            summary_prompt: Optional custom prompt template
            
        Returns:
            A string containing the generated summary
        """
        try:
            # Format messages into a text prompt
            message_text = self._format_messages(messages)
            
            # Get the date range in string format
            date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            
            # Build the prompt
            base_prompt = summary_prompt or os.getenv("SUMMARY_PROMPT", "")
            
            if not base_prompt:
                base_prompt = """Create a comprehensive summary of the following WhatsApp chat messages.
Focus on key points, decisions, tasks assigned, and any important information shared.
Format the summary with clear sections and bullet points.
"""
            
            system_prompt = f"You are an expert summarizer tasked with creating a concise summary of WhatsApp messages for the period: {date_range}. The summary should be well-structured and capture all important information."
            
            user_prompt = f"{base_prompt}\n\nHere are the messages to summarize:\n\n{message_text}"
            
            # Call the OpenAI API directly with requests
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": self.max_tokens,
                "temperature": 0.7
            }
            
            logger.info(f"Sending request to OpenAI API using model {self.model}")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            
            # Process the response
            if response.status_code == 200:
                result = response.json()
                summary = result["choices"][0]["message"]["content"]
                logger.info(f"Successfully generated summary of {len(summary)} characters")
                return summary
            else:
                logger.error(f"Error from OpenAI API: {response.status_code} - {response.text}")
                return f"Error generating summary: API returned status code {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    def _format_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Format a list of messages into a text representation for the prompt."""
        formatted_text = ""
        
        for msg in messages:
            timestamp = msg.get('timestamp', datetime.utcnow())
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except (ValueError, TypeError):
                    timestamp = datetime.utcnow()
                    
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            sender = msg.get('sender_name', 'Unknown')
            text = msg.get('message_text', '')
            
            formatted_text += f"[{time_str}] {sender}: {text}\n\n"
        
        return formatted_text 