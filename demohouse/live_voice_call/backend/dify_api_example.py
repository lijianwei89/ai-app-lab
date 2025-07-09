#!/usr/bin/env python3
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# Licensed under the 【火山方舟】原型应用软件自用许可协议
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at 
#     https://www.volcengine.com/docs/82379/1433703
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License. 

"""
Simple example demonstrating exact Dify API call structure.
This shows the raw HTTP request equivalent to what the DifyClient sends.
"""

import json
import asyncio
import aiohttp


async def example_dify_api_call():
    """
    Example of direct Dify API call matching the curl command from requirements.
    """
    
    # Configuration
    API_KEY = "app-JqtJdpgiEKukUAxxT8oiJR4u"  # Replace with your actual API key
    BASE_URL = "https://api.dify.ai"
    
    # Example payload matching voice call system parameters
    payload = {
        "inputs": {
            # LLM parameters from frontend
            "question": "What is the capital of France?",
            "answer": "Paris",
            "question_stem": "Geography question about European capitals",
            "student_name": "Alice",
            "question_category": "Geography",
            
            # Runtime parameters
            "user_input": "Tell me about the capital of France",
            "user_responds": "Tell me about the capital of France",  # From ASR
            
            # Conversation context
            "conversation_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there! How can I help you today?"}
            ]
        },
        "response_mode": "streaming",
        "user": "voice_chat_user_001"
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Dify API Call Example")
    print("=" * 50)
    
    print("\n📋 Request Details:")
    print(f"URL: {BASE_URL}/v1/workflows/run")
    print(f"Method: POST")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    print("\n📡 Equivalent curl command:")
    print(f"""curl -X POST '{BASE_URL}/v1/workflows/run' \\
--header 'Authorization: Bearer {API_KEY}' \\
--header 'Content-Type: application/json' \\
--data-raw '{json.dumps(payload)}'""")
    
    if API_KEY == "app-JqtJdpgiEKukUAxxT8oiJR4u":
        print("\n⚠️  Note: Update API_KEY with your actual Dify API key to test the call")
        return
    
    print("\n🔄 Making actual API call...")
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(
                f"{BASE_URL}/v1/workflows/run",
                json=payload
            ) as response:
                
                print(f"📊 Response Status: {response.status}")
                print(f"📋 Response Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    print("\n✅ API call successful!")
                    print("📄 Streaming response:")
                    
                    chunk_count = 0
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                chunk_count += 1
                                print(f"Chunk {chunk_count}: {json.dumps(data, indent=2)}")
                            except json.JSONDecodeError:
                                continue
                else:
                    error_text = await response.text()
                    print(f"❌ API call failed: {error_text}")
                    
    except Exception as e:
        print(f"❌ Request error: {str(e)}")


def show_parameter_mapping():
    """Show how voice call parameters map to Dify inputs."""
    
    print("\n🔗 Parameter Mapping: Voice Call → Dify API")
    print("=" * 60)
    
    mapping = {
        "Frontend Input Fields": "Dify API inputs",
        "question": "inputs.question",
        "answer": "inputs.answer", 
        "question_stem": "inputs.question_stem",
        "student_name": "inputs.student_name",
        "question_category": "inputs.question_category",
        "ASR Result": "inputs.user_responds",
        "Current Input": "inputs.user_input",
        "Chat History": "inputs.conversation_history"
    }
    
    for source, target in mapping.items():
        print(f"  {source:<20} → {target}")
    
    print(f"\n📋 Complete Dify inputs structure:")
    example_inputs = {
        "question": "from frontend form",
        "answer": "from frontend form",
        "question_stem": "from frontend form", 
        "student_name": "from frontend form",
        "question_category": "from frontend form",
        "user_input": "current ASR result",
        "user_responds": "same as user_input",
        "conversation_history": "array of message objects"
    }
    
    print(json.dumps(example_inputs, indent=2))


if __name__ == "__main__":
    print("🎯 Dify API Integration Example")
    
    # Show parameter mapping
    show_parameter_mapping()
    
    # Run API call example
    asyncio.run(example_dify_api_call())