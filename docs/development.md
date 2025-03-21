# Development Guide  
  
## Project Structure  
  
```plaintext  
project_root/  
ÃÄÄ config/              # Configuration files  
ÃÄÄ database/           # Database layer  
ÃÄÄ docs/               # Documentation  
ÃÄÄ llm/                # LLM integration  
ÃÄÄ api/                # API integration  
ÃÄÄ services/           # Business logic  
ÃÄÄ utils/              # Utility functions  
ÃÄÄ tests/              # Test suite  
ÃÄÄ .env                # Environment variables  
ÀÄÄ main.py             # Entry point  
``` 
  
## Development Environment Setup  
  
### Prerequisites  
  
- Python 3.9 or higher  
- Git  
- PostgreSQL (local or Neon account)  
- OpenAI API key  
- Green API account  
  
### Setting Up the Environment  
  
```bash  
# Clone the repository  
git clone https://github.com/yourusername/whatsapp-bot.git  
cd whatsapp-bot  
  
# Using Miniconda (as specified in setup.md)  
C:\pinokio\bin\miniconda\condabin\conda create -n whatsapp-bot python=3.9  
C:\pinokio\bin\miniconda\condabin\conda activate whatsapp-bot  
  
# Install dependencies  
pip install -r requirements.txt  
``` 
  
## Development Workflow  
  
1. **Create a branch**: For each new feature or bugfix, create a new branch.  
2. **Run the local development server**: Use python main.py --dev for development mode.  
3. **Set up webhook forwarding**: For testing webhooks locally, use ngrok.  
4. **Run tests**: Always run tests before submitting a pull request.  
  
## Coding Standards  
  
- Follow PEP 8 style guide for Python code.  
- Use 4 spaces for indentation (no tabs).  
- Add docstrings to all functions, classes, and modules.  
- Write unit tests for all new code.  
- Handle errors gracefully (refer to error_handling.md).  
- Log important events and errors (refer to monitoring.md). 
