import { MessageCollector } from './messageCollector';
import { MessageAnalyzer } from './messageAnalyzer';
import { sendMessage } from './whatsapp';

interface ScheduledTask {
  groupId: string;
  nextRunTime: Date;
  retryCount: number;
  lastError?: string;
}

export class SummaryScheduler {
  private static instance: SummaryScheduler;
  private tasks: Map<string, ScheduledTask> = new Map();
  private messageCollector: MessageCollector;
  private checkInterval: NodeJS.Timeout | null = null;

  private constructor() {
    this.messageCollector = MessageCollector.getInstance();
  }

  public static getInstance(): SummaryScheduler {
    if (!SummaryScheduler.instance) {
      SummaryScheduler.instance = new SummaryScheduler();
    }
    return SummaryScheduler.instance;
  }

  public startScheduler() {
    if (this.checkInterval) return;

    this.checkInterval = setInterval(() => {
      this.checkAndRunTasks();
    }, 60000); // Check every minute

    console.log('Scheduler started');
  }

  public stopScheduler() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
      console.log('Scheduler stopped');
    }
  }

  private async checkAndRunTasks() {
    const now = new Date();

    for (const [groupId, task] of this.tasks.entries()) {
      if (now >= task.nextRunTime) {
        await this.runTask(groupId, task);
      }
    }
  }

  private async runTask(groupId: string, task: ScheduledTask) {
    try {
      console.log(`Running summary task for group ${groupId}`);
      
      // Get today's messages
      const messages = this.messageCollector.getDailySummaryMessages(groupId);
      
      // Analyze messages
      const analysis = MessageAnalyzer.analyzeMessages(messages);
      
      // Format and send summary
      const summary = MessageAnalyzer.formatAnalysis(analysis);
      
      await sendMessage(groupId, summary);
      
      // Update next run time to tomorrow at same time
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(20, 0, 0, 0); // Set to 20:00
      
      this.tasks.set(groupId, {
        ...task,
        nextRunTime: tomorrow,
        retryCount: 0,
        lastError: undefined
      });

      console.log(`Summary sent successfully for group ${groupId}`);
    } catch (error: any) {
      console.error(`Failed to send summary for group ${groupId}:`, error);
      
      // Handle retry logic
      if (task.retryCount < 3) {
        const retryDelay = Math.pow(2, task.retryCount) * 5 * 60000; // Exponential backoff
        const nextRetry = new Date(Date.now() + retryDelay);
        
        this.tasks.set(groupId, {
          ...task,
          nextRunTime: nextRetry,
          retryCount: task.retryCount + 1,
          lastError: error.message
        });
        
        console.log(`Will retry summary for group ${groupId} at ${nextRetry}`);
      } else {
        // Reset for tomorrow after max retries
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(20, 0, 0, 0);
        
        this.tasks.set(groupId, {
          ...task,
          nextRunTime: tomorrow,
          retryCount: 0,
          lastError: `Max retries exceeded: ${error.message}`
        });
        
        console.log(`Max retries reached for group ${groupId}, scheduled for tomorrow`);
      }
    }
  }

  public addTask(groupId: string) {
    // Set initial run time to today at 20:00
    const nextRun = new Date();
    nextRun.setHours(20, 0, 0, 0);
    
    // If it's already past 20:00, schedule for tomorrow
    if (nextRun <= new Date()) {
      nextRun.setDate(nextRun.getDate() + 1);
    }

    this.tasks.set(groupId, {
      groupId,
      nextRunTime: nextRun,
      retryCount: 0
    });

    console.log(`Task added for group ${groupId}, next run at ${nextRun}`);
  }

  public removeTask(groupId: string) {
    this.tasks.delete(groupId);
    console.log(`Task removed for group ${groupId}`);
  }

  public getTask(groupId: string): ScheduledTask | undefined {
    return this.tasks.get(groupId);
  }

  public getAllTasks(): Map<string, ScheduledTask> {
    return new Map(this.tasks);
  }
} 