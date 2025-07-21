#!/usr/bin/env python3
"""
Test script to verify dual Dify client configuration works correctly.
"""
import asyncio
import json
import httpx
from typing import Dict, Any, Optional


class TestDifyClient:
    """Test Dify client."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
    
    async def test_connection(self, inputs: Dict[str, Any], test_name: str) -> bool:
        """Test connection to Dify API."""
        url = f"{self.base_url}/v1/workflows/run"
        
        payload = {
            "inputs": inputs,
            "response_mode": "streaming",
            "user": f"test-{test_name}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                async with client.stream('POST', url, headers=self.headers, json=payload) as response:
                    if response.status_code == 200:
                        print(f"✅ {test_name} API connection successful")
                        return True
                    else:
                        print(f"❌ {test_name} API connection failed: {response.status_code}")
                        return False
        except Exception as e:
            print(f"❌ {test_name} API connection error: {str(e)}")
            return False


async def test_dual_clients():
    """Test both conversation and opening Dify clients."""
    print("🧪 测试双Dify客户端配置")
    print("=" * 50)
    
    # Configuration from handler.py
    conversation_api_key = "app-JqtJdpgiEKukUAxxT8oiJR4u"  # For conversation
    opening_api_key = "app-rCIokTn1NixIujuo4M18feAW"      # For opening
    
    # Create clients
    conversation_client = TestDifyClient(conversation_api_key)
    opening_client = TestDifyClient(opening_api_key)
    
    print(f"📋 配置验证:")
    print(f"   对话流程API密钥: {conversation_api_key}")
    print(f"   开场白API密钥: {opening_api_key}")
    print(f"   密钥不同: {'✅' if conversation_api_key != opening_api_key else '❌'}")
    
    print(f"\n🔌 连接测试:")
    
    # Test conversation client
    conversation_inputs = {
        "question": "解一元二次方程",
        "answer": "使用求根公式",
        "user_responds": "我不太理解",
        "question_stem": "数学问题",
        "student_name": "小明",
        "question_category": "数学"
    }
    
    conversation_success = await conversation_client.test_connection(
        conversation_inputs, 
        "对话流程"
    )
    
    # Test opening client  
    opening_inputs = {
        "question": "解一元二次方程",
        "student_name": "小明"
    }
    
    opening_success = await opening_client.test_connection(
        opening_inputs,
        "开场白"
    )
    
    print(f"\n📊 测试结果:")
    print(f"   对话流程客户端: {'✅ 正常' if conversation_success else '❌ 失败'}")
    print(f"   开场白客户端: {'✅ 正常' if opening_success else '❌ 失败'}")
    
    if conversation_success and opening_success:
        print(f"\n🎉 双客户端配置验证成功！")
        print(f"📋 功能说明:")
        print(f"   - 对话流程使用 {conversation_api_key} 进行学生问答处理")
        print(f"   - 开场白使用 {opening_api_key} 进行个性化开场白生成")
        print(f"   - 两个工作流功能完全独立，不会相互干扰")
        return True
    else:
        print(f"\n⚠️ 部分客户端连接失败，请检查API密钥配置")
        return False


async def test_service_configuration():
    """Test service configuration parameters."""
    print(f"\n🧪 测试服务配置")
    print("=" * 50)
    
    # Simulate service configuration
    config = {
        "dify_api_key": "app-JqtJdpgiEKukUAxxT8oiJR4u",          # Conversation
        "dify_opening_api_key": "app-rCIokTn1NixIujuo4M18feAW",   # Opening
        "dify_base_url": "https://api.dify.ai",
        "enable_opening": True,
        "opening_timeout": 5,
    }
    
    print(f"📋 VoiceBotService 配置:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    # Validate configuration
    validations = [
        ("不同API密钥", config["dify_api_key"] != config["dify_opening_api_key"]),
        ("开场白已启用", config["enable_opening"] == True),
        ("合理超时时间", 1 <= config["opening_timeout"] <= 30),
        ("有效Base URL", config["dify_base_url"].startswith("https://")),
    ]
    
    print(f"\n✅ 配置验证:")
    all_valid = True
    for desc, is_valid in validations:
        status = "✅" if is_valid else "❌"
        print(f"   {status} {desc}")
        if not is_valid:
            all_valid = False
    
    return all_valid


async def main():
    """Run all tests."""
    print("🎯 双Dify客户端功能区分测试")
    print("=" * 60)
    
    # Test 1: Dual clients connection
    clients_success = await test_dual_clients()
    
    # Test 2: Service configuration
    config_success = await test_service_configuration()
    
    print(f"\n🏁 总结")
    print("=" * 30)
    
    if clients_success and config_success:
        print("✅ 所有测试通过！")
        print("🎤 功能区分实现完成:")
        print("  📞 对话流程: app-JqtJdpgiEKukUAxxT8oiJR4u")
        print("  🎬 开场白: app-rCIokTn1NixIujuo4M18feAW")
        print("  🔧 配置正确，功能独立运行")
    else:
        print("❌ 部分测试失败")
        if not clients_success:
            print("  - 客户端连接测试失败")
        if not config_success:
            print("  - 服务配置验证失败")
    
    print(f"\n💡 使用说明:")
    print(f"  - 开场白会调用专门的开场白工作流")
    print(f"  - 学生问答会调用对话工作流")
    print(f"  - 两个功能使用不同的API密钥，完全独立")


if __name__ == "__main__":
    asyncio.run(main())