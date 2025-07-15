#!/usr/bin/env python3
"""
Singleton-based TTS test using cluster and voice_type parameters.

This test demonstrates a new TTS invocation strategy that aligns with the 
official ByteDance TTS demo, using cluster and voice_type as primary parameters.
"""

import asyncio
import time
from typing import Optional, AsyncIterable
from arkitect.core.component.tts import AsyncTTSClient, AudioParams, ConnectionParams
from arkitect.core.component.tts.constants import EventTTSSentenceStart, EventTTSSentenceEnd, EventSessionFinished


class SingletonTTSManager:
    """Singleton TTS manager using cluster and voice_type strategy."""
    
    _instance: Optional['SingletonTTSManager'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.tts_client: Optional[AsyncTTSClient] = None
            self.current_cluster: Optional[str] = None
            self.current_voice_type: Optional[str] = None
            self.app_key: Optional[str] = None
            self.access_key: Optional[str] = None
            SingletonTTSManager._initialized = True
    
    async def initialize(self, app_key: str, access_key: str, 
                        cluster: str = "volcano_icl", 
                        voice_type: str = "S_pic297Bs1"):
        """Initialize TTS client with cluster and voice_type parameters."""
        self.app_key = app_key
        self.access_key = access_key
        
        await self._create_client(cluster, voice_type)
        print(f"✅ TTS Manager initialized with cluster={cluster}, voice_type={voice_type}")
    
    async def _create_client(self, cluster: str, voice_type: str):
        """Create TTS client with specified parameters."""
        if self.tts_client and getattr(self.tts_client, 'inited', False):
            await self.tts_client.close()
        
        # Use voice_type as speaker for backwards compatibility
        connection_params = ConnectionParams(
            speaker=voice_type,  # Map voice_type to speaker
            audio_params=AudioParams(),
            cluster=cluster,
            voice_type=voice_type
        )
        
        self.tts_client = AsyncTTSClient(
            app_key=self.app_key,
            access_key=self.access_key,
            connection_params=connection_params,
        )
        
        await self.tts_client.init()
        self.current_cluster = cluster
        self.current_voice_type = voice_type
    
    async def update_voice(self, cluster: str = None, voice_type: str = None):
        """Update voice parameters and reinitialize client if needed."""
        new_cluster = cluster or self.current_cluster
        new_voice_type = voice_type or self.current_voice_type
        
        if new_cluster != self.current_cluster or new_voice_type != self.current_voice_type:
            print(f"🔄 Updating voice: cluster={new_cluster}, voice_type={new_voice_type}")
            await self._create_client(new_cluster, new_voice_type)
            return True
        return False
    
    async def synthesize_text(self, text: str) -> bytes:
        """Synthesize text and return audio data."""
        if not self.tts_client or not getattr(self.tts_client, 'inited', False):
            raise RuntimeError("TTS client not initialized")
        
        async def text_stream():
            yield text
        
        audio_buffer = bytearray()
        
        async for tts_response in self.tts_client.tts(source=text_stream()):
            if tts_response.event == EventTTSSentenceStart:
                print(f"🎤 TTS Start: {tts_response.transcript}")
            elif tts_response.audio:
                audio_buffer.extend(tts_response.audio)
            elif tts_response.event == EventTTSSentenceEnd:
                print(f"✅ TTS End: {len(audio_buffer)} bytes")
            elif tts_response.event == EventSessionFinished:
                print("🏁 TTS Session Finished")
                break
        
        return bytes(audio_buffer)
    
    async def cleanup(self):
        """Cleanup TTS client."""
        if self.tts_client and getattr(self.tts_client, 'inited', False):
            await self.tts_client.close()
            print("🧹 TTS client cleaned up")


async def test_tts_strategy():
    """Test the new TTS invocation strategy."""
    print("🚀 Starting TTS Singleton Strategy Test")
    print("=" * 50)
    
    # Configuration from tts_http_demo.py
    APP_KEY = "3735242956"
    ACCESS_KEY = "WDubf8FD7TunKdtBdzMnmLRuEzvximVu"
    DEFAULT_CLUSTER = "volcano_icl"
    DEFAULT_VOICE_TYPE = "S_pic297Bs1"
    
    # Test text
    test_text = "您好，这是一个TTS测试。"
    
    try:
        # Get singleton instance
        tts_manager = SingletonTTSManager()
        
        # Test 1: Initialize with default parameters
        print("\n📋 Test 1: Initialize with default parameters")
        await tts_manager.initialize(
            app_key=APP_KEY,
            access_key=ACCESS_KEY,
            cluster=DEFAULT_CLUSTER,
            voice_type=DEFAULT_VOICE_TYPE
        )
        
        # Test 2: Synthesize text
        print(f"\n📋 Test 2: Synthesize text: '{test_text}'")
        start_time = time.time()
        audio_data = await tts_manager.synthesize_text(test_text)
        duration = time.time() - start_time
        
        print(f"✅ Synthesis completed in {duration:.2f}s, audio size: {len(audio_data)} bytes")
        
        # Test 3: Update voice parameters
        print("\n📋 Test 3: Update voice parameters")
        updated = await tts_manager.update_voice(voice_type="zh_female_sajiaonvyou_moon_bigtts")
        print(f"Voice updated: {updated}")
        
        # Test 4: Synthesize with new voice
        print(f"\n📋 Test 4: Synthesize with new voice: '{test_text}'")
        start_time = time.time()
        audio_data_2 = await tts_manager.synthesize_text(test_text)
        duration = time.time() - start_time
        
        print(f"✅ Synthesis completed in {duration:.2f}s, audio size: {len(audio_data_2)} bytes")
        
        # Test 5: Verify singleton behavior
        print("\n📋 Test 5: Verify singleton behavior")
        tts_manager_2 = SingletonTTSManager()
        print(f"Same instance: {tts_manager is tts_manager_2}")
        print(f"Current cluster: {tts_manager_2.current_cluster}")
        print(f"Current voice_type: {tts_manager_2.current_voice_type}")
        
        # Cleanup
        await tts_manager.cleanup()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_tts_strategy())