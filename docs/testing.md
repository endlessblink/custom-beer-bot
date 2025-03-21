# Testing Strategy  
  
## Overview  
  
A comprehensive testing strategy ensures the WhatsApp Bot operates reliably and consistently across all environments.  
This document outlines the testing approach for the bot's components and integration points.  
  
## Test Types  
  
### Unit Tests  
  
Unit tests verify the functionality of individual components in isolation:  
  
```python  
# Example unit test for a message processor  
import unittest  
from unittest.mock import MagicMock, patch  
from message_processor import MessageProcessor  
  
class TestMessageProcessor(unittest.TestCase):  
    def setUp(self):  
        self.db_client = MagicMock()  
        self.api_client = MagicMock()  
        self.processor = MessageProcessor(self.db_client, self.api_client)  
  
    def test_process_new_message(self):  
        # Arrange  
        test_message = {  
            "id": "test-id-123",  
            "body": "Test message content",  
            "chat_id": "group-123",  
            "timestamp": 1637507391  
        }  
        self.db_client.message_exists.return_value = False  
  
        # Act  
        result = self.processor.process_message(test_message)  
  
        # Assert  
        self.assertTrue(result)  
        self.db_client.save_message.assert_called_once_with(test_message)  
        self.api_client.send_receipt.assert_called_once()  
  
    def test_skip_existing_message(self):  
        # Arrange  
        test_message = {"id": "existing-id-456"}  
        self.db_client.message_exists.return_value = True  
  
        # Act  
        result = self.processor.process_message(test_message)  
  
        # Assert  
        self.assertFalse(result)  
        self.db_client.save_message.assert_not_called()  
```  
  
### Integration Tests  
  
Integration tests verify that components work together as expected:  
  
```python  
# Example integration test  
import unittest  
from database.neon_client import NeonDatabaseClient  
from api.openai_client import OpenAIClient  
from message_processor import MessageProcessor  
  
class TestMessageProcessorIntegration(unittest.TestCase):  
    @classmethod  
    def setUpClass(cls):  
        # Use test database  
        cls.db_client = NeonDatabaseClient(connection_string="postgresql://user:pass@test-host/test_db")  
        cls.api_client = OpenAIClient(api_key="test-key")  
        cls.processor = MessageProcessor(cls.db_client, cls.api_client)  
  
        # Set up test database  
        cls.db_client.initialize_tables()  
  
    def test_end_to_end_message_processing(self):  
        # Create a test message  
        test_message = {  
            "id": f"test-{int(time.time())}",  
            "body": "Test integration message",  
            "chat_id": "test-group-integration",  
            "timestamp": int(time.time())  
        }  
  
        # Process the message  
        result = self.processor.process_message(test_message)  
        self.assertTrue(result)  
  
        # Verify it was saved to database  
        saved_message = self.db_client.get_message(test_message["id"])  
        self.assertIsNotNone(saved_message)  
        self.assertEqual(saved_message["body"], test_message["body"])  
  
    @classmethod  
    def tearDownClass(cls):  
        # Clean up test data  
        cls.db_client.execute_query("DELETE FROM messages WHERE chat_id = 'test-group-integration'")  
        cls.db_client.close()  
``` 
### API Mocking  
  
For testing components that interact with external APIs, we use mocking to simulate API responses:  
  
```python  
# Example of API mocking  
import unittest  
from unittest.mock import patch, MagicMock  
from api.openai_client import OpenAIClient  
  
class TestOpenAIClient(unittest.TestCase):  
    def setUp(self):  
        self.api_key = "test-key-123"  
        self.client = OpenAIClient(api_key=self.api_key)  
  
    @patch('openai.ChatCompletion.create')  
    def test_generate_summary(self, mock_create):  
        # Set up the mock to return a specific response  
        mock_response = MagicMock()  
        mock_response.choices = [MagicMock()]  
        mock_response.choices[0].message.content = "This is a test summary."  
        mock_create.return_value = mock_response  
  
        # Call the method  
        messages = [  
            {"body": "First test message"},  
            {"body": "Second test message"}  
        ]  
        summary = self.client.generate_summary(messages)  
  
        # Assert the result  
        self.assertEqual(summary, "This is a test summary.")  
  
        # Verify API was called with expected parameters  
        mock_create.assert_called_once()  
        args, kwargs = mock_create.call_args  
        self.assertEqual(kwargs["model"], "gpt-3.5-turbo")  
        self.assertIn("messages", kwargs)  
```  
  
## Test Database  
  
For integration tests that require a database, we use a separate test database:  
  
```python  
# database_config.py  
import os  
  
def get_connection_string():  
    """Return the appropriate database connection string based on environment"""  
    env = os.getenv('APP_ENV', 'development')  
  
    if env == 'test':  
        return os.getenv('TEST_DATABASE_URL', 'postgresql://user:pass@test-host/test_db')  
    elif env == 'production':  
        return os.getenv('DATABASE_URL')  
    else:  # development  
        return os.getenv('DEV_DATABASE_URL', 'postgresql://user:pass@localhost/dev_db')  
```  
  
## Running Tests  
  
### Running Unit Tests  
  
```bash  
# Run all unit tests  
python -m unittest discover tests/unit  
  
# Run a specific test file  
python -m unittest tests/unit/test_message_processor.py  
  
# Run a specific test case  
python -m unittest tests.unit.test_message_processor.TestMessageProcessor.test_process_new_message  
```  
  
### Running Integration Tests  
  
```bash  
# Set environment to test  
export APP_ENV=test  
  
# Run all integration tests  
python -m unittest discover tests/integration  
```  
  
## Test Best Practices  
  
1. **Write Tests First:** Follow test-driven development where possible, writing tests before implementing features.  
  
2. **Isolate Test Data:** Ensure tests don't depend on each other's data and can run independently.  
  
3. **Clean Up After Tests:** Always clean up any test data created during tests.  
  
4. **Mock External Dependencies:** Use mocking to isolate tests from external services like APIs.  
  
5. **Test Edge Cases:** Include tests for boundary conditions and error scenarios.  
  
6. **Maintain Test Coverage:** Aim for high test coverage, especially for critical paths.  
  
7. **Keep Tests Fast:** Optimize tests to run quickly to encourage frequent testing.  
  
8. **Use Descriptive Test Names:** Name tests clearly to describe what they're testing.  
  
## Continuous Integration  
  
Set up a CI pipeline to run tests automatically on every commit:  
  
1. **Automated Test Runs:** Configure CI to run all tests on each push.  
  
2. **Test Coverage Reports:** Generate and track test coverage metrics.  
  
3. **Linting and Style Checks:** Include code style verification in the pipeline.  
  
4. **Block Merges on Test Failures:** Prevent merging code that fails tests. 
