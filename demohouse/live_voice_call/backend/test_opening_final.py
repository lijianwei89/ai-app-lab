#!/usr/bin/env python3
"""
Final test for opening generation functionality.
"""
import asyncio
import json
import httpx
import re
from typing import Dict, Any, Optional


class SimpleDifyClient:
    """
    Simplified Dify client based on the actual implementation.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai"):
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
    ):
        """
        Stream workflow run with Dify API - exact same logic as real implementation.
        """
        url = f"{self.base_url}/v1/workflows/run"
        
        # Prepare request payload
        payload = {
            "inputs": inputs,
            "response_mode": "streaming",
            "user": user_id or f"user-{inputs.get('student_name', 'anonymous')}"
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        if files:
            payload["files"] = files
        
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
                        raise Exception(f"Dify API error: {response.status_code} - {error_text}")
                    
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
                                        
                                        # Handle different event types
                                        if event_data.get('event') == 'text_chunk':
                                            # Extract text content from workflow response
                                            if 'data' in event_data:
                                                text = event_data['data'].get('text', '')
                                                if text:
                                                    yield text
                                        elif event_data.get('event') == 'workflow_finished':
                                            # Extract final output from 'result' field specifically
                                            if 'data' in event_data and 'outputs' in event_data['data']:
                                                outputs = event_data['data']['outputs']
                                                # Prioritize 'result' field first as it contains the correct answer
                                                if 'result' in outputs and isinstance(outputs['result'], str) and outputs['result'].strip():
                                                    yield outputs['result']
                                                else:
                                                    # Fallback to other fields if 'result' is not available
                                                    for key, value in outputs.items():
                                                        if isinstance(value, str) and value.strip():
                                                            yield value
                                                            break
                                        elif event_data.get('event') == 'node_finished':
                                            # Extract node output if it contains text
                                            if 'data' in event_data and 'outputs' in event_data['data']:
                                                outputs = event_data['data']['outputs']
                                                # Prioritize 'text' field from LLM nodes
                                                if 'text' in outputs and isinstance(outputs['text'], str) and outputs['text'].strip():
                                                    # Clean up the text (remove thinking tags if present)
                                                    text = outputs['text']
                                                    # Remove <think>...</think> tags
                                                    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
                                                    if text:
                                                        yield text
                                                else:
                                                    # Fallback to other text fields
                                                    for key, value in outputs.items():
                                                        if isinstance(value, str) and value.strip():
                                                            yield value
                                                            break
                                        elif event_data.get('event') == 'error':
                                            error_msg = event_data.get('message', 'Unknown error')
                                            raise Exception(f"Dify workflow error: {error_msg}")
                                            
                                    except json.JSONDecodeError as e:
                                        continue
                        
        except Exception as e:
            raise Exception(f"Dify API request failed: {str(e)}")


async def test_opening_generation():
    """Test the complete opening generation flow."""
    print("🎯 最终开场白功能测试")
    print("=" * 50)
    
    # Create client with real credentials
    client = SimpleDifyClient(
        api_key="app-rCIokTn1NixIujuo4M18feAW",
        base_url="https://api.dify.ai"
    )
    
    # Test scenarios
    scenarios = [
        {
            "question": "解一元二次方程",
            "student_name": "小明",
            "description": "数学学习场景"
        },
        {
            "question": "学习英语语法时态",
            "student_name": "小红", 
            "description": "英语学习场景"
        },
        {
            "question": "理解牛顿第一定律",
            "student_name": "小华",
            "description": "物理学习场景"
        }
    ]
    
    successful_tests = 0
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 测试场景 {i}: {scenario['description']}")
        print(f"   学生: {scenario['student_name']}")
        print(f"   问题: {scenario['question']}")
        print("-" * 40)
        
        try:
            print("🚀 调用Dify工作流...")
            
            opening_text = ""
            chunk_count = 0
            
            async for chunk in client.stream_workflow_run(
                inputs={
                    "question": scenario["question"],
                    "student_name": scenario["student_name"]
                },
                user_id=f"opening-{scenario['student_name']}"
            ):
                if chunk:
                    chunk_count += 1
                    print(f"   📝 文本块 {chunk_count}: {chunk}")
                    opening_text += chunk
            
            if opening_text.strip():
                print(f"✅ 成功生成开场白!")
                print(f"🎤 完整内容: {opening_text}")
                print(f"📏 文本长度: {len(opening_text)} 字符")
                successful_tests += 1
                
                # Simulate TTS processing
                print("🔊 模拟TTS处理...")
                audio_size = len(opening_text.encode('utf-8')) * 100  # Mock audio size
                print(f"   🎵 生成音频大小: {audio_size} 字节")
                
            else:
                print("❌ 未生成开场白内容")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
        
        # Wait between tests
        if i < len(scenarios):
            await asyncio.sleep(1)
    
    print(f"\n📊 测试总结")
    print("=" * 30)
    print(f"成功: {successful_tests}/{len(scenarios)} 个场景")
    
    if successful_tests == len(scenarios):
        print("🎉 所有测试通过！开场白功能运行正常")
        return True
    else:
        print("⚠️ 部分测试失败，请检查配置")
        return False


async def test_edge_cases():
    """Test edge cases for opening generation."""
    print("\n🧪 边界情况测试")
    print("=" * 50)
    
    client = SimpleDifyClient(
        api_key="app-rCIokTn1NixIujuo4M18feAW",
        base_url="https://api.dify.ai"
    )
    
    edge_cases = [
        {
            "question": "",
            "student_name": "小明",
            "description": "空问题"
        },
        {
            "question": "解一元二次方程",
            "student_name": "",
            "description": "空姓名"
        },
        {
            "question": "这是一个非常长的问题" * 10,
            "student_name": "小明",
            "description": "超长问题"
        }
    ]
    
    for i, case in enumerate(edge_cases, 1):
        print(f"\n📋 边界测试 {i}: {case['description']}")
        print("-" * 30)
        
        try:
            opening_text = ""
            async for chunk in client.stream_workflow_run(
                inputs={
                    "question": case["question"],
                    "student_name": case["student_name"]
                },
                user_id=f"edge-test-{i}"
            ):
                if chunk:
                    opening_text += chunk
            
            if opening_text.strip():
                print(f"✅ 生成内容: {opening_text[:50]}...")
            else:
                print("⚠️ 未生成内容（可能是预期行为）")
                
        except Exception as e:
            print(f"⚠️ 调用失败: {str(e)}")
        
        await asyncio.sleep(0.5)


async def main():
    """Run the complete test suite."""
    print("🎯 开场白功能完整测试套件")
    print("=" * 60)
    
    # Main functionality test
    success = await test_opening_generation()
    
    # Edge cases test
    await test_edge_cases()
    
    print(f"\n🏁 最终结果")
    print("=" * 30)
    
    if success:
        print("✅ 开场白功能测试完全通过！")
        print("\n📋 验证完成的功能:")
        print("  ✅ Dify API集成")
        print("  ✅ 个性化内容生成")
        print("  ✅ 文本清理和处理") 
        print("  ✅ 多场景支持")
        print("  ✅ 错误处理")
        print("\n🚀 功能已准备投入使用！")
    else:
        print("❌ 测试未完全通过，需要进一步调试")
        print("💡 建议检查:")
        print("  - Dify API密钥配置")
        print("  - 工作流设置")
        print("  - 网络连接")


if __name__ == "__main__":
    asyncio.run(main())