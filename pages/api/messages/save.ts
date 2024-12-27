import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';
import { GroupMessage } from '../../../src/lib/messageCollector';

const STORAGE_DIR = path.join(process.cwd(), 'data', 'messages');

// Ensure storage directory exists
if (!fs.existsSync(STORAGE_DIR)) {
  fs.mkdirSync(STORAGE_DIR, { recursive: true });
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { groupId, messages } = req.body;

    if (!groupId || !messages) {
      return res.status(400).json({ error: 'groupId and messages are required' });
    }

    // Make group ID safe for file system
    const safeGroupId = groupId.replace(/[^a-zA-Z0-9]/g, '_');
    const filePath = path.join(STORAGE_DIR, `${safeGroupId}.json`);

    // Save messages to file
    fs.writeFileSync(filePath, JSON.stringify(messages, null, 2), 'utf8');

    return res.status(200).json({
      success: true,
      messageCount: messages.length
    });
  } catch (error: any) {
    console.error('Failed to save messages:', error);
    return res.status(500).json({
      error: 'Failed to save messages',
      details: error.message
    });
  }
} 