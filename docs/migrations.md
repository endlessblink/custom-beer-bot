# Database Migrations  
  
## Overview  
  
This guide outlines the process for managing database migrations in the WhatsApp Bot project. Migrations are a controlled way to make changes to the database schema over time. 
  
## Migration Structure  
  
Each migration file should contain:  
  
1. A comment explaining the purpose of the migration  
2. The SQL statements for applying the changes  
3. The SQL statements for rolling back the changes (if possible)  
  
Example migration file:  
  
```sql  
-- Migration: Create messages table  
-- Description: Creates the initial messages table for storing WhatsApp messages  
  
-- Up Migration  
CREATE TABLE IF NOT EXISTS messages (  
    id SERIAL PRIMARY KEY,  
    chat_id VARCHAR(255) NOT NULL,  
    message_id VARCHAR(255) NOT NULL,  
    sender VARCHAR(255) NOT NULL,  
    content TEXT NOT NULL,  
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),  
    processed BOOLEAN NOT NULL DEFAULT FALSE  
);  
  
-- Down Migration  
DROP TABLE IF EXISTS messages;  
``` 
  
## Best Practices  
  
1. **Keep migrations small and focused**: Each migration should do one logical change to the schema.  
  
2. **Test migrations thoroughly**: Before applying to production, test migrations in a development environment.  
  
3. **Make migrations reversible**: When possible, provide a way to roll back changes.  
  
4. **Version control**: Always commit migration files to version control.  
  
5. **Document complex migrations**: For complex changes, add detailed comments explaining the purpose and impacts.  
  
6. **Backup before migrating**: Always backup the database before applying migrations in production. 
