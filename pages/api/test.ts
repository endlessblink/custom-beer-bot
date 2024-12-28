import { NextApiRequest, NextApiResponse } from 'next';
import { MessageCollector, GroupMessage } from '../../src/lib/messageCollector';
import { MessageAnalyzer } from '../../src/lib/messageAnalyzer';
import { WhatsAppAPI } from '../../src/lib/whatsapp';
import { config } from '../../src/lib/config';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { endpoint } = req.query;

  if (endpoint === 'generateTestSummary') {
    try {
      // Get the group ID from the request
      const { groupId } = req.body;
      if (!groupId) {
        console.error('Missing group ID in request body');
        return res.status(400).json({ error: 'Group ID is required' });
      }

      console.log('Generating test summary for group:', {
        groupId,
        requestBody: req.body,
        whatsappConfig: {
          idInstance: config.whatsapp.idInstance,
          hasToken: !!config.whatsapp.apiTokenInstance
        }
      });

      // Create sample messages for testing
      const sampleMessages: GroupMessage[] = [
        {
          timestamp: new Date(),
          sender: '1234567890',
          senderName: 'Test User 1',
          content: 'היי, יש לנו פגישה חשובה מחר בשעה 10:00',
          type: 'text'
        },
        {
          timestamp: new Date(),
          sender: '0987654321',
          senderName: 'Test User 2',
          content: 'אני אהיה שם. יש לי כמה עדכונים חשובים לשתף.',
          type: 'text'
        },
        {
          timestamp: new Date(),
          sender: '1111111111',
          senderName: 'Test User 3',
          content: 'שלחתי לכם מסמך חשוב לעיון לפני הפגישה',
          type: 'text'
        }
      ];

      console.log('Sample messages prepared:', {
        count: sampleMessages.length,
        messages: sampleMessages.map(m => ({
          sender: m.senderName,
          content: m.content
        }))
      });

      // Analyze messages
      const analysis = await MessageAnalyzer.analyzeMessages(sampleMessages);
      console.log('Message analysis results:', analysis);

      // Format the summary
      const summary = MessageAnalyzer.formatAnalysis(analysis);
      console.log('Formatted summary:', {
        length: summary.length,
        content: summary
      });

      // Send the summary to WhatsApp
      try {
        console.log('Attempting to send summary to WhatsApp:', {
          groupId,
          summaryLength: summary.length,
          summary: summary.substring(0, 100) + '...' // Log first 100 chars
        });

        // Create a test message
        const formattedMessage = [
          '📊 *Group Summary*',
          '-------------------',
          summary,
          '\n_Generated at: ' + new Date().toLocaleString() + '_'
        ].join('\n\n');

        // Get WhatsApp API instance
        const api = WhatsAppAPI.getInstance();

        // Check instance state first
        const isAuthorized = await api.checkInstanceState();
        console.log('WhatsApp instance state:', isAuthorized);

        if (!isAuthorized) {
          throw new Error('WhatsApp instance not authorized');
        }

        // Send message directly using the API instance
        console.log('Sending message with payload:', {
          groupId,
          messageLength: formattedMessage.length,
          messagePreview: formattedMessage.substring(0, 100) + '...'
        });

        const result = await api.sendMessage(groupId, formattedMessage);
        console.log('WhatsApp send message result:', result);

        if (!result || result.error) {
          throw new Error(result?.error || result?.details || 'Failed to send message');
        }

        return res.status(200).json({
          success: true,
          summary,
          messageCount: sampleMessages.length,
          whatsappSent: true,
          response: result
        });
      } catch (sendError: any) {
        console.error('Failed to send summary to WhatsApp:', {
          error: sendError.message,
          response: sendError.response?.data,
          status: sendError.response?.status,
          groupId,
          summaryLength: summary.length,
          summaryPreview: summary.substring(0, 100) + '...',
          stack: sendError.stack,
          whatsappConfig: {
            idInstance: config.whatsapp.idInstance,
            hasToken: !!config.whatsapp.apiTokenInstance
          }
        });
        
        return res.status(500).json({
          error: 'Failed to send summary to WhatsApp',
          details: sendError.message,
          response: sendError.response?.data,
          groupId,
          stack: sendError.stack
        });
      }
    } catch (error: any) {
      console.error('Failed to generate test summary:', {
        error: error.message,
        stack: error.stack,
        type: error.constructor.name
      });
      
      return res.status(500).json({
        error: 'Failed to generate test summary',
        details: error.message,
        type: error.constructor.name,
        stack: error.stack
      });
    }
  }

  return res.status(400).json({ error: 'Invalid endpoint' });
}
