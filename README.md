# WhatsApp Group Summarizer Bot

A bot that monitors WhatsApp group messages, stores them in a database, and generates summaries using AI. The bot can be controlled through a terminal menu, run in background mode, or through a Discord bot.

## Features

- ✅ Monitor and store WhatsApp group messages using the Green API
- ✅ Generate summaries of group messages using OpenAI
- ✅ Schedule automated summaries at specific times
- ✅ Control the bot through a terminal menu, in background mode, or via Discord
- ✅ Test mode for generating summaries without sending them
- ✅ Detailed logging to track bot activity

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database (or any SQLAlchemy-compatible database)
- Green API account for WhatsApp
- OpenAI API account
- Discord Bot Token (optional, for Discord control)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd whatsapp-summarizer-bot
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on the `.env.template`:
   ```bash
   cp .env.template .env
   ```

5. Edit the `.env` file and fill in your configuration details:
   - Database URL
   - Green API credentials
   - WhatsApp group IDs
   - OpenAI API key
   - Discord bot token (if using Discord control)

## Usage

The bot can be run in three different modes:

### Terminal Menu Mode (Default)

```bash
python -m src.main --mode menu
```

This mode provides a terminal-based menu interface for interacting with the bot:
- Generate and send summaries
- Manage schedules
- Debug and test connections
- View bot status

### Background Mode

```bash
python -m src.main --mode background
```

This mode runs the bot in the background, continuously monitoring for messages and executing scheduled tasks. It's useful for running the bot on a server.

### Discord Bot Mode

```bash
python -m src.main --mode discord
```

This mode starts a Discord bot that allows you to control the WhatsApp bot through Discord commands.

Available Discord commands:
- `/status` - Check the current status of the WhatsApp bot
- `/start` - Start the WhatsApp bot
- `/stop` - Stop the WhatsApp bot
- `/summary` - Generate and optionally send a summary
- `/active_groups` - Set active WhatsApp groups
- `/schedule` - Configure summary schedule

### Direct Bot Script

For direct use without a menu interface, you can use the `run_bot.py` script:

```bash
python run_bot.py --source GROUP_ID --target GROUP_ID --days 1 --debug
```

This script performs the complete message flow in one command:
1. Retrieves messages from the specified source group
2. Stores them in the database
3. Generates a summary of the messages
4. Posts the summary to the target group

Parameters:
- `--source`: WhatsApp group ID to retrieve messages from (required)
- `--target`: WhatsApp group ID to send the summary to (optional)
- `--days`: Number of days to include in the summary (default: 1)
- `--debug`: Enable debug logging (optional)

## WhatsApp Group Configuration

To monitor a WhatsApp group, you need to:

1. Get the group ID from the Green API
2. Add the group ID to the `WHATSAPP_GROUP_IDS` environment variable
3. Make sure the WhatsApp number connected to your Green API account is a member of the group

## Database Schema

The bot uses the following database tables:
- `whatsapp_messages` - Stores all received messages
- `message_summaries` - Stores generated summaries
- `schedule_config` - Stores scheduling configuration
- `bot_status` - Stores the current bot status

## Logging

Logs are stored in the `logs` directory with daily rotation. The log level can be configured in the `.env` file.

## License

[MIT License](LICENSE) 
