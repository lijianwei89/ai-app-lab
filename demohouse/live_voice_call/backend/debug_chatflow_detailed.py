#!/usr/bin/env python3
"""
详细测试chatflow API并显示完整日志
"""

import asyncio
import httpx
import json
import time

async def test_chatflow_detailed():
    api_key = "app-nxb7ZW4Uy9DZmeEMoE2ibTDY"
    base_url = "https://api.dify.ai"
    
    url = f"{base_url}/v1/chat-messages"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    test_inputs = [
        "你是谁",
        "？",
        "你好"
    ]
    
    user_id = "debug-user"
    conversation_id = ""
    
    print("🔍 详细Chatflow API测试")
    print("=" * 50)
    
    for message in test_inputs:
        print(f"\n📤 发送: '{message}'")
        print(f"⏰ 时间: {time.strftime('%H:%M:%S')}")
        
        payload = {
            "query": message,
            "inputs": {"user_input": message},
            "response_mode": "blocking",
            "user": user_id,
            "conversation_id": conversation_id
        }
        
        print(f"📝 完整参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                print(f"📊 状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"📥 完整回复: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    print(f"💬 AI回复: {result.get('answer', '无回复')}")
                    
                    if not conversation_id:
                        conversation_id = result.get('conversation_id', '')
                        print(f"🆔 会话ID: {conversation_id}")
                else:
                    print(f"❌ 错误详情: {response.text}")
                    
        except Exception as e:
            print(f"💥 异常: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_chatflow_detailed())