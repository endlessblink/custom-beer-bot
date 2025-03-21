import os
import asyncio
import datetime
from typing import Dict, List, Tuple
import inquirer
from loguru import logger
from prettytable import PrettyTable
from art import text2art
import colorama
from colorama import Fore, Style
from dotenv import load_dotenv

from ..whatsapp.bot import WhatsAppBot
from ..database.operations import DatabaseOperations
from ..database.model import Message, Summary, BotStatus
from ..discord.bot import DiscordBot

# Initialize colorama
colorama.init()

# Load environment variables
load_dotenv()

class WindowsMenu:
    """Command-line menu for controlling the WhatsApp and Discord bots."""

    def __init__(self, db_operations: DatabaseOperations):
        """Initialize the Windows menu with database operations."""
        self.db = db_operations
        self.whatsapp_bot = WhatsAppBot(db_operations)
        self.discord_bot = DiscordBot(self.db)
        
        # Load available WhatsApp groups from environment variables
        self.available_groups = self._load_whatsapp_groups()
        
        # Flag to control the main menu loop
        self.running = True
        
        logger.info("Windows menu initialized")

    def _load_whatsapp_groups(self) -> Dict[str, str]:
        """Load available WhatsApp groups from environment variables."""
        group_ids = os.getenv("WHATSAPP_GROUP_IDS", "").split(",")
        group_names = os.getenv("WHATSAPP_GROUP_NAMES", "").split(",")
        
        groups = {}
        
        # Create a dictionary of group_id -> group_name
        for i in range(min(len(group_ids), len(group_names))):
            group_id = group_ids[i].strip()
            group_name = group_names[i].strip()
            
            if group_id and group_name:
                groups[group_id] = group_name
        
        return groups
        
    def display_header(self):
        """Display the header for the WhatsApp/Discord Bot menu."""
        print("\n" + "=" * 60)
        print(Fore.CYAN + Style.BRIGHT + text2art("Beer Bots", font="small") + Style.RESET_ALL)
        print(Fore.YELLOW + Style.BRIGHT + "WhatsApp Message Manager & Discord Integration" + Style.RESET_ALL)
        print("=" * 60 + "\n")
    
    def display_bot_status(self):
        """Display the current status of the bots."""
        try:
            status = self.db.get_bot_status()
            
            if not status:
                print(f"{Fore.RED}No status information available{Style.RESET_ALL}")
                return
                
            whatsapp_status = Fore.GREEN + "Connected" + Style.RESET_ALL if status.whatsapp_connected else Fore.RED + "Disconnected" + Style.RESET_ALL
            whatsapp_running = Fore.GREEN + "Running" + Style.RESET_ALL if status.is_running else Fore.RED + "Stopped" + Style.RESET_ALL
            whatsapp_mode = Fore.YELLOW + "Background" + Style.RESET_ALL if status.is_background_mode else Fore.CYAN + "Foreground" + Style.RESET_ALL
            
            discord_connected = Fore.GREEN + "Connected" + Style.RESET_ALL if status.discord_connected else Fore.RED + "Disconnected" + Style.RESET_ALL
            discord_running = Fore.GREEN + "Running" + Style.RESET_ALL if status.discord_is_running else Fore.RED + "Stopped" + Style.RESET_ALL
            
            target_group = self.whatsapp_bot.authorized_target_group
            target_name = self.available_groups.get(target_group, "None") if target_group else "None"
            message_auth = Fore.GREEN + "Authorized" + Style.RESET_ALL if self.whatsapp_bot.message_sending_authorized else Fore.RED + "Not Authorized" + Style.RESET_ALL
            
            last_summary_time = status.last_summary_time.strftime("%Y-%m-%d %H:%M") if status.last_summary_time else "Never"
            
            status_table = PrettyTable()
            status_table.field_names = ["Service", "Status", "Running", "Mode/Details"]
            status_table.add_row(["WhatsApp", whatsapp_status, whatsapp_running, whatsapp_mode])
            status_table.add_row(["Discord", discord_connected, discord_running, ""])
            status_table.add_row(["Target Group", target_name, "", target_group if target_group else ""])
            status_table.add_row(["Sending", message_auth, "", ""])
            status_table.add_row(["Last Summary", last_summary_time, "", ""])
            
            print(status_table)
            print()
            
        except Exception as e:
            logger.error(f"Error displaying bot status: {str(e)}")
            print(f"{Fore.RED}Error displaying bot status: {str(e)}{Style.RESET_ALL}")
        
    def display_main_menu(self) -> List[str]:
        """Display the main menu options and get user's choice."""
        menu_options = [
            "WhatsApp Bot Control",
            "WhatsApp Message Management",
            "Discord Bot Control",
            "View Bot Status",
            "Exit"
        ]
        
        questions = [
            inquirer.List(
                'option',
                message="Select an option",
                choices=menu_options,
            ),
        ]
        
        return inquirer.prompt(questions)['option']
        
    def display_whatsapp_control_menu(self) -> str:
        """Display the WhatsApp bot control menu options and get user's choice."""
        menu_options = [
            "Connect to WhatsApp",
            "Start Bot (Foreground)",
            "Start Bot (Background)",
            "Stop Bot",
            "Set Target Group",
            "Authorize Message Sending",
            "Back to Main Menu"
        ]
        
        questions = [
            inquirer.List(
                'option',
                message="Select a WhatsApp control option",
                choices=menu_options,
            ),
        ]
        
        return inquirer.prompt(questions)['option']
    
    def display_whatsapp_message_menu(self) -> str:
        """Display the WhatsApp message management menu options and get user's choice."""
        menu_options = [
            "Generate Summary (Last Day)",
            "Generate Summary (Custom Timeframe)",
            "Send Latest Summary",
            "View Recent Summaries",
            "View Recent Messages",
            "Back to Main Menu"
        ]
        
        questions = [
            inquirer.List(
                'option',
                message="Select a message management option",
                choices=menu_options,
            ),
        ]
        
        return inquirer.prompt(questions)['option']
    
    def display_discord_control_menu(self) -> str:
        """Display the Discord bot control menu options and get user's choice."""
        menu_options = [
            "Connect to Discord",
            "Start Discord Bot",
            "Stop Discord Bot",
            "Back to Main Menu"
        ]
        
        questions = [
            inquirer.List(
                'option',
                message="Select a Discord control option",
                choices=menu_options,
            ),
        ]
        
        return inquirer.prompt(questions)['option']
        
    def select_whatsapp_group(self) -> str:
        """Prompt the user to select a WhatsApp group."""
        if not self.available_groups:
            print(f"{Fore.RED}No WhatsApp groups configured.{Style.RESET_ALL}")
            return None
            
        group_options = [f"{name} ({group_id})" for group_id, name in self.available_groups.items()]
        group_options.append("Cancel")
        
        questions = [
            inquirer.List(
                'group',
                message="Select a WhatsApp group",
                choices=group_options,
            ),
        ]
        
        selected = inquirer.prompt(questions)['group']
        
        if selected == "Cancel":
            return None
            
        # Extract the group ID from the selected option
        for group_id in self.available_groups:
            if group_id in selected:
                return group_id
                
        return None
        
    def select_days_for_summary(self) -> int:
        """Prompt the user to select how many days to include in the summary."""
        questions = [
            inquirer.List(
                'days',
                message="Select timeframe for summary",
                choices=["1 day", "3 days", "7 days", "14 days", "30 days", "Custom", "Cancel"],
            ),
        ]
        
        selected = inquirer.prompt(questions)['days']
        
        if selected == "Cancel":
            return None
            
        if selected == "Custom":
            days_question = [
                inquirer.Text(
                    'custom_days',
                    message="Enter number of days",
                    validate=lambda _, x: x.isdigit() and int(x) > 0,
                ),
            ]
            
            custom_days = inquirer.prompt(days_question)['custom_days']
            return int(custom_days)
            
        # Extract the number of days from the selected option
        return int(selected.split()[0])
        
    def display_summaries(self, summaries: List[Summary]):
        """Display a table of summaries."""
        if not summaries:
            print(f"{Fore.YELLOW}No summaries available.{Style.RESET_ALL}")
            return
            
        table = PrettyTable()
        table.field_names = ["ID", "Date", "Group", "Messages", "Sent", "Length"]
        
        for summary in summaries:
            group_name = self.available_groups.get(summary.group_id, "Unknown")
            sent_status = Fore.GREEN + "✓" + Style.RESET_ALL if summary.is_sent else Fore.RED + "✗" + Style.RESET_ALL
            
            table.add_row([
                summary.id,
                summary.created_at.strftime("%Y-%m-%d %H:%M"),
                group_name,
                summary.message_count,
                sent_status,
                len(summary.summary_text)
            ])
            
        print(table)
        
        # Prompt to view summary text
        questions = [
            inquirer.List(
                'action',
                message="Select action",
                choices=["View Summary Text", "Back"],
            ),
        ]
        
        action = inquirer.prompt(questions)['action']
        
        if action == "View Summary Text":
            # Prompt for summary ID
            id_question = [
                inquirer.Text(
                    'summary_id',
                    message="Enter summary ID to view",
                    validate=lambda _, x: x.isdigit() and int(x) > 0,
                ),
            ]
            
            summary_id = inquirer.prompt(id_question)['summary_id']
            self.display_summary_text(int(summary_id))
            
    def display_summary_text(self, summary_id: int):
        """Display the text of a specific summary."""
        summary = self.db.get_summary_by_id(summary_id)
        
        if not summary:
            print(f"{Fore.RED}Summary with ID {summary_id} not found.{Style.RESET_ALL}")
            return
            
        group_name = self.available_groups.get(summary.group_id, "Unknown")
        
        print("\n" + "=" * 60)
        print(f"{Fore.CYAN}Summary #{summary.id} - {group_name}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Generated: {summary.created_at.strftime('%Y-%m-%d %H:%M')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Message Count: {summary.message_count}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Status: {'Sent' if summary.is_sent else 'Not Sent'}{Style.RESET_ALL}")
        print("=" * 60)
        print(f"\n{summary.summary_text}\n")
        print("=" * 60 + "\n")
        
    def display_messages(self, messages: List[Message]):
        """Display a table of messages."""
        if not messages:
            print(f"{Fore.YELLOW}No messages available.{Style.RESET_ALL}")
            return
            
        table = PrettyTable()
        table.field_names = ["ID", "Timestamp", "Group", "Sender", "Message"]
        table.max_width["Message"] = 50
        
        for message in messages:
            group_name = self.available_groups.get(message.chat_id, "Unknown")
            message_text = message.message_text[:47] + "..." if len(message.message_text) > 50 else message.message_text
            
            table.add_row([
                message.id,
                message.timestamp.strftime("%Y-%m-%d %H:%M"),
                group_name,
                message.sender_name,
                message_text
            ])
            
        print(table)
        
    async def handle_whatsapp_control(self, option: str):
        """Handle the selected WhatsApp control option."""
        if option == "Connect to WhatsApp":
            connected = await self.whatsapp_bot.check_connection()
            
            if connected:
                print(f"{Fore.GREEN}Successfully connected to WhatsApp.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Failed to connect to WhatsApp. Check your API credentials.{Style.RESET_ALL}")
                
        elif option == "Start Bot (Foreground)":
            if await self.whatsapp_bot.start(background_mode=False):
                print(f"{Fore.GREEN}WhatsApp bot started in foreground mode.{Style.RESET_ALL}")
                
                # Start the message processing loop
                try:
                    print(f"{Fore.YELLOW}Processing messages... Press Ctrl+C to stop.{Style.RESET_ALL}")
                    await self.whatsapp_bot.process_messages_loop()
                except KeyboardInterrupt:
                    print(f"{Fore.YELLOW}Stopping bot...{Style.RESET_ALL}")
                    await self.whatsapp_bot.stop()
            else:
                print(f"{Fore.RED}Failed to start WhatsApp bot.{Style.RESET_ALL}")
                
        elif option == "Start Bot (Background)":
            if await self.whatsapp_bot.start(background_mode=True):
                print(f"{Fore.GREEN}WhatsApp bot started in background mode.{Style.RESET_ALL}")
                
                # Start the message processing loop in a background task
                asyncio.create_task(self.whatsapp_bot.process_messages_loop())
            else:
                print(f"{Fore.RED}Failed to start WhatsApp bot.{Style.RESET_ALL}")
                
        elif option == "Stop Bot":
            if await self.whatsapp_bot.stop():
                print(f"{Fore.GREEN}WhatsApp bot stopped.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Failed to stop WhatsApp bot.{Style.RESET_ALL}")

        elif option == "Set Target Group":
            group_id = self.select_whatsapp_group()
            if group_id:
                success = self.whatsapp_bot.set_target_group(group_id)
                if success:
                    group_name = self.available_groups.get(group_id, "Unknown")
                    print(f"{Fore.GREEN}Target group set to: {group_name} ({group_id}){Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Failed to set target group.{Style.RESET_ALL}")
        
        elif option == "Authorize Message Sending":
            questions = [
                inquirer.Confirm(
                    'confirm',
                    message="Are you sure you want to authorize message sending? This will allow the bot to send messages.",
                    default=False
                ),
            ]
            
            confirmed = inquirer.prompt(questions)['confirm']
            
            if confirmed:
                if not self.whatsapp_bot.authorized_target_group:
                    print(f"{Fore.RED}No target group set. Please set a target group first.{Style.RESET_ALL}")
                    return
                
                self.whatsapp_bot.authorize_message_sending(True)
                print(f"{Fore.GREEN}Message sending authorized.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Note: Authorization will be reset after sending a message or restarting the bot.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Message sending authorization cancelled.{Style.RESET_ALL}")
    
    async def handle_whatsapp_messages(self, option: str):
        """Handle the selected WhatsApp message management option."""
        if option == "Generate Summary (Last Day)":
            # Prompt for group selection
            group_id = self.select_whatsapp_group()
            
            if not group_id:
                return
                
            print(f"{Fore.YELLOW}Generating summary for the last day...{Style.RESET_ALL}")
            summary = await self.whatsapp_bot.generate_summary(group_id, days=1)
            
            if summary:
                print(f"{Fore.GREEN}Summary generated successfully!{Style.RESET_ALL}")
                self.display_summary_text(summary['summary_id'])
            else:
                print(f"{Fore.RED}Failed to generate summary. Check logs for details.{Style.RESET_ALL}")
                
        elif option == "Generate Summary (Custom Timeframe)":
            # Prompt for group selection
            group_id = self.select_whatsapp_group()
            
            if not group_id:
                return
                
            # Prompt for days
            days = self.select_days_for_summary()
            
            if not days:
                return
                
            print(f"{Fore.YELLOW}Generating summary for the last {days} days...{Style.RESET_ALL}")
            summary = await self.whatsapp_bot.generate_summary(group_id, days=days)
            
            if summary:
                print(f"{Fore.GREEN}Summary generated successfully!{Style.RESET_ALL}")
                self.display_summary_text(summary['summary_id'])
            else:
                print(f"{Fore.RED}Failed to generate summary. Check logs for details.{Style.RESET_ALL}")
                
        elif option == "Send Latest Summary":
            if not self.whatsapp_bot.authorized_target_group:
                print(f"{Fore.RED}No target group set. Please set a target group first.{Style.RESET_ALL}")
                group_id = self.select_whatsapp_group()
                if group_id:
                    self.whatsapp_bot.set_target_group(group_id)
                else:
                    return
            
            if not self.whatsapp_bot.message_sending_authorized:
                questions = [
                    inquirer.Confirm(
                        'authorize',
                        message="Message sending is not authorized. Authorize now?",
                        default=False
                    ),
                ]
                
                authorize = inquirer.prompt(questions)['authorize']
                
                if authorize:
                    self.whatsapp_bot.authorize_message_sending(True)
                else:
                    print(f"{Fore.YELLOW}Message sending cancelled.{Style.RESET_ALL}")
                    return
            
            # Get latest summary
            latest_summary = self.db.get_latest_summary()
            
            if not latest_summary:
                print(f"{Fore.RED}No summaries available to send.{Style.RESET_ALL}")
                return
                
            # Confirm sending
            group_name = self.available_groups.get(self.whatsapp_bot.authorized_target_group, "Unknown")
            
            questions = [
                inquirer.Confirm(
                    'confirm',
                    message=f"Send latest summary to {group_name}?",
                    default=False
                ),
            ]
            
            confirmed = inquirer.prompt(questions)['confirm']
            
            if confirmed:
                print(f"{Fore.YELLOW}Sending summary...{Style.RESET_ALL}")
                success = await self.whatsapp_bot.send_summary(latest_summary.id)
                
                if success:
                    print(f"{Fore.GREEN}Summary sent successfully!{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Failed to send summary. Check logs for details.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Sending cancelled.{Style.RESET_ALL}")
                
        elif option == "View Recent Summaries":
            # Get recent summaries
            summaries = self.db.get_recent_summaries(limit=10)
            self.display_summaries(summaries)
            
        elif option == "View Recent Messages":
            # Prompt for group selection
            group_id = self.select_whatsapp_group()
            
            if not group_id:
                return
                
            # Get recent messages for the selected group
            messages = self.db.get_recent_messages(group_id, limit=20)
            self.display_messages(messages)
            
    async def handle_discord_control(self, option: str):
        """Handle the selected Discord control option."""
        if option == "Connect to Discord":
            connected = self.discord_bot.check_connection()
            
            if connected:
                print(f"{Fore.GREEN}Successfully connected to Discord.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Failed to connect to Discord. Check your bot token.{Style.RESET_ALL}")
                
        elif option == "Start Discord Bot":
            if self.discord_bot.is_running:
                print(f"{Fore.YELLOW}Discord bot is already running.{Style.RESET_ALL}")
                return
                
            print(f"{Fore.YELLOW}Starting Discord bot...{Style.RESET_ALL}")
            success = await self.discord_bot.start()
            
            if success:
                print(f"{Fore.GREEN}Discord bot started successfully.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Failed to start Discord bot. Check logs for details.{Style.RESET_ALL}")
                
        elif option == "Stop Discord Bot":
            if not self.discord_bot.is_running:
                print(f"{Fore.YELLOW}Discord bot is not running.{Style.RESET_ALL}")
                return
                
            print(f"{Fore.YELLOW}Stopping Discord bot...{Style.RESET_ALL}")
            success = await self.discord_bot.stop()
            
            if success:
                print(f"{Fore.GREEN}Discord bot stopped successfully.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Failed to stop Discord bot. Check logs for details.{Style.RESET_ALL}")
                
    async def run(self):
        """Run the Windows menu."""
        try:
            while self.running:
                self.display_header()
                self.display_bot_status()
                
                option = self.display_main_menu()
                
                if option == "WhatsApp Bot Control":
                    whatsapp_option = self.display_whatsapp_control_menu()
                    
                    if whatsapp_option != "Back to Main Menu":
                        await self.handle_whatsapp_control(whatsapp_option)
                        
                elif option == "WhatsApp Message Management":
                    message_option = self.display_whatsapp_message_menu()
                    
                    if message_option != "Back to Main Menu":
                        await self.handle_whatsapp_messages(message_option)
                        
                elif option == "Discord Bot Control":
                    discord_option = self.display_discord_control_menu()
                    
                    if discord_option != "Back to Main Menu":
                        await self.handle_discord_control(discord_option)
                        
                elif option == "View Bot Status":
                    # Just show the status and wait for user to press enter
                    input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                    
                elif option == "Exit":
                    self.running = False
                    break
                    
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
            
        finally:
            # Clean up resources
            await self.whatsapp_bot.stop()
            await self.discord_bot.stop()
            print(f"{Fore.GREEN}Thank you for using the WhatsApp Bot Manager!{Style.RESET_ALL}")
            
async def main():
    """Main entry point for the Windows menu."""
    # Create database operations instance
    db_operations = DatabaseOperations()
    
    # Create and run the Windows menu
    menu = WindowsMenu(db_operations)
    await menu.run()
    
if __name__ == "__main__":
    asyncio.run(main()) 