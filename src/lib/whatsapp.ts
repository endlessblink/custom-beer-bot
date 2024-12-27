import axios from 'axios';
import { config } from './config';
import { GroupConfig } from './config';

const RATE_LIMIT_DELAY = 5000; // 5 seconds between requests
const MAX_RETRIES = 3;
const CACHE_DURATION = 300000; // 5 minutes cache
const BASE_BACKOFF_DELAY = 6000; // 6 seconds base backoff
const RETRY_DELAY = 6000; // 6 seconds

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

interface RequestQueueItem {
  endpoint: string;
  data?: any;
  resolve: (value: any) => void;
  reject: (reason: any) => void;
}

export class WhatsAppAPI {
  private static instance: WhatsAppAPI;
  private readonly baseUrl: string;
  private requestQueue: RequestQueueItem[] = [];
  private isProcessing: boolean = false;
  private requestCount: number = 0;
  private lastResetTime: number = Date.now();
  private readonly MAX_REQUESTS_PER_MINUTE = 100;
  private readonly MIN_REQUEST_INTERVAL = 1000;
  private readonly idInstance: string;
  private readonly apiTokenInstance: string;
  private cache = new Map<string, { data: any; timestamp: number }>();
  private readonly CACHE_DURATION = 60000; // 1 minute cache

  constructor() {
    const { idInstance, apiTokenInstance } = config.whatsapp;
    this.baseUrl = '/api/whatsapp';
    this.idInstance = idInstance;
    this.apiTokenInstance = apiTokenInstance;
    setInterval(() => {
      this.requestCount = 0;
      this.lastResetTime = Date.now();
    }, 60000);
    this.processQueue = this.processQueue.bind(this);
  }

  public static getInstance(): WhatsAppAPI {
    if (!WhatsAppAPI.instance) {
      WhatsAppAPI.instance = new WhatsAppAPI();
    }
    return WhatsAppAPI.instance;
  }

  private async checkInstanceState(): Promise<boolean> {
    try {
      const response = await this.makeRequest('getStateInstance');
      console.log('Instance state response:', response);

      // Check if the response has the expected structure
      if (response && typeof response.stateInstance === 'string') {
        const state = response.stateInstance;
        console.log('Instance state:', state);
        return state === 'authorized';
      }

      console.warn('Unexpected instance state response:', response);
      return false;
    } catch (error: any) {
      if (error.response?.status === 429) {
        // If rate limited, assume authorized to prevent cascading retries
        console.log('Rate limited during state check, assuming authorized');
        return true;
      }

      console.error('Failed to check instance state:', error);
      return false;
    }
  }

  public async makeRequest(endpoint: string, data?: any): Promise<any> {
    return new Promise((resolve, reject) => {
      this.requestQueue.push({
        endpoint,
        data,
        resolve,
        reject,
      });
      if (!this.isProcessing) {
        this.processQueue();
      }
    });
  }

  private async processQueue() {
    if (this.isProcessing || this.requestQueue.length === 0) {
      return;
    }

    this.isProcessing = true;
    while (this.requestQueue.length > 0) {
      const request = this.requestQueue.shift();
      if (request) {
        try {
          const response = await this.makeRequestToApi(request.endpoint, request.data);
          request.resolve(response);
        } catch (error) {
          request.reject(error);
        }
      }
    }
    this.isProcessing = false;
  }

  private async makeRequestToApi(endpoint: string, data?: any, retryCount = 0): Promise<any> {
    try {
      const url = `${this.baseUrl}/${endpoint}`;
      console.log(`Making request to ${url}...`, {
        method: data ? 'POST' : 'GET',
        endpoint,
        dataSize: data ? JSON.stringify(data).length : 0
      });

      const config = {
        headers: { 
          'Content-Type': 'application/json'
        }
      };

      const response = data 
        ? await axios.post(url, data, config)
        : await axios.get(url, config);

      // Add delay between requests to prevent rate limiting
      await this.delay(1000);

      return response.data;
    } catch (error: any) {
      if (error.response?.status === 429 && retryCount < MAX_RETRIES) {
        const backoffDelay = BASE_BACKOFF_DELAY * Math.pow(2, retryCount);
        console.log(`Rate limited, retrying in ${backoffDelay}ms... (Attempt ${retryCount + 1}/${MAX_RETRIES})`);
        await this.delay(backoffDelay);
        return this.makeRequestToApi(endpoint, data, retryCount + 1);
      }

      throw error;
    }
  }

