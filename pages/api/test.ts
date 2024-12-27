import { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';
import { config } from '../../src/lib/config';

const { idInstance, apiTokenInstance, apiUrl } = config.whatsapp;

// Debug helper
const debugInfo = {
  idInstance,
  apiUrl,
  // Don't log full token for security
  tokenPreview: apiTokenInstance ? `${apiTokenInstance.substring(0, 8)}...` : 'not set'
};

// Cache state check results for 30 seconds
let stateCache: { data: any; timestamp: number } | null = null;
const STATE_CACHE_DURATION = 30000; // 30 seconds

async function checkState() {
  // Return cached state if valid
  if (stateCache && Date.now() - stateCache.timestamp < STATE_CACHE_DURATION) {
    return stateCache.data;
  }

  const stateUrl = `${apiUrl}/waInstance${idInstance}/getStateInstance/${apiTokenInstance}`;
  const stateResponse = await axios.get(stateUrl, {
    headers: {
      'Content-Type': 'application/json'
    }
  });

  // Cache the result
  stateCache = {
    data: stateResponse.data,
    timestamp: Date.now()
  };

  return stateResponse.data;
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    // Check authorization state first (using cache when possible)
    const state = await checkState();
    
    if (state.stateInstance !== 'authorized') {
      return res.status(401).json({
        success: false,
        error: 'WhatsApp instance is not authorized',
        state: state.stateInstance,
        message: 'Please verify your WhatsApp instance is properly connected in Green API dashboard',
        debug: {
          ...debugInfo,
          responseState: state.stateInstance
        }
      });
    }

    if (req.method === 'GET') {
      const endpoint = req.query.endpoint as string;

      if (endpoint === 'getGroups') {
        // Get all chats to filter groups
        const response = await axios.get(
          `${apiUrl}/waInstance${idInstance}/getChats/${apiTokenInstance}`
        );

        // Filter only group chats
        const groups = (response.data || []).filter((chat: any) => 
          chat.id && chat.id.includes('@g.us')
        );

        return res.status(200).json({
          success: true,
          groups: groups.map((group: any) => ({
            id: group.id,
            name: group.name
          }))
        });
      }

      // Default state check response
      return res.status(200).json({
        success: true,
        instanceState: state,
        debug: debugInfo
      });
    } else if (req.method === 'POST') {
      const endpoint = req.query.endpoint as string;
      const { groupId, message } = req.body;
      
      if (!groupId) {
        return res.status(400).json({
          success: false,
          error: 'groupId is required'
        });
      }

      if (endpoint === 'sendTestSummary') {
        try {
          console.log('Starting test message process...');
          console.log('Debug info:', debugInfo);
          console.log('Current state:', state);
          
          // Ensure group ID has correct format
          const formattedGroupId = groupId.includes('@g.us') ? groupId : `${groupId}@g.us`;
          console.log('Using group ID:', formattedGroupId);

          // Verify instance status before sending
          const statusUrl = `${apiUrl}/waInstance${idInstance}/getStatusInstance/${apiTokenInstance}`;
          const statusResponse = await axios.get(statusUrl);
          console.log('Instance status:', statusResponse.data);

          // Try sending message using sendMessage endpoint first
          const messageUrl = `${apiUrl}/waInstance${idInstance}/sendMessage/${apiTokenInstance}`;
          console.log('Sending message to:', messageUrl);
          
          const timestamp = new Date().toLocaleTimeString();
          const messagePayload = {
            chatId: formattedGroupId,
            message: `🤖 Test Message (${timestamp}) 🚨\n\nThis is a test message after upgrading to Business Plan.\nGroup ID: ${formattedGroupId}\n\nIf you see this, please reply with "OK".`
          };
          
          console.log('Message payload:', JSON.stringify(messagePayload, null, 2));
          
          try {
            console.log('Attempting to send group message...');
            const messageResponse = await axios.post(messageUrl, messagePayload);
            console.log('Full message response:', JSON.stringify(messageResponse.data, null, 2));
            
            return res.status(200).json({
              success: true,
              messageData: messageResponse.data,
              debug: {
                groupId,
                formattedGroupId,
                method: 'group',
                timestamp
              }
            });
          } catch (sendError: any) {
            console.log('Group message failed:', {
              status: sendError.response?.status,
              data: sendError.response?.data,
              error: sendError.message
            });
            
            if (sendError.response?.status === 466 || sendError.response?.status === 403) {
              // Try sending to personal number
              console.log('Attempting to send to personal number...');
              const personalPayload = {
                chatId: '972526784960@c.us',
                message: `🤖 WhatsApp Bot Test Message (Personal) 🤖\n\nTime: ${timestamp}\n\nThis message was sent to your personal number because group messaging failed.\nError: ${sendError.response?.status}\n\nIf you see this message, please reply with "OK" to confirm the bot is working.`
              };

              try {
                console.log('Sending personal message with payload:', personalPayload);
                const personalResponse = await axios.post(messageUrl, personalPayload);
                console.log('Personal message response:', personalResponse.data);

                return res.status(200).json({
                  success: true,
                  messageData: personalResponse.data,
                  warning: 'Message sent to personal number due to group message limitations',
                  debug: {
                    groupId,
                    formattedGroupId,
                    method: 'personal',
                    timestamp,
                    originalError: {
                      status: sendError.response?.status,
                      message: sendError.message
                    }
                  }
                });
              } catch (personalError: any) {
                console.error('Personal message failed:', {
                  status: personalError.response?.status,
                  data: personalError.response?.data,
                  message: personalError.message,
                  payload: personalPayload
                });

                // Return a 200 status but with error info
                return res.status(200).json({
                  success: false,
                  error: 'Failed to send message to both group and personal number',
                  details: {
                    groupError: {
                      status: sendError.response?.status,
                      message: sendError.message
                    },
                    personalError: {
                      status: personalError.response?.status,
                      message: personalError.message
                    }
                  }
                });
              }
            }
            
            // If not a quota error or personal message failed
            throw sendError;
          }
        } catch (error: any) {
          console.error('Error in sendTestSummary:', {
            message: error.message,
            status: error.response?.status,
            data: error.response?.data,
            url: error.config?.url,
            method: error.config?.method,
            headers: error.config?.headers,
            payload: error.config?.data
          });

          // Always return 200 but with error info
          return res.status(200).json({
            success: false,
            error: error.response?.status === 466 
              ? 'Monthly quota exceeded. Please upgrade your plan.'
              : error.response?.data?.message || error.message || 'Failed to send message',
            details: {
              message: error.message,
              response: error.response?.data,
              status: error.response?.status,
              url: error.config?.url
            }
          });
        }
      }

      // Get group data
      console.log('Fetching group data:', { groupId, ...debugInfo });

      const response = await axios.post(
        `${apiUrl}/waInstance${idInstance}/getGroupData/${apiTokenInstance}`,
        { groupId },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      return res.status(200).json({
        success: true,
        groupData: response.data
      });
    }

    return res.status(405).json({ error: 'Method not allowed' });
  } catch (error: any) {
    console.error('API Error:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      config: debugInfo
    });

    // Check if it's an authentication error
    if (error.response?.status === 401) {
      return res.status(401).json({
        success: false,
        error: 'Authentication failed. Please verify your Green API credentials.',
        details: {
          message: error.response?.data?.message || error.message,
          ...debugInfo
        }
      });
    }

    return res.status(error.response?.status || 500).json({
      success: false,
      error: error.response?.data || error.message,
      debug: {
        ...debugInfo,
        errorDetails: {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data
        }
      }
    });
  }
}
