import os
import json
from datetime import datetime
from typing import List, Optional
from loguru import logger
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

class OpenAISummarizer:
    """Class for generating summaries using OpenAI models."""
    
    def __init__(self):
        """Initialize the OpenAI summarizer with API keys."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "4000"))
        self.prompt_template = os.getenv("SUMMARY_PROMPT", "")
        
        if not self.api_key:
            logger.error("OpenAI API key not found")
            raise ValueError("OPENAI_API_KEY environment variable must be set")
            
        if not self.prompt_template:
            logger.warning("Summary prompt template not found, using default")
            self.prompt_template = "Summarize the following conversation:"
            
        # Set up the OpenAI client
        openai.api_key = self.api_key
        
        logger.debug(f"OpenAI summarizer initialized with model: {self.model}")
    
    async def generate_summary(self, messages: List[str], start_date: datetime, end_date: datetime) -> Optional[str]:
        """Generate a summary of the given messages using OpenAI."""
        try:
            if not messages:
                logger.warning("No messages provided for summarization")
                return None
                
            # Format the date range information
            date_info = {
                "date": end_date.strftime("%Y-%m-%d"),
                "start_time": start_date.strftime("%Y-%m-%d %H:%M"),
                "end_time": end_date.strftime("%Y-%m-%d %H:%M")
            }
            
            # Prepare the conversation text
            conversation_text = "\n".join(messages)
            
            # Build the prompt
            prompt = f"{self.prompt_template}\n\n"
            prompt += f"Date Range: {date_info['start_time']} to {date_info['end_time']}\n\n"
            prompt += f"Conversation:\n{conversation_text}"
            
            # Call the OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes group chats."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3  # Lower temperature for more consistent summaries
            )
            
            # Extract the summary text
            summary_text = response.choices[0].message.content.strip()
            
            # Log completion tokens for monitoring
            logger.debug(f"OpenAI API used {response.usage.completion_tokens} completion tokens")
            
            return summary_text
            
        except Exception as e:
            logger.error(f"Error generating summary with OpenAI: {str(e)}")
            return None
    
    def format_summary(self, summary_text: str, group_name: str = None) -> str:
        """Format the summary with additional information if needed."""
        if not group_name:
            group_name = os.getenv("GROUP_NAME", "WhatsApp Group")
            
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Check if the summary already has a title
        if not summary_text.startswith("#"):
            formatted_summary = f"# {group_name} Summary - {date_str}\n\n{summary_text}"
        else:
            formatted_summary = summary_text
            
        return formatted_summary 