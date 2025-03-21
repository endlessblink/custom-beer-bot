# Architecture  
  
## Overview  
  
The WhatsApp Bot is built using a modular, layered architecture to ensure separation of concerns and maintainability.  
  
## Core Components  
  
### 1. Data Layer  
  
- **Neon Database Client**: Handles all database operations with connection pooling  
- **Data Models**: Defines schema and relationships  
- **Data Access Objects**: Abstracts database operations  
  
### 2. API Integration Layer  
  
- **Green API Client**: Manages WhatsApp communication  
- **OpenAI Client**: Handles AI processing and summaries  
- **API Error Handling**: Centralized error management  
  
### 3. Business Logic Layer  
  
- **Message Processor**: Processes incoming messages  
- **Summary Generator**: Creates conversation summaries  
- **Group Manager**: Manages WhatsApp groups  
  
### 4. Presentation Layer  
  
- **Console UI**: Text-based user interface  
- **Progress Indicators**: Visual feedback for long operations  
- **Menu System**: User interaction management  
  
## Dependency Flow  
  
```   
ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿     ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿     ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿  
³  Presentation   ³ÄÄÄÄ?³  Business Logic ³ÄÄÄÄ?³  API Integration³  
ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÙ     ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÙ     ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÙ  
        ³                       ³                      ³  
        ³                       ³                      ³  
        ³                                             ³  
        ³             ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿            ³  
        ÀÄÄÄÄÄÄÄÄÄÄÄÄ?³    Data Layer   ³?ÄÄÄÄÄÄÄÄÄÄÄÙ  
                      ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÙ  
```  
  
## Key Design Principles  
  
1. **Single Responsibility**: Each class/module has one clear purpose  
2. **Dependency Injection**: Components receive dependencies rather than creating them  
3. **Error Isolation**: Errors in one component don't crash the entire system  
4. **Configuration Externalization**: All configuration in environment variables or config files  
5. **Interface Segregation**: Clients only depend on methods they actually use 
