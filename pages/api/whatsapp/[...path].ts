import { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';
import { config } from '../../../src/lib/config';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { path } = req.query;
  const endpoint = Array.isArray(path) ? path.join('/') : path;

  try {
    console.log('WhatsApp API request:', {
      method: req.method,
      endpoint,
      body: req.body,
      config: {
        idInstance: config.whatsapp.idInstance,
        hasToken: !!config.whatsapp.apiTokenInstance
      }
    });

    const { idInstance, apiTokenInstance } = config.whatsapp;
    if (!idInstance || !apiTokenInstance) {
      console.error('Missing WhatsApp API configuration');
      return res.status(500).json({
        error: 'WhatsApp API configuration missing',
        details: 'idInstance or apiTokenInstance is not configured'
      });
    }

    const baseUrl = `https://api.green-api.com/waInstance${idInstance}`;
    
    // Special handling for sendMessage endpoint
    if (endpoint === 'sendMessage') {
      const { chatId, message } = req.body;
      if (!chatId || !message) {
        console.error('Invalid sendMessage request:', {
          chatId,
          hasMessage: !!message,
          messageLength: message?.length
        });
        return res.status(400).json({
          error: 'Bad Request',
          details: 'chatId and message are required for sending messages'
        });
      }

      // Format the request body according to Green API specs
      const formattedBody = {
        chatId,
        message,
        quotedMessageId: req.body.quotedMessageId,
        archiveChat: false,
        linkPreview: false
      };

      console.log('Sending message to WhatsApp:', {
        chatId,
        messageLength: message.length,
        messagePreview: message.substring(0, 100) + '...',
        formattedBody
      });

      // Update the request body
      req.body = formattedBody;
    }

    const url = `${baseUrl}/${endpoint}/${apiTokenInstance}`;

    console.log('Making request to Green API:', {
      url,
      method: req.method,
      bodySize: req.body ? JSON.stringify(req.body).length : 0,
      body: req.body ? JSON.stringify(req.body).substring(0, 100) + '...' : undefined,
      endpoint
    });

    try {
      const response = await axios({
        method: req.method,
        url,
        data: req.method !== 'GET' ? req.body : undefined,
        headers: {
          'Content-Type': 'application/json'
        },
        validateStatus: null // Don't throw on any status
      });

      console.log('Green API response:', {
        status: response.status,
        data: response.data,
        headers: response.headers
      });

      // Check for specific error responses from Green API
      if (response.status === 401) {
        return res.status(401).json({
          error: 'Unauthorized',
          details: 'Invalid WhatsApp API credentials'
        });
      }

      if (response.status === 466) {
        return res.status(466).json({
          error: 'Instance not authorized',
          details: 'Please scan the QR code in the Green API dashboard'
        });
      }

      if (response.status === 400 && response.data?.description) {
        return res.status(400).json({
          error: 'Bad Request',
          details: response.data.description
        });
      }

      if (response.status >= 400) {
        return res.status(response.status).json({
          error: 'WhatsApp API error',
          details: response.data || 'Unknown error',
          status: response.status
        });
      }

      return res.status(response.status).json(response.data);
    } catch (apiError: any) {
      console.error('Green API error response:', {
        status: apiError.response?.status,
        data: apiError.response?.data,
        error: apiError.message,
        config: {
          url: apiError.config?.url,
          method: apiError.config?.method,
          data: apiError.config?.data ? JSON.stringify(apiError.config.data).substring(0, 100) + '...' : undefined
        }
      });

      return res.status(apiError.response?.status || 500).json({
        error: 'WhatsApp API error',
        details: apiError.response?.data || apiError.message,
        endpoint,
        requestData: {
          url: apiError.config?.url,
          method: apiError.config?.method
        }
      });
    }
  } catch (error: any) {
    console.error('WhatsApp API handler error:', {
      error: error.message,
      stack: error.stack,
      endpoint,
      body: req.body
    });

    return res.status(500).json({
      error: 'WhatsApp API error',
      details: error.message,
      endpoint
    });
  }
}