  private delay(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async getGroups(): Promise<{ id: string; name: string; contactName?: string; type: string }[]> {
    try {
      // Check cache first
      const cached = this.cache.get('groups');
      if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
        console.log('Using cached groups data');
        return cached.data;
      }

      console.log('Checking instance state...');
      const isAuthorized = await this.checkInstanceState();
      if (!isAuthorized) {
        throw new Error('WhatsApp instance is not authorized. Please scan the QR code in the Green API dashboard.');
      }

      console.log('Fetching groups from WhatsApp API...');
      const response = await this.makeRequest('getContacts');
      
      if (!response || !Array.isArray(response)) {
        console.warn('Unexpected response format from getContacts:', response);
        return [];
      }

      // Filter and map the groups
      const groups = response
        .filter(contact => contact.type === 'group')
        .map(group => ({
          id: this.formatChatId(group.id),
          name: group.name || 'Unknown Group',
          contactName: group.contact,
          type: 'group'
        }));

      console.log('Successfully fetched groups:', groups);

      // Cache the results
      this.cache.set('groups', {
        data: groups,
        timestamp: Date.now()
      });

      return groups;
    } catch (error: any) {
      console.error('Failed to fetch groups:', {
        error: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      throw new Error(`Failed to fetch WhatsApp groups: ${error.message}`);
    }
  }

  async sendMessage(chatId: string, message: string): Promise<any> {
    let formattedChatId: string;

    try {
      formattedChatId = this.formatChatId(chatId);

      console.log('Sending message:', {
        originalChatId: chatId,
        formattedChatId,
        messageLength: message.length
      });

      // Match the exact API request format
      const payload = {
        chatId: formattedChatId,
        message: message
      };

      console.log('Request payload:', payload);
      const response = await this.makeRequest('sendMessage', payload);
      console.log('Send message response:', response);
      return response;
    } catch (error: any) {
      console.error('Failed to send message:', {
        error: error.message,
        response: error.response?.data,
        status: error.response?.status,
        chatId: chatId,
        formattedChatId: formattedChatId!,
        payload: error.config?.data
      });
      throw error;
    }
  }

  async sendGroupSummary(group: GroupConfig, summary: string): Promise<void> {
    if (!group?.groupId) {
      throw new Error('Group configuration must include a valid groupId');
    }

    if (!summary) {
      throw new Error('Summary message cannot be empty');
    }

    // Validate group ID format using regex
    const groupIdRegex = /^\d+-\d+@g\.us$/;
    if (!groupIdRegex.test(group.groupId)) {
      throw new Error('Invalid group ID format. Group ID must include both creator\'s phone number and timestamp (e.g., "123456789-1234567890@g.us")');
    }

    try {
      // Log the incoming group ID for debugging
      console.log('Preparing to send group summary:', {
        groupId: group.groupId,
        summaryLength: summary.length,
        groupName: group.name || 'Unknown Group',
        formattedGroupId: this.formatChatId(group.groupId)
      });

      const formattedMessage = [
        '📊 *Group Summary*',
        '-------------------',
        summary,
        '\n_Generated at: ' + new Date().toLocaleString() + '_'
      ].join('\n\n');

      const result = await this.sendMessage(group.groupId, formattedMessage);

      console.log('Successfully sent group summary:', {
        groupId: group.groupId,
        messageId: result.id,
        timestamp: result.timestamp
      });
    } catch (error: any) {
      const errorDetails = {
        groupId: group.groupId,
        error: error.message,
        response: error.response?.data,
        status: error.response?.status
      };
      console.error('Failed to send group summary:', errorDetails);
      throw new Error(`Failed to send group summary: ${error.message}`);
    }
  }

  private formatChatId(chatId: string): string {
    if (!chatId) {
      throw new Error('Chat ID cannot be empty');
    }

    // If the ID already has the correct format, return it as is
    if (chatId.endsWith('@g.us') || chatId.endsWith('@c.us')) {
      return chatId;
    }

    // For group chats (contains @c.us or is a group ID format)
    if (chatId.includes('@c.us')) {
      return chatId;
    }

    // For group chats without suffix
    if (chatId.includes('-')) {
      return `${chatId}@g.us`;
    }

    // For personal chats
    return chatId;
  }
}
