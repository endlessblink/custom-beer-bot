# Deployment Guide  
  
## Overview 
  
This document outlines the process for deploying the WhatsApp Bot to production environments. The deployment process focuses on reliability, security, and ease of maintenance. 
  
## Prerequisites  
  
- Python 3.9+ installed on the target server  
- PostgreSQL Neon database account and connection details  
- Green API account with API key  
- OpenAI API key with appropriate rate limits  
- Git access to the repository 
  
## Deployment Process  
  
### 1. Environment Setup  
  
```bash  
# Clone the repository  
git clone https://github.com/yourusername/whatsapp-bot.git  
cd whatsapp-bot  
  
# Create and activate virtual environment  
python -m venv venv  
source venv/bin/activate  # On Windows: venv\Scripts\activate  
  
# Install dependencies  
pip install -r requirements.txt  
``` 
  
### 2. Configuration  
  
Create a `.env` file in the root directory with the following environment variables:  
  
```plaintext  
# Database  
DB_HOST=your-neon-db-host.example.com  
DB_NAME=whatsapp_bot  
DB_USER=your_username  
DB_PASSWORD=your_secure_password  
DB_PORT=5432  
  
# Green API  
GREEN_API_TOKEN=your_green_api_token  
GREEN_API_INSTANCE=123456  
  
# OpenAI  
OPENAI_API_KEY=your_openai_api_key  
  
# Webhook  
WEBHOOK_URL=https://your-domain.com/webhook/whatsapp-webhook  
``` 
  
### 3. Database Setup  
  
Run the migration scripts to set up the database:  
  
```bash  
python scripts/db_migrate.py  
```  
  
### 4. Starting the Service  
  
For production, it's recommended to use a process manager like Supervisor:  
  
```bash  
# Install Supervisor  
sudo apt-get install supervisor  
```  
  
Refer to the [monitoring.md](monitoring.md) documentation for setting up proper monitoring. 
