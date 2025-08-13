#!/usr/bin/env python3
"""
测试前端到后端的完整链路
"""

import asyncio
import httpx
import json
from service import VoiceBotService
from typing import AsyncIterable

async def test_frontend_link():
    """模拟前端调用测试"""
    
    # 创建服务实例
    service = VoiceBotService(
        llm_ep_id="test",
        tts_app_key="test",
        tts_access_key="test",
        asr_app_key="test",
        asr_access_key="test",
        llm_provider="dify",
        dify_api_key="app-nxb7ZW4Uy9DZmeEMoE2ibTDY",
        dify_base_url="https://api.dify.ai"
    )
    
    # 模拟ASR识别结果
    test_texts = [
        "你是谁",
        "你好",
        "？"
    ]
    
    print("🧪 前端链路调试测试")
    print("=" * 40)
    
    for text in test_texts:
        print(f"\n📝 测试文本: '{text}'")
        
        # 模拟调用流
        try:
            async for chunk in service._stream_dify_chat(text):
                print(f"✅ 后端返回: '{chunk}'")
        except Exception as e:
            print(f"❌ 错误: {e}")
            
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(test_frontend_link())