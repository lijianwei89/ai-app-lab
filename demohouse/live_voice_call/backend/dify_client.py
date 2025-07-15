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
        Stream workflow run with Dify API.
        
        This method supports both regular conversation workflows and opening generation workflows.
        For opening generation, the inputs should contain 'question' and 'student_name'.
        
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
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    'POST',
                    url,
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        ERROR(f"Dify API error: {response.status_code} - {error_text}")
                        raise Exception(f"Dify API error: {response.status_code}")
                    
                    buffer = ""
                    llm_output = None  # Store LLM node output as fallback
                    
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
                                    # If we reach the end and have stored LLM output but no final result, yield it
                                    if llm_output:
                                        yield llm_output
                                    return
                                if data:
                                    try:
                                        event_data = json.loads(data)
                                        INFO(f"Dify streaming event: {event_data}")
                                        
                                        # Handle different event types
                                        if event_data.get('event') == 'text_chunk':
                                            # Extract text content from workflow response (for streaming workflows)
                                            if 'data' in event_data:
                                                text = event_data['data'].get('text', '')
                                                if text:
                                                    yield text
                                        elif event_data.get('event') == 'workflow_finished':
                                            # Extract final output from 'result' field specifically (non-streaming)
                                            if 'data' in event_data and 'outputs' in event_data['data']:
                                                outputs = event_data['data']['outputs']
                                                # Prioritize 'result' field first as it contains the correct answer
                                                if 'result' in outputs and isinstance(outputs['result'], str) and outputs['result'].strip():
                                                    yield outputs['result']
                                                    return  # Exit after getting the final result
                                                else:
                                                    # Check for other output fields in workflow_finished
                                                    for key, value in outputs.items():
                                                        if isinstance(value, str) and value.strip():
                                                            yield value
                                                            return  # Exit after getting any result
                                            
                                            # If workflow_finished has no valid outputs, use stored LLM output
                                            if llm_output:
                                                yield llm_output
                                                return
                                                
                                        elif event_data.get('event') == 'node_finished':
                                            # Extract node output if it contains text (as intermediate processing)
                                            if 'data' in event_data and 'outputs' in event_data['data']:
                                                outputs = event_data['data']['outputs']
                                                # Check if this is an LLM node with text output
                                                node_data = event_data.get('data', {})
                                                node_type = node_data.get('node_type', '')
                                                
                                                if node_type == 'llm' and 'text' in outputs and isinstance(outputs['text'], str) and outputs['text'].strip():
                                                    # Clean up the text (remove thinking tags if present)
                                                    import re
                                                    text = outputs['text']
                                                    # Remove <think>...</think> tags
                                                    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
                                                    if text:
                                                        # Store as potential result for use if workflow_finished is empty
                                                        llm_output = text
                                                        INFO(f"Stored LLM output as fallback: {text}")
                                                        
                                        elif event_data.get('event') == 'error':
                                            error_msg = event_data.get('message', 'Unknown error')
                                            ERROR(f"Dify workflow error: {error_msg}")
                                            raise Exception(f"Dify workflow error: {error_msg}")
                                            
                                    except json.JSONDecodeError as e:
                                        ERROR(f"Failed to parse Dify response: {e}")
                                        continue
                        
        except Exception as e:
            ERROR(f"Dify API request failed: {str(e)}")
            raise