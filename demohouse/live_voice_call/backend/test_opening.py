#!/usr/bin/env python3
"""
Test script for opening generation functionality.
"""
import asyncio
from service import VoiceBotService, LLMProvider
from event import UserParametersPayload, OpeningStartPayload, OpeningDonePayload, OPENING_START, OPENING_DONE


async def test_opening_generation():
    """Test opening generation workflow."""
    print("🧪 Testing opening generation functionality...")
    
    # Create service instance
    service = VoiceBotService(
        llm_ep_id="test-endpoint",
        tts_app_key="test-tts-key",
        tts_access_key="test-tts-access",
        asr_app_key="test-asr-key", 
        asr_access_key="test-asr-access",
        llm_provider=LLMProvider.DIFY,
        dify_api_key="test-dify-key",
        dify_base_url="https://api.dify.ai",
        use_http_tts=True,
        tts_cluster="volcano_icl",
        tts_voice_type="S_pic297Bs1",
        enable_opening=True,
        opening_timeout=5,
    )
    
    # Mock the dify client to avoid actual API calls
    class MockDifyClient:
        async def stream_workflow_run(self, inputs, user_id=None):
            # Mock response for opening generation
            student_name = inputs.get("student_name", "同学")
            question = inputs.get("question", "数学问题")
            mock_response = f"你好{student_name}，我是你的学习助手乔青青。今天我们一起来学习{question}，相信你一定能够掌握这个知识点！"
            yield mock_response
    
    # Mock HTTP TTS manager
    class MockHTTPTTSManager:
        async def initialize(self, **kwargs):
            pass
            
        async def synthesize(self, text):
            class MockResponse:
                success = True
                audio_data = b"mock_audio_data"
                error_message = None
            return MockResponse()
    
    # Set up mocks
    service.dify_client = MockDifyClient()
    service.http_tts_manager = MockHTTPTTSManager()
    
    # Test case 1: Check initial state
    print("✅ Test 1: Initial state")
    assert service.opening_generated == False
    assert service.enable_opening == True
    assert service.should_generate_opening() == False  # Missing parameters
    print("   Initial state correct")
    
    # Test case 2: Set parameters and check if opening should be generated
    print("✅ Test 2: Set parameters")
    service.current_question = "解一元二次方程"
    service.current_student_name = "小明"
    service.state = "Idle"
    
    assert service.should_generate_opening() == True
    print("   Parameters set correctly, should generate opening")
    
    # Test case 3: Generate opening
    print("✅ Test 3: Generate opening")
    events = []
    async for event in service.generate_opening():
        events.append(event)
        print(f"   Generated event: {event.event}")
        if hasattr(event, 'payload'):
            print(f"   Payload: {event.payload}")
    
    # Verify events
    assert len(events) >= 3, f"Expected at least 3 events, got {len(events)}"
    assert events[0].event == OPENING_START
    assert events[-1].event == OPENING_DONE
    assert service.opening_generated == True
    assert service.state == "Idle"
    print("   Opening generation completed successfully")
    
    # Test case 4: Verify opening not generated again
    print("✅ Test 4: Verify opening not generated again")
    assert service.should_generate_opening() == False
    print("   Opening not generated again (correct)")
    
    print("🎉 All tests passed! Opening generation functionality is working correctly.")


if __name__ == "__main__":
    asyncio.run(test_opening_generation())