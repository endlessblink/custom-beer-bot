# Environment Configuration  
  
## Overview  
  
The WhatsApp Bot supports multiple environments (development, test, production) through environment-specific configuration. This document outlines the environment setup and management.  
  
## Environment Variables  
  
The application uses environment variables for configuration. Create a `.env` file in the project root for local development:  
  
```text  
# Application environment (development, test, production)  
APP_ENV=development  
  
# API Keys  
OPENAI_API_KEY=your_openai_api_key  
GREEN_API_INSTANCE_ID=your_instance_id  
GREEN_API_TOKEN=your_token  
  
# Database  
NEON_DB_URL=postgresql://username:password@host:port/database  
TEST_DB_URL=postgresql://username:password@host:port/test_database  
  
# Logging  
LOG_LEVEL=INFO  
  
# Webhook  
WEBHOOK_URL=https://a48f-46-210-13-196.ngrok-free.app/webhook/whatsapp-webhook  
```  
  
## Loading Environment Variables  
  
Use the `python-dotenv` package to load environment variables:  
  
```python  
import os  
from dotenv import load_dotenv  
  
# Load environment variables from .env file  
load_dotenv()  
  
# Get current environment  
app_env = os.getenv("APP_ENV", "development")  
```  
  
## Environment-Specific Configuration  
  
Implement environment-specific settings with a configuration manager:  
  
```python  
# config.py  
import os  
from dotenv import load_dotenv  
  
# Load .env file if it exists  
load_dotenv()  
  
class Config:  
    """Base configuration class"""  
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  
    GREEN_API_INSTANCE_ID = os.getenv("GREEN_API_INSTANCE_ID")  
    GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")  
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")  
  
  
class DevelopmentConfig(Config):  
    """Development environment configuration"""  
    DEBUG = True  
    DATABASE_URL = os.getenv("NEON_DB_URL")  
    CACHE_ENABLED = False  
    LOG_TO_FILE = False  
  
  
class TestConfig(Config):  
    """Test environment configuration"""  
    DEBUG = True  
    DATABASE_URL = os.getenv("TEST_DB_URL")  
    CACHE_ENABLED = False  
    LOG_TO_FILE = False  
    # Use lower rate limits for testing  
    RATE_LIMIT_MAX_CALLS = 5  
    RATE_LIMIT_PERIOD = 60  
  
  
class ProductionConfig(Config):  
    """Production environment configuration"""  
    DEBUG = False  
    DATABASE_URL = os.getenv("NEON_DB_URL")  
    CACHE_ENABLED = True  
    LOG_TO_FILE = True  
    # Higher rate limits for production  
    RATE_LIMIT_MAX_CALLS = 20  
    RATE_LIMIT_PERIOD = 60  
  
  
def get_config():  
    """Get the appropriate configuration based on environment"""  
    env = os.getenv("APP_ENV", "development").lower()  
  
    if env == "production":  
        return ProductionConfig()  
    elif env == "test":  
        return TestConfig()  
    else:  # development is default  
        return DevelopmentConfig()  
  
  
# Create a global config object  
config = get_config()  
```  
  
## Usage Example  
  
```python  
# Import the config object  
from config import config  
  
# Use configuration settings  
def setup_logging():  
    """Set up logging based on environment"""  
    log_level = config.LOG_LEVEL  
    log_to_file = config.LOG_TO_FILE  
  
    # Configure logging based on environment settings  
    if log_to_file:  
        # Production logging to file  
        setup_file_logging(log_level)  
    else:  
        # Development/test logging to console  
        setup_console_logging(log_level)  
``` 
