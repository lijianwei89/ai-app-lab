#!/usr/bin/env python3
"""
自建音色HTTP测试 - 最小化实现
"""
import asyncio
import httpx
import json
import base64

class SimpleCustomTTSTest:
    """简单的自建音色测试"""
    
    def __init__(self):
        self.base_url = "https://speech-internal.tal.com"
        self.appid = "200000054"
        self.token = "bebc3b8ce075b6fd94d04407e1ed6937"
        self.voice_type = "S_dwiOyLR61"
    
    async def test_tts(self):
        """测试TTS"""
        url = f"{self.base_url}/tts/v1"
        
        payload = {
            "text": "你好，我是使用自建音色的AI助手",
            "voice_type": self.voice_type,
            "format": "mp3",
            "sample_rate": 24000,
            "speed": 1.0,
            "volume": 1.0,
            "pitch": 1.0
        }
        
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                print(f"状态码: {response.status_code}")
                print(f"响应: {response.text[:200]}...")
                return response.status_code == 200
        except Exception as e:
            print(f"错误: {e}")
            return False

async def main():
    """主测试"""
    tester = SimpleCustomTTSTest()
    success = await tester.test_tts()
    print(f"测试{'成功' if success else '失败'}")

if __name__ == "__main__":
    asyncio.run(main())