#!/usr/bin/env python3
"""
Test service integration with HTTP TTS.
"""

import asyncio
import sys
import os

# Add the backend directory to path to import service
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service import VoiceBotService, LLMProvider


async def test_service_integration():
    """Test service integration with HTTP TTS."""
    print("🚀 Testing Service Integration with HTTP TTS")
    print("=" * 60)
    
    # Configuration
    service = VoiceBotService(
        asr_app_key="test_asr_key",
        asr_access_key="test_asr_access",
        tts_app_key="3735242956",
        tts_access_key="WDubf8FD7TunKdtBdzMnmLRuEzvximVu",
        llm_ep_id="test_llm_ep",
        llm_provider=LLMProvider.ARK,
        use_http_tts=True,  # Enable HTTP TTS
        tts_cluster="volcano_icl",
        tts_voice_type="S_pic297Bs1"
    )
    
    try:
        # Test initialization
        print("\n📋 Test 1: Initialize service with HTTP TTS")
        # We can only test TTS initialization since ASR requires the full arkitect environment
        
        # Initialize just the HTTP TTS manager
        from tts_http_client import SingletonHTTPTTSManager
        service.http_tts_manager = SingletonHTTPTTSManager()
        await service.http_tts_manager.initialize(
            app_id=service.tts_app_key,
            access_token=service.tts_access_key,
            cluster=service.tts_cluster,
            voice_type=service.tts_voice_type
        )
        print("✅ HTTP TTS manager initialized successfully")
        
        # Test LLM text generation simulation
        print("\n📋 Test 2: Test TTS response handling")
        
        async def mock_llm_output():
            """Mock LLM output for testing."""
            test_chunks = ["您好，", "这是一个", "测试消息。"]
            for chunk in test_chunks:
                yield chunk
                await asyncio.sleep(0.1)  # Simulate streaming delay
        
        # Test HTTP TTS response handling
        payload_count = 0
        async for payload in service._handle_http_tts_response(mock_llm_output()):
            payload_count += 1
            payload_type = type(payload).__name__
            print(f"  📦 Received payload {payload_count}: {payload_type}")
            
            if hasattr(payload, 'sentence'):
                print(f"    📝 Sentence: {payload.sentence[:50]}{'...' if len(payload.sentence) > 50 else ''}")
            elif hasattr(payload, 'data'):
                print(f"    🎵 Audio data: {len(payload.data)} bytes")
        
        print(f"✅ Received {payload_count} TTS payloads")
        
        # Test configuration update
        print("\n📋 Test 3: Test configuration update")
        original_voice_type = service.tts_voice_type
        service.tts_voice_type = "zh_female_sajiaonvyou_moon_bigtts"  # Alternative voice
        
        if service.http_tts_manager:
            updated = await service.http_tts_manager.update_voice_config(
                cluster=service.tts_cluster,
                voice_type=service.tts_voice_type
            )
            print(f"✅ Configuration updated: {updated}")
            print(f"   New voice_type: {service.tts_voice_type}")
        
        # Cleanup
        await service.http_tts_manager.cleanup()
        
        print("\n🎉 Service integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_service_integration())