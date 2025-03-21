import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional
from simple_term_menu import TerminalMenu
from loguru import logger

from ..whatsapp.bot import WhatsAppBot
from ..database.operations import DatabaseOperations

class BotMenu:
    """Terminal Menu for controlling the WhatsApp bot."""
    
    def __init__(self, whatsapp_bot: WhatsAppBot, db_operations: DatabaseOperations):
        """Initialize the terminal menu with a WhatsApp bot instance."""
        self.bot = whatsapp_bot
        self.db = db_operations
        self.running = False
        self.loop = asyncio.get_event_loop()
        
        # Menu configuration
        self.main_menu_title = "WhatsApp Bot - Main Menu"
        self.main_menu_items = [
            "Generate and Send Summary",
            "Schedule Management",
            "Debug Tools",
            "Bot Status",
            "Exit"
        ]
        
        self.back_option = "Go Back"
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Print a header with the given title."""
        self.clear_screen()
        print(f"\n{'=' * 50}")
        print(f"{title.center(50)}")
        print(f"{'=' * 50}\n")
    
    def display_main_menu(self):
        """Display the main menu and handle user selection."""
        self.running = True
        
        while self.running:
            self.print_header(self.main_menu_title)
            
            # Check bot status
            status = self.bot.get_status()
            status_line = f"Bot Status: {'Running' if status['running'] else 'Stopped'} | "
            status_line += f"Mode: {'Background' if status['background_mode'] else 'Foreground'} | "
            status_line += f"Connected: {'Yes' if status['whatsapp_connected'] else 'No'}"
            print(f"{status_line}\n")
            
            terminal_menu = TerminalMenu(
                self.main_menu_items,
                title="Select an option:",
                menu_cursor="→ ",
                menu_cursor_style=("fg_green", "bold"),
                menu_highlight_style=("bg_green", "fg_black"),
            )
            
            menu_selection_index = terminal_menu.show()
            
            if menu_selection_index is None:
                # If ESC or Ctrl+C was pressed
                self.running = False
                continue
                
            selection = self.main_menu_items[menu_selection_index]
            
            if selection == "Generate and Send Summary":
                self.show_generate_summary_menu()
            elif selection == "Schedule Management":
                self.show_schedule_menu()
            elif selection == "Debug Tools":
                self.show_debug_menu()
            elif selection == "Bot Status":
                self.show_status_menu()
            elif selection == "Exit":
                self.running = False
    
    def show_generate_summary_menu(self):
        """Show the menu for generating and sending summaries."""
        self.print_header("Generate and Send Summary")
        
        # Get active groups
        active_groups = self.bot.active_group_ids
        if not active_groups:
            print("No active groups configured. Please set up groups first.")
            input("\nPress Enter to continue...")
            return
            
        # Ask for the source group
        group_menu_items = [f"{i+1}. {group}" for i, group in enumerate(active_groups)]
        group_menu_items.append(self.back_option)
        
        terminal_menu = TerminalMenu(
            group_menu_items,
            title="Select source group for summary:",
            menu_cursor="→ ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("bg_green", "fg_black"),
        )
        
        menu_selection_index = terminal_menu.show()
        
        if menu_selection_index is None or group_menu_items[menu_selection_index] == self.back_option:
            return
            
        source_group = active_groups[menu_selection_index]
        
        # Ask for the target group (or same as source)
        send_menu_items = ["Send to the same group", "Send to a different group", "Don't send (preview only)", self.back_option]
        
        terminal_menu = TerminalMenu(
            send_menu_items,
            title="Select target option:",
            menu_cursor="→ ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("bg_green", "fg_black"),
        )
        
        menu_selection_index = terminal_menu.show()
        
        if menu_selection_index is None or send_menu_items[menu_selection_index] == self.back_option:
            return
            
        send_option = send_menu_items[menu_selection_index]
        target_group = None
        send_summary = False
        
        if send_option == "Send to the same group":
            target_group = source_group
            send_summary = True
        elif send_option == "Send to a different group":
            # Select a different target group
            target_menu_items = [f"{i+1}. {group}" for i, group in enumerate(active_groups)]
            target_menu_items.append(self.back_option)
            
            terminal_menu = TerminalMenu(
                target_menu_items,
                title="Select target group for summary:",
                menu_cursor="→ ",
                menu_cursor_style=("fg_green", "bold"),
                menu_highlight_style=("bg_green", "fg_black"),
            )
            
            menu_selection_index = terminal_menu.show()
            
            if menu_selection_index is None or target_menu_items[menu_selection_index] == self.back_option:
                return
                
            target_group = active_groups[menu_selection_index]
            send_summary = True
        
        # Generate and optionally send the summary
        print("\nGenerating summary...")
        
        try:
            summary_result = self.loop.run_until_complete(
                self.bot.generate_and_send_summary(
                    source_group_id=source_group,
                    target_group_id=target_group,
                    send=send_summary
                )
            )
            
            if summary_result:
                print(f"\nSummary generated with {summary_result['message_count']} messages.")
                print("\n--- Summary Preview ---")
                print(summary_result['summary_text'][:1000] + "..." if len(summary_result['summary_text']) > 1000 else summary_result['summary_text'])
                print("--- End of Preview ---\n")
                
                if send_summary:
                    print(f"Summary {'sent' if summary_result.get('sent', False) else 'not sent'} to group.")
            else:
                print("\nFailed to generate summary. Not enough messages or an error occurred.")
                
        except Exception as e:
            print(f"\nError: {str(e)}")
            
        input("\nPress Enter to continue...")
    
    def show_schedule_menu(self):
        """Show the menu for managing scheduled summaries."""
        while True:
            self.print_header("Schedule Management")
            
            # Get current schedule
            schedule_config = self.db.get_schedule_config()
            
            if schedule_config:
                print(f"Current schedule: {schedule_config.schedule_time}")
                print(f"Active: {'Yes' if schedule_config.is_active else 'No'}")
                print(f"Source group: {schedule_config.source_group_id}")
                print(f"Target group: {schedule_config.target_group_id}")
                print(f"Test mode: {'Yes' if schedule_config.test_mode else 'No'}\n")
                
                schedule_menu_items = [
                    "Update Schedule",
                    f"{'Disable' if schedule_config.is_active else 'Enable'} Schedule",
                    f"{'Disable' if schedule_config.test_mode else 'Enable'} Test Mode",
                    "Start Background Processing",
                    self.back_option
                ]
            else:
                print("No schedule configured.\n")
                schedule_menu_items = ["Configure New Schedule", self.back_option]
            
            terminal_menu = TerminalMenu(
                schedule_menu_items,
                title="Select an option:",
                menu_cursor="→ ",
                menu_cursor_style=("fg_green", "bold"),
                menu_highlight_style=("bg_green", "fg_black"),
            )
            
            menu_selection_index = terminal_menu.show()
            
            if menu_selection_index is None or schedule_menu_items[menu_selection_index] == self.back_option:
                break
                
            selection = schedule_menu_items[menu_selection_index]
            
            if selection == "Configure New Schedule" or selection == "Update Schedule":
                self.configure_schedule()
            elif "Disable Schedule" in selection or "Enable Schedule" in selection:
                new_status = not schedule_config.is_active
                self.db.update_schedule_status(new_status)
                print(f"\nSchedule {'enabled' if new_status else 'disabled'}.")
                input("\nPress Enter to continue...")
            elif "Test Mode" in selection:
                new_test_mode = not schedule_config.test_mode
                self.db.save_schedule_config(
                    source_group_id=schedule_config.source_group_id,
                    target_group_id=schedule_config.target_group_id,
                    schedule_time=schedule_config.schedule_time,
                    is_active=schedule_config.is_active,
                    test_mode=new_test_mode
                )
                print(f"\nTest mode {'enabled' if new_test_mode else 'disabled'}.")
                input("\nPress Enter to continue...")
            elif selection == "Start Background Processing":
                self.start_background_processing()
    
    def configure_schedule(self):
        """Configure a new schedule or update an existing one."""
        self.print_header("Configure Schedule")
        
        # Get active groups
        active_groups = self.bot.active_group_ids
        if not active_groups:
            print("No active groups configured. Please set up groups first.")
            input("\nPress Enter to continue...")
            return
        
        # Select source group
        group_menu_items = [f"{i+1}. {group}" for i, group in enumerate(active_groups)]
        group_menu_items.append(self.back_option)
        
        terminal_menu = TerminalMenu(
            group_menu_items,
            title="Select source group for scheduled summaries:",
            menu_cursor="→ ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("bg_green", "fg_black"),
        )
        
        menu_selection_index = terminal_menu.show()
        
        if menu_selection_index is None or group_menu_items[menu_selection_index] == self.back_option:
            return
            
        source_group = active_groups[menu_selection_index]
        
        # Select target group
        terminal_menu = TerminalMenu(
            group_menu_items,
            title="Select target group for scheduled summaries:",
            menu_cursor="→ ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("bg_green", "fg_black"),
        )
        
        menu_selection_index = terminal_menu.show()
        
        if menu_selection_index is None or group_menu_items[menu_selection_index] == self.back_option:
            return
            
        target_group = active_groups[menu_selection_index]
        
        # Enter schedule time
        valid_time = False
        schedule_time = None
        
        while not valid_time:
            self.print_header("Configure Schedule")
            print(f"Source group: {source_group}")
            print(f"Target group: {target_group}\n")
            
            schedule_time = input("Enter schedule time (HH:MM in 24-hour format): ")
            
            try:
                hour, minute = map(int, schedule_time.split(':'))
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    valid_time = True
                else:
                    print("\nInvalid time format. Hours must be 0-23, minutes 0-59.")
                    input("\nPress Enter to try again...")
            except ValueError:
                print("\nInvalid time format. Use HH:MM format (e.g., 14:30).")
                input("\nPress Enter to try again...")
        
        # Test mode
        test_mode_menu = TerminalMenu(
            ["Yes, enable test mode", "No, use production mode"],
            title="Enable test mode?",
            menu_cursor="→ ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("bg_green", "fg_black"),
        )
        
        test_mode_index = test_mode_menu.show()
        test_mode = test_mode_index == 0
        
        # Save the configuration
        self.db.save_schedule_config(
            source_group_id=source_group,
            target_group_id=target_group,
            schedule_time=schedule_time,
            is_active=True,
            test_mode=test_mode
        )
        
        print(f"\nSchedule configured for {schedule_time}.")
        input("\nPress Enter to continue...")
    
    def start_background_processing(self):
        """Start the bot in background processing mode."""
        self.print_header("Start Background Processing")
        
        # Check if the bot is already running
        status = self.bot.get_status()
        if status['running']:
            print("Bot is already running.")
            input("\nPress Enter to continue...")
            return
        
        print("Starting bot in background mode...")
        
        try:
            # Start the bot in background mode
            success = self.loop.run_until_complete(self.bot.start(background_mode=True))
            
            if success:
                # Start the message processing loop in a separate task
                asyncio.create_task(self.bot.process_messages_loop())
                print("\nBot started in background mode and is now monitoring for messages.")
            else:
                print("\nFailed to start bot. Check logs for details.")
        except Exception as e:
            print(f"\nError: {str(e)}")
        
        input("\nPress Enter to continue...")
    
    def show_debug_menu(self):
        """Show the debug tools menu."""
        while True:
            self.print_header("Debug Tools")
            
            debug_menu_items = [
                "Test WhatsApp Connection",
                "View Database Status",
                "View Message Count",
                "View Latest Summary",
                "Send Test Message",
                self.back_option
            ]
            
            terminal_menu = TerminalMenu(
                debug_menu_items,
                title="Select a debug tool:",
                menu_cursor="→ ",
                menu_cursor_style=("fg_green", "bold"),
                menu_highlight_style=("bg_green", "fg_black"),
            )
            
            menu_selection_index = terminal_menu.show()
            
            if menu_selection_index is None or debug_menu_items[menu_selection_index] == self.back_option:
                break
                
            selection = debug_menu_items[menu_selection_index]
            
            if selection == "Test WhatsApp Connection":
                self.test_whatsapp_connection()
            elif selection == "View Database Status":
                self.view_database_status()
            elif selection == "View Message Count":
                self.view_message_count()
            elif selection == "View Latest Summary":
                self.view_latest_summary()
            elif selection == "Send Test Message":
                self.send_test_message()
    
    def test_whatsapp_connection(self):
        """Test the WhatsApp connection."""
        self.print_header("Test WhatsApp Connection")
        
        print("Testing WhatsApp connection...")
        
        try:
            connection_status = self.loop.run_until_complete(self.bot.check_connection())
            
            if connection_status:
                print("\nSuccess! WhatsApp connection is active.")
            else:
                print("\nFailed to connect to WhatsApp. Check your credentials and network.")
        except Exception as e:
            print(f"\nError: {str(e)}")
            
        input("\nPress Enter to continue...")
    
    def view_database_status(self):
        """View the database status."""
        self.print_header("Database Status")
        
        try:
            # Count messages
            messages_query = self.db.session.query(self.db.session.get_bind().get_mapper().mapped_table.name).count()
            
            # Count summaries
            summaries_query = self.db.session.query(self.db.session.get_bind().get_mapper().mapped_table.name).count()
            
            print(f"Total messages stored: {messages_query}")
            print(f"Total summaries stored: {summaries_query}")
            
            # Get database connection status
            bot_status = self.db.get_or_create_bot_status()
            print(f"\nDatabase connected: {'Yes' if bot_status.database_connected else 'No'}")
            
        except Exception as e:
            print(f"Error querying database: {str(e)}")
            
        input("\nPress Enter to continue...")
    
    def view_message_count(self):
        """View the message count for groups."""
        self.print_header("Message Count")
        
        # Get active groups
        active_groups = self.bot.active_group_ids
        
        if not active_groups:
            print("No active groups configured.")
            input("\nPress Enter to continue...")
            return
            
        for group_id in active_groups:
            try:
                # Count total messages
                total_count = self.db.get_message_count(group_id)
                
                # Count unprocessed messages
                unprocessed_messages = self.db.get_unprocessed_messages(group_id)
                unprocessed_count = len(unprocessed_messages)
                
                print(f"Group: {group_id}")
                print(f"  Total messages: {total_count}")
                print(f"  Unprocessed messages: {unprocessed_count}")
                print()
                
            except Exception as e:
                print(f"Error getting message count for {group_id}: {str(e)}")
                
        input("\nPress Enter to continue...")
    
    def view_latest_summary(self):
        """View the latest summary."""
        self.print_header("Latest Summary")
        
        try:
            latest_summary = self.db.get_latest_summary()
            
            if latest_summary:
                print(f"Summary ID: {latest_summary.id}")
                print(f"Group: {latest_summary.group_id}")
                print(f"Created: {latest_summary.created_at}")
                print(f"Messages: {latest_summary.message_count}")
                print(f"Sent: {'Yes' if latest_summary.sent_to_group else 'No'}")
                
                if latest_summary.sent_to_group:
                    print(f"Sent at: {latest_summary.sent_at}")
                    
                print("\n--- Summary Text ---")
                print(latest_summary.summary_text[:1000] + "..." if len(latest_summary.summary_text) > 1000 else latest_summary.summary_text)
                print("--- End of Summary ---")
            else:
                print("No summaries found in the database.")
                
        except Exception as e:
            print(f"Error retrieving latest summary: {str(e)}")
            
        input("\nPress Enter to continue...")
    
    def send_test_message(self):
        """Send a test message to a group."""
        self.print_header("Send Test Message")
        
        # Get active groups
        active_groups = self.bot.active_group_ids
        
        if not active_groups:
            print("No active groups configured.")
            input("\nPress Enter to continue...")
            return
            
        # Select target group
        group_menu_items = [f"{i+1}. {group}" for i, group in enumerate(active_groups)]
        group_menu_items.append(self.back_option)
        
        terminal_menu = TerminalMenu(
            group_menu_items,
            title="Select target group for test message:",
            menu_cursor="→ ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("bg_green", "fg_black"),
        )
        
        menu_selection_index = terminal_menu.show()
        
        if menu_selection_index is None or group_menu_items[menu_selection_index] == self.back_option:
            return
            
        target_group = active_groups[menu_selection_index]
        
        # Enter message
        self.print_header("Send Test Message")
        print(f"Target group: {target_group}\n")
        
        test_message = input("Enter test message: ")
        
        if not test_message:
            print("\nEmpty message. Aborting.")
            input("\nPress Enter to continue...")
            return
            
        # Send message
        print("\nSending test message...")
        
        try:
            # Check if message sending is disabled
            if os.getenv("BOT_MESSAGE_SENDING_DISABLED", "false").lower() == "true":
                print("\nMessage sending is disabled in configuration. Would have sent:")
                print(f"To: {target_group}")
                print(f"Message: {test_message}")
            else:
                response = self.bot.api_client.send_message(target_group, test_message)
                print("\nMessage sent successfully.")
                print(f"Response: {response}")
                
        except Exception as e:
            print(f"\nError sending message: {str(e)}")
            
        input("\nPress Enter to continue...")
    
    def show_status_menu(self):
        """Show the bot status menu."""
        self.print_header("Bot Status")
        
        status = self.bot.get_status()
        
        print(f"Running: {'Yes' if status['running'] else 'No'}")
        print(f"Mode: {'Background' if status['background_mode'] else 'Foreground'}")
        print(f"WhatsApp Connected: {'Yes' if status['whatsapp_connected'] else 'No'}")
        print(f"Test Mode: {'Yes' if status['test_mode'] else 'No'}")
        
        if status['active_groups']:
            print("\nActive Groups:")
            for group in status['active_groups']:
                print(f"  - {group}")
        else:
            print("\nNo active groups.")
            
        # Get schedule information
        schedule_config = self.db.get_schedule_config()
        
        if schedule_config:
            print("\nSchedule Configuration:")
            print(f"  Time: {schedule_config.schedule_time}")
            print(f"  Active: {'Yes' if schedule_config.is_active else 'No'}")
            print(f"  Source Group: {schedule_config.source_group_id}")
            print(f"  Target Group: {schedule_config.target_group_id}")
            print(f"  Test Mode: {'Yes' if schedule_config.test_mode else 'No'}")
        else:
            print("\nNo schedule configured.")
            
        # Show status options
        print("\nOptions:")
        
        status_menu_items = [
            "Start Bot" if not status['running'] else "Stop Bot",
            "Enable Test Mode" if not status['test_mode'] else "Disable Test Mode",
            self.back_option
        ]
        
        terminal_menu = TerminalMenu(
            status_menu_items,
            menu_cursor="→ ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("bg_green", "fg_black"),
        )
        
        menu_selection_index = terminal_menu.show()
        
        if menu_selection_index is None or status_menu_items[menu_selection_index] == self.back_option:
            return
            
        selection = status_menu_items[menu_selection_index]
        
        if selection == "Start Bot":
            background_menu = TerminalMenu(
                ["Start in background mode", "Start in foreground mode"],
                title="Select start mode:",
                menu_cursor="→ ",
                menu_cursor_style=("fg_green", "bold"),
                menu_highlight_style=("bg_green", "fg_black"),
            )
            
            bg_index = background_menu.show()
            
            if bg_index is None:
                return
                
            background_mode = bg_index == 0
            
            print(f"\nStarting bot in {'background' if background_mode else 'foreground'} mode...")
            
            try:
                success = self.loop.run_until_complete(self.bot.start(background_mode=background_mode))
                
                if success:
                    print("\nBot started successfully.")
                    
                    if background_mode:
                        # Start the message processing loop in a separate task
                        asyncio.create_task(self.bot.process_messages_loop())
                else:
                    print("\nFailed to start bot. Check logs for details.")
            except Exception as e:
                print(f"\nError: {str(e)}")
                
        elif selection == "Stop Bot":
            print("\nStopping bot...")
            
            try:
                success = self.loop.run_until_complete(self.bot.stop())
                
                if success:
                    print("\nBot stopped successfully.")
                else:
                    print("\nFailed to stop bot. Check logs for details.")
            except Exception as e:
                print(f"\nError: {str(e)}")
                
        elif selection == "Enable Test Mode" or selection == "Disable Test Mode":
            new_test_mode = selection == "Enable Test Mode"
            
            print(f"\n{'Enabling' if new_test_mode else 'Disabling'} test mode...")
            
            self.bot.set_test_mode(new_test_mode)
            print("\nTest mode updated.")
            
        input("\nPress Enter to continue...")
        
    def start(self):
        """Start the menu interface."""
        try:
            self.display_main_menu()
        except KeyboardInterrupt:
            print("\nExiting menu...")
        finally:
            # Stop the bot if it's running
            if self.bot.running:
                print("\nStopping bot before exit...")
                self.loop.run_until_complete(self.bot.stop())
                
            print("\nGoodbye!") 