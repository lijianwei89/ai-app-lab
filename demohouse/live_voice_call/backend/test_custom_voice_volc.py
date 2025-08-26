#!/usr/bin/env python3
"""
自建音色测试 - 使用现有火山方舟接口
"""
import asyncio
from arkitect.core.component.tts import AsyncTTSClient, AudioParams, ConnectionParams

class CustomVoiceTest:
    """测试自建音色"""
    
    def __init__(self):
        # 使用你提供的内网配置
        self.app_key = "200000054"  # 对应 tts.akid
        self.access_key = "bebc3b8ce075b6fd94d04407e1ed6937"  # 对应 tts.akkey
        self.voice_type = "S_dwiOyLR61"  # 自建音色ID
        
    async def test_custom_voice(self):
        """测试自定义音色"""
        print(f"🎯 测试自建音色: {self.voice_type}")
        
        # 配置TTS客户端
        connection_params = ConnectionParams(
            speaker=self.voice_type,
            audio_params=AudioParams()
        )
        
        # 使用内网环境
        tts_client = AsyncTTSClient(
            app_key=self.app_key,
            access_key=self.access_key,
            connection_params=connection_params,
            base_url="https://speech-internal.tal.com"  # 内网地址
        )
        
        try:
            await tts_client.init()
            print("✅ TTS客户端初始化成功")
            
            # 测试文本
            test_text = "你好，我是使用自建音色的AI助手"
            
            # 合成音频
            audio_chunks = []
            async for response in tts_client.tts(source=test_text):
                if response.audio:
                    audio_chunks.append(response.audio)
                    print(f"📦 收到音频数据: {len(response.audio)} 字节")
            
            if audio_chunks:
                total_size = sum(len(chunk) for chunk in audio_chunks)
                print(f"✅ 合成成功！总音频大小: {total_size} 字节")
                
                # 保存测试文件
                with open("custom_voice_test.pcm", "wb") as f:
                    for chunk in audio_chunks:
                        f.write(chunk)
                print("📁 已保存为 custom_voice_test.pcm")
                return True
            else:
                print("❌ 未收到音频数据")
                return False
                
        except Exception as e:
            print(f"❌ TTS测试失败: {e}")
            return False
        finally:
            await tts_client.close()

async def main():
    """主测试函数"""
    tester = CustomVoiceTest()
    success = await tester.test_custom_voice()
    
    if success:
        print("🎉 自建音色测试通过！可以集成到主程序")
    else:
        print("⚠️  自建音色测试失败，请检查配置")

if __name__ == "__main__":
    asyncio.run(main())