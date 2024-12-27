import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';

const STORAGE_DIR = path.join(process.cwd(), 'data', 'messages');

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { groupId } = req.body;

    if (!groupId) {
      return res.status(400).json({ error: 'groupId is required' });
    }

    // Make group ID safe for file system
    const safeGroupId = groupId.replace(/[^a-zA-Z0-9]/g, '_');
    const filePath = path.join(STORAGE_DIR, `${safeGroupId}.json`);

    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }

    return res.status(200).json({
      success: true,
      message: `Messages cleared for group ${groupId}`
    });
  } catch (error: any) {
    console.error('Failed to clear messages:', error);
    return res.status(500).json({
      error: 'Failed to clear messages',
      details: error.message
    });
  }
} 