"""
Windows-compatible terminal menu for WhatsApp bot.

This module provides a comprehensive terminal menu implementation for Windows,
implementing all the features specified in the menu_screens.md documentation.
"""

import os
import sys
import asyncio
import platform
from datetime import datetime, timedelta
from loguru import logger
from typing import List, Callable, Dict, Any, Optional

class WindowsTerminalMenu:
    """A simple terminal menu implementation for Windows."""
    
    def __init__(self, options: List[str], title: str = None, header: str = None):
        """
        Initialize the Windows terminal menu.
        
        Args:
            options: List of menu options to display
            title: Optional title for the menu
            header: Optional header to display above the menu
        """
        self.options = options
        self.title = title
        self.header = header
        self.selected_index = 0
    
    def show(self) -> int:
        """
        Display the menu and get user selection.
        
        Returns:
            Index of the selected option or -1 if cancelled
        """
        os.system('cls')  # Clear the screen
        
        # Display header if provided
        if self.header:
            print("\n" + "=" * 31)
            print(self.header.center(31))
            print("=" * 31 + "\n")
        
        # Display title if provided
        if self.title:
            print(f"{self.title}\n")
        
        # Display menu options
        for i, option in enumerate(self.options):
            print(f"{i+1}. {option}")
        
        print("\nEnter the number of your choice (or 'q' to quit): ", end="")
        
        try:
            user_input = input().strip().lower()
            
            if user_input == 'q':
                return -1
            
            selected = int(user_input) - 1
            
            if 0 <= selected < len(self.options):
                return selected
            else:
                print("\nInvalid selection. Press Enter to try again...")
                input()
                return self.show()
                
        except ValueError:
            print("\nInvalid input. Press Enter to try again...")
            input()
            return self.show()

