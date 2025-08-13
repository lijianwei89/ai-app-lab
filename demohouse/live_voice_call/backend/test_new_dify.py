#!/usr/bin/env python3
"""
测试新的Dify工作流（仅user_input参数）
"""

import asyncio
import httpx
import json

async def test_new_dify_workflow():
    api_key = "app-xfFd1o2XZ4eNV0DRjPHGClrE"
    base_url = "https://api.dify.ai"
    
    # 测试普通对话
    test_inputs = [
        {"user_input": "你好"},
        {"user_input": "请介绍一下一元二次方程"},
        {"user_input": "小明问：什么是好朋友数"},
    ]
    
    url = f"{base_url}/v1/workflows/run"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    for inputs in test_inputs:
        payload = {
            "inputs": inputs,
            "response_mode": "streaming",
            "user": "test-user-123"
        }
        
        print(f"\n🧪 测试输入: {inputs}")
        print("-" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream('POST', url, headers=headers, json=payload) as response:
                    if response.status_code == 200:
                        full_response = ""
                        async for line in response.ait_lines():
                            line = line.decode('utf-8') if isinstance(line, bytes) else line
                            if line.startswith('data: '):
                                data = line[6:]
                                if data == '[DONE]':
                                    break
                                try:
                                    event_data = json.loads(data)
                                    if event_data.get('event') == 'text_chunk':
                                        full_response += event_data.get('data', '')
                                    elif event_data.get('event') == 'workflow_finished':
                                        outputs = event_data.get('data', {}).get('outputs', {})
                                        if 'pet_reply' in outputs:
                                            full_response = outputs['pet_reply']
                                except:
                                    continue
                        
                        print(f"✅ 响应: {full_response}")
                    else:
                        print(f"❌ 错误: {response.status_code} - {await response.aread()}")
                        
        except Exception as e:
            print(f"❌ 异常: {e}")

if __name__ == "__main__":
    asyncio.run(test_new_dify_workflow())