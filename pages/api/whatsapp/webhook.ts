import { NextApiRequest, NextApiResponse } from 'next';
import { MessageCollector, GroupMessage } from '../../../src/lib/messageCollector';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const webhook = req.body;
    console.log('Received webhook:', JSON.stringify(webhook, null, 2));

    // Handle different types of webhooks
    if (webhook.messageData) {
      const messageData = webhook.messageData;
      const chatId = messageData.chatId;

      // Only collect group messages
      if (!chatId.includes('@g.us')) {
        return res.status(200).json({ success: true, message: 'Ignored non-group message' });
      }

      const collector = MessageCollector.getInstance();
      
      const message: GroupMessage = {
        timestamp: new Date(),
        sender: messageData.senderId || 'unknown',
        senderName: messageData.senderName,
        content: messageData.textMessage || messageData.caption || '',
        type: determineMessageType(messageData)
      };

      collector.collectMessage(chatId, message);
      
      console.log('Collected message:', {
        chatId,
        messageType: message.type,
        sender: message.sender,
        contentLength: message.content.length
      });
    }

    return res.status(200).json({ success: true });
  } catch (error: any) {
    console.error('Webhook error:', error);
    return res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
}

function determineMessageType(messageData: any): GroupMessage['type'] {
  if (messageData.textMessage) return 'text';
  if (messageData.fileMessage || messageData.imageMessage || messageData.videoMessage) return 'media';
  return 'system';
} 