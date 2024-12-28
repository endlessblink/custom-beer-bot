import { NextApiRequest, NextApiResponse } from 'next';
import { WhatsAppAPI } from '@/lib/whatsapp';
import { MessageAnalyzer } from '@/lib/messageAnalyzer';
import { GroupMessage } from '@/lib/messageCollector';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const { endpoint } = req.query;
    const { groupId } = req.body;

    console.log('Test endpoint called:', {
      endpoint,
      groupId,
      method: req.method,
      body: req.body
    });

    if (endpoint === 'generateTestSummary') {
      if (!groupId) {
        throw new Error('Group ID is required');
      }

      const api = new WhatsAppAPI();
      const analyzer = new MessageAnalyzer();

      // Generate sample messages for testing
      const sampleMessages: GroupMessage[] = [
        {
          sender: '1234567890',
          senderName: 'Test User 1',
          content: 'Important meeting tomorrow at 10 AM',
          timestamp: new Date(Date.now() - 3600000),
          type: 'text'
        },
        {
          sender: '0987654321',
          senderName: 'Test User 2',
          content: 'Please review the project proposal',
          timestamp: new Date(Date.now() - 7200000),
          type: 'text'
        },
        {
          sender: '1111111111',
          senderName: 'Test User 3',
          content: 'Deadline for submissions is next Friday',
          timestamp: new Date(Date.now() - 10800000),
          type: 'text'
        }
      ];

      console.log('Generating test summary with sample messages:', {
        groupId,
        messageCount: sampleMessages.length,
        messages: sampleMessages.map(m => m.content)
      });

      // Analyze messages first
      const analysis = await MessageAnalyzer.analyzeMessages(sampleMessages);
      
      // Then format the analysis
      const summary = MessageAnalyzer.formatAnalysis(analysis);

      console.log('Generated summary:', {
        groupId,
        summaryLength: summary.length,
        summaryPreview: summary.substring(0, 100) + '...'
      });

      // Format the message with proper styling
      const formattedMessage = [
        '📊 *Test Summary*',
        '-------------------',
        summary,
        '\n_Generated at: ' + new Date().toLocaleString() + '_'
      ].join('\n\n');

      // Send the summary to the group using sendGroupSummary
      await api.sendGroupSummary({
        groupId,
        name: 'Test Group',
        schedules: []
      }, formattedMessage);

      console.log('Test summary sent successfully to group:', groupId);
      return res.status(200).json({ success: true });
    }

    throw new Error(`Unknown endpoint: ${endpoint}`);
  } catch (error: any) {
    console.error('Test endpoint error:', {
      error: error.message,
      response: error.response?.data,
      status: error.response?.status
    });
    return res.status(500).json({ error: error.message });
  }
}
