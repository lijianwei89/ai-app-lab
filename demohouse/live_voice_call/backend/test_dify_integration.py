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

import asyncio
import json
from dify_client import DifyClient

async def test_dify_integration():
    """
    Test the Dify API integration.
    """
    # Initialize Dify client
    client = DifyClient(
        api_key="app-JqtJdpgiEKukUAxxT8oiJR4u",
        base_url="https://api.dify.ai"
    )
    
    # Test inputs with all required parameters
    test_inputs = {
        "question": "什么是Python?",
        "answer": "Python是一种编程语言",
        "user_responds": "我想学习Python编程", 
        "question_stem": "编程语言基础",
        "student_name": "张三",
        "question_category": "编程学习"
    }
    
    print("Testing Dify API integration...")
    print(f"Inputs: {json.dumps(test_inputs, ensure_ascii=False, indent=2)}")
    print("\nStreaming response:")
    print("-" * 50)
    
    try:
        response_buffer = ""
        async for chunk in client.stream_workflow_run(
            inputs=test_inputs,
            user_id="test-user-123"
        ):
            if chunk:
                print(chunk, end="", flush=True)
                response_buffer += chunk
        
        print("\n" + "-" * 50)
        print(f"Complete response: {response_buffer}")
        print("✓ Dify integration test completed successfully")
        
    except Exception as e:
        print(f"✗ Dify integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_dify_integration())