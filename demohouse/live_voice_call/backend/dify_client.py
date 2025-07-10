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

import json
import uuid
from typing import AsyncIterable, Dict, Any, Optional

import aiohttp
from pydantic import BaseModel

# 兼容性日志函数
try:
    from arkitect.telemetry.logger import INFO, ERROR
except ImportError:
    def INFO(msg):
        print(f"[INFO] {msg}")

    def ERROR(msg):
        print(f"[ERROR] {msg}")


class DifyClient:
    """
    Dify API client for workflow execution.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai"):
        """
        Initialize Dify client.
        
        Args:
            api_key (str): Dify API key
            base_url (str): Dify API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
    
    async def stream_workflow_run(
        self,
        inputs: Dict[str, Any],
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        files: Optional[list] = None
    ) -> AsyncIterable[str]:
        """
        Stream workflow run with Dify API.
        
        Args:
            inputs (Dict[str, Any]): Input variables for the workflow
            user_id (Optional[str]): User ID for the request
            conversation_id (Optional[str]): Conversation ID for context
            files (Optional[list]): File attachments
            
        Yields:
            str: Streaming response content
        """
        url = f"{self.base_url}/v1/workflows/run"
        
        # Prepare request payload
        payload = {
            "inputs": inputs,
            "response_mode": "streaming",
            "user": user_id or f"user-{uuid.uuid4().hex[:8]}"
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        if files:
            payload["files"] = files
            
        INFO(f"Dify API request: {url}")
        INFO(f"Dify API payload: {json.dumps(payload, indent=2)}")
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        ERROR(f"Dify API error: {response.status} - {error_text}")
                        raise Exception(f"Dify API error: {response.status}")
                    
                    # Process Server-Sent Events format like in direct_dify_test
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        
                        if not line:
                            continue
                        
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                event_type = data.get('event', '')
                                INFO(f"Dify streaming event: {event_type}")
                                
                                # Handle different event types (based on successful test)
                                if event_type == 'text_chunk':
                                    text = data.get('data', {}).get('text', '')
                                    if text:
                                        yield text
                                elif event_type == 'workflow_finished':
                                    # Extract final result like in direct_dify_test
                                    outputs = data.get('data', {}).get('outputs', {})
                                    final_result = outputs.get('result', '')
                                    if final_result:
                                        yield final_result
                                    break
                                elif event_type == 'node_finished':
                                    # Check for text outputs in node completion
                                    node_data = data.get('data', {})
                                    outputs = node_data.get('outputs', {})
                                    if 'text' in outputs and outputs['text']:
                                        yield outputs['text']
                                elif event_type == 'error':
                                    error_msg = data.get('data', {}).get('message', 'Unknown error')
                                    ERROR(f"Dify workflow error: {error_msg}")
                                    raise Exception(f"Dify workflow error: {error_msg}")
                                        
                            except json.JSONDecodeError as e:
                                ERROR(f"Failed to parse Dify response: {e}")
                                continue
                        
        except Exception as e:
            ERROR(f"Dify API request failed: {str(e)}")
            raise