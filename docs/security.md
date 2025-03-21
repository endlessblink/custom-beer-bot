# Security Best Practices  
  
## Overview  
  
Security is a critical aspect of the WhatsApp Bot implementation. This document outlines security best practices and implementation details to protect data and prevent unauthorized access.  
  
## API Key Management  
  
Proper API key management is essential for security:  
  
```python  
import os  
from dotenv import load_dotenv  
  
# Load environment variables from .env file  
load_dotenv()  
  
def get_api_key(key_name):  
    """Securely retrieve API key from environment variables"""  
    api_key = os.getenv(key_name)  
    if not api_key:  
        logging.error(f"Missing API key: {key_name}")  
        raise ValueError(f"Required API key '{key_name}' is not set in environment")  
  
    # Basic validation of API key  
    if key_name == "OPENAI_API_KEY" and not api_key.startswith("sk-"):  
        logging.warning(f"Invalid {key_name} format")  
        raise ValueError(f"{key_name} appears to be invalid")  
  
    return api_key  
```  
  
## Environment Variable Management  
  
1. **Use .env files for local development**  
2. **Never commit .env files to version control**  
3. **Use environment-specific settings for different environments (dev, test, prod)**  
4. **Keep a .env.example file with dummy values in version control**  
  
Example .env.example file:  
  
```text  
# API Keys  
OPENAI_API_KEY=sk-your-openai-key-here  
GREEN_API_INSTANCE_ID=your-instance-id  
GREEN_API_TOKEN=your-token  
  
# Database  
NEON_DB_URL=postgresql://user:password@host:port/database  
  
# Application Settings  
LOG_LEVEL=INFO  
WEBHOOK_URL=https://your-webhook-url.com/webhook  
```  
  
## Input Validation  
  
Always validate user input and API responses:  
  
```python  
def validate_message(message):  
    """Validate incoming message structure"""  
    required_fields = ['id', 'body', 'chatId', 'timestamp']  
  
    # Check all required fields exist  
    for field in required_fields:  
        if field not in message:  
            logging.warning(f"Invalid message: missing {field}")  
            return False  
  
    # Validate field types  
    if not isinstance(message['id'], str) or not message['id']:  
        logging.warning("Invalid message ID")  
        return False  
  
    if not isinstance(message['chatId'], str) or not message['chatId']:  
        logging.warning("Invalid chat ID")  
        return False  
  
    return True  
```  
  
## Database Security  
  
Protect your database with these practices:  
  
1. **Use Parameterized Queries** to prevent SQL injection:  
  
```python  
# BAD - Vulnerable to SQL injection  
def unsafe_query(user_id):  
    query = f"SELECT * FROM users WHERE id = '{user_id}'"  
    return execute_query(query)  
  
# GOOD - Using parameterized query  
def safe_query(user_id):  
    query = "SELECT * FROM users WHERE id = %s"  
    return execute_query(query, (user_id,))  
```  
  
2. **Limit Database Privileges** - Use a database user with minimal required permissions  
  
3. **Encrypt Sensitive Data** - Hash passwords and encrypt sensitive information:  
  
```python  
import hashlib  
import os  
  
def hash_password(password):  
    """Securely hash a password"""  
    # Generate a random salt  
    salt = os.urandom(32)  
    # Hash password with salt  
    hash = hashlib.pbkdf2_hmac(  
        'sha256',  # Hash algorithm  
        password.encode('utf-8'),  # Convert password to bytes  
        salt,  # Salt  
        100000  # Number of iterations  
    )  
    return salt + hash  # Store salt with hash  
``` 
