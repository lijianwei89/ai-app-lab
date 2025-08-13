#!/usr/bin/env python3
"""
最简单的Dify上下文测试
"""

import requests
import json

def quick_test():
    api_key = "app-xfFd1o2XZ4eNV0DRjPHGClrE"
    
    # 测试连续对话
    conversations = [
        {"user_input": "你好", "user": "test-user-1"},
        {"user_input": "刚才我说了什么", "user": "test-user-1"},
        {"user_input": "现在呢", "user": "test-user-1"}
    ]
    
    for i, conv in enumerate(conversations):
        payload = {
            "inputs": {"user_input": conv["user_input"]},
            "response_mode": "blocking",
            "user": conv["user"]
        }
        
        response = requests.post(
            'https://api.dify.ai/v1/workflows/run',
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            reply = result.get('data', {}).get('outputs', {}).get('pet_reply', '无回复')
            print(f"第{i+1}轮: {conv['user_input']}")
            print(f"AI回复: {reply}")
            print("-" * 40)
        else:
            print(f"错误: {response.status_code}")

if __name__ == "__main__":
    quick_test()