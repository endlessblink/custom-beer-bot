import { NextApiRequest, NextApiResponse } from 'next';
import { MessageCollector, GroupMessage } from '../../src/lib/messageCollector';
import { MessageAnalyzer } from '../../src/lib/messageAnalyzer';
import { sendMessage } from '../../src/lib/whatsapp';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { endpoint } = req.query;

  if (endpoint === 'generateTestSummary') {
    try {
      // Get the group ID from the request
      const { groupId } = req.body;
      if (!groupId) {
        return res.status(400).json({ error: 'Group ID is required' });
      }

      // Get the message collector instance
      const collector = MessageCollector.getInstance();

      // Get last 10 messages from the group
      const messages = collector.getLastMessages(groupId, 10);

      // Log messages for debugging
      console.log('Retrieved last 10 messages:', messages);

      // Analyze messages
      const analysis = await MessageAnalyzer.analyzeMessages(messages);

      // Format the summary
      const summary = MessageAnalyzer.formatAnalysis(analysis);

      // Send the summary to WhatsApp
      try {
        await sendMessage(groupId, summary);
        console.log('Summary sent to WhatsApp successfully');
      } catch (sendError) {
        console.error('Failed to send summary to WhatsApp:', sendError);
      }

      return res.status(200).json({
        success: true,
        summary,
        messageCount: messages.length,
        rawMessages: messages,
        whatsappSent: true
      });
    } catch (error: any) {
      console.error('Failed to generate test summary:', error);
      return res.status(500).json({
        error: 'Failed to generate test summary',
        details: error.message,
        stack: error.stack
      });
    }
  }

  return res.status(400).json({ error: 'Invalid endpoint' });
}
