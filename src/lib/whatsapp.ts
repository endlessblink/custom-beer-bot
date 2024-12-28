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

export interface IWhatsAppAPI {
  checkInstanceState(): Promise<boolean>;
  makeRequest(endpoint: string, data?: any): Promise<any>;
  getGroups(): Promise<{ id: string; name: string; contactName?: string; type: string }[]>;
  sendMessage(chatId: string, message: string): Promise<any>;
  sendGroupSummary(group: GroupConfig, summary: string): Promise<void>;
}

export class WhatsAppAPI implements IWhatsAppAPI {
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

  public async checkInstanceState(): Promise<boolean> {
    try {
      const response = await this.makeRequest('getStateInstance');
      console.log('Instance state response:', response);

      if (response && typeof response.stateInstance === 'string') {
        const state = response.stateInstance;
        console.log('Instance state:', state);
        return state === 'authorized';
      }

      console.warn('Unexpected instance state response:', response);
      return false;
    } catch (error: any) {
      if (error.response?.status === 429) {
        console.log('Rate limited during state check, assuming authorized');
        return true;
      }

      console.error('Failed to check instance state:', error);
      return false;
    }
  }

  public async makeRequest(endpoint: string, data?: any): Promise<any> {
    try {
      const { idInstance, apiTokenInstance } = config.whatsapp;
      const baseUrl = `https://api.green-api.com/waInstance${idInstance}`;
      const url = `${baseUrl}/${endpoint}/${apiTokenInstance}`;

      console.log('Making request to Green API:', {
        endpoint,
        method: data ? 'POST' : 'GET',
        dataSize: data ? JSON.stringify(data).length : 0,
        data: data ? JSON.stringify(data) : undefined,
        url: url.replace(apiTokenInstance, '****') // Log URL without token
      });

      const response = await fetch(url, {
        method: data ? 'POST' : 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: data ? JSON.stringify(data) : undefined
      });

      let responseData;
      const responseText = await response.text();

      try {
        responseData = responseText ? JSON.parse(responseText) : null;
      } catch (error) {
        console.error('Failed to parse response:', {
          text: responseText,
          error: error instanceof Error ? error.message : String(error)
        });
        throw new Error('Invalid JSON response from API');
      }

      console.log('Green API response:', {
        endpoint,
        status: response.status,
        statusText: response.statusText,
        data: responseData
      });

      // Handle specific error cases
      if (responseData?.statusCode === 401) {
        throw new Error('WhatsApp instance not authorized');
      }

      if (responseData?.statusCode === 466) {
        throw new Error('Request rate limit exceeded');
      }

      if (responseData?.statusCode === 400) {
        throw new Error(`Bad request: ${responseData.message || 'Unknown error'}`);
      }

      if (!response.ok || responseData?.error) {
        throw new Error(
          responseData?.error || 
          responseData?.message || 
          `Request failed with status ${response.status}`
        );
      }

      return responseData;
    } catch (error: any) {
      // Log the complete error details
      console.error('Request failed:', {
        endpoint,
        error: {
          message: error.message,
          stack: error.stack,
          response: error.response?.data,
          status: error.response?.status
        },
        requestData: data
      });
      throw error;
    }
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

  private async makeRequestToApi(endpoint: string, data?: any): Promise<any> {
    try {
      const { idInstance, apiTokenInstance } = config.whatsapp;
      const baseUrl = `https://api.green-api.com/waInstance${idInstance}`;
      const url = `${baseUrl}/${endpoint}/${apiTokenInstance}`;

      console.log('Making direct request to Green API:', {
        endpoint,
        method: data ? 'POST' : 'GET',
        dataSize: data ? JSON.stringify(data).length : 0,
        data: data ? JSON.stringify(data).substring(0, 100) + '...' : undefined,
        url: url.replace(apiTokenInstance, '****') // Log URL without token
      });

      const response = await fetch(url, {
        method: data ? 'POST' : 'GET',
        headers: {
          'Content-Type': 'application/json'
        },
        body: data ? JSON.stringify(data) : undefined
      });

      const responseData = await response.json();
      console.log('Green API response:', {
        endpoint,
        status: response.status,
        data: responseData
      });

      if (!response.ok) {
        throw new Error(responseData.error || responseData.details || 'Green API request failed');
      }

      return responseData;
    } catch (error: any) {
      console.error('Green API request failed:', {
        endpoint,
        error: error.message,
        response: error.response?.data,
        status: error.response?.status,
        data
      });
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

  public async sendMessage(chatId: string, message: string): Promise<any> {
    try {
      const formattedChatId = this.formatChatId(chatId);
      console.log('Sending message to WhatsApp:', {
        chatId: formattedChatId,
        messageLength: message.length,
        messagePreview: message.substring(0, 100) + '...'
      });

      const response = await this.makeRequest('sendMessage', {
        chatId: formattedChatId,
        message
      });

      console.log('Message sent successfully:', {
        chatId: formattedChatId,
        response
      });

      return response;
    } catch (error: any) {
      console.error('Failed to send message:', {
        chatId,
        error: error.message,
        response: error.response?.data,
        status: error.response?.status
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

    try {
      // Format the message with proper styling
      const formattedMessage = [
        '📊 *Group Summary*',
        '-------------------',
        summary,
        '\n_Generated at: ' + new Date().toLocaleString() + '_'
      ].join('\n\n');

      // Log the incoming group ID for debugging
      console.log('Preparing to send group summary:', {
        groupId: group.groupId,
        summaryLength: formattedMessage.length,
        groupName: group.name || 'Unknown Group',
        messagePreview: formattedMessage.substring(0, 100) + '...'
      });

      // Ensure group ID has correct suffix
      const formattedGroupId = this.formatChatId(group.groupId);

      // First try to verify the group exists
      const groups = await this.getGroups();
      const groupExists = groups.some(g => g.id === formattedGroupId);
      
      if (!groupExists) {
        throw new Error(`Group not found: ${formattedGroupId}`);
      }

      // Send message using the API
      const result = await this.sendMessage(formattedGroupId, formattedMessage);

      if (!result?.idMessage) {
        throw new Error('Failed to send message: No message ID in response');
      }

      console.log('Successfully sent group summary:', {
        groupId: formattedGroupId,
        messageId: result.idMessage,
        response: result
      });
    } catch (error: any) {
      console.error('Failed to send group summary:', {
        groupId: group.groupId,
        error: {
          message: error.message,
          stack: error.stack,
          response: error.response?.data,
          status: error.response?.status
        }
      });
      throw new Error(`Failed to send group summary: ${error.message}`);
    }
  }

  private formatChatId(chatId: string): string {
    if (!chatId) {
      throw new Error('Chat ID is required');
    }

    // Log the incoming chat ID for debugging
    console.log('Formatting chat ID:', {
      original: chatId,
      hasGUsSuffix: chatId.endsWith('@g.us'),
      hasCUsSuffix: chatId.endsWith('@c.us')
    });

    // If it already has a valid suffix, return as is
    if (chatId.endsWith('@g.us') || chatId.endsWith('@c.us')) {
      return chatId;
    }

    // Determine if this is a group chat ID based on format or length
    const isGroup = chatId.includes('-') || chatId.length > 15;
    const suffix = isGroup ? '@g.us' : '@c.us';

    console.log('Chat ID formatting result:', {
      original: chatId,
      isGroup,
      suffix,
      formatted: `${chatId}${suffix}`
    });

    return `${chatId}${suffix}`;
  }
}

// Export a simplified sendMessage function for the scheduler
export async function sendMessage(groupId: string, message: string): Promise<any> {
  const api = WhatsAppAPI.getInstance();
  return api.sendMessage(groupId, message);
}
