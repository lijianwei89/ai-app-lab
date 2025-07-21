#!/usr/bin/env python3
"""
Test script for opening generation with real Dify API calls.
"""
import asyncio
import json
import httpx
from typing import Dict, Any, Optional


class DifyOpeningClient:
    """
    Simplified Dify client for testing opening generation.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
    
    async def test_opening_generation(
        self,
        question: str,
        student_name: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Test opening generation with Dify API.
        """
        url = f"{self.base_url}/v1/workflows/run"
        
        # Prepare request payload for opening generation
        payload = {
            "inputs": {
                "question": question,
                "student_name": student_name,
            },
            "response_mode": "streaming",
            "user": user_id or f"opening-test-{student_name}"
        }
        
        print(f"🚀 Testing Dify opening generation...")
        print(f"📋 URL: {url}")
        print(f"📋 API Key: {self.api_key}")
        print(f"📋 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        print("-" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    'POST',
                    url,
                    headers=self.headers,
                    json=payload
                ) as response:
                    print(f"📊 Response Status: {response.status_code}")
                    print(f"📊 Response Headers: {dict(response.headers)}")
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        print(f"❌ Dify API error: {response.status_code}")
                        print(f"❌ Error content: {error_text.decode()}")
                        return ""
                    
                    print("📡 Streaming response:")
                    buffer = ""
                    full_response = ""
                    
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
                                    print("✅ Stream completed")
                                    return full_response
                                if data:
                                    try:
                                        event_data = json.loads(data)
                                        print(f"📨 Event: {json.dumps(event_data, indent=2, ensure_ascii=False)}")
                                        
                                        # Handle different event types
                                        if event_data.get('event') == 'text_chunk':
                                            if 'data' in event_data:
                                                text = event_data['data'].get('text', '')
                                                if text:
                                                    print(f"📝 Text chunk: {text}")
                                                    full_response += text
                                        elif event_data.get('event') == 'workflow_finished':
                                            if 'data' in event_data and 'outputs' in event_data['data']:
                                                outputs = event_data['data']['outputs']
                                                print(f"🏁 Workflow outputs: {json.dumps(outputs, indent=2, ensure_ascii=False)}")
                                                # Prioritize 'result' field
                                                if 'result' in outputs and isinstance(outputs['result'], str) and outputs['result'].strip():
                                                    final_result = outputs['result']
                                                    print(f"✅ Final result: {final_result}")
                                                    return final_result
                                                else:
                                                    # Fallback to other fields
                                                    for key, value in outputs.items():
                                                        if isinstance(value, str) and value.strip():
                                                            print(f"✅ Fallback result ({key}): {value}")
                                                            return value
                                        elif event_data.get('event') == 'node_finished':
                                            if 'data' in event_data and 'outputs' in event_data['data']:
                                                outputs = event_data['data']['outputs']
                                                print(f"🔧 Node outputs: {json.dumps(outputs, indent=2, ensure_ascii=False)}")
                                                
                                                # Extract text from LLM node if available
                                                if 'text' in outputs and isinstance(outputs['text'], str) and outputs['text'].strip():
                                                    # Clean up the text (remove thinking tags if present)
                                                    text = outputs['text']
                                                    # Remove <think>...</think> tags
                                                    import re
                                                    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
                                                    if text:
                                                        print(f"🎤 Extracted opening text: {text}")
                                                        full_response = text  # Store as potential result
                                        elif event_data.get('event') == 'error':
                                            error_msg = event_data.get('message', 'Unknown error')
                                            print(f"❌ Dify workflow error: {error_msg}")
                                            return ""
                                            
                                    except json.JSONDecodeError as e:
                                        print(f"⚠️ Failed to parse event: {e}")
                                        print(f"⚠️ Raw data: {data}")
                                        continue
                    
                    return full_response
                        
        except Exception as e:
            print(f"💥 Request failed: {str(e)}")
            return ""


async def test_multiple_scenarios():
    """Test opening generation with multiple scenarios."""
    
    # Use the updated Dify configuration
    api_key = "app-rCIokTn1NixIujuo4M18feAW"
    base_url = "https://api.dify.ai"
    
    client = DifyOpeningClient(api_key, base_url)
    
    # Test scenarios
    test_cases = [
        {
            "question": "解一元二次方程",
            "student_name": "小明",
            "description": "数学问题 - 小明"
        },
        {
            "question": "学习英语语法",
            "student_name": "小红",
            "description": "英语学习 - 小红"
        },
        {
            "question": "物理力学基础",
            "student_name": "小华",
            "description": "物理学习 - 小华"
        }
    ]
    
    print("🧪 开始测试开场白Dify调用...")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试用例 {i}: {test_case['description']}")
        print("=" * 40)
        
        result = await client.test_opening_generation(
            question=test_case["question"],
            student_name=test_case["student_name"]
        )
        
        if result:
            print(f"✅ 开场白生成成功:")
            print(f"🎤 内容: {result}")
        else:
            print(f"❌ 开场白生成失败")
        
        print("-" * 40)
        
        # Wait a bit between requests
        await asyncio.sleep(1)
    
    print("\n🎉 测试完成!")


async def test_single_case():
    """Test a single opening generation case."""
    api_key = "app-rCIokTn1NixIujuo4M18feAW"
    base_url = "https://api.dify.ai"
    
    client = DifyOpeningClient(api_key, base_url)
    
    print("🧪 单一测试用例：数学学习场景")
    print("=" * 40)
    
    result = await client.test_opening_generation(
        question="解一元二次方程",
        student_name="小明"
    )
    
    if result:
        print(f"✅ 测试成功!")
        print(f"🎤 生成的开场白: {result}")
        print(f"📏 文本长度: {len(result)} 字符")
    else:
        print(f"❌ 测试失败")
        print("请检查:")
        print("1. Dify API密钥是否正确")
        print("2. 工作流是否已配置")
        print("3. 网络连接是否正常")
        print("4. 输入参数是否符合工作流要求")


if __name__ == "__main__":
    # 直接运行单一测试用例
    asyncio.run(test_single_case())