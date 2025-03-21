# WhatsApp Bot Menu Screens 
  
## Main Menu  
  
The main menu is the primary interface for the WhatsApp Bot. It provides access to all key functionality.  
  
```plaintext  
===============================  
WHATSAPP GROUP SUMMARY GENERATOR  
===============================  
  
Main Menu:  
1. Generate New Summary  
2. Fetch New Messages  
3. Background Mode  
4. Settings  
5. Debug Mode  
6. Exit  
  
Enter your choice:  
``` 
  
## Generate New Summary (Option 1)  
  
This option allows you to generate a summary of messages from a selected WhatsApp group for a specified time period.  
  
### Group Selection  
  
```plaintext  
===============================  
WHATSAPP GROUP SUMMARY GENERATOR  
===============================  
  
Select a Group:  
1. Family Group  
2. Work Team  
3. Hiking Club  
  
Enter your choice:  
```  
  
### Days Selection  
  
```plaintext  
===============================  
WHATSAPP GROUP SUMMARY GENERATOR  
===============================  
  
Select number of days to summarize:  
1. 1 day  
2. 3 days  
3. 7 days  
4. Custom number of days  
  
Enter your choice:  
```  
  
### Debug Mode Toggle  
  
```plaintext  
Enable debug mode? (y/n):  
```  
  
### Summary Result  
  
```plaintext  
? Summary generated successfully!  
  
[Summary text appears here]  
  
Send this summary to the group? (y/n):  
``` 
  
## Fetch New Messages (Option 2)  
  
This option fetches new messages from all available groups and stores them in the database.  
  
```plaintext  
? Fetching new messages...  
  
? Messages fetched and stored successfully  
  
Press Enter to continue...  
```  
  
## Background Mode (Option 3)  
  
This option allows you to configure and start the bot in background mode, which periodically fetches messages and generates summaries on a schedule.  
  
```plaintext  
===============================  
WHATSAPP GROUP SUMMARY GENERATOR  
===============================  
  
Background Mode:  
1. Start Bot in Background  
2. Set Scheduled Posting Time  
3. Set Source Group (for fetching messages)  
4. Set Target Group (for posting summaries)  
5. Set Test Group (for testing summaries)  
6. View Current Background Settings  
7. Back  
  
Enter your choice:  
```  
  
### Start Bot in Background (Option 3.1)  
  
```plaintext  
===============================  
WHATSAPP GROUP SUMMARY GENERATOR  
===============================  
  
Start Bot in Background  
  
?? Running in background mode will keep the bot active and executing scheduled tasks.  
?? The terminal window must remain open while the bot is running.  
  
Start the bot in background mode? (y/n):  
``` 
  
## Settings Menu (Option 4)  
  
This menu allows you to configure various settings for the WhatsApp Bot.  
  
```plaintext  
===============================  
WHATSAPP GROUP SUMMARY GENERATOR  
===============================  
  
Settings:  
1. Set Preferred Group  
2. Set OpenAI Model  
3. View Current Settings  
4. Back  
  
Enter your choice:  
```  
  
### Set Preferred Group (Option 4.1)  
  
```plaintext  
===============================  
WHATSAPP GROUP SUMMARY GENERATOR  
===============================  
  
Set Preferred Group  
  
Select a Group:  
1. Family Group  
2. Work Team  
3. Hiking Club  
  
Enter your choice:  
```  
  
### Set OpenAI Model (Option 4.2)  
  
```plaintext  
===============================  
WHATSAPP GROUP SUMMARY GENERATOR  
===============================  
  
Select OpenAI Model:  
1. GPT-4o  
2. GPT-4o-mini  
3. GPT-3.5 Turbo  
4. Claude 3 Opus  
5. Claude 3 Sonnet  
6. Claude 3 Haiku  
7. Cancel  
  
Enter your choice:  
```  
  
### View Current Settings (Option 4.3)  
  
```plaintext  
===============================  
WHATSAPP GROUP SUMMARY GENERATOR  
===============================  
  
Current Settings  
  
User Settings:  
  PREFERRED_GROUP_ID: 1234567890@g.us (Family Group)  
  OPENAI_MODEL: gpt-4o-mini  
  SCHEDULED_POST_TIME: 08:00  
  
Environment Variables:  
  OPENAI_API_KEY: sk-***  
  GREEN_API_ID_INSTANCE: 123456  
  GREEN_API_TOKEN: ***  
  BOT_TARGET_LANGUAGE: hebrew  
  BOT_MESSAGE_SENDING_DISABLED: False  
  
Press Enter to continue...  
``` 
  
## Debug Menu (Option 5)  
  
This menu provides various debugging tools and options to troubleshoot issues with the WhatsApp Bot.  
  
```plaintext  
===============================  
WHATSAPP GROUP SUMMARY GENERATOR  
===============================  
  
Debug Menu:  
1. Test API Connections  
2. Export Message Data  
3. View Log Files  
4. Back  
  
Enter your choice:  
```  
  
### Test API Connections (Option 5.1)  
  
```plaintext  
===============================  
WHATSAPP GROUP SUMMARY GENERATOR  
===============================  
  
Testing API Connections  
  
? Green API connection: authorized  
? OpenAI connection: OK  
?? Supabase client not initialized  
  
Press Enter to continue...  
```  
  
### View Log Files (Option 5.3)  
  
```plaintext  
===============================  
WHATSAPP GROUP SUMMARY GENERATOR  
===============================  
  
View Log Files  
  
Select a log file to view:  
1. app_2023-05-15.log  
2. error_2023-05-15.log  
3. app_2023-05-14.log  
b. Back  
  
Enter your choice:  
```  
  
## Exit (Option 6)  
  
```plaintext  
Exiting...  
  
Goodbye!  
``` 
  
## Menu Implementation Details  
  
The menu system is implemented using a core menu display function that handles:  
  
- Consistent display of headers and options  
- Graceful handling of unavailable components  
- Input validation  
- User feedback and error messages  
  
The key functions for the menu system are:  
  
- `show_menu()`: Core function for displaying menus and getting user input  
- `print_header()`: Displays the application header  
- `select_group()`: Helper for choosing a WhatsApp group  
- `select_days()`: Helper for choosing a time period  
- `confirm_action()`: Asks for confirmation before performing actions  
- `display_error_and_continue()`: Shows error messages to the user 
# Discord Bot Integration 
  
"The Discord Bot integration allows users to control the WhatsApp Bot directly from Discord. This provides remote management capabilities and expands the bot's accessibility." 
  
"## Discord Integration Menu"  
  
"```plaintext"  
"==============================="  
"WHATSAPP GROUP SUMMARY GENERATOR"  
"==============================="  
  
"Discord Integration:"  
"1. Configure Discord Bot"  
"2. Manage Discord Commands"  
"3. Set Discord Permissions"  
"4. View Discord Logs"  
"5. Test Discord Connection"  
"6. Back"  
  
"Enter your choice: "  
"```" 
  
"## Discord Commands"  
  
"The Discord bot supports the following commands to control the WhatsApp Bot:"  
  
"| Discord Command | Description |"  
"|----------------|-------------|"  
"| `/summary [group] [days]` | Generate a summary for the specified group and time period |"  
"| `/fetch` | Fetch new messages from all WhatsApp groups |"  
"| `/groups` | List all available WhatsApp groups |"  
"| `/status` | Check the current status of the WhatsApp Bot |"  
"| `/settings` | View or modify settings |"  
"| `/background start/stop` | Control background mode |" 
  
"## Discord Permission Levels"  
  
"```plaintext"  
"==============================="  
"WHATSAPP GROUP SUMMARY GENERATOR"  
"==============================="  
  
"Discord Permission Levels:"  
  
"1. Admin (Full access to all commands and settings)"  
"2. Operator (Can generate summaries and fetch messages)"  
"3. Viewer (Can only view status and groups)"  
  
"Configure Discord roles:"  
  
"- Admin Role: [Bot Admin]"  
"- Operator Role: [Bot Operator]"  
"- Viewer Role: [Bot Viewer]"  
  
"Enter role to configure or 'b' to go back: "  
"```" 
  
"## Discord-WhatsApp Integration Workflow"  
  
"The Discord-WhatsApp integration follows this workflow:"  
  
"1. **Setup**: Administrator configures the Discord bot with appropriate tokens and permissions"  
"2. **Connection**: The WhatsApp Bot establishes a connection with the Discord Bot"  
"3. **Command Processing**:"  
"   - Discord users send commands using slash commands"  
"   - The Discord Bot validates permissions and forwards commands to the WhatsApp Bot"  
"   - The WhatsApp Bot processes the command and returns results"  
"   - The Discord Bot formats and displays results in Discord"  
"4. **Notifications**: The WhatsApp Bot can send automatic notifications to Discord channels"  
  
"This integration makes it possible to manage your WhatsApp Bot remotely through Discord, expanding its accessibility and usability." 
