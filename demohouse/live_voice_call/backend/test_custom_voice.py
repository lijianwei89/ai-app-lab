#!/usr/bin/env python3
"""
最小单例测试：自建音色调用 - 字节方舟标准格式
"""
import asyncio
import httpx
from typing import Optional
import json
import base64

class CustomTTSTest:
    """最小化的TTS测试类"""
    
    def __init__(self):
        self.base_url = "https://speech-internal.tal.com"
        self.appid = "200000054"
        self.token = "bebc3b8ce075b6fd94d04407e1ed6937"
        self.voice_type = "S_dwiOyLR61"
    
    async def synthesize_text(self, text: str) -> Optional[bytes]:
        """合成文本为音频 - 字节方舟标准格式"""
        url = f"{self.base_url}/api/v1/tts"
        
        payload = {
            "text": text,
            "voice_type": self.voice_type,
            "format": "mp3",
            "sample_rate": 24000,
            "speed": 1.0,
            "volume": 1.0,
            "pitch": 1.0
        }
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-App-Id": self.appid
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                print(f"📡 响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"📦 响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    
                    # 检查不同可能的响应格式
                    if result.get("data"):
                        audio_data = result["data"]
                        if isinstance(audio_data, str):
                            return base64.b64decode(audio_data)
                        elif isinstance(audio_data, dict) and audio_data.get("audio"):
                            return base64.b64decode(audio_data["audio"])
                        else:
                            return audio_data
                    else:
                        print(f"❌ 无音频数据: {result}")
                        return None
                else:
                    print(f"❌ TTS失败: {response.status_code} - {response.text}")
                    return None
            except Exception as e:
                print(f"❌ TTS异常: {e}")
                return None

async def main():
    """测试主函数"""
    tts = CustomTTSTest()
    
    test_text = "你好，我是使用自建音色的AI助手"
    print(f"🎤 测试文本: {test_text}")
    print(f"🎯 音色ID: {tts.voice_type}")
    
    audio_data = await tts.synthesize_text(test_text)
    
    if audio_data:
        print(f"✅ 合成成功！音频大小: {len(audio_data)} bytes")
        
        # 保存测试文件
        with open("test_custom_voice.mp3", "wb") as f:
            f.write(audio_data)
        print("📁 已保存为 test_custom_voice.mp3")
    else:
        print("❌ 合成失败")

if __name__ == "__main__":
    asyncio.run(main())