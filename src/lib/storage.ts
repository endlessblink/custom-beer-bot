import { GroupMessage } from './messageCollector';
import { GroupConfig } from './config';

export class Storage {
  private static instance: Storage;
  private messageCache: Map<string, GroupMessage[]> = new Map();
  private groupCache: GroupConfig[] | null = null;
  
  private constructor() {}

  public static getInstance(): Storage {
    if (!Storage.instance) {
      Storage.instance = new Storage();
    }
    return Storage.instance;
  }

  // Group management
  public getGroups(): GroupConfig[] {
    if (this.groupCache !== null) {
      return this.groupCache;
    }

    try {
      const storedGroups = localStorage.getItem('whatsapp-groups');
      if (storedGroups) {
        this.groupCache = JSON.parse(storedGroups);
        return this.groupCache;
      }
    } catch (error) {
      console.error('Failed to load groups from storage:', error);
    }

    return [];
  }

  public saveGroups(groups: GroupConfig[]): void {
    try {
      localStorage.setItem('whatsapp-groups', JSON.stringify(groups));
      this.groupCache = groups;
    } catch (error) {
      console.error('Failed to save groups to storage:', error);
    }
  }

  // Message management
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
      this.messageCache.set(groupId, messages);
      console.log(`Saved ${messages.length} messages for group ${groupId}`);
    } catch (error) {
      console.error(`Failed to save messages for group ${groupId}:`, error);
    }
  }

  public async loadMessages(groupId: string): Promise<GroupMessage[]> {
    try {
      // Check cache first
      if (this.messageCache.has(groupId)) {
        return this.messageCache.get(groupId)!;
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
      this.messageCache.set(groupId, messages);
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
      this.messageCache.delete(groupId);
      console.log(`Cleared messages for group ${groupId}`);
    } catch (error) {
      console.error(`Failed to clear messages for group ${groupId}:`, error);
    }
  }
}

// Create and export default instance
export const storage = Storage.getInstance(); 