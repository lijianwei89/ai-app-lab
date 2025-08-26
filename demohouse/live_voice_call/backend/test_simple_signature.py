#!/usr/bin/env python3
"""
简化的字节方舟TTS签名测试
"""
import asyncio
import httpx
import json
import time
import hashlib
import hmac

class SimpleTTSTest:
    def __init__(self):
        self.base_url = "https://speech-internal.tal.com"
        self.appid = "200000054"
        self.secret_key = "bebc3b8ce075b6fd94d04407e1ed6937"
        self.voice_type = "S_dwiOyLR61"
    
    def _generate_signature(self, timestamp: str) -> str:
        """简单签名"""
        sign_str = f"appId={self.appid}&timestamp={timestamp}"
        return hmac.new(
            self.secret_key.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def test_tts(self):
        """测试"""
        url = f"{self.base_url}/v1/tts"
        
        timestamp = str(int(time.time()))
        signature = self._generate_signature(timestamp)
        
        params = {
            "appId": self.appid,
            "timestamp": timestamp,
            "signature": signature
        }
        
        payload = {
            "text": "你好",
            "voice_type": self.voice_type
        }
        
        full_url = f"{url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        headers = {"Content-Type": "application/json"}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(full_url, json=payload, headers=headers)
                print(f"状态码: {response.status_code}")
                print(f"响应: {response.text}")
                return response.status_code == 200
        except Exception as e:
            print(f"错误: {e}")
            return False

async def main():
    tester = SimpleTTSTest()
    success = await tester.test_tts()
    print(f"结果: {'成功' if success else '失败'}")

if __name__ == "__main__":
    asyncio.run(main())