import axios from 'axios';

async function testEndpoint(endpoint: string, method: 'GET' | 'POST' = 'GET', data?: any) {
  const idInstance = '7105169202';
  const apiTokenInstance = 'fcd7e60dde584aa4823949c3032fcad318375231ff1f4df6b4';
  
  try {
    const url = `https://api.green-api.com/waInstance${idInstance}/${endpoint}/${apiTokenInstance}`;
    console.log(`Testing ${method} ${url}`);
    
    const response = await axios({
      method,
      url,
      data,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log('Success:', {
      status: response.status,
      data: response.data
    });
    return true;
  } catch (error: any) {
    console.error('Error:', {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    return false;
  }
}

async function runTests() {
  console.log('Starting API endpoint tests...\n');

  // Test 1: Get Contacts
  console.log('Test 1: Get Contacts');
  await testEndpoint('getContacts');

  // Test 2: Get State
  console.log('\nTest 2: Get State');
  await testEndpoint('getStateInstance');

  // Test 3: Send Message
  console.log('\nTest 3: Send Message');
  await testEndpoint('sendMessage', 'POST', {
    chatId: '1234567890@g.us',
    message: 'Test message'
  });

  console.log('\nTests completed.');
}

// Run the tests
runTests(); 