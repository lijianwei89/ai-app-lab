#!/usr/bin/env python3
"""
最简单的Dify chatflow测试
"""

import asyncio
import httpx
import json

async def test_simple_chatflow():
    api_key = "app-nxb7ZW4Uy9DZmeEMoE2ibTDY"
    base_url = "https://api.dify.ai"
    
    url = f"{base_url}/v1/chat-messages"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    # 简单的测试对话
    test_messages = [
        "你好",
        "我是谁",
        "刚才我们聊了什么"
    ]
    
    user_id = "test-user-simple"
    conversation_id = ""
    
    print("🧪 最简单的Dify chatflow测试")
    print("=" * 40)
    
    for i, message in enumerate(test_messages, 1):
        payload = {
            "query": message,
            "inputs": {"user_input": message},
            "response_mode": "blocking",
            "user": user_id,
            "conversation_id": conversation_id
        }
        
        print(f"\n第{i}轮：")
        print(f"用户：{message}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    ai_reply = result.get('answer', '无回复')
                    print(f"AI：{ai_reply}")
                    
                    # 保存conversation_id用于上下文
                    if not conversation_id and result.get('conversation_id'):
                        conversation_id = result['conversation_id']
                        print(f"会话ID：{conversation_id}")
                else:
                    print(f"❌ 错误：{response.status_code} - {response.text}")
                    
        except Exception as e:
            print(f"❌ 异常：{e}")
    
    print("\n" + "=" * 40)
    print("测试完成！")

if __name__ == "__main__":
    asyncio.run(test_simple_chatflow())