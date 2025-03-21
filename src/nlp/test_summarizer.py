#!/usr/bin/env python
"""
Test script for OpenAI summarizer.
This script verifies the functionality of the OpenAI summarizer.
"""

import os
import sys
from dotenv import load_dotenv
from loguru import logger
from datetime import datetime, timedelta
import json

# Add parent directory to path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import summarizer
from src.nlp.summarizer import OpenAISummarizer

def main():
    """Test the OpenAI summarizer."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Configure logger
        logger.remove()
        logger.add(sys.stderr, level="INFO")
        
        logger.info("Testing OpenAI summarizer...")
        
        # Create sample messages
        sample_messages = [
            {
                "sender_name": "User 1",
                "message_text": "Hey everyone, let's talk about the new AI models that were released this week.",
                "timestamp": datetime.now() - timedelta(hours=5)
            },
            {
                "sender_name": "User 2",
                "message_text": "I've been experimenting with GPT-4 for my project, and the results are impressive!",
                "timestamp": datetime.now() - timedelta(hours=4)
            },
            {
                "sender_name": "User 3",
                "message_text": "Has anyone tried using it for code generation? I'm having some issues with handling complex logic.",
                "timestamp": datetime.now() - timedelta(hours=3)
            },
            {
                "sender_name": "User 1",
                "message_text": "I found that providing detailed context and examples helps a lot with complex code generation.",
                "timestamp": datetime.now() - timedelta(hours=2)
            },
            {
                "sender_name": "User 4",
                "message_text": "There's also a new paper on prompt engineering techniques that might be helpful: https://example.com/paper",
                "timestamp": datetime.now() - timedelta(hours=1)
            },
            {
                "sender_name": "User 2",
                "message_text": "Thanks for sharing! I'll check it out. By the way, are we meeting next week to discuss the project progress?",
                "timestamp": datetime.now() - timedelta(minutes=30)
            },
            {
                "sender_name": "User 3",
                "message_text": "Yes, Tuesday at 3 PM works for me.",
                "timestamp": datetime.now() - timedelta(minutes=15)
            }
        ]
        
        # Set date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        # Initialize summarizer
        summarizer = OpenAISummarizer()
        
        # Check if API key is available
        if not summarizer.api_key:
            logger.error("OpenAI API key not found in environment variables")
            return False
        
        # Generate summary
        logger.info("Generating summary for sample messages...")
        summary = summarizer.generate_summary(
            sample_messages,
            start_date,
            end_date
        )
        
        # Print the summary
        logger.info("\n--- Generated Summary ---\n")
        print(summary)
        logger.info("\n------------------------\n")
        
        logger.info("OpenAI summarizer test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error testing OpenAI summarizer: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        sys.exit(1) 