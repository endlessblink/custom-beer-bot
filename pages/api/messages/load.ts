import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';
import { GroupMessage } from '../../../src/lib/messageCollector';

const STORAGE_DIR = path.join(process.cwd(), 'data', 'messages');

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { groupId } = req.query;

    if (!groupId || typeof groupId !== 'string') {
      return res.status(400).json({ error: 'groupId is required' });
    }

    // Make group ID safe for file system
    const safeGroupId = groupId.replace(/[^a-zA-Z0-9]/g, '_');
    const filePath = path.join(STORAGE_DIR, `${safeGroupId}.json`);

    if (!fs.existsSync(filePath)) {
      return res.status(200).json({ messages: [] });
    }

    // Load messages from file
    const data = fs.readFileSync(filePath, 'utf8');
    const messages = JSON.parse(data) as GroupMessage[];

    return res.status(200).json({
      success: true,
      messages,
      messageCount: messages.length
    });
  } catch (error: any) {
    console.error('Failed to load messages:', error);
    return res.status(500).json({
      error: 'Failed to load messages',
      details: error.message
    });
  }
} 