"""
Main entry point for the WhatsApp bot application.

This module provides the main entry point for running the WhatsApp bot
in various modes (terminal menu, background, or Discord).
"""

import os
import sys
import asyncio
import platform
from pathlib import Path
from dotenv import load_dotenv
import argparse
from loguru import logger

from src.database.connection import create_db_engine, get_db_session
from src.database.operations import DatabaseOperations
from src.whatsapp.bot import WhatsAppBot
from src.scheduler.scheduler import Scheduler
# Import both menu implementations - we'll choose based on platform
if platform.system() == 'Windows':
    from src.menu.windows_menu import WindowsBotMenu as BotMenu, create_bot_menu
else:
    from src.menu.terminal_menu import BotMenu


def setup_logging(log_level="INFO"):
    """Configure logging for the application."""
    # Clear any existing handlers
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Add file handler for all logs
    logger.add(
        "logs/bot.log",
        level=log_level,
        rotation="10 MB",  # Rotate when the file reaches 10MB
        retention="1 week",  # Keep logs for 1 week
        compression="zip",  # Compress rotated logs
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # Add file handler for errors only
    logger.add(
        "logs/errors.log",
        level="ERROR",
        rotation="10 MB",
        retention="1 month",  # Keep error logs longer
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    logger.info("Logging configured successfully")


async def run_application(mode):
    """Run the application in the specified mode."""
    logger.info(f"Starting application in {mode} mode")
    
    try:
        # Initialize database
        engine = create_db_engine()
        session = get_db_session(engine)
        db_operations = DatabaseOperations(session)
        
        # Initialize WhatsApp bot
        whatsapp_bot = WhatsAppBot(db_operations)
        
        # Initialize scheduler
        scheduler = Scheduler(whatsapp_bot, db_operations)
        
        try:
            if mode == "discord":
                from src.discord.bot import DiscordBot
                
                # Initialize Discord bot
                discord_bot = DiscordBot(whatsapp_bot, db_operations)
                
                # Start WhatsApp bot in background mode
                await whatsapp_bot.start(background_mode=True)
                
                # Start the scheduler
                await scheduler.start()
                
                # Start Discord bot (blocking call)
                await discord_bot.start()
                
            elif mode == "background":
                # Start WhatsApp bot in background mode
                await whatsapp_bot.start(background_mode=True)
                
                # Start the scheduler
                await scheduler.start()
                
                # Keep the application running
                while True:
                    await asyncio.sleep(60)
                    
            elif mode == "menu":
                # Initialize Discord bot if discord mode is enabled
                discord_bot = None
                if os.getenv("ENABLE_DISCORD", "false").lower() == "true":
                    try:
                        from src.discord.bot import DiscordBot
                        discord_bot = DiscordBot(whatsapp_bot, db_operations)
                        logger.info("Discord bot initialized for menu mode")
                    except Exception as e:
                        logger.error(f"Error initializing Discord bot: {str(e)}")
                        discord_bot = None
                
                # Create and start menu
                if platform.system() == 'Windows':
                    # Use the create_bot_menu function for Windows
                    menu = create_bot_menu(whatsapp_bot, db_operations, discord_bot)
                else:
                    # Use the BotMenu class for other platforms
                    menu = BotMenu(whatsapp_bot, db_operations)
                
                menu.start()
                
        except asyncio.CancelledError:
            logger.info("Application task cancelled")
            await whatsapp_bot.stop()
            if scheduler:
                await scheduler.stop()
            
        except Exception as e:
            logger.error(f"Error in application: {str(e)}")
            await whatsapp_bot.stop()
            if scheduler:
                await scheduler.stop()
            
        finally:
            # Clean up resources
            session.close()
            
    except Exception as e:
        logger.error(f"Error initializing application: {str(e)}")
        sys.exit(1)


def main():
    """Entry point for the WhatsApp bot application."""
    # Load environment variables
    load_dotenv()
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="WhatsApp Group Summary Bot")
    parser.add_argument(
        "--mode",
        "-m",
        choices=["menu", "background", "discord"],
        default="menu",
        help="Operation mode: menu (default), background, or discord"
    )
    parser.add_argument(
        "--log-level",
        "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    
    # Run the application in the specified mode
    try:
        asyncio.run(run_application(args.mode))
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()  
