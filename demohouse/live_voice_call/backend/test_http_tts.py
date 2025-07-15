#!/usr/bin/env python3
"""
Test script for HTTP TTS client with cluster and voice_type support.
"""

import asyncio
import time
from tts_http_client import SingletonHTTPTTSManager


async def test_http_tts():
    """Test the HTTP TTS implementation."""
    print("🚀 Starting HTTP TTS Test")
    print("=" * 50)
    
    # Configuration from tts_http_demo.py
    APP_ID = "3735242956"
    ACCESS_TOKEN = "WDubf8FD7TunKdtBdzMnmLRuEzvximVu"
    DEFAULT_CLUSTER = "volcano_icl"
    DEFAULT_VOICE_TYPE = "S_pic297Bs1"
    
    # Test text
    test_text = "您好，这是HTTP TTS测试。"
    
    try:
        # Get singleton instance
        tts_manager = SingletonHTTPTTSManager()
        
        # Test 1: Initialize with default parameters
        print("\n📋 Test 1: Initialize with default parameters")
        await tts_manager.initialize(
            app_id=APP_ID,
            access_token=ACCESS_TOKEN,
            cluster=DEFAULT_CLUSTER,
            voice_type=DEFAULT_VOICE_TYPE
        )
        
        # Test 2: Synthesize text
        print(f"\n📋 Test 2: Synthesize text: '{test_text}'")
        start_time = time.time()
        response = await tts_manager.synthesize(test_text)
        duration = time.time() - start_time
        
        if response.success:
            print(f"✅ Synthesis completed in {duration:.2f}s, audio size: {len(response.audio_data)} bytes")
        else:
            print(f"❌ Synthesis failed: {response.error_message}")
        
        # Test 3: Update voice parameters
        print("\n📋 Test 3: Update voice parameters")
        updated = await tts_manager.update_voice_config(voice_type="BV700_streaming")
        print(f"Voice updated: {updated}")
        
        # Test 4: Synthesize with new voice (if voice exists)
        print(f"\n📋 Test 4: Synthesize with updated config: '{test_text}'")
        start_time = time.time()
        response_2 = await tts_manager.synthesize(test_text)
        duration = time.time() - start_time
        
        if response_2.success:
            print(f"✅ Synthesis completed in {duration:.2f}s, audio size: {len(response_2.audio_data)} bytes")
        else:
            print(f"❌ Synthesis failed: {response_2.error_message}")
        
        # Test 5: Verify singleton behavior
        print("\n📋 Test 5: Verify singleton behavior")
        tts_manager_2 = SingletonHTTPTTSManager()
        print(f"Same instance: {tts_manager is tts_manager_2}")
        print(f"Current cluster: {tts_manager_2.current_config.cluster if tts_manager_2.current_config else 'None'}")
        print(f"Current voice_type: {tts_manager_2.current_config.voice_type if tts_manager_2.current_config else 'None'}")
        
        # Cleanup
        await tts_manager.cleanup()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_http_tts())