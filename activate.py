#!/usr/bin/env python3
"""
WhatsApp Bot Activation Script

This script provides a simple way to start the WhatsApp bot
with the Windows menu interface.

Usage:
    python activate.py
"""

import os
import sys
from dotenv import load_dotenv
from loguru import logger

def main():
    """Main entry point for the activation script."""
    # Load environment variables
    load_dotenv()
    
    # Import the main module and run it
    try:
        # Add the current directory to the Python path
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        
        # Import the main module
        from src.main import main as run_main
        
        # Run the main function (which will start the menu interface)
        run_main()
        
    except ImportError as e:
        print(f"Error importing modules: {str(e)}")
        print("Make sure you have installed all required dependencies.")
        print("Try running: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting WhatsApp bot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 