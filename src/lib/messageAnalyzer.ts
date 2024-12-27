import { GroupMessage } from './messageCollector';
import { LLMService } from './llm';

interface MessageAnalysis {
  topActiveHours: { hour: number; count: number }[];
  topParticipants: { sender: string; messageCount: number }[];
  messageTypes: Record<string, number>;
  keywordFrequency: Record<string, number>;
  activityTrend: 'increasing' | 'decreasing' | 'stable';
  importantMessages: GroupMessage[];
  llmInsights?: string;
}

export class MessageAnalyzer {
  private static readonly IMPORTANT_KEYWORDS = [
    'חשוב', 'דחוף', 'תשומת לב', 'בבקשה', 'עזרה',
    'דדליין', 'פגישה', 'עדכון', 'חדשות', 'הודעה'
  ];

  private static readonly MESSAGE_TYPE_TRANSLATIONS: Record<string, string> = {
    'text': 'טקסט',
    'media': 'מדיה',
    'system': 'מערכת'
  };

  private static readonly TREND_TRANSLATIONS: Record<string, string> = {
    'increasing': 'במגמת עלייה',
    'decreasing': 'במגמת ירידה',
    'stable': 'יציבה'
  };

  public static async analyzeMessages(messages: GroupMessage[]): Promise<MessageAnalysis> {
    // Get LLM insights
    const llmService = LLMService.getInstance();
    const llmInsights = await llmService.generateMessageInsights(messages);

    return {
      topActiveHours: this.getTopActiveHours(messages),
      topParticipants: this.getTopParticipants(messages),
      messageTypes: this.getMessageTypes(messages),
      keywordFrequency: this.getKeywordFrequency(messages),
      activityTrend: this.getActivityTrend(messages),
      importantMessages: this.findImportantMessages(messages),
      llmInsights
    };
  }

  private static getTopActiveHours(messages: GroupMessage[]): { hour: number; count: number }[] {
    const hourCounts = new Map<number, number>();
    
    messages.forEach(msg => {
      const hour = msg.timestamp.getHours();
      hourCounts.set(hour, (hourCounts.get(hour) || 0) + 1);
    });

    return Array.from(hourCounts.entries())
      .map(([hour, count]) => ({ hour, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 3);
  }

  private static getTopParticipants(messages: GroupMessage[]): { sender: string; messageCount: number }[] {
    const participantCounts = new Map<string, number>();
    
    messages.forEach(msg => {
      const sender = msg.senderName || msg.sender;
      participantCounts.set(sender, (participantCounts.get(sender) || 0) + 1);
    });

    return Array.from(participantCounts.entries())
      .map(([sender, messageCount]) => ({ sender, messageCount }))
      .sort((a, b) => b.messageCount - a.messageCount)
      .slice(0, 5);
  }

  private static getMessageTypes(messages: GroupMessage[]): Record<string, number> {
    const typeCounts: Record<string, number> = {};
    
    messages.forEach(msg => {
      typeCounts[msg.type] = (typeCounts[msg.type] || 0) + 1;
    });

    return typeCounts;
  }

  private static getKeywordFrequency(messages: GroupMessage[]): Record<string, number> {
    const keywordCounts: Record<string, number> = {};
    
    messages.forEach(msg => {
      if (msg.type !== 'text') return;
      
      // Split by whitespace and punctuation
      const words = msg.content.split(/[\s,.!?()[\]{}'"\/\\;:-]+/);
      words.forEach(word => {
        // Keep English technical terms as is, translate others to lowercase
        const processedWord = /[a-zA-Z]/.test(word) ? 
          word : 
          word.toLowerCase();
          
        if (word.length > 2) { // Include shorter Hebrew words
          keywordCounts[processedWord] = (keywordCounts[processedWord] || 0) + 1;
        }
      });
    });

    // Sort and keep top 10 keywords
    return Object.fromEntries(
      Object.entries(keywordCounts)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10)
    );
  }

  private static getActivityTrend(messages: GroupMessage[]): 'increasing' | 'decreasing' | 'stable' {
    if (messages.length < 2) return 'stable';

    // Split messages into two halves and compare
    const midPoint = Math.floor(messages.length / 2);
    const firstHalf = messages.slice(0, midPoint);
    const secondHalf = messages.slice(midPoint);

    const firstHalfRate = firstHalf.length / (
      (firstHalf[firstHalf.length - 1].timestamp.getTime() - firstHalf[0].timestamp.getTime()) / 3600000
    );
    const secondHalfRate = secondHalf.length / (
      (secondHalf[secondHalf.length - 1].timestamp.getTime() - secondHalf[0].timestamp.getTime()) / 3600000
    );

    const difference = secondHalfRate - firstHalfRate;
    if (difference > 0.1) return 'increasing';
    if (difference < -0.1) return 'decreasing';
    return 'stable';
  }

  private static findImportantMessages(messages: GroupMessage[]): GroupMessage[] {
    return messages.filter(msg => {
      if (msg.type !== 'text') return false;
      
      const content = msg.content.toLowerCase();
      return this.IMPORTANT_KEYWORDS.some(keyword => content.includes(keyword));
    }).slice(-5); // Keep last 5 important messages
  }

  public static formatAnalysis(analysis: MessageAnalysis): string {
    // Filter only truly important messages
    const importantMessages = analysis.importantMessages
      .filter(msg => {
        const content = msg.content;
        return content.includes('פגישה') || 
               content.includes('דחוף') ||
               content.includes('חשוב') ||
               content.includes('דדליין');
      })
      .map(msg => `• ${msg.senderName}: ${msg.content}`);

    // Get any media updates
    const mediaMessages = analysis.importantMessages
      .filter(msg => msg.type === 'media')
      .map(msg => `• ${msg.senderName}: ${msg.content}`);

    return `📊 *עדכונים חשובים מהקבוצה*

${importantMessages.length > 0 ? importantMessages.join('\n') : 'אין עדכונים חשובים'}

${mediaMessages.length > 0 ? `*קבצים ומדיה*\n${mediaMessages.join('\n')}` : ''}

_נוצר אוטומטית ${new Date().toLocaleTimeString('he-IL')}_`;
  }
} 