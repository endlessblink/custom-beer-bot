# Webhook Setup  
  
## Overview  
  
This document provides instructions for setting up and configuring webhooks for the WhatsApp Bot. Webhooks are essential for receiving real-time notifications from Green API when messages are received.  
  
## Requirements  
  
- Ngrok account (for development)  
- Green API account  
- Flask webhook server (included in the project)  
  
## Setup Steps  
  
### 1. Start the Webhook Server  
  
The webhook server is part of the main application. It runs on port 5000 by default.  
  
```bash  
python main.py  
```  
  
### 2. Expose Webhook with Ngrok  
  
For development, you'll need to expose your local webhook server to the internet using Ngrok:  
  
```bash  
ngrok http 5000  
```  
  
This will generate a public URL like `https://a48f-46-210-13-196.ngrok-free.app`. Note this URL as you'll need it for the next step.  
  
### 3. Configure Green API Webhook  
  
1. Log in to your Green API account  
2. Navigate to your instance settings  
3. Find the webhook configuration section  
4. Enter your Ngrok URL followed by the webhook path:  
   `https://a48f-46-210-13-196.ngrok-free.app/webhook/whatsapp-webhook`  
5. Save the settings  
  
### 4. Update .env File  
  
Update your .env file with the webhook URL:  
  
```plaintext  
WEBHOOK_URL=https://a48f-46-210-13-196.ngrok-free.app/webhook/whatsapp-webhook  
```  
  
## Webhook Server Implementation  
  
The webhook server is implemented in `webhook_server.py`. The core implementation looks like this:  
  
```python  
from flask import Flask, request, jsonify  
from services.message_processor import MessageProcessor  
import logging  
  
app = Flask(__name__)  
message_processor = MessageProcessor()  
  
@app.route('/webhook/whatsapp-webhook', methods=['POST'])  
def whatsapp_webhook():  
    try:  
        # Get the incoming webhook data  
        webhook_data = request.json  
        logging.info(f"Received webhook: {webhook_data}")  
  
        # Process the incoming message  
        message_processor.process_webhook(webhook_data)  
  
        # Return success response  
        return jsonify({"status": "success"}), 200  
    except Exception as e:  
        logging.error(f"Error processing webhook: {str(e)}")  
        return jsonify({"status": "error", "message": str(e)}), 500  
  
def start_webhook_server():  
    app.run(host='0.0.0.0', port=5000)  
```  
  
## Webhook Security Considerations  
  
1. **Authentication**: In production, implement webhook authentication to ensure requests are coming from Green API.  
  
2. **HTTPS**: Always use HTTPS for webhook endpoints in production.  
  
3. **Input Validation**: Validate incoming webhook data before processing.  
  
4. **Rate Limiting**: Implement rate limiting to prevent abuse.  
  
## Troubleshooting  
  
### Not Receiving Notifications  
  
If you're not receiving notifications:  
  
1. Check that your webhook server is running  
2. Verify that Ngrok is running and the URL is correct  
3. Confirm the webhook URL is correctly configured in Green API  
4. Check the logs for any errors  
  
### Ngrok Session Expired  
  
Ngrok free sessions expire after a few hours. If your webhook stops working:  
  
1. Restart Ngrok to get a new URL  
2. Update the webhook URL in Green API  
3. Update the WEBHOOK_URL in your .env file  
  
## Production Deployment  
  
For production, you should:  
  
1. Set up a proper domain name instead of using Ngrok  
2. Configure HTTPS with a valid SSL certificate  
3. Set up a reverse proxy (like Nginx) to handle incoming webhook requests  
4. Implement proper authentication and security measures  
  
Refer to the [deployment.md](deployment.md) guide for more details on production deployment. 
