# Database Design  
  
## Overview  
  
This project uses Neon PostgreSQL as the primary database for storing WhatsApp messages, summaries, and application data.  
The database schema is designed to optimize for both read and write operations with proper indexing.  
  
## Schema  
  
### Messages Table  
  
```sql  
CREATE TABLE IF NOT EXISTS messages (  
    id SERIAL PRIMARY KEY,  
    message_id TEXT NOT NULL UNIQUE,  
    group_id TEXT NOT NULL,  
    sender_id TEXT NOT NULL,  
    sender_name TEXT NOT NULL,  
    message_text TEXT NOT NULL,  
    content TEXT,  
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,  
    message_type TEXT NOT NULL DEFAULT 'text',  
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),  
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()  
);  
  
-- Indexes  
CREATE INDEX IF NOT EXISTS idx_messages_group_id ON messages(group_id);  
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);  
CREATE UNIQUE INDEX IF NOT EXISTS idx_messages_message_id ON messages(message_id);  
```  
  
### Summaries Table  
  
```sql  
CREATE TABLE IF NOT EXISTS summaries (  
    id SERIAL PRIMARY KEY,  
    group_id TEXT NOT NULL,  
    content TEXT NOT NULL,  
    message_count INTEGER NOT NULL,  
    date TIMESTAMP WITH TIME ZONE,  
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL,  
    participants JSONB,  
    status TEXT DEFAULT 'completed',  
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()  
);  
  
-- Indexes  
CREATE INDEX IF NOT EXISTS idx_summaries_group_id ON summaries(group_id);  
CREATE INDEX IF NOT EXISTS idx_summaries_created_at ON summaries(created_at);  
```  
  
### Message Logs Table  
  
```sql  
CREATE TABLE IF NOT EXISTS message_logs (  
    id SERIAL PRIMARY KEY,  
    data JSONB,  
    error_type TEXT,  
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()  
);  
``` 
  
## Connection Management  
  
### Connection Pooling  
  
The application uses connection pooling to efficiently manage database connections:  
  
```python  
# Example of connection pool implementation  
self.connection_pool = pool.ThreadedConnectionPool(  
    min_connections=1,  
    max_connections=10,  
    dsn=connection_string,  
    cursor_factory=RealDictCursor  
)  
```  
  
### Connection Handling  
  
- Acquire connections from the pool when needed  
- Always release connections back to the pool after use  
- Use context managers to ensure connections are properly released  
  
```python  
def _get_connection(self):  
    """Get a connection from the pool"""  
    return self.connection_pool.getconn()  
  
def _release_connection(self, conn):  
    """Release the connection back to the pool"""  
    self.connection_pool.putconn(conn)  
```  
  
## Best Practices  
  
1. **Use Parameterized Queries**: Always use parameterized queries to prevent SQL injection  
2. **Handle Unique Constraints**: Implement proper handling for unique constraint violations  
3. **Transactional Operations**: Use transactions for multi-step operations  
4. **Error Logging**: Log database errors with detailed context  
5. **Regular Maintenance**: Implement vacuum and analyze operations  
6. **Batch Operations**: Use batch operations for inserting multiple records  
7. **Connection Timeout**: Set appropriate connection timeout values  
8. **Retry Logic**: Implement retry logic for transient failures  
9. **Monitoring**: Monitor connection counts and query performance  
10. **Backup Strategy**: Regular automated backups with restore testing 
