import { MessageStorage } from './storage';

export interface GroupMessage {
  timestamp: Date;
  sender: string;
  content: string;
  type: 'text' | 'media' | 'system';
  senderName?: string;
}

export class MessageCollector {
  private static instance: MessageCollector;
  private messages: Map<string, GroupMessage[]>;
  private readonly MAX_MESSAGES_PER_GROUP = 1000;
  private storage: MessageStorage;
  
  private constructor() {
    this.messages = new Map();
    this.storage = MessageStorage.getInstance();
  }

  public static getInstance(): MessageCollector {
    if (!MessageCollector.instance) {
      MessageCollector.instance = new MessageCollector();
    }
    return MessageCollector.instance;
  }

  public collectMessage(groupId: string, message: GroupMessage) {
    // Initialize array if it doesn't exist
    if (!this.messages.has(groupId)) {
      this.messages.set(groupId, []);
    }

    const groupMessages = this.messages.get(groupId)!;
    groupMessages.push(message);

    // Keep only the last MAX_MESSAGES_PER_GROUP messages
    if (groupMessages.length > this.MAX_MESSAGES_PER_GROUP) {
      groupMessages.shift(); // Remove oldest message
    }

    // Save to storage
    this.storage.saveMessages(groupId, groupMessages);

    console.log(`Collected message for group ${groupId}, total messages: ${groupMessages.length}`);
  }

  public getMessages(groupId: string, since?: Date): GroupMessage[] {
    const messages = this.messages.get(groupId) || [];
    
    if (since) {
      return messages.filter(msg => msg.timestamp >= since);
    }
    
    return messages;
  }

  public clearMessages(groupId: string) {
    this.messages.set(groupId, []);
    this.storage.clearMessages(groupId);
    console.log(`Cleared messages for group ${groupId}`);
  }

  public getDailySummaryMessages(groupId: string): GroupMessage[] {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    return this.getMessages(groupId, today);
  }

  public getMessageStats(groupId: string, since?: Date): {
    totalMessages: number;
    messagesByType: Record<string, number>;
    activeParticipants: Set<string>;
  } {
    const messages = since ? this.getMessages(groupId, since) : this.getMessages(groupId);
    
    const stats = {
      totalMessages: messages.length,
      messagesByType: {} as Record<string, number>,
      activeParticipants: new Set<string>()
    };

    messages.forEach(msg => {
      // Count by type
      stats.messagesByType[msg.type] = (stats.messagesByType[msg.type] || 0) + 1;
      
      // Track unique participants
      if (msg.sender) {
        stats.activeParticipants.add(msg.sender);
      }
    });

    return stats;
  }

  public getLastMessages(groupId: string, count: number = 10): GroupMessage[] {
    const messages = this.messages.get(groupId) || [];
    return messages.slice(-count); // Get last 'count' messages
  }
} 