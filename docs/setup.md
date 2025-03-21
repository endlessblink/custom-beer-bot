# Setup Guide  
  
## Environment Setup  
  
This guide will help you set up the WhatsApp Bot environment.  
  
### Prerequisites  
  
- Python 3.9 or higher  
- Pinokio and Miniconda installed  
- Neon PostgreSQL database account  
- OpenAI API key  
- Green API account  
  
### Setup Steps  
  
#### 1. Create a Python Environment  
  
```bash  
# Create a new conda environment  
C:\pinokio\bin\miniconda\condabin\conda create -n whatsapp-bot python=3.9  
  
# Activate the environment  
C:\pinokio\bin\miniconda\condabin\conda activate whatsapp-bot  
```  
  
#### 2. Clone the Repository  
  
```bash  
# Clone the repository  
git clone https://github.com/your-username/whatsapp-bot.git  
cd whatsapp-bot  
```  
  
#### 3. Install Dependencies  
  
```bash  
# Install required packages  
pip install -r requirements.txt  
```  
  
#### 4. Configure Environment Variables  
  
Create a `.env` file in the project root with the following content:  
  
```text  
# API Keys  
OPENAI_API_KEY=your_openai_api_key  
GREEN_API_INSTANCE_ID=your_green_api_instance_id  
GREEN_API_TOKEN=your_green_api_token  
  
# Database  
NEON_DB_URL=postgresql://username:password@host:port/database  
  
# Application Settings  
APP_ENV=development  # Can be development, test, or production  
LOG_LEVEL=INFO  
WEBHOOK_URL=https://a48f-46-210-13-196.ngrok-free.app/webhook/whatsapp-webhook  
```  
  
#### 5. Set Up the Database  
  
Run the database initialization script:  
  
```bash  
python scripts/init_database.py  
```  
  
#### 6. Start the Webhook Server  
  
```bash  
# Start ngrok to expose the webhook  
ngrok http 5000  
  
# In another terminal, start the webhook server  
python webhook_server.py  
```  
  
#### 7. Configure Green API  
  
1. Log in to your Green API account  
2. Set up a webhook notification with the URL from ngrok  
3. Enable notifications for incoming messages  
  
## Running the Bot  
  
To run the bot manually:  
  
```bash  
# Activate the environment if not already activated  
C:\pinokio\bin\miniconda\condabin\conda activate whatsapp-bot  
  
# Run the main script  
python run_menu.py  
```  
  
## Troubleshooting  
  
### Common Issues  
  
#### OpenAI API Key Issues  
  
If you encounter errors related to the OpenAI API key:  
  
1. Verify the API key is correct and has not expired  
2. Check that the API key has sufficient quota and permissions  
3. Ensure the API key is correctly formatted in the .env file  
  
#### Database Connection Issues  
  
If you have trouble connecting to the database:  
  
1. Verify your database credentials and connection string  
2. Check that the Neon database is online and accessible  
3. Ensure your IP is allowed in the database firewall settings  
  
#### Webhook Connection Issues  
  
If webhooks are not being received:  
  
1. Check that ngrok is running and the URL is correctly configured in Green API  
2. Verify that the webhook server is running and listening on the correct port  
3. Check the logs for any webhook-related errors 
