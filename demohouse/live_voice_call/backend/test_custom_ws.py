#!/usr/bin/env python3
"""
自建音色WebSocket测试 - 内网环境
"""
import asyncio
import websockets
import json
import ssl

class CustomVoiceWSTest:
    """WebSocket测试自建音色"""
    
    def __init__(self):
        # 内网WebSocket地址
        self.ws_url = "wss://speech-internal.tal.com/tts"
        self.appid = "200000054"
        self.token = "bebc3b8ce075b6fd94d04407e1ed6937"
        self.voice_type = "S_dwiOyLR61"
    
    async def test_connection(self):
        """测试WebSocket连接"""
        print(f"🎯 测试WebSocket: {self.ws_url}")
        print(f"🎤 音色: {self.voice_type}")
        
        try:
            # 创建WebSocket连接
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            async with websockets.connect(
                self.ws_url,
                extra_headers={
                    "Authorization": f"Bearer {self.token}",
                    "X-App-Id": self.appid
                },
                ssl=ssl_context
            ) as websocket:
                
                print("✅ WebSocket连接成功")
                
                # 发送TTS请求
                request = {
                    "text": "你好，我是使用自建音色的AI助手",
                    "voice_type": self.voice_type,
                    "format": "mp3",
                    "sample_rate": 24000
                }
                
                await websocket.send(json.dumps(request))
                print("📡 发送TTS请求")
                
                # 接收响应
                audio_chunks = []
                async for message in websocket:
                    data = json.loads(message)
                    if data.get("type") == "audio":
                        audio_chunks.append(data["data"])
                        print(f"📦 收到音频: {len(data['data'])} 字节")
                    elif data.get("type") == "end":
                        print("✅ TTS完成")
                        break
                
                return len(audio_chunks) > 0
                
        except Exception as e:
            print(f"❌ WebSocket测试失败: {e}")
            return False

async def main():
    """主测试"""
    tester = CustomVoiceWSTest()
    success = await tester.test_connection()
    print(f"测试{'成功' if success else '失败'}")

if __name__ == "__main__":
    asyncio.run(main())