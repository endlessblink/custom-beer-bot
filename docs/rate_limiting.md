# Rate Limiting  
  
## Overview  
  
Rate limiting is crucial for maintaining stable performance and preventing API quota exhaustion. This document outlines the rate limiting strategies implemented in the WhatsApp Bot.  
  
## API Rate Limiting  
  
### OpenAI API  
  
The OpenAI API has specific rate limits. Our implementation includes mechanisms to respect these limits:  
  
```python  
import time  
import logging  
  
class RateLimiter:  
    def __init__(self, max_calls, time_period):  
        """Initialize rate limiter >> rate_limiting.md && echo. >> rate_limiting.md && echo         Args: >> rate_limiting.md && echo             max_calls (int): Maximum number of calls allowed >> rate_limiting.md && echo             time_period (float): Time period in seconds >> rate_limiting.md && echo         """  
        self.max_calls = max_calls  
        self.time_period = time_period  
        self.calls = []  
  
    def _cleanup_old_calls(self):  
        """Remove calls older than the time period"""  
        current_time = time.time()  
        cutoff_time = current_time - self.time_period  
        self.calls = [call_time for call_time in self.calls if call_time  
  
    def can_make_call(self):  
        """Check if a new call can be made under the rate limit"""  
        self._cleanup_old_calls()  
