#!/usr/bin/env python3
"""
字节方舟内网TTS签名测试
"""
import asyncio
import httpx
import json
import time
import hashlib
import hmac
import uuid

class SignatureTTSTest:
    def __init__(self):
        self.base_url = "https://speech-internal.tal.com"
        self.appid = "200000054"
        self.secret_key = "bebc3b8ce075b6fd94d04407e1ed6937"
        self.voice_type = "S_dwiOyLR61"
    
    def _generate_signature(self, method: str, uri: str, headers: dict, params: dict, body: str = "") -> str:
        """生成字节方舟签名"""
        # 规范化的HTTP请求
        canonical_headers = "\n".join([f"{k.lower()}:{v}" for k, v in sorted(headers.items())])
        canonical_query = "\u0026".join([f"{k}={v}" for k, v in sorted(params.items())])
        
        # 签名串
        sign_str = f"{method}\n{uri}\n{canonical_query}\n{canonical_headers}\n{body}"
        
        # 使用HMAC-SHA256签名
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    async def test_tts(self):
        """测试带签名的TTS"""
        uri = "/v1/tts"
        url = f"{self.base_url}{uri}"
        
        # 请求参数
        timestamp = str(int(time.time()))
        nonce = str(uuid.uuid4())[:8]
        
        params = {
            "Action": "CreateTtsTask",
            "Version": "2022-12-01",
            "Timestamp": timestamp,
            "Nonce": nonce,
            "AppId": self.appid
        }
        
        # 请求体
        body = json.dumps({
            "text": "你好，我是使用自建音色的AI助手",
            "voice_type": self.voice_type,
            "format": "mp3",
            "sample_rate": 24000,
            "speed": 1.0,
            "volume": 1.0,
            "pitch": 1.0
        })
        
        # 签名头
        headers = {
            "Content-Type": "application/json",
            "X-Date": timestamp
        }
        
        # 生成签名
        signature = self._generate_signature("POST", uri, headers, params, body)
        params["Signature"] = signature
        
        # 完整URL
        full_url = f"{url}?{"&".join([f"{k}={v}" for k, v in params.items()])}"
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(full_url, data=body, headers=headers)
                print(f"🎯 测试成功！")
                print(f"状态码: {response.status_code}")
                print(f"响应: {response.text}")
                
                return response.status_code == 200
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False

async def main():
    tester = SignatureTTSTest()
    success = await tester.test_tts()
    print(f"\n🎉 测试结果: {'成功' if success else '失败'}")

if __name__ == "__main__":
    asyncio.run(main())