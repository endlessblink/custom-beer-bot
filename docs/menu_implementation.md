# Menu Implementation Documentation

## Overview

This document describes the implementation of the WhatsApp Bot menu system. The menu system provides a terminal-based interface for controlling the WhatsApp Bot and accessing its features.

## Menu Structure

The menu system follows the structure defined in `docs/menu_screens.md`, with the following main components:

1. **Main Menu**
   - Generate New Summary
   - Fetch New Messages
   - Background Mode
   - Settings
   - Debug Mode
   - Discord Integration (when available)
   - Exit

2. **Generate Summary Flow**
   - Group selection
   - Days selection
   - Debug mode toggle
   - Summary generation and displaying
   - Option to send summary

3. **Background Mode Menu**
   - Start bot in background
   - Configure scheduled posting
   - Set source/target groups
   - View current settings

4. **Settings Menu**
   - Set preferred group
   - Select OpenAI model
   - View current settings

5. **Debug Menu**
   - Test API connections
   - Export message data
   - View log files

6. **Discord Integration Menu** (when Discord bot is available)
   - Configure Discord bot
   - Manage commands
   - Set permissions
   - View Discord logs
   - Test connection

## Implementation Details

### Platform-Specific Menus

The menu system has two implementations:

1. **Windows Menu (`WindowsBotMenu` in `src/menu/windows_menu.py`)**
   - A custom implementation for Windows systems
   - Uses direct console input/output for compatibility
   - Provides all the features of the menu system

2. **Terminal Menu (`BotMenu` in `src/menu/terminal_menu.py`)**
   - Uses the `simple_term_menu` library for Unix-like systems
   - Provides a more visually appealing menu interface
   - Has the same functionality as the Windows menu

The appropriate menu is chosen at runtime based on the platform:

```python
if platform.system() == 'Windows':
    from src.menu.windows_menu import WindowsBotMenu as BotMenu
else:
    from src.menu.terminal_menu import BotMenu
```

### Discord Integration

The Discord integration menu is implemented in `src/menu/discord_menu.py` and is loaded dynamically when a Discord bot instance is available. This modular design allows the Discord integration to be optional, making the bot more flexible.

### Key Classes

1. **`WindowsTerminalMenu`**
   - Basic menu display and input handling for Windows
   - Displays options and returns user selection

2. **`WindowsBotMenu`**
   - Main menu implementation for Windows
   - Handles all menu actions and application logic

3. **`DiscordMenu`**
   - Discord integration menu
   - Provides Discord-specific configuration options

## Usage

To use the menu system in your code:

```python
from src.menu.windows_menu import create_bot_menu

# Create menu instance with required dependencies
menu = create_bot_menu(whatsapp_bot, db_operations, discord_bot)

# Start the menu interface
menu.start()
```

The menu will handle user input and execute the appropriate actions based on user selection.

## Customization

To add a new menu option:

1. Add the option to the relevant menu options list in the menu class
2. Implement the handler method for the new option
3. Add the option to the menu actions dictionary in `_setup_menu_actions()`

For example, to add a new option to the main menu:

```python
def _setup_menu_actions(self):
    """Configure menu actions."""
    # Main menu actions
    self.main_menu_actions = {
        # Existing options
        "New Option": self._handle_new_option,
        "Exit": self._exit_app
    }

def _handle_new_option(self):
    """Handle the new option."""
    # Implementation
    pass
```

## Error Handling

Each menu action is wrapped in a try-except block to catch and log errors. This ensures that the menu system remains operational even if individual actions fail. Errors are logged using the loguru logger and displayed to the user when appropriate.

## Best Practices

1. **Clear Screen**: Always clear the screen before displaying a new menu to keep the interface clean
2. **Consistent Header**: Use the same header format across all menu screens
3. **Navigation**: Always provide a way to go back to the previous menu
4. **Confirmation**: Ask for confirmation before performing destructive actions
5. **Error Handling**: Catch and log all exceptions to prevent the menu from crashing 