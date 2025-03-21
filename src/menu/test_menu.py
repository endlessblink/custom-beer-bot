"""
Test script for the Windows terminal menu.

This script creates mock objects to test the terminal menu
without requiring a full WhatsApp bot setup.
"""

import os
import sys
import platform
from pathlib import Path

# Add the parent directory to the path so we can import modules
parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(parent_dir))

from loguru import logger

# Create mock classes
class MockWhatsAppBot:
    """Mock WhatsApp bot for testing the menu."""
    
    def __init__(self):
        """Initialize the mock bot."""
        self.running = False
        self.background_mode = False
        self.active_groups = ["123456789", "987654321"]
    
    async def start(self, background_mode=False):
        """Start the mock bot."""
        self.running = True
        self.background_mode = background_mode
        logger.info(f"Mock bot started (background mode: {background_mode})")
        return True
    
    async def stop(self):
        """Stop the mock bot."""
        self.running = False
        logger.info("Mock bot stopped")
        return True
    
    async def check_connection(self):
        """Check connection to WhatsApp API."""
        logger.info("Checking mock WhatsApp connection")
        return True
    
    def get_status(self):
        """Get the status of the mock bot."""
        return {
            "running": self.running,
            "background_mode": self.background_mode,
            "whatsapp_connected": True,
            "active_groups": self.active_groups
        }


class MockDatabaseOperations:
    """Mock database operations for testing the menu."""
    
    def __init__(self):
        """Initialize mock database operations."""
        pass
    
    def get_message_count(self, group_id):
        """Get mock message count."""
        return 42
    
    def get_unprocessed_messages(self, group_id):
        """Get mock unprocessed messages."""
        return []


def main():
    """Main function to test the terminal menu."""
    # Set up logging
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    # Create mock objects
    mock_bot = MockWhatsAppBot()
    mock_db = MockDatabaseOperations()
    
    # Import the appropriate menu based on platform
    if platform.system() == 'Windows':
        from src.menu.windows_menu import WindowsBotMenu
        menu_class = WindowsBotMenu
    else:
        from src.menu.terminal_menu import BotMenu
        menu_class = BotMenu
    
    print(f"Using menu class: {menu_class.__name__}")
    
    # Create and start the menu
    terminal_menu = menu_class(mock_bot, mock_db)
    terminal_menu.start()


if __name__ == "__main__":
    main() 