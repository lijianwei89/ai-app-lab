#!/usr/bin/env python3
"""
最终测试：字节方舟自建音色调用
"""
import asyncio
import httpx
import json

class FinalTTSTest:
    def __init__(self):
        self.base_url = "https://speech-internal.tal.com"
        self.appid = "200000054"
        self.access_key = "bebc3b8ce075b6fd94d04407e1ed6937"
        self.voice_type = "S_dwiOyLR61"
    
    async def test_tts(self):
        """测试正确端点"""
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
        
        headers = {
            "appId": self.appid,
            "serverKey": self.access_key,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                print(f"🎯 测试成功！")
                print(f"状态码: {response.status_code}")
                print(f"响应: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ TTS调用成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    return True
                else:
                    print(f"❌ 调用失败: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False

async def main():
    tester = FinalTTSTest()
    success = await tester.test_tts()
    print(f"\n🎉 测试结果: {'成功' if success else '失败'}")

if __name__ == "__main__":
    asyncio.run(main())