# Discord Integration for WhatsApp Group Summarizer Bot

This document explains how to set up and use the Discord integration with the WhatsApp Group Summarizer Bot.

## Overview

The Discord integration allows you to control the WhatsApp bot remotely through a Discord interface. This provides added flexibility and accessibility for managing the bot's operations.

## Setup

### 1. Prerequisites

- A Discord account
- Permission to create a Discord bot
- A Discord server where you have administrative privileges

### 2. Creating a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name (e.g., "WhatsApp Summarizer")
3. Navigate to the "Bot" tab
4. Click "Add Bot"
5. Under the "TOKEN" section, click "Copy" to copy your bot token
6. Enable these "Privileged Gateway Intents":
   - Presence Intent
   - Server Members Intent
   - Message Content Intent

### 3. Adding the Bot to Your Server

1. Go to the "OAuth2" > "URL Generator" tab
2. Select the following scopes:
   - `bot`
   - `applications.commands`
3. Select the following bot permissions:
   - "Send Messages"
   - "Embed Links"
   - "Read Message History"
   - "Use Slash Commands"
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### 4. Configuring the Bot

Update your `.env` file with the following settings:

```
# Discord Configuration
ENABLE_DISCORD=true
DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN
DISCORD_GUILD_ID=YOUR_GUILD_ID
DISCORD_NOTIFICATION_CHANNEL=YOUR_CHANNEL_ID
```

Replace:
- `YOUR_DISCORD_BOT_TOKEN` with the token you copied earlier
- `YOUR_GUILD_ID` with your Discord server ID
- `YOUR_CHANNEL_ID` with the channel ID where you want notifications to be sent

To get IDs, enable Developer Mode in Discord (User Settings > Advanced > Developer Mode), then right-click on the server/channel name and select "Copy ID".

## Available Discord Commands

The Discord bot provides the following slash commands:

| Command | Description |
|---------|-------------|
| `/whatsapp_status` | Get the current status of the WhatsApp bot |
| `/start_whatsapp [background]` | Start the WhatsApp bot (with optional background mode) |
| `/stop_whatsapp` | Stop the WhatsApp bot |
| `/generate_summary [group_id] [send]` | Generate a summary for the specified group |
| `/set_groups [group_ids]` | Set the active WhatsApp groups to monitor |
| `/set_schedule [source_group] [target_group] [time] [test_mode]` | Configure automatic summarization schedule |
| `/toggle_schedule [enabled]` | Enable or disable scheduled summarization |

## Discord Permission Levels

The bot supports different permission levels:

1. **Admin**: Full access to all commands and settings
2. **Operator**: Can generate summaries and fetch messages
3. **Viewer**: Can only view status and groups

To set up permissions, use the Discord Integration menu in the Windows terminal interface.

## Troubleshooting

### Bot Not Responding to Commands

1. Check that the bot is online in your Discord server
2. Verify that you've entered the correct bot token in the `.env` file
3. Make sure the bot has the necessary permissions in your Discord server
4. Check the application logs for any errors

### Bot Online but Commands Not Working

1. Make sure you've enabled the "Message Content Intent" in the Discord Developer Portal
2. Verify that the slash commands are registered (may take up to an hour to propagate)
3. Try reinviting the bot to your server with the correct permissions

## Resources

- [Discord Developer Documentation](https://discord.com/developers/docs)
- [discord.py Documentation](https://discordpy.readthedocs.io/) 