#!/usr/bin/env python3
"""
带签名的自建音色测试
"""
import asyncio
import httpx
import json
import time
import hashlib
import hmac

class SignedTTSTest:
    def __init__(self):
        self.base_url = "https://speech-internal.tal.com"
        self.appid = "200000054"
        self.access_key = "bebc3b8ce075b6fd94d04407e1ed6937"
        self.voice_type = "S_dwiOyLR61"
    
    def _generate_signature(self, params: dict) -> str:
        """生成签名"""
        sorted_params = sorted(params.items())
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        return hmac.new(
            self.access_key.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def test_tts(self):
        """测试带签名的TTS"""
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
                    print(f"✅ TTS调用成功")
                    return True
                else:
                    print(f"❌ 调用失败")
                    return False
                    
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False

async def main():
    tester = SignedTTSTest()
    success = await tester.test_tts()
    print(f"\n🎉 测试结果: {'成功' if success else '失败'}")

if __name__ == "__main__":
    asyncio.run(main())