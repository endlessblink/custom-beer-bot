import { GroupMessage } from './messageCollector';

export class LLMService {
  private static instance: LLMService;
  private apiKey: string;
  private apiEndpoint = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent';

  private constructor() {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      throw new Error('GEMINI_API_KEY environment variable is not set');
    }
    this.apiKey = apiKey;
  }

  public static getInstance(): LLMService {
    if (!LLMService.instance) {
      LLMService.instance = new LLMService();
    }
    return LLMService.instance;
  }

  public async generateMessageInsights(messages: GroupMessage[]): Promise<string> {
    try {
      const prompt = this.createPrompt(messages);
      
      const response = await fetch(`${this.apiEndpoint}?key=${this.apiKey}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: prompt
            }]
          }],
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 500,
            topP: 0.8,
            topK: 40
          }
        })
      });

      if (!response.ok) {
        throw new Error(`Gemini API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      // Extract the generated text from Gemini's response
      const generatedText = data.candidates?.[0]?.content?.parts?.[0]?.text;
      
      if (!generatedText) {
        throw new Error('No text generated from Gemini API');
      }

      return generatedText;
    } catch (error) {
      console.error('Failed to generate LLM insights:', error);
      return 'לא ניתן היה לייצר תובנות - נא לנסות שוב מאוחר יותר';
    }
  }

  private createPrompt(messages: GroupMessage[]): string {
    const formattedMessages = messages.map(msg => {
      const time = msg.timestamp.toLocaleTimeString('he-IL');
      return `[${time}] ${msg.senderName || msg.sender}: ${msg.content}`;
    }).join('\n');

    return `You are a WhatsApp group analysis assistant. Analyze these messages and provide insights in Hebrew.
Keep technical terms in English. Use RTL formatting. Be concise but informative.

Messages to analyze:
${formattedMessages}

Please provide the following sections in Hebrew:
1. תקציר כללי של הדיונים
2. נושאים טכניים שעלו (השאר מונחים טכניים באנגלית)
3. החלטות או הודעות חשובות
4. משימות או דדליינים שהוזכרו
5. תובנות נוספות

Make sure to:
- Keep all technical terms in English (like API, Stable Diffusion, etc.)
- Use RTL formatting for Hebrew text
- Be concise but informative
- Focus on key insights and patterns
- Highlight important decisions and deadlines`;
  }
} 