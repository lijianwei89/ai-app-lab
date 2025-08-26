#!/usr/bin/env python3
import asyncio
import httpx

API_KEY = "app-nxb7ZW4Uy9DZmeEMoE2ibTDY"
BASE_URL = "https://api.dify.ai"

async def test_s003_conversation():
    """测试S003会话的连贯性"""
    session_id = "S003"
    turns = [
        "有人跟我说作弊没关系。",
        "我觉得这样不太好。", 
        "如果他让我一起怎么办？"
    ]
    
    conversation_id = None
    
    for i, user_input in enumerate(turns, 1):
        print(f"🗣️ 第{i}轮: {user_input}")
        
        payload = {
            "query": user_input,
            "inputs": {"user_input": user_input},
            "response_mode": "blocking",
            "user": session_id
        }
        
        if conversation_id and i > 1:
            payload["conversation_id"] = conversation_id
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{BASE_URL}/v1/chat-messages",
                    headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'},
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get('answer', '').strip()
                    print(f"🤖 回复: {answer}")
                    
                    if i == 1:
                        conversation_id = data.get('conversation_id', '')
                        print(f"📱 对话ID: {conversation_id}")
                else:
                    print(f"❌ 错误: {response.status_code} - {response.text}")
                    break
                    
        except Exception as e:
            print(f"💥 异常: {e}")
            break
        
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_s003_conversation())