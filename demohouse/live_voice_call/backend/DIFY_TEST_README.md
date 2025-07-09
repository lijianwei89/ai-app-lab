# Dify API Integration Test Suite

This directory contains comprehensive test scripts for verifying the Dify API integration functionality.

## 📋 Overview

The test suite provides standalone testing for Dify API integration, independent from the main voice call system. It includes both streaming and blocking workflow tests with various scenarios.

## 🗂️ Files

- **`test_dify.py`** - Main comprehensive test suite
- **`run_dify_test.py`** - Quick test runner for specific scenarios
- **`dify_client.py`** - Dify API client implementation
- **`DIFY_TEST_README.md`** - This documentation

## ⚙️ Configuration

Before running tests, update the API configuration in `test_dify.py`:

```python
TEST_CONFIG = {
    "api_key": "your-actual-dify-api-key",  # Replace with your Dify API key
    "base_url": "https://api.dify.ai",       # Or your custom Dify instance
    "user_id": "test_user_001"               # Test user identifier
}
```

## 🚀 Running Tests

### Quick Tests

Use the quick test runner for specific test types:

```bash
# Test basic API connection
python run_dify_test.py connection

# Test streaming workflow
python run_dify_test.py streaming

# Test blocking workflow  
python run_dify_test.py blocking

# Run comprehensive test suite
python run_dify_test.py full

# Show help
python run_dify_test.py help
```

### Comprehensive Test Suite

Run the full test suite with all scenarios:

```bash
python test_dify.py
```

## 📊 Test Scenarios

The test suite includes the following scenarios:

### 1. Basic Conversation Test
Tests basic conversation with all LLM parameters:
- **Question**: "What is the capital of France?"
- **Answer**: "Paris"
- **Student**: "Alice"
- **Category**: "Geography"

### 2. Educational Scenario
Tests educational conversation flow:
- **Question**: "Explain photosynthesis"
- **Student**: "Bob"
- **Category**: "Biology"

### 3. Math Problem Test
Tests mathematical problem solving:
- **Question**: "Solve: 2x + 5 = 13"
- **Answer**: "x = 4"
- **Student**: "Carol"
- **Category**: "Mathematics"

### 4. Empty Parameters Test
Tests with minimal parameters to verify fallback behavior.

## 📈 Test Coverage

The test suite verifies:

✅ **API Connection** - Basic connectivity to Dify API  
✅ **Streaming Mode** - Real-time workflow execution  
✅ **Blocking Mode** - Standard API response  
✅ **Parameter Passing** - All LLM parameters in inputs  
✅ **Error Handling** - Proper exception handling  
✅ **Performance** - Response time measurements  
✅ **Data Structure** - Input/output format validation  

## 📋 Sample Test Data

Each test scenario includes:

```json
{
  "inputs": {
    "question": "What is the capital of France?",
    "answer": "Paris",
    "question_stem": "Geography question about European capitals",
    "student_name": "Alice",
    "question_category": "Geography",
    "user_input": "Tell me about the capital of France",
    "user_responds": "Tell me about the capital of France",
    "conversation_history": [
      {"role": "user", "content": "Hello"},
      {"role": "assistant", "content": "Hi there! How can I help you today?"}
    ]
  },
  "response_mode": "streaming",
  "user": "test_user_001"
}
```

## 📊 Test Output

### Console Output
The tests provide real-time console output showing:
- Test scenario details
- API request/response data
- Streaming chunks (for streaming tests)
- Performance metrics
- Success/failure status

### Example Output
```
🔄 Testing Streaming Mode: Basic Conversation Test
Description: Test basic conversation with LLM parameters
Inputs: {
  "question": "What is the capital of France?",
  "answer": "Paris",
  ...
}

📡 Starting streaming request...
📝 Chunk 1: The capital
📝 Chunk 2:  of France
📝 Chunk 3:  is Paris
📝 Chunk 4: , which is...

✅ Streaming test completed successfully!
⏱️  Execution time: 2.34 seconds
📊 Total chunks received: 15
📄 Complete response: The capital of France is Paris, which is...
```

### JSON Results File
Test results are automatically saved to `dify_test_results.json`:

```json
{
  "config": {
    "api_key": "app-***",
    "base_url": "https://api.dify.ai",
    "user_id": "test_user_001"
  },
  "summary": {
    "total_tests": 8,
    "successful_tests": 8,
    "failed_tests": 0,
    "success_rate": 100.0
  },
  "results": [...]
}
```

## 🛠️ Dependencies

The test scripts require:
- **Python 3.8+**
- **aiohttp** - For HTTP client functionality
- **asyncio** - For async/await support

Install dependencies:
```bash
pip install aiohttp
```

## 🔧 Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   ❌ Please update the API key in TEST_CONFIG before running!
   ```
   **Solution**: Update `TEST_CONFIG['api_key']` with your actual Dify API key.

2. **Connection Error**
   ```
   ❌ Connection failed: HTTP 401 Unauthorized
   ```
   **Solution**: Verify your API key is correct and has proper permissions.

3. **Timeout Error**
   ```
   ❌ Dify API error: Request timeout
   ```
   **Solution**: Check network connectivity and Dify service status.

### Debug Mode

For detailed debugging, modify the logging level in the test scripts:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Integration Notes

The test results help verify:

1. **Parameter Mapping** - All frontend parameters are correctly passed to Dify
2. **Streaming Performance** - Real-time response suitable for TTS
3. **Error Handling** - Graceful fallback mechanisms
4. **API Compliance** - Proper Dify API usage patterns

## 🎯 Next Steps

After successful testing:

1. Update `handler.py` with your actual Dify API key
2. Configure your Dify workflow to handle the input parameters
3. Test the full voice call integration
4. Monitor performance in production

## 📞 Integration with Voice Call System

The test validates the same API calls used in the voice call system:

**Voice Call Flow**: ASR → Dify API → TTS  
**Test Flow**: Test Data → Dify API → Validation

This ensures the API integration works correctly before deploying to the full system.