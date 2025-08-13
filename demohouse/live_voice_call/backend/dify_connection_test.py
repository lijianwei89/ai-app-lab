#!/usr/bin/env python3
"""
Dify连接验证单例测试
用于验证当前Dify API密钥和连接是否正常
"""

import requests
import json
import sys
import os
from typing import Dict, Any

class DifyConnectionTest:
    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def test_workflow_connection(self, user_input: str = "你好，请介绍一下自己") -> Dict[str, Any]:
        """测试工作流连接"""
        url = f"{self.base_url}/v1/workflows/run"
        
        payload = {
            "inputs": {
                "user_input": user_input
            },
            "response_mode": "streaming",
            "user": "test-user-123"
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, stream=True)
            
            if response.status_code == 200:
                # 读取流式响应
                full_response = ""
                for line in response.iter_lines(decode_unicode=True):
                    if line and line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])
                            if data.get('event') == 'message' and data.get('data'):
                                full_response += data['data']
                        except json.JSONDecodeError:
                            continue
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response": full_response,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "response": None,
                    "error": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "response": None,
                "error": str(e)
            }
    
    def test_chat_completion(self, user_input: str = "你好") -> Dict[str, Any]:
        """测试聊天完成接口"""
        url = f"{self.base_url}/v1/chat-messages"
        
        payload = {
            "inputs": {},
            "query": user_input,
            "response_mode": "blocking",
            "conversation_id": "",
            "user": "test-user-123"
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else None,
                "error": response.text if response.status_code != 200 else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "response": None,
                "error": str(e)
            }

def main():
    # 使用当前的API密钥
    api_key = "app-xfFd1o2XZ4eNV0DRjPHGClrE"
    base_url = "https://api.dify.ai"
    
    # 使用命令行参数或默认值
    import sys
    user_input = sys.argv[1] if len(sys.argv) > 1 else "你好，请介绍一下自己"
    
    print("🔍 Dify连接验证测试")
    print("=" * 50)
    print(f"API密钥: {api_key[:20]}...")
    print(f"测试内容: {user_input}")
    
    tester = DifyConnectionTest(api_key, base_url)
    
    # 测试工作流连接
    print(f"\n🧪 测试工作流连接...")
    print("-" * 30)
    
    result = tester.test_workflow_connection(user_input)
    
    if result["success"]:
        print("✅ 工作流连接成功！")
        print(f"状态码: {result['status_code']}")
        print(f"响应: {result['response'][:200]}...")
    else:
        print("❌ 工作流连接失败！")
        print(f"状态码: {result['status_code']}")
        print(f"错误: {result['error']}")
    
    # 测试聊天完成接口
    print(f"\n🧪 测试聊天完成接口...")
    print("-" * 30)
    
    chat_result = tester.test_chat_completion(user_input)
    
    if chat_result["success"]:
        print("✅ 聊天接口正常！")
        print(f"状态码: {chat_result['status_code']}")
        if chat_result["response"]:
            answer = chat_result["response"].get("answer", "")
            print(f"响应: {answer[:200]}...")
    else:
        print("❌ 聊天接口异常！")
        print(f"状态码: {chat_result['status_code']}")
        print(f"错误: {chat_result['error']}")

if __name__ == "__main__":
    main()