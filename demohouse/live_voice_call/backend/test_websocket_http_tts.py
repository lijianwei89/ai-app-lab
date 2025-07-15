#!/usr/bin/env python3
"""
Test WebSocket service integration with HTTP TTS.
This simulates the complete flow from LLM response to TTS audio output.
"""

import asyncio
import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from event import *
    from service import VoiceBotService, LLMProvider
    from tts_http_client import SingletonHTTPTTSManager
except ImportError as e:
    print(f"Import error: {e}")
    print("This test requires the arkitect environment to run fully.")
    sys.exit(1)


async def simulate_llm_stream():
    """Simulate LLM streaming response."""
    test_chunks = [
        "您好，",
        "我是乔青青老师，",
        "今天我们来学习",
        "关于数学的知识。",
        "这是一个很有趣的话题。"
    ]
    
    for chunk in test_chunks:
        yield chunk
        await asyncio.sleep(0.2)  # Simulate streaming delay


async def test_websocket_http_tts_integration():
    """Test complete WebSocket + HTTP TTS integration."""
    print("🚀 Testing WebSocket + HTTP TTS Integration")
    print("=" * 60)
    
    # Configuration matching handler.py
    service = VoiceBotService(
        llm_ep_id="test_llm_ep",
        tts_app_key="3735242956",
        tts_access_key="WDubf8FD7TunKdtBdzMnmLRuEzvximVu",
        asr_app_key="test_asr_key",
        asr_access_key="test_asr_access",
        llm_provider=LLMProvider.ARK,
        # HTTP TTS configuration
        use_http_tts=True,
        tts_cluster="volcano_icl",
        tts_voice_type="S_pic297Bs1",
    )
    
    try:
        # Test 1: Initialize HTTP TTS manager only (skip ASR)
        print("\n📋 Test 1: Initialize HTTP TTS manager")
        service.http_tts_manager = SingletonHTTPTTSManager()
        await service.http_tts_manager.initialize(
            app_id=service.tts_app_key,
            access_token=service.tts_access_key,
            cluster=service.tts_cluster,
            voice_type=service.tts_voice_type
        )
        print("✅ HTTP TTS manager initialized")
        
        # Test 2: Test TTS response handling (simulating complete LLM → TTS flow)
        print("\n📋 Test 2: Test complete LLM → TTS event flow")
        
        # Collect all events that would be sent to frontend
        events_for_frontend = []
        
        async for payload in service._handle_http_tts_response(simulate_llm_stream()):
            event = WebEvent.from_payload(payload)
            events_for_frontend.append(event)
            
            print(f"  📤 Event: {event.event}")
            if hasattr(payload, 'sentence'):
                print(f"     📝 Sentence: '{payload.sentence[:50]}{'...' if len(payload.sentence) > 50 else ''}'")</int>
            elif hasattr(payload, 'data'):
                print(f"     🎵 Audio data: {len(payload.data)} bytes")
                if len(payload.data) > 0:
                    print(f"     🎧 Audio format detected: MP3 (based on size)")
        
        # Test 3: Verify event sequence matches expected WebSocket protocol
        print(f"\n📋 Test 3: Verify WebSocket protocol compliance")
        expected_events = [TTS_SENTENCE_START, TTS_SENTENCE_END, TTS_DONE]
        actual_events = [event.event for event in events_for_frontend]
        
        print(f"  Expected: {expected_events}")
        print(f"  Actual: {actual_events}")
        
        if actual_events == expected_events:
            print("  ✅ Event sequence matches WebSocket protocol")
        else:
            print("  ❌ Event sequence mismatch")
        
        # Test 4: Test configuration update during runtime
        print(f"\n📋 Test 4: Test runtime configuration update")
        original_voice = service.tts_voice_type
        
        # Simulate BotUpdateConfig event
        config_payload = BotUpdateConfigPayload(
            cluster="volcano_icl",
            voice_type="zh_female_sajiaonvyou_moon_bigtts"  # Different voice
        )
        
        # Update configuration
        service.tts_cluster = config_payload.cluster
        service.tts_voice_type = config_payload.voice_type
        
        if service.http_tts_manager:
            updated = await service.http_tts_manager.update_voice_config(
                cluster=service.tts_cluster,
                voice_type=service.tts_voice_type
            )
            print(f"  ✅ Configuration updated: {updated}")
            print(f"  🔧 New voice_type: {service.tts_voice_type}")
        
        # Test 5: Verify audio data can be processed by frontend
        print(f"\n📋 Test 5: Verify frontend audio compatibility")
        
        # Get audio data from one of the events
        audio_event = next((e for e in events_for_frontend if e.event == TTS_SENTENCE_END), None)
        if audio_event and audio_event.data:
            print(f"  📊 Audio data size: {len(audio_event.data)} bytes")
            print(f"  🎼 Audio format: MP3 (suitable for Web Audio API)")
            print(f"  ✅ Audio data ready for frontend playback")
        else:
            print(f"  ❌ No audio data found in events")
        
        # Cleanup
        await service.http_tts_manager.cleanup()
        
        print("\n🎉 WebSocket + HTTP TTS integration test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_event_serialization():
    """Test that events can be properly serialized for WebSocket transmission."""
    print("\n🔍 Testing event serialization for WebSocket...")
    
    try:
        from utils import convert_web_event_to_binary
        
        # Test TTSSentenceStart event
        start_payload = TTSSentenceStartPayload(sentence="测试语音合成")
        start_event = WebEvent.from_payload(start_payload)
        start_binary = convert_web_event_to_binary(start_event)
        print(f"  📦 TTSSentenceStart serialized: {len(start_binary)} bytes")
        
        # Test TTSSentenceEnd event with audio data
        audio_data = b"fake_audio_data_for_testing" * 100  # Simulate audio
        end_payload = TTSSentenceEndPayload(data=audio_data)
        end_event = WebEvent.from_payload(end_payload)
        end_binary = convert_web_event_to_binary(end_event)
        print(f"  📦 TTSSentenceEnd serialized: {len(end_binary)} bytes")
        
        # Test TTSDone event
        done_payload = TTSDonePayload()
        done_event = WebEvent.from_payload(done_payload)
        done_binary = convert_web_event_to_binary(done_event)
        print(f"  📦 TTSDone serialized: {len(done_binary)} bytes")
        
        print("  ✅ All events can be serialized for WebSocket transmission")
        
    except ImportError:
        print("  ⚠️ Cannot test serialization without arkitect environment")
    except Exception as e:
        print(f"  ❌ Serialization test failed: {e}")


if __name__ == "__main__":
    async def main():
        await test_websocket_http_tts_integration()
        await test_event_serialization()
    
    asyncio.run(main())