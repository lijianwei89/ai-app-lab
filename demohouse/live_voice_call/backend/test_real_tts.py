#!/usr/bin/env python3
"""
真实字节方舟自建音色测试
"""
import asyncio
import httpx
import json
import base64
import time
import hashlib
import hmac

class RealCustomTTSTest:
    """真实字节方舟TTS测试"""
    
    def __init__(self):
        # 字节方舟内网地址
        self.base_url = "https://speech-internal.tal.com"
        self.appid = "200000054"
        self.token = "bebc3b8ce075b6fd94d04407e1ed6937"
        self.voice_type = "S_dwiOyLR61"
    
    def _generate_signature(self, timestamp: str) -> str:
        """生成签名"""
        sign_str = f"accesskey={self.token}&timestamp={timestamp}"
        return hmac.new(
            self.token.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def test_all_endpoints(self):
        """测试所有可能的端点"""
        endpoints = [
            "/api/v1/tts",
            "/tts/v1",
            "/v1/tts",
            "/tts",
            "/api/tts/synthesize"
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            print(f"🎯 测试: {url}")
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    payload = {
                        "text": "你好",
                        "voice_type": self.voice_type,
                        "format": "mp3",
                        "sample_rate": 24000
                    }
                    
                    headers = {
                        "Authorization": f"Bearer {self.token}",
                        "Content-Type": "application/json"
                    }
                    
                    response = await client.post(url, json=payload, headers=headers)
                    print(f"   状态码: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"   ✅ 成功: {endpoint}")
                        return True
                    elif response.status_code != 404:
                        print(f"   📦 响应: {response.text[:100]}...")
                        
            except Exception as e:
                print(f"   ❌ 错误: {e}")
        
        return False
    
    async def test_with_get_method(self):
        """测试GET方法"""
        url = f"{self.base_url}/api/v1/tts"
        params = {
            "text": "你好",
            "voice_type": self.voice_type,
            "format": "mp3"
        }
        
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                print(f"GET 状态码: {response.status_code}")
                return response.status_code == 200
        except Exception as e:
            print(f"GET 错误: {e}")
            return False

async def main():
    """主测试"""
    tester = RealCustomTTSTest()
    
    print("🔍 开始测试字节方舟内网TTS...")
    
    # 测试所有端点
    success = await tester.test_all_endpoints()
    
    if not success:
        print("\n🔍 尝试GET方法...")
        success = await tester.test_with_get_method()
    
    print(f"\n🎉 测试{'成功' if success else '失败'}")

if __name__ == "__main__":
    asyncio.run(main())