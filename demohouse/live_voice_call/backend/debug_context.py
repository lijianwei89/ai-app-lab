#!/usr/bin/env python3
"""
检查Dify工作流上下文和承接性问题
"""

import requests
import json

def test_dify_context():
    api_key = "app-xfFd1o2XZ4eNV0DRjPHGClrE"
    base_url = "https://api.dify.ai"
    
    # 测试连续对话
    test_conversation = [
        "你好",
        "请介绍一下一元二次方程",
        "那什么是好朋友数呢",
        "这个和刚才的问题有什么关系吗"
    ]
    
    url = f"{base_url}/v1/workflows/run"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    print("🔍 Dify工作流上下文测试")
    print("=" * 60)
    
    # 单独测试每个输入
    for i, user_input in enumerate(test_conversation):
        payload = {
            "inputs": {"user_input": user_input},
            "response_mode": "blocking",  # 使用blocking模式获取完整响应
            "user": f"test-user-{i+1}"
        }
        
        print(f"\n🧪 第{i+1}轮对话:")
        print(f"用户: {user_input}")
        print("-" * 40)
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'data' in result and 'outputs' in result['data']:
                    reply = result['data']['outputs'].get('pet_reply', '无响应')
                    print(f"AI回复: {reply}")
                else:
                    print(f"❌ 响应格式异常: {result}")
            else:
                print(f"❌ HTTP错误: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 测试完成！")
    print("如果所有回复都相同，说明工作流缺少上下文记忆")
    print("建议：检查Dify工作流是否启用了会话记忆功能")

if __name__ == "__main__":
    test_dify_context()