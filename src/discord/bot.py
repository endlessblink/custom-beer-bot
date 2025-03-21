import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from typing import Dict, List, Optional
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DiscordBot:
    """Discord Bot for controlling the WhatsApp bot."""
    
    def __init__(self, whatsapp_bot=None, db_operations=None):
        """
        Initialize the Discord bot.
        
        Args:
            whatsapp_bot: Optional WhatsApp bot instance
            db_operations: Optional database operations instance
        """
        self.token = os.getenv("DISCORD_BOT_TOKEN")
        self.guild_id = int(os.getenv("DISCORD_GUILD_ID", "0"))
        self.notification_channel_id = int(os.getenv("DISCORD_NOTIFICATION_CHANNEL", "0"))
        
        if not self.token:
            logger.error("Discord token not found")
            raise ValueError("DISCORD_BOT_TOKEN environment variable must be set")
        
        # Create a Discord bot with intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        self.whatsapp_bot = whatsapp_bot  # May be set externally if None
        self.db_operations = db_operations
        
        # Set up event handlers
        self._setup_event_handlers()
        # Set up commands
        self._setup_commands()
        
        logger.info("Discord bot initialized")
    
    def _setup_event_handlers(self):
        """Set up Discord event handlers."""
        
        @self.bot.event
        async def on_ready():
            """Handle bot ready event."""
            logger.info(f"Discord bot logged in as {self.bot.user}")
            
            # Sync commands with Discord
            try:
                synced = await self.bot.tree.sync()
                logger.info(f"Synced {len(synced)} command(s)")
            except Exception as e:
                logger.error(f"Error syncing commands: {str(e)}")
    
    def _setup_commands(self):
        """Set up Discord slash commands."""
        
        @self.bot.tree.command(name="whatsapp_status", description="Get the status of the WhatsApp bot")
        async def whatsapp_status(interaction: discord.Interaction):
            """Get the status of the WhatsApp bot."""
            if not self.whatsapp_bot:
                await interaction.response.send_message("WhatsApp bot is not initialized")
                return
                
            status = self.whatsapp_bot.get_status()
            
            # Create an embed with the status information
            embed = discord.Embed(
                title="WhatsApp Bot Status",
                color=discord.Color.green() if status['whatsapp_connected'] else discord.Color.red()
            )
            
            embed.add_field(name="Running", value=str(status['running']), inline=True)
            embed.add_field(name="Background Mode", value=str(status['background_mode']), inline=True)
            embed.add_field(name="Test Mode", value=str(status['test_mode']), inline=True)
            embed.add_field(name="WhatsApp Connected", value=str(status['whatsapp_connected']), inline=True)
            
            if status['active_groups']:
                embed.add_field(name="Active Groups", value="\n".join(status['active_groups']), inline=False)
            else:
                embed.add_field(name="Active Groups", value="No active groups", inline=False)
                
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="start_whatsapp", description="Start the WhatsApp bot")
        @app_commands.describe(background="Run in background mode")
        async def start_whatsapp(interaction: discord.Interaction, background: bool = False):
            """Start the WhatsApp bot."""
            if not self.whatsapp_bot:
                await interaction.response.send_message("WhatsApp bot is not initialized")
                return
                
            # Defer the response as this might take a moment
            await interaction.response.defer()
            
            # Start the WhatsApp bot
            success = await self.whatsapp_bot.start(background_mode=background)
            
            if success:
                await interaction.followup.send(f"WhatsApp bot started in {'background' if background else 'foreground'} mode")
                
                # Start the message processing loop if in background mode
                if background:
                    asyncio.create_task(self.whatsapp_bot.process_messages_loop())
            else:
                await interaction.followup.send("Failed to start WhatsApp bot. Check logs for details.")
        
        @self.bot.tree.command(name="stop_whatsapp", description="Stop the WhatsApp bot")
        async def stop_whatsapp(interaction: discord.Interaction):
            """Stop the WhatsApp bot."""
            if not self.whatsapp_bot:
                await interaction.response.send_message("WhatsApp bot is not initialized")
                return
                
            success = await self.whatsapp_bot.stop()
            
            if success:
                await interaction.response.send_message("WhatsApp bot stopped")
            else:
                await interaction.response.send_message("Failed to stop WhatsApp bot. Check logs for details.")
        
        @self.bot.tree.command(name="generate_summary", description="Generate a summary of messages from a group")
        @app_commands.describe(
            group_id="The WhatsApp group ID to summarize messages from",
            send="Whether to send the summary to the group"
        )
        async def generate_summary(interaction: discord.Interaction, group_id: str, send: bool = False):
            """Generate a summary of messages from a group."""
            if not self.whatsapp_bot:
                await interaction.response.send_message("WhatsApp bot is not initialized")
                return
                
            # Defer the response as this might take a while
            await interaction.response.defer()
            
            # Generate the summary
            summary_result = await self.whatsapp_bot.generate_and_send_summary(
                source_group_id=group_id,
                target_group_id=group_id if send else None,
                send=send
            )
            
            if summary_result:
                # Create an embed with the summary
                embed = discord.Embed(
                    title="Message Summary",
                    description=f"Summary generated from {summary_result['message_count']} messages",
                    color=discord.Color.blue()
                )
                
                # Use the first 4000 characters of the summary to avoid Discord's limit
                summary_text = summary_result['summary_text'][:4000]
                if len(summary_result['summary_text']) > 4000:
                    summary_text += "... (truncated)"
                    
                embed.add_field(name="Summary", value=summary_text, inline=False)
                
                if send:
                    embed.add_field(name="Sent to Group", value=str(summary_result.get('sent', False)), inline=True)
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("Failed to generate summary. Not enough messages or an error occurred.")
        
        @self.bot.tree.command(name="set_groups", description="Set the active WhatsApp groups to monitor")
        @app_commands.describe(group_ids="Comma-separated list of WhatsApp group IDs to monitor")
        async def set_groups(interaction: discord.Interaction, group_ids: str):
            """Set the active WhatsApp groups to monitor."""
            if not self.whatsapp_bot:
                await interaction.response.send_message("WhatsApp bot is not initialized")
                return
                
            # Parse the group IDs
            groups = [g.strip() for g in group_ids.split(",") if g.strip()]
            
            if not groups:
                await interaction.response.send_message("No valid group IDs provided")
                return
                
            # Set the active groups
            self.whatsapp_bot.set_active_groups(groups)
            
            await interaction.response.send_message(f"Active groups updated. Now monitoring {len(groups)} group(s).")
        
        @self.bot.tree.command(name="set_schedule", description="Set the schedule for automatic summarization")
        @app_commands.describe(
            source_group="The WhatsApp group ID to summarize messages from",
            target_group="The WhatsApp group ID to send summaries to",
            time="The time to send summaries (HH:MM in 24-hour format)",
            test_mode="Whether to run in test mode"
        )
        async def set_schedule(
            interaction: discord.Interaction, 
            source_group: str, 
            target_group: str, 
            time: str, 
            test_mode: bool = False
        ):
            """Set the schedule for automatic summarization."""
            if not self.whatsapp_bot or not hasattr(self.whatsapp_bot, 'db'):
                await interaction.response.send_message("WhatsApp bot is not initialized")
                return
                
            # Validate the time format
            try:
                hour, minute = map(int, time.split(':'))
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    raise ValueError("Invalid time")
            except Exception:
                await interaction.response.send_message("Invalid time format. Use HH:MM in 24-hour format.")
                return
                
            # Save the schedule configuration
            try:
                self.whatsapp_bot.db.save_schedule_config(
                    source_group_id=source_group,
                    target_group_id=target_group,
                    schedule_time=time,
                    is_active=True,
                    test_mode=test_mode
                )
                
                await interaction.response.send_message(
                    f"Schedule configured. Summaries will be generated from {source_group} "
                    f"and sent to {target_group} at {time} daily. "
                    f"Test mode: {test_mode}"
                )
            except Exception as e:
                logger.error(f"Error setting schedule: {str(e)}")
                await interaction.response.send_message(f"Failed to set schedule: {str(e)}")
        
        @self.bot.tree.command(name="toggle_schedule", description="Enable or disable the scheduled summarization")
        @app_commands.describe(enabled="Whether the schedule should be enabled")
        async def toggle_schedule(interaction: discord.Interaction, enabled: bool):
            """Enable or disable the scheduled summarization."""
            if not self.whatsapp_bot or not hasattr(self.whatsapp_bot, 'db'):
                await interaction.response.send_message("WhatsApp bot is not initialized")
                return
                
            # Update the schedule status
            config = self.whatsapp_bot.db.update_schedule_status(is_active=enabled)
            
            if config:
                await interaction.response.send_message(
                    f"Schedule {'enabled' if enabled else 'disabled'}. "
                    f"Configured for {config.schedule_time}."
                )
            else:
                await interaction.response.send_message("No schedule configuration found. Please set a schedule first.")
    
    async def start(self):
        """Start the Discord bot."""
        if not self.token:
            logger.error("Cannot start Discord bot: No token provided")
            return False
            
        try:
            await self.bot.start(self.token)
            return True
        except Exception as e:
            logger.error(f"Error starting Discord bot: {str(e)}")
            return False
    
    async def send_notification(self, message: str, embed: discord.Embed = None):
        """Send a notification to the designated channel."""
        if not self.notification_channel_id:
            logger.warning("No notification channel ID set, can't send notification")
            return False
            
        try:
            channel = self.bot.get_channel(self.notification_channel_id)
            if not channel:
                logger.warning(f"Could not find channel with ID {self.notification_channel_id}")
                return False
                
            if embed:
                await channel.send(content=message, embed=embed)
            else:
                await channel.send(content=message)
                
            return True
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return False
            
    def set_whatsapp_bot(self, whatsapp_bot):
        """Set the WhatsApp bot instance for the Discord bot to control."""
        self.whatsapp_bot = whatsapp_bot
        logger.info("WhatsApp bot instance set in Discord bot") 