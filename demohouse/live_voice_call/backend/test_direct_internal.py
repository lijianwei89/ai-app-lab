#!/usr/bin/env python3
"""
内网直连测试 - 无需签名
"""
import asyncio
import httpx

class DirectInternalTest:
    def __init__(self):
        self.base_url = "https://speech-internal-test.tal.com"
        self.appid = "200000054"
        self.api_key = "bebc3b8ce075b6fd94d04407e1ed6937"
        self.voice_type = "S_dwiOyLR61"
    
    async def test_direct_connection(self):
        """测试内网直连"""
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
        
        # 测试不同的鉴权方式
        auth_methods = [
            {"Authorization": f"Bearer {self.api_key}"},
            {"api-key": self.api_key},
            {"Authorization": self.api_key},
            {"X-API-Key": self.api_key}
        ]
        
        for i, auth_header in enumerate(auth_methods):
            headers = {**auth_header, "Content-Type": "application/json"}
            
            print(f"\n🔍 测试鉴权方式 {i+1}: {list(auth_header.keys())[0]}")
            print(f"URL: {url}")
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    print(f"   状态码: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("   ✅ 成功！")
                        return True
                    else:
                        print(f"   响应: {response.text[:100]}...")
                        
            except Exception as e:
                print(f"   错误: {e}")
        
        return False

async def main():
    tester = DirectInternalTest()
    success = await tester.test_direct_connection()
    print(f"\n🎉 内网直连测试: {'成功' if success else '失败'}")

if __name__ == "__main__":
    asyncio.run(main())