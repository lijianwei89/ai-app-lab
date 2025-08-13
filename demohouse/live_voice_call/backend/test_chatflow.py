#!/usr/bin/env python3
"""
测试新的Dify chatflow
"""

import asyncio
import httpx
import json

async def test_chatflow():
    api_key = "app-nxb7ZW4Uy9DZmeEMoE2ibTDY"
    base_url = "https://api.dify.ai"
    
    # 测试连续对话
    test_inputs = [
        {"user_input": "你好"},
        {"user_input": "请介绍一下一元二次方程"},
        {"user_input": "刚才我说了什么"},
    ]
    
    url = f"{base_url}/v1/chat-messages"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    # 使用相同的user_id来测试上下文记忆
    user_id = "test-user-consistent"
    
    for inputs in test_inputs:
        payload = {
            "query": inputs["user_input"],
            "inputs": inputs,
            "response_mode": "streaming",
            "user": user_id,
            "conversation_id": ""
        }
        
        print(f"\n🧪 测试输入: {inputs['user_input']}")
        print("-" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream('POST', url, headers=headers, json=payload) as response:
                    if response.status_code == 200:
                        full_response = ""
                        async for line in response.aiter_lines():
                            if line.startswith('data: '):
                                data = line[6:]
                                if data == '[DONE]':
                                    break
                                try:
                                    event_data = json.loads(data)
                                    if event_data.get('event') in ['message', 'agent_message']:
                                        text = event_data.get('answer', '')
                                        if text:
                                            full_response += text
                                except:
                                    continue
                        
                        print(f"✅ AI回复: {full_response}")
                    else:
                        print(f"❌ 错误: {response.status_code} - {await response.aread()}")
                        
        except Exception as e:
            print(f"❌ 异常: {e}")

if __name__ == "__main__":
    asyncio.run(test_chatflow())