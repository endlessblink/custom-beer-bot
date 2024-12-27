'use client';

import { useEffect } from 'react';
import { storage } from '@/lib/storage';
import { MessageCollector } from '@/lib/messageCollector';

export default function Home() {
  useEffect(() => {
    // Initialize storage and collector
    const collector = MessageCollector.getInstance();
    
    // Test the summary generation
    const testSummary = async () => {
      try {
        const response = await fetch('/api/test?endpoint=generateTestSummary', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            groupId: '120363271484974874@g.us'
          })
        });

        const data = await response.json();
        console.log('Summary generated:', data);
      } catch (error) {
        console.error('Failed to generate summary:', error);
      }
    };

    testSummary();
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1>WhatsApp Bot</h1>
      <p>Check the console for test results</p>
    </main>
  );
}
