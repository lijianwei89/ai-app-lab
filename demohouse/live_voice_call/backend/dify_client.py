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

import httpx
from pydantic import BaseModel
from arkitect.telemetry.logger import INFO, ERROR


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
        Stream chat with Dify chatflow (previously workflow).
        
        Args:
            inputs (Dict[str, Any]): Input variables
            user_id (Optional[str]): User ID for context continuity
            conversation_id (Optional[str]): Conversation ID for context
            files (Optional[list]): File attachments
            
        Yields:
            str: Streaming response content
        """
        url = f"{self.base_url}/v1/chat-messages"
        
        # Prepare request payload for chatflow
        payload = {
            "query": inputs.get("user_input", ""),
            "inputs": inputs,
            "response_mode": "blocking",
            "user": user_id or f"user-{uuid.uuid4().hex[:8]}"
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        if files:
            payload["files"] = files
            
        INFO(f"Dify Chatflow API request: {url}")
        INFO(f"Dify Chatflow API payload: {json.dumps(payload, indent=2)}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if payload.get("response_mode") == "blocking":
                    # Handle blocking mode response
                    response = await client.post(url, headers=self.headers, json=payload)
                    if response.status_code != 200:
                        error_text = await response.aread()
                        ERROR(f"Dify Chatflow API error: {response.status_code} - {error_text}")
                        raise Exception(f"Dify Chatflow API error: {response.status_code}")
                    
                    result = response.json()
                    text_content = result.get('answer', '')
                    if text_content:
                        yield text_content
                else:
                    # Handle streaming mode (original logic)
                    async with client.stream(
                        'POST',
                        url,
                        headers=self.headers,
                        json=payload
                    ) as response:
                        if response.status_code != 200:
                            error_text = await response.aread()
                            ERROR(f"Dify Chatflow API error: {response.status_code} - {error_text}")
                            raise Exception(f"Dify Chatflow API error: {response.status_code}")
                        
                        buffer = ""
                        async for chunk in response.aiter_text():
                            buffer += chunk
                            # Process Server-Sent Events format
                            lines = buffer.split('\n')
                            buffer = lines[-1]  # Keep incomplete line in buffer
                            
                            for line in lines[:-1]:
                                line = line.strip()
                                if line.startswith('data: '):
                                    data = line[6:]  # Remove 'data: ' prefix
                                    if data == '[DONE]':
                                        return
                                    if data:
                                        try:
                                            event_data = json.loads(data)
                                            INFO(f"Dify chatflow streaming event: {event_data}")
                                            
                                            # Handle chatflow event types
                                            event_type = event_data.get('event')
                                            if event_type in ['message', 'agent_message']:
                                                text_content = event_data.get('answer', '')
                                                if text_content:
                                                    yield text_content
                                            elif event_type == 'error':
                                                error_msg = event_data.get('message', 'Unknown error')
                                                ERROR(f"Dify chatflow error: {error_msg}")
                                                raise Exception(f"Dify chatflow error: {error_msg}")
                                                
                                        except json.JSONDecodeError as e:
                                            ERROR(f"Failed to parse Dify chatflow response: {e}")
                                            continue
        except Exception as e:
            ERROR(f"Dify Chatflow API request failed: {str(e)}")
            raise