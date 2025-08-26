#!/usr/bin/env python3
"""
Test the updated TTS configuration with custom voice
"""
import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tts_http_client import HTTPTTSClient, TTSConfig

async def test_updated_tts():
    """Test the updated TTS configuration"""
    
    # Create TTS configuration for internal service
    config = TTSConfig(
        app_id="200000054",
        access_token="200000054:bebc3b8ce075b6fd94d04407e1ed6937",
        cluster="volcengine",
        voice_type="S_dwiOyLR61",
        host="speech-internal.tal.com"
    )
    
    # Create HTTP TTS client
    client = HTTPTTSClient(config)
    
    try:
        # Test synthesis
        print("🎯 Testing updated TTS configuration...")
        response = await client.synthesize_text("你好，我是使用自建音色的AI助手")
        
        if response.success:
            print("✅ TTS configuration test successful!")
            print(f"📊 Audio data size: {len(response.audio_data)} bytes")
            print(f"🆔 Request ID: {response.request_id}")
            return True
        else:
            print(f"❌ TTS test failed: {response.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during test: {e}")
        return False
    finally:
        await client.close()

async def main():
    success = await test_updated_tts()
    print(f"\n🎉 Final result: {'SUCCESS' if success else 'FAILED'}")

if __name__ == "__main__":
    asyncio.run(main())