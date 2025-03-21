# Webhook Configuration  
  
## Overview  
  
Webhooks allow your application to receive real-time notifications when new messages arrive in WhatsApp.  
This eliminates the need for constant polling and ensures immediate message processing.  
  
## Current Webhook URL  
  
The current webhook URL configured for this project is:  
  
```   
@https://a48f-46-210-13-196.ngrok-free.app/webhook/whatsapp-webhook  
``` 
  
## Important Notes about ngrok URLs  
  
- This is an ngrok URL which provides a public endpoint that forwards to your local server  
- The URL will change each time you restart ngrok unless you have a paid account with a fixed subdomain  
- When the URL changes, you must update it in the Green API settings  
  
## Setting Up the Webhook in Green API  
  
1. Log in to your Green API account  
2. Navigate to the instance settings  
3. In the "Webhook" section, enter the current webhook URL  
4. Click "Save" to apply the changes  
5. Use the "Test" button to verify the webhook is working correctly 
  
## Running ngrok  
  
To start ngrok and create a new public URL:  
  
```bash  
# Install ngrok if you haven't already  
npm install -g ngrok  # or use your preferred installation method  
  
# Start ngrok on the port your application is running on (example: 3000)  
ngrok http 3000  
```  
  
After starting ngrok, note the new URL and update it in the Green API settings.  
  
## Webhook Endpoint Implementation  
  
The webhook endpoint in your application should be implemented to:  
  
1. Validate incoming requests from Green API  
2. Process the message data  
3. Store messages in the database  
4. Return a `200 OK` response to acknowledge receipt  
  
See the `app.py` or relevant route handler file for implementation details. 
