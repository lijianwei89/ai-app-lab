# Dify API Integration

This document describes the Dify API integration for the live voice call system.

## Overview

The system now supports both ARK and Dify as LLM providers. When using Dify, the system will call the Dify workflow API with all user parameters collected from the frontend.

## Configuration

### Environment Variables

Update the following variables in `handler.py`:

```python
# LLM Provider Configuration
LLM_PROVIDER = "dify"  # or "ark"
DIFY_API_KEY = "app-JqtJdpgiEKukUAxxT8oiJR4u"
DIFY_BASE_URL = "https://api.dify.ai"
```

### User Parameters

The system automatically collects and sends the following parameters to Dify:

- `question`: The question text
- `answer`: The answer text  
- `user_responds`: ASR recognition result (user's spoken response)
- `question_stem`: The question stem
- `student_name`: Student's name
- `question_category`: Question category

## API Flow

1. **Frontend**: User fills in parameters and speaks
2. **ASR**: Converts speech to text (`user_responds`)
3. **Backend**: Collects all parameters and sends to Dify
4. **Dify**: Processes workflow with all inputs
5. **TTS**: Converts Dify response to speech
6. **Frontend**: Plays audio response

## Dify Workflow Configuration

Your Dify workflow should expect the following input variables:

```json
{
  "question": "string",
  "answer": "string", 
  "user_responds": "string",
  "question_stem": "string",
  "student_name": "string",
  "question_category": "string"
}
```

## Testing

Run the integration test:

```bash
cd backend
python test_dify_integration.py
```

## Error Handling

- If Dify API fails, the system will return a fallback error message
- All API errors are logged for debugging
- The system maintains conversation history for context

## Dependencies

The integration requires the following Python packages:

```toml
httpx = "^0.27.0"
pydantic = "^2.0.0"
```

## Switching Between Providers

To switch between ARK and Dify:

1. Update `LLM_PROVIDER` in `handler.py`
2. Restart the backend service
3. The system will automatically use the selected provider

## Troubleshooting

### Common Issues

1. **Dify API Key Issues**: Ensure your API key is valid and has proper permissions
2. **Network Connectivity**: Check if you can reach the Dify API endpoint
3. **Workflow Configuration**: Verify your Dify workflow accepts all required input variables
4. **Parameter Mapping**: Ensure frontend parameters match expected workflow inputs

### Debugging

- Check backend logs for detailed error messages
- Use the test script to verify Dify API connectivity
- Monitor network requests to identify API issues