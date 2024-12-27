import { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';
import { config } from '../../../src/lib/config';

const { idInstance, apiTokenInstance, apiUrl } = config.whatsapp;

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    // Get the endpoint from the path
    const endpoint = Array.isArray(req.query.path) ? req.query.path[0] : req.query.path;
    
    // Construct the Green API URL
    const url = `${apiUrl}/waInstance${idInstance}/${endpoint}/${apiTokenInstance}`;
    
    console.log('Making request to Green API:', {
      endpoint,
      method: req.method,
      url
    });

    let response;
    if (req.method === 'POST') {
      response = await axios.post(url, req.body, {
        headers: { 'Content-Type': 'application/json' }
      });
    } else {
      response = await axios.get(url);
    }

    console.log('Green API Response:', {
      status: response.status,
      data: response.data
    });

    return res.status(200).json(response.data);
  } catch (error: any) {
    console.error('WhatsApp API Error:', {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });

    return res.status(error.response?.status || 500).json({
      error: error.response?.data || error.message
    });
  }
}
