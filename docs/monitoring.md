# Monitoring  
  
## Overview  
  
Proper monitoring is essential for maintaining the health and performance of the WhatsApp Bot. This document outlines the monitoring strategy and implementation details.  
  
## Logging Strategy  
  
### Logging Configuration  
  
```python  
import logging  
import os  
from datetime import datetime  
  
def setup_logging():  
    """Set up application logging"""  
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()  
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")  
    os.makedirs(log_dir, exist_ok=True)  
  
    # Configure log file path with date  
    log_date = datetime.now().strftime("%Y-%m-%d")  
    log_file = os.path.join(log_dir, f"whatsapp-bot-{log_date}.log")  
  
    # Configure logging  
    logging.basicConfig(  
        level=getattr(logging, log_level),  
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  
        handlers=[  
            logging.FileHandler(log_file),  
            logging.StreamHandler()  
        ]  
    )  
  
    # Log startup information  
    logging.info("==== WhatsApp Bot Starting ====")  
    logging.info(f"Log level: {log_level}")  
    logging.info(f"Environment: {os.getenv('APP_ENV', 'development')}")  
    return log_file  
```  
  
### Log Categories  
  
Use different loggers for different components:  
  
```python  
# Create component-specific loggers  
db_logger = logging.getLogger("database")  
api_logger = logging.getLogger("api")  
webhook_logger = logging.getLogger("webhook")  
message_logger = logging.getLogger("messages")  
```  
  
## Performance Metrics  
  
Track key performance indicators:  
  
```python  
import time  
  
class MetricsCollector:  
    def __init__(self):  
        self.metrics = {  
            "api_calls": 0,  
            "api_errors": 0,  
            "messages_processed": 0,  
            "summaries_generated": 0,  
            "database_queries": 0,  
            "response_times": [],  
            "errors": {}  
        }  
  
    def record_api_call(self, success=True):  
        """Record an API call"""  
        self.metrics["api_calls"] += 1  
        if not success:  
            self.metrics["api_errors"] += 1  
  
    def record_message_processed(self):  
        """Record a message being processed"""  
        self.metrics["messages_processed"] += 1  
  
    def record_summary_generated(self):  
        """Record a summary being generated"""  
        self.metrics["summaries_generated"] += 1  
  
    def record_db_query(self):  
        """Record a database query"""  
        self.metrics["database_queries"] += 1  
  
    def record_response_time(self, duration):  
        """Record response time in seconds"""  
        self.metrics["response_times"].append(duration)  
  
    def record_error(self, error_type):  
        """Record an error by type"""  
        if error_type not in self.metrics["errors"]:  
            self.metrics["errors"][error_type] = 0  
        self.metrics["errors"][error_type] += 1  
  
    def get_metrics_report(self):  
        """Get a report of all metrics"""  
        avg_response_time = 0  
        if self.metrics["response_times"]:  
            avg_response_time = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])  
  
        return {  
            "api_calls": self.metrics["api_calls"],  
            "api_error_rate": self.metrics["api_errors"] / max(1, self.metrics["api_calls"]),  
            "messages_processed": self.metrics["messages_processed"],  
            "summaries_generated": self.metrics["summaries_generated"],  
            "database_queries": self.metrics["database_queries"],  
            "avg_response_time": avg_response_time,  
            "errors": self.metrics["errors"]  
        }  
  
# Create a global metrics collector  
metrics = MetricsCollector()  
``` 