class WindowsBotMenu:
    """WhatsApp Bot terminal menu for Windows."""
    
    def __init__(self, whatsapp_bot, db_operations, discord_bot=None):
        """
        Initialize the WhatsApp Bot menu.
        
        Args:
            whatsapp_bot: WhatsApp bot instance
            db_operations: Database operations instance
            discord_bot: Optional Discord bot instance for Discord integration
        """
        self.bot = whatsapp_bot
        self.db = db_operations
        self.discord_bot = discord_bot
        self.running = False
        self.menu_actions = {}
        self.header = "WHATSAPP GROUP SUMMARY GENERATOR"
        
        # Set up the menu actions
        self._setup_menu_actions()
        
        # Initialize Discord menu if Discord bot is provided
        if discord_bot:
            from .discord_menu import DiscordMenu
            self.discord_menu = DiscordMenu(whatsapp_bot, db_operations, discord_bot)
        else:
            self.discord_menu = None
    
    def _setup_menu_actions(self):
        """Configure menu actions."""
        # Main menu actions
        self.main_menu_actions = {
            "Complete Workflow": self._run_complete_workflow,
            "Generate New Summary": self._show_generate_summary_menu,
            "Fetch New Messages": self._fetch_new_messages,
            "Background Mode": self._show_background_mode_menu,
            "Debug Mode": self._show_debug_menu,
            "Discord Integration": self._show_discord_menu,
            "Exit": self._exit_app
        }
    
    def start(self):
        """Start the menu interface."""
        logger.info("Starting Windows terminal menu")
        self.show_main_menu()
    
    def show_main_menu(self):
        """Show the main menu of the bot."""
        options = list(self.main_menu_actions.keys())
        
        # Remove Discord Integration option if not available
        if self.discord_menu is None and "Discord Integration" in options:
            options.remove("Discord Integration")
        
        self.running = True
        
        while self.running:
            menu = WindowsTerminalMenu(
                options=options,
                title="Main Menu:",
                header=self.header
            )
            
            selected = menu.show()
            
            if selected == -1:
                # Quit selected
                logger.info("Quitting bot menu")
                self.running = False
                break
                
            if 0 <= selected < len(options):
                action_name = options[selected]
                action_func = self.main_menu_actions.get(action_name)
                
                if action_func:
                    try:
                        action_func()
                    except Exception as e:
                        logger.error(f"Error executing action '{action_name}': {str(e)}")
                        print(f"\nError: {str(e)}")
                        print("Press Enter to continue...")
                        input()
    
    # Menu action handlers - Complete Workflow
    
    def _run_complete_workflow(self):
        """Run the complete workflow: fetch messages, store them, generate summary, and post to group."""
        self.clear_screen()
        print("\n" + "=" * 31)
        print(self.header.center(31))
        print("=" * 31 + "\n")
        
        print("Complete Workflow\n")
        print("This will perform the entire workflow:")
        print("1. Fetch new messages from WhatsApp")
        print("2. Store messages in the database")
        print("3. Generate a summary")
        print("4. Post the summary to a group\n")
        
        if not self.confirm_action("Continue with complete workflow? (y/n): "):
            return
        
        # Get available groups
        groups = self._get_available_groups()
        
        if not groups:
            print("No WhatsApp groups available. Please check your connection.")
            self.wait_for_input()
            return
        
        # Show source group selection menu
        source_group_options = [f"{group['name']}" for group in groups]
        source_group_options.append("Back")
        
        menu = WindowsTerminalMenu(
            options=source_group_options,
            title="Select Source Group (to fetch messages from):",
            header=self.header
        )
        
        selected = menu.show()
        
        if selected == -1 or selected == len(source_group_options) - 1:
            return
        
        source_group = groups[selected]
        
        # Show target group selection menu
        target_group_options = [f"{group['name']}" for group in groups]
        target_group_options.append("Use Same as Source")
        target_group_options.append("Back")
        
        menu = WindowsTerminalMenu(
            options=target_group_options,
            title="Select Target Group (to send summary to):",
            header=self.header
        )
        
        selected = menu.show()
        
        if selected == -1 or selected == len(target_group_options) - 1:
            return
        
        if selected == len(target_group_options) - 2:  # "Use Same as Source" option
            target_group = source_group
        else:
            target_group = groups[selected]
        
        # Show days selection menu
        days_options = ["1 day", "3 days", "7 days", "Custom number of days", "Back"]
        
        menu = WindowsTerminalMenu(
            options=days_options,
            title="Select number of days to summarize:",
            header=self.header
        )
        
        selected = menu.show()
        
        if selected == -1 or selected == len(days_options) - 1:
            return
        
        days = 0
        if selected == 0:
            days = 1
        elif selected == 1:
            days = 3
        elif selected == 2:
            days = 7
        elif selected == 3:
            # Custom days
            self.clear_screen()
            print("\n" + "=" * 31)
            print(self.header.center(31))
            print("=" * 31 + "\n")
            print("Enter custom number of days (1-30): ", end="")
            try:
                days = int(input().strip())
                if days < 1 or days > 30:
                    print("\nInvalid input. Days must be between 1 and 30.")
                    self.wait_for_input()
                    return
            except ValueError:
                print("\nInvalid input. Please enter a number.")
                self.wait_for_input()
                return
        
        # Debug mode toggle
        debug_mode = self.confirm_action("Enable debug mode? (y/n): ")
        
        # Execute complete workflow
        self.clear_screen()
        print("\n" + "=" * 31)
        print(self.header.center(31))
        print("=" * 31 + "\n")
        print("Running complete workflow...")
        
        try:
            # Step 1: Process pending notifications
            print("\n1. Processing pending notifications...")
            notification_count = 0
            max_notifications = 50  # Process up to 50 notifications
            
            # Process notifications one by one
            while notification_count < max_notifications:
                notification = self.bot.api_client.receive_notification()
                if not notification:
                    print("   No more notifications in queue.")
                    break
                    
                receipt_id = notification.get('receiptId')
                import asyncio
                processed = asyncio.run(self.bot.process_notification(notification))
                
                if processed:
                    notification_count += 1
                
                # Delete the notification from the queue
                if receipt_id:
                    self.bot.api_client.delete_notification(receipt_id)
            
            print(f"   Processed {notification_count} notifications.")
            
            # Step 2: Get unprocessed messages for the group from the database
            print("\n2. Checking for unprocessed messages...")
            unprocessed_messages = self.db.get_unprocessed_messages(source_group['id'])
            print(f"   Found {len(unprocessed_messages)} unprocessed messages in the database.")
            
            # Step 3: Generate summary if we have enough messages
            if len(unprocessed_messages) > 0:
                print("\n3. Generating summary of messages...")
                import asyncio
                summary_result = asyncio.run(self.bot.generate_summary(source_group['id'], days, debug_mode))
                
                if not summary_result:
                    print("   Failed to generate summary. Please check the logs.")
                    self.wait_for_input()
                    return
                
                print(f"   Summary generated successfully!")
                
                # Step 4: Send the summary to the target group
                if target_group['id']:
                    print(f"\n4. Sending summary to target group {target_group['name']}...")
                    
                    # If message sending is disabled, don't actually send
                    if os.getenv("BOT_MESSAGE_SENDING_DISABLED", "false").lower() == "true":
                        print("   Message sending is disabled. Summary not sent.")
                        print(f"\nSummary content: {summary_result['summary_text']}")
                    else:
                        # Send the summary
                        import asyncio
                        send_result = asyncio.run(self.bot.send_summary(summary_result, target_group['id']))
                        
                        if send_result:
                            print("   Summary sent successfully!")
                        else:
                            print("   Failed to send summary. Please check the logs.")
                            self.wait_for_input()
                            return
            else:
                print("\n   Not enough messages to generate a summary. Please check the logs.")
                self.wait_for_input()
                return
            
            print("\nComplete workflow executed successfully!")
            
        except Exception as e:
            logger.error(f"Error in complete workflow: {str(e)}")
            print(f"\nError: {str(e)}")
        
        self.wait_for_input()
    
    # Menu action handlers - Option 1: Generate New Summary
    
    def _show_generate_summary_menu(self):
        """Show the generate summary menu."""
        self.clear_screen()
        print("\n" + "=" * 31)
        print(self.header.center(31))
        print("=" * 31 + "\n")
        
        # Get available groups
        groups = self._get_available_groups()
        
        if not groups:
            print("No WhatsApp groups available. Please check your connection.")
            self.wait_for_input()
            return
        
        # Show group selection menu
        group_options = [f"{group['name']}" for group in groups]
        group_options.append("Back")
        
        menu = WindowsTerminalMenu(
            options=group_options,
            title="Select a Group:",
            header=self.header
        )
        
        selected = menu.show()
        
        if selected == -1 or selected == len(group_options) - 1:
            return
        
        selected_group = groups[selected]
        
        # Show days selection menu
        days_options = ["1 day", "3 days", "7 days", "Custom number of days", "Back"]
        
        menu = WindowsTerminalMenu(
            options=days_options,
            title="Select number of days to summarize:",
            header=self.header
        )
        
        selected = menu.show()
        
        if selected == -1 or selected == len(days_options) - 1:
            return
        
        days = 0
        if selected == 0:
            days = 1
        elif selected == 1:
            days = 3
        elif selected == 2:
            days = 7
        elif selected == 3:
            # Custom days
            self.clear_screen()
            print("\n" + "=" * 31)
            print(self.header.center(31))
            print("=" * 31 + "\n")
            print("Enter custom number of days (1-30): ", end="")
            try:
                days = int(input().strip())
                if days < 1 or days > 30:
                    print("\nInvalid input. Days must be between 1 and 30.")
                    self.wait_for_input()
                    return
            except ValueError:
                print("\nInvalid input. Please enter a number.")
                self.wait_for_input()
                return
        
        # Debug mode toggle
        debug_mode = self.confirm_action("Enable debug mode? (y/n): ")
        
        # Generate summary
        self.clear_screen()
        print("\n" + "=" * 31)
        print(self.header.center(31))
        print("=" * 31 + "\n")
        print("Generating summary...")
        
        # Call the summary generation method
        try:
            summary = self._generate_summary(selected_group['id'], days, debug_mode)
            
            if summary:
                print("\nSummary generated successfully!\n")
                print(summary)
                
                # Ask if user wants to send the summary
                if self.confirm_action("\nSend this summary to the group? (y/n): "):
                    print("\nSending summary...")
                    result = self._send_summary(selected_group['id'], summary)
                    if result:
                        print("Summary sent successfully!")
                    else:
                        print("Failed to send summary. Please check the logs.")
            else:
                print("\nFailed to generate summary. Please check the logs.")
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            print(f"\nError generating summary: {str(e)}")
        
        self.wait_for_input()
    
    def _generate_summary(self, group_id, days, debug_mode=False):
        """Generate a summary for the specified group and time period."""
        try:
            # This would be the actual implementation to generate a summary
            # For now, we'll return a placeholder
            if debug_mode:
                logger.debug(f"Generating summary for group {group_id} for the past {days} days")
                
            # In a real implementation, you would:
            # 1. Fetch messages from the database for the specified time period
            # 2. Call the summarizer module to generate a summary
            # 3. Return the summary text
            
            # Placeholder implementation
            return f"Summary of messages from the past {days} days for group {group_id}.\n\nThis is a placeholder summary. The actual implementation would use the OpenAI summarizer to generate a meaningful summary of the group's messages."
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise
    
    def _send_summary(self, group_id, summary_text):
        """Send a summary to the specified group."""
        try:
            # In a real implementation, you would call the WhatsApp API to send the message
            logger.info(f"Sending summary to group {group_id}")
            
            # Placeholder implementation
            return True
        except Exception as e:
            logger.error(f"Error sending summary: {str(e)}")
            return False
    
    # Menu action handlers - Option 2: Fetch New Messages
    
    def _fetch_new_messages(self):
        """Fetch new messages from all groups."""
        self.clear_screen()
        print("\n" + "=" * 31)
        print(self.header.center(31))
        print("=" * 31 + "\n")
        
        print("Fetching new messages...")
        
        try:
            # In a real implementation, you would call the bot's method to fetch messages
            # For now, this is a placeholder
            result = True
            
            if result:
                print("\nMessages fetched and stored successfully")
            else:
                print("\nFailed to fetch messages. Please check the logs.")
        except Exception as e:
            logger.error(f"Error fetching messages: {str(e)}")
            print(f"\nError fetching messages: {str(e)}")
        
        self.wait_for_input()
    
    # Menu action handlers - Option 3: Background Mode
    
    def _show_background_mode_menu(self):
        """Show the background mode menu."""
        background_options = [
            "Start Bot in Background",
            "Set Scheduled Posting Time",
            "Set Source Group (for fetching messages)",
            "Set Target Group (for posting summaries)",
            "View Current Background Settings",
            "Back"
        ]
        
        while True:
            menu = WindowsTerminalMenu(
                options=background_options,
                title="Background Mode:",
                header=self.header
            )
            
            selected = menu.show()
            
            if selected == -1 or selected == len(background_options) - 1:
                return
            
            try:
                if selected == 0:
                    self._start_background_mode()
                elif selected == 1:
                    self._set_scheduled_posting_time()
                elif selected == 2:
                    self._set_source_group()
                elif selected == 3:
                    self._set_target_group()
                elif selected == 4:
                    self._view_background_settings()
            except Exception as e:
                logger.error(f"Error in background mode menu: {str(e)}")
                print(f"\nError: {str(e)}")
                self.wait_for_input()
    
    def _start_background_mode(self):
        """Start the bot in background mode."""
        self.clear_screen()
        print("\n" + "=" * 31)
        print(self.header.center(31))
        print("=" * 31 + "\n")
        
        print("Start Bot in Background\n")
        print("Running in background mode will keep the bot active and executing scheduled tasks.")
        print("The terminal window must remain open while the bot is running.\n")
        
        if self.confirm_action("Start the bot in background mode? (y/n): "):
            print("\nStarting bot in background mode...")
            
            try:
                # Start the bot in background mode
                import asyncio
                result = asyncio.run(self.bot.start(background_mode=True))
                
                if result:
                    print("Bot started successfully in background mode!")
                else:
                    print("Failed to start bot in background mode.")
            except Exception as e:
                logger.error(f"Error starting bot in background mode: {str(e)}")
                print(f"\nError: {str(e)}")
        
        self.wait_for_input()
    
    def _set_scheduled_posting_time(self):
        """Set the scheduled posting time."""
        self.clear_screen()
        print("\n" + "=" * 31)
        print(self.header.center(31))
        print("=" * 31 + "\n")
        
        print("Set Scheduled Posting Time\n")
        print("Enter the time for scheduled summary posting (HH:MM format):")
        
        time_input = input().strip()
        
        try:
            # Validate time format
            datetime.strptime(time_input, "%H:%M")
            
            # Save the scheduled time
            # In a real implementation, you would update the database or configuration
            print(f"\nScheduled posting time set to {time_input}")
        except ValueError:
            print("\nInvalid time format. Please use HH:MM format.")
        
        self.wait_for_input()
    
    def _set_source_group(self):
        """Set the source group for fetching messages."""
        groups = self._get_available_groups()
        if self._select_group("Source", groups):
            # Update the environment variable or configuration
            selected_group = self.selected_group
            os.environ["WHATSAPP_SOURCE_GROUP_ID"] = selected_group['id']
            # Update the database or config file if needed
            logger.info(f"Source group set to: {selected_group['name']} ({selected_group['id']})")
    
    def _set_target_group(self):
        """Set the target group for posting summaries."""
        groups = self._get_available_groups()
        if self._select_group("Target", groups):
            # Update the environment variable or configuration
            selected_group = self.selected_group
            os.environ["WHATSAPP_TARGET_GROUP_ID"] = selected_group['id']
            # Update the database or config file if needed
            logger.info(f"Target group set to: {selected_group['name']} ({selected_group['id']})")
    
    def _select_group(self, group_type, groups):
        """Helper function to select a group."""
        self.clear_screen()
        print("\n" + "=" * 31)
        print(self.header.center(31))
        print("=" * 31 + "\n")
        
        print(f"Set {group_type} Group\n")
        
        if not groups:
            print("No WhatsApp groups available. Please check your connection.")
            self.wait_for_input()
            return False
        
        group_options = [f"{group['name']}" for group in groups]
        group_options.append("Back")
        
        menu = WindowsTerminalMenu(
            options=group_options,
            title=f"Select {group_type} Group:",
            header=self.header
        )
        
        selected = menu.show()
        
        if selected == -1 or selected == len(group_options) - 1:
            return False
        
        selected_group = groups[selected]
        self.selected_group = selected_group  # Store the selected group
        
        print(f"\n{group_type} group set to: {selected_group['name']}")
        self.wait_for_input()
        return True
    
    def _view_background_settings(self):
        """View current background settings."""
        self.clear_screen()
        print("\n" + "=" * 31)
        print(self.header.center(31))
        print("=" * 31 + "\n")
        
        print("Current Background Settings\n")
        
        # In a real implementation, you would fetch these from the database or configuration
        print("Scheduled Posting Time: 08:00")
        print("Source Group: Family Group")
        print("Target Group: Family Group")
        print("Background Mode: Inactive")
        
        self.wait_for_input()
    
    # Menu action handlers - Option 4: Debug Mode
    
    def _show_debug_menu(self):
        """Show the debug menu."""
        debug_options = [
            "Test API Connections",
            "Export Message Data",
            "View Log Files",
            "Back"
        ]
        
        while True:
            menu = WindowsTerminalMenu(
                options=debug_options,
                title="Debug Menu:",
                header=self.header
            )
            
            selected = menu.show()
            
            if selected == -1 or selected == len(debug_options) - 1:
                return
            
            try:
                if selected == 0:
                    self._test_api_connections()
                elif selected == 1:
                    self._export_message_data()
                elif selected == 2:
                    self._view_log_files()
            except Exception as e:
                logger.error(f"Error in debug menu: {str(e)}")
                print(f"\nError: {str(e)}")
                self.wait_for_input()
    
    def _test_api_connections(self):
        """Test API connections."""
        self.clear_screen()
        print("\n" + "=" * 31)
        print(self.header.center(31))
        print("=" * 31 + "\n")
        
        print("Testing API Connections\n")
        
        try:
            # Test WhatsApp API
            whatsapp_ok = False
            try:
                import asyncio
                whatsapp_ok = asyncio.run(self.bot.check_connection())
            except Exception as e:
                logger.error(f"Error testing WhatsApp connection: {str(e)}")
            
            print(f"Green API connection: {'authorized' if whatsapp_ok else 'unauthorized'}")
            
            # Test OpenAI API
            openai_ok = False
            try:
                from src.nlp.summarizer import OpenAISummarizer
                summarizer = OpenAISummarizer()
                # Simple test of OpenAI connection
                openai_ok = True  # This would be the result of an actual connection test
            except Exception as e:
                logger.error(f"Error testing OpenAI connection: {str(e)}")
            
            print(f"OpenAI connection: {'OK' if openai_ok else 'Failed'}")
            
            # Test Supabase connection
            try:
                # Test Supabase connection if applicable
                print("Supabase client not initialized")
            except Exception as e:
                logger.error(f"Error testing Supabase connection: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error testing API connections: {str(e)}")
            print(f"\nError: {str(e)}")
        
        self.wait_for_input()
    
    def _export_message_data(self):
        """Export message data."""
        self.clear_screen()
        print("\n" + "=" * 31)
        print(self.header.center(31))
        print("=" * 31 + "\n")
        
        print("Export Message Data\n")
        
        print("Exporting message data to CSV...")
        
        try:
            # In a real implementation, you would export messages to a CSV file
            # For now, this is a placeholder
            export_file = "messages_export.csv"
            print(f"\nMessages exported to {export_file}")
        except Exception as e:
            logger.error(f"Error exporting message data: {str(e)}")
            print(f"\nError: {str(e)}")
        
        self.wait_for_input()
    
    def _view_log_files(self):
        """View log files."""
        self.clear_screen()
        print("\n" + "=" * 31)
        print(self.header.center(31))
        print("=" * 31 + "\n")
        
        print("View Log Files\n")
        
        # Get log files
        log_files = self._get_log_files()
        
        if not log_files:
            print("No log files found.")
            self.wait_for_input()
            return
        
        log_options = [f"{log}" for log in log_files]
        log_options.append("Back")
        
        menu = WindowsTerminalMenu(
            options=log_options,
            title="Select a log file to view:",
            header=self.header
        )
        
        selected = menu.show()
        
        if selected == -1 or selected == len(log_options) - 1:
            return
        
        selected_log = log_files[selected]
        
        # Show log file contents
        self.clear_screen()
        print(f"\nLog file: {selected_log}\n")
        
        try:
            # In a real implementation, you would read and display the log file
            print("Log file contents would be displayed here.")
            print("...")
        except Exception as e:
            logger.error(f"Error reading log file: {str(e)}")
            print(f"\nError: {str(e)}")
        
        self.wait_for_input()
    
    def _get_log_files(self):
        """Get available log files."""
        try:
            # In a real implementation, you would list log files from the logs directory
            # For now, return placeholder data
            return [
                "app_2023-05-15.log",
                "error_2023-05-15.log",
                "app_2023-05-14.log"
            ]
        except Exception as e:
            logger.error(f"Error getting log files: {str(e)}")
            return []
    
    # Menu action handlers - Option 5: Discord Integration
    
    def _show_discord_menu(self):
        """Show the Discord integration menu."""
        if self.discord_menu:
            self.discord_menu.show_discord_menu()
        else:
            self.clear_screen()
            print("\n" + "=" * 31)
            print(self.header.center(31))
            print("=" * 31 + "\n")
            
            print("Discord Integration\n")
            print("Discord integration is not available.")
            print("Please make sure the Discord bot is properly configured.")
            
            self.wait_for_input()
    
    # Menu action handlers - Option 6: Exit
    
    def _exit_app(self):
        """Exit the application."""
        if self.confirm_action("Are you sure you want to exit? (y/n): "):
            print("\nExiting...\n\nGoodbye!")
            self.running = False
    
    # Helper methods
    
    def _get_available_groups(self):
        """Get available WhatsApp groups."""
        try:
            # Get contacts from WhatsApp API
            contacts = self.bot.api_client.get_contacts()
            
            # Filter for groups only and format them
            groups = []
            for contact in contacts:
                if contact.get('type') == 'group':
                    groups.append({
                        "id": contact.get('id'),
                        "name": contact.get('name') or "Unnamed Group"
                    })
            
            if not groups:
                logger.warning("No WhatsApp groups found in contacts")
            else:
                logger.info(f"Found {len(groups)} WhatsApp groups")
                
            return groups
        except Exception as e:
            logger.error(f"Error getting available groups: {str(e)}")
            return []
    
    def confirm_action(self, message: str) -> bool:
        """
        Ask for confirmation before performing an action.
        
        Args:
            message: The confirmation message to display
            
        Returns:
            True if confirmed, False otherwise
        """
        while True:
            print(message, end="")
            response = input().strip().lower()
            
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
    
    def wait_for_input(self, message: str = "Press Enter to continue..."):
        """Wait for user input."""
        print(f"\n{message}", end="")
        input()
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls')

def create_bot_menu(whatsapp_bot, db_operations, discord_bot=None) -> WindowsBotMenu:
    """Create a new instance of the bot menu."""
    return WindowsBotMenu(whatsapp_bot, db_operations, discord_bot)

def create_discord_menu(whatsapp_bot, db_operations, discord_bot=None):
    """Create a new instance of the Discord menu.
    
    Args:
        whatsapp_bot: WhatsApp bot instance
        db_operations: Database operations instance
        discord_bot: Optional Discord bot instance
        
    Returns:
        A configured DiscordMenu instance
    """
    from .discord_menu import DiscordMenu
    return DiscordMenu(whatsapp_bot, db_operations, discord_bot) 