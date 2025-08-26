#!/usr/bin/env python3
"""
直接测试字节方舟自建音色
"""
import asyncio
import httpx
import json

class DirectTTSTest:
    def __init__(self):
        self.base_url = "https://speech-internal.tal.com"
        self.appid = "200000054"
        self.access_key = "bebc3b8ce075b6fd94d04407e1ed6937"
        self.voice_type = "S_dwiOyLR61"
    
    async def test_tts(self):
        """直接测试"""
        url = f"{self.base_url}/v1/tts"
        
        payload = {
            "text": "你好，我是使用自建音色的AI助手",
            "voice_type": self.voice_type,
            "format": "mp3",
            "sample_rate": 24000,
            "speed": 1.0,
            "volume": 1.0,
            "pitch": 1.0
        }
        
        # 尝试不同的鉴权头组合
        headers_list = [
            {"appId": self.appid, "serverKey": self.access_key},
            {"app-id": self.appid, "access-key": self.access_key},
            {"Authorization": f"Bearer {self.access_key}"},
            {"X-API-Key": self.access_key},
            {"api-key": self.access_key}
        ]
        
        for i, headers in enumerate(headers_list):
            print(f"\n🔍 尝试鉴权方式 {i+1}: {list(headers.keys())}")
            
            headers["Content-Type"] = "application/json"
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    print(f"   状态码: {response.status_code}")
                    
                    if response.status_code != 404:
                        print(f"   响应: {response.text}")
                        
                    if response.status_code == 200:
                        print("✅ 成功！")
                        return True
                        
            except Exception as e:
                print(f"   错误: {e}")
        
        return False

async def main():
    tester = DirectTTSTest()
    success = await tester.test_tts()
    print(f"\n🎉 最终结果: {'成功' if success else '失败'}")

if __name__ == "__main__":
    asyncio.run(main())