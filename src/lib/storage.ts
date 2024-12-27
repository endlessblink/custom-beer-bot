import { GroupMessage } from './messageCollector';

export class MessageStorage {
  private static instance: MessageStorage;
  private cache: Map<string, GroupMessage[]> = new Map();
  
  private constructor() {}

  public static getInstance(): MessageStorage {
    if (!MessageStorage.instance) {
      MessageStorage.instance = new MessageStorage();
    }
    return MessageStorage.instance;
  }

  public async saveMessages(groupId: string, messages: GroupMessage[]) {
    try {
      const response = await fetch('/api/messages/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          groupId,
          messages
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save messages');
      }

      // Update cache
      this.cache.set(groupId, messages);
      console.log(`Saved ${messages.length} messages for group ${groupId}`);
    } catch (error) {
      console.error(`Failed to save messages for group ${groupId}:`, error);
    }
  }

  public async loadMessages(groupId: string): Promise<GroupMessage[]> {
    try {
      // Check cache first
      if (this.cache.has(groupId)) {
        return this.cache.get(groupId)!;
      }

      const response = await fetch(`/api/messages/load?groupId=${encodeURIComponent(groupId)}`);
      
      if (!response.ok) {
        throw new Error('Failed to load messages');
      }

      const data = await response.json();
      const messages = data.messages as GroupMessage[];
      
      // Convert string dates back to Date objects
      messages.forEach(msg => {
        msg.timestamp = new Date(msg.timestamp);
      });

      // Update cache
      this.cache.set(groupId, messages);
      console.log(`Loaded ${messages.length} messages for group ${groupId}`);
      return messages;
    } catch (error) {
      console.error(`Failed to load messages for group ${groupId}:`, error);
      return [];
    }
  }

  public async clearMessages(groupId: string) {
    try {
      const response = await fetch('/api/messages/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ groupId })
      });

      if (!response.ok) {
        throw new Error('Failed to clear messages');
      }

      // Clear cache
      this.cache.delete(groupId);
      console.log(`Cleared messages for group ${groupId}`);
    } catch (error) {
      console.error(`Failed to clear messages for group ${groupId}:`, error);
    }
  }
}

// Create and export default instance
export const storage = MessageStorage.getInstance(); 