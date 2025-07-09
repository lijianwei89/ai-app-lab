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
import logging
from typing import AsyncIterable, Dict, Any, Optional
import aiohttp
import uuid

from arkitect.telemetry.logger import INFO

class DifyClient:
    """
    Dify API client for workflow execution with streaming support.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai"):
        """
        Initialize Dify client.
        
        Args:
            api_key (str): Dify API key (Bearer token)
            base_url (str): Dify API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self.session
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def stream_workflow(
        self, 
        inputs: Dict[str, Any],
        user_id: str = None,
        files: Optional[list] = None
    ) -> str:
        """
        Execute a Dify workflow and return the final result.
        
        Args:
            inputs (Dict[str, Any]): Input parameters for the workflow
            user_id (str, optional): User identifier. Defaults to generated UUID.
            files (list, optional): File inputs for the workflow
            
        Returns:
            str: Final result content from workflow execution
        """
        if user_id is None:
            user_id = str(uuid.uuid4())
            
        session = await self._get_session()
        
        # Prepare the request payload
        payload = {
            "inputs": inputs,
            "response_mode": "streaming",
            "user": user_id
        }
        
        # Add files if provided
        if files:
            payload["files"] = files
            
        INFO(f"Dify API request: {json.dumps(payload, indent=2)}")
        
        try:
            async with session.post(
                f"{self.base_url}/v1/workflows/run",
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Dify API error {response.status}: {error_text}")
                
                INFO("Dify API streaming response started")
                
                # Process streaming response and wait for final result
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if not line:
                        continue
                        
                    # Handle Server-Sent Events format
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])  # Remove 'data: ' prefix
                            
                            # Handle different event types
                            event_type = data.get('event', '')
                            
                            if event_type == 'workflow_finished':
                                INFO("Dify workflow finished")
                                # Extract result from workflow outputs
                                outputs = data.get('data', {}).get('outputs', {})
                                result = outputs.get('result', '')
                                INFO(f"Dify workflow result: {result}")
                                return result
                                
                            elif event_type == 'error':
                                error_msg = data.get('data', {}).get('message', 'Unknown error')
                                raise Exception(f"Dify workflow error: {error_msg}")
                                
                        except json.JSONDecodeError:
                            # Skip invalid JSON lines
                            continue
                
                # If we reach here, workflow didn't finish properly
                raise Exception("Dify workflow did not complete successfully")
                            
        except Exception as e:
            logging.error(f"Dify API error: {str(e)}")
            raise
    
    async def run_workflow(
        self, 
        inputs: Dict[str, Any],
        user_id: str = None,
        files: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Execute a Dify workflow with blocking response.
        
        Args:
            inputs (Dict[str, Any]): Input parameters for the workflow
            user_id (str, optional): User identifier. Defaults to generated UUID.
            files (list, optional): File inputs for the workflow
            
        Returns:
            Dict[str, Any]: Complete workflow execution result
        """
        if user_id is None:
            user_id = str(uuid.uuid4())
            
        session = await self._get_session()
        
        # Prepare the request payload
        payload = {
            "inputs": inputs,
            "response_mode": "blocking",
            "user": user_id
        }
        
        # Add files if provided
        if files:
            payload["files"] = files
            
        INFO(f"Dify API blocking request: {json.dumps(payload, indent=2)}")
        
        try:
            async with session.post(
                f"{self.base_url}/v1/workflows/run",
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Dify API error {response.status}: {error_text}")
                
                result = await response.json()
                INFO(f"Dify API blocking response: {json.dumps(result, indent=2)}")
                
                return result
                
        except Exception as e:
            logging.error(f"Dify API error: {str(e)}")
            raise
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        if self.session and not self.session.closed:
            # Note: This is not ideal for async cleanup, but provides a fallback
            pass