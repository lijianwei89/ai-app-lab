#!/usr/bin/env python3
"""
Dify 400错误调试工具
用于查看具体的错误信息
"""

import httpx
import json
import asyncio

async def debug_dify_request():
    api_key = "app-xfFd1o2XZ4eNV0DRjPHGClrE"
    base_url = "https://api.dify.ai"
    
    # 模拟后端实际发送的请求
    test_inputs = {
        "user_input": "你好",
        "question": "解一元二次方程",
        "answer": "使用求根公式",
        "student_name": "小明",
        "question_category": "数学"
    }
    
    url = f"{base_url}/v1/workflows/run"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    payload = {
        "inputs": test_inputs,
        "response_mode": "streaming",
        "user": "debug-user-123"
    }
    
    print("🔍 Dify 400错误调试")
    print("=" * 50)
    print(f"请求URL: {url}")
    print(f"请求头: {json.dumps(headers, indent=2)}")
    print(f"请求体: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应体: {response.text}")
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    print(f"\n📋 详细错误信息:")
                    for key, value in error_data.items():
                        print(f"  {key}: {value}")
                except:
                    print(f"\n❌ 原始错误响应: {response.text}")
                    
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

if __name__ == "__main__":
    asyncio.run(debug_dify_request())