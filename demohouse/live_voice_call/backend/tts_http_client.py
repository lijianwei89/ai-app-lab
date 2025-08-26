#!/usr/bin/env python3
"""
HTTP-based TTS client with cluster and voice_type support.

This implementation replaces the WebSocket-based AsyncTTSClient to provide 
proper support for cluster and voice_type parameters as demonstrated in 
the official ByteDance TTS demo.
"""

import asyncio
import base64
import json
import uuid
import time
from typing import Optional, AsyncIterable, Any, Dict
from dataclasses import dataclass
import aiohttp

# Try to import arkitect logger, fallback to print if not available
try:
    from arkitect.telemetry.logger import INFO, ERROR
except ImportError:
    def INFO(msg): print(f"INFO: {msg}")
    def ERROR(msg): print(f"ERROR: {msg}")


@dataclass
class TTSConfig:
    """TTS configuration parameters."""
    app_id: str
    access_token: str
    cluster: str = "volcano_icl"
    voice_type: str = "S_pic297Bs1"
    encoding: str = "mp3"
    speed_ratio: float = 1.0
    volume_ratio: float = 1.0
    pitch_ratio: float = 1.0
    host: str = "speech-internal.tal.com"


@dataclass
class TTSResponse:
    """TTS response with audio data and metadata."""
    audio_data: bytes
    request_id: str
    success: bool
    error_message: Optional[str] = None


class HTTPTTSClient:
    """HTTP-based TTS client supporting cluster and voice_type parameters."""
    
    def __init__(self, config: TTSConfig):
        self.config = config
        self.api_url = f"https://{config.host}/v1/tts"
        self.headers = {"Authorization": f"Bearer {config.access_token}", "Content-Type": "application/json"}
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close the HTTP client session."""
        if self._session and not self._session.closed:
            await self._session.close()
            INFO("[HTTP_TTS] 🧹 HTTP session closed")
    
    def _build_request_payload(self, text: str) -> Dict[str, Any]:
        """Build TTS request payload for internal TTS service."""
        return {
            "voice": f"{self.config.cluster}:{self.config.voice_type}",
            "text": text,
            "format": self.config.encoding,
            "sample_rate": 24000,
            "speed": int(self.config.speed_ratio),
            "volume": int(self.config.volume_ratio),
            "pitch": int(self.config.pitch_ratio)
        }
    
    async def synthesize_text(self, text: str) -> TTSResponse:
        """Synthesize text to speech via HTTP API."""
        if not text.strip():
            return TTSResponse(
                audio_data=b"",
                request_id="",
                success=False,
                error_message="Empty text provided"
            )
        
        request_payload = self._build_request_payload(text)
        request_id = str(uuid.uuid4())
        
        INFO(f"[HTTP_TTS] 🚀 Synthesizing text (reqid={request_id[:8]}): '{text[:50]}{'...' if len(text) > 50 else ''}'")
        INFO(f"[HTTP_TTS] 🔧 Config: cluster={self.config.cluster}, voice_type={self.config.voice_type}")
        
        try:
            session = await self._get_session()
            start_time = time.time()
            
            async with session.post(
                self.api_url,
                data=json.dumps(request_payload),
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30.0)
            ) as response:
                duration = time.time() - start_time
                
                if response.status != 200:
                    error_msg = f"HTTP {response.status}: {await response.text()}"
                    ERROR(f"[HTTP_TTS] ❌ Request failed: {error_msg}")
                    return TTSResponse(
                        audio_data=b"",
                        request_id=request_id,
                        success=False,
                        error_message=error_msg
                    )
                
                response_data = await response.json()
                
                # Check for internal TTS service format with nested data
                if "data" in response_data and isinstance(response_data["data"], dict):
                    data_obj = response_data["data"]
                    if "audio" in data_obj:
                        audio_data = base64.b64decode(data_obj["audio"])
                    else:
                        error_msg = f"No audio field in data object: {list(data_obj.keys())}"
                        ERROR(f"[HTTP_TTS] ❌ {error_msg}")
                        return TTSResponse(
                            audio_data=b"",
                            request_id=request_id,
                            success=False,
                            error_message=error_msg
                        )
                elif "audio" in response_data:
                    audio_data = base64.b64decode(response_data["audio"])
                elif "data" in response_data:
                    audio_data = base64.b64decode(response_data["data"])
                else:
                    error_msg = f"No audio data in response: {list(response_data.keys())}"
                    ERROR(f"[HTTP_TTS] ❌ {error_msg}")
                    return TTSResponse(
                        audio_data=b"",
                        request_id=request_id,
                        success=False,
                        error_message=error_msg
                    )
                
                INFO(f"[HTTP_TTS] ✅ Synthesis successful in {duration:.2f}s: {len(audio_data)} bytes")
                
                return TTSResponse(
                    audio_data=audio_data,
                    request_id=request_id,
                    success=True
                )
                
        except asyncio.TimeoutError:
            error_msg = "Request timeout"
            ERROR(f"[HTTP_TTS] ⏰ {error_msg}")
            return TTSResponse(
                audio_data=b"",
                request_id=request_id,
                success=False,
                error_message=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            ERROR(f"[HTTP_TTS] 💥 {error_msg}")
            return TTSResponse(
                audio_data=b"",
                request_id=request_id,
                success=False,
                error_message=error_msg
            )
    
    async def stream_synthesize(self, text_stream: AsyncIterable[str]) -> AsyncIterable[TTSResponse]:
        """Stream synthesis for multiple text chunks."""
        async for text in text_stream:
            if text.strip():
                response = await self.synthesize_text(text)
                yield response


class SingletonHTTPTTSManager:
    """Singleton HTTP TTS manager supporting cluster and voice_type."""
    
    _instance: Optional['SingletonHTTPTTSManager'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.client: Optional[HTTPTTSClient] = None
            self.current_config: Optional[TTSConfig] = None
            SingletonHTTPTTSManager._initialized = True
    
    async def initialize(self, app_id: str, access_token: str, 
                        cluster: str = "volcano_icl", 
                        voice_type: str = "S_pic297Bs1") -> bool:
        """Initialize TTS client with configuration."""
        new_config = TTSConfig(
            app_id=app_id,
            access_token=access_token,
            cluster=cluster,
            voice_type=voice_type
        )
        
        # Check if config changed
        if (self.current_config is None or 
            self.current_config.cluster != new_config.cluster or
            self.current_config.voice_type != new_config.voice_type or
            self.current_config.app_id != new_config.app_id or
            self.current_config.access_token != new_config.access_token):
            
            # Close existing client
            if self.client:
                await self.client.close()
            
            # Create new client
            self.client = HTTPTTSClient(new_config)
            self.current_config = new_config
            
            INFO(f"[TTS_MANAGER] ✅ Initialized with cluster={cluster}, voice_type={voice_type}")
            return True
        
        return False
    
    async def update_voice_config(self, cluster: Optional[str] = None, 
                                 voice_type: Optional[str] = None) -> bool:
        """Update voice configuration."""
        if not self.current_config:
            raise RuntimeError("TTS manager not initialized")
        
        new_cluster = cluster or self.current_config.cluster
        new_voice_type = voice_type or self.current_config.voice_type
        
        return await self.initialize(
            app_id=self.current_config.app_id,
            access_token=self.current_config.access_token,
            cluster=new_cluster,
            voice_type=new_voice_type
        )
    
    async def synthesize(self, text: str) -> TTSResponse:
        """Synthesize text using current configuration."""
        if not self.client:
            raise RuntimeError("TTS manager not initialized")
        
        return await self.client.synthesize_text(text)
    
    async def stream_synthesize(self, text_stream: AsyncIterable[str]) -> AsyncIterable[TTSResponse]:
        """Stream synthesis for text chunks."""
        if not self.client:
            raise RuntimeError("TTS manager not initialized")
        
        async for response in self.client.stream_synthesize(text_stream):
            yield response
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.client:
            await self.client.close()
            self.client = None
            self.current_config = None
            INFO("[TTS_MANAGER] 🧹 Cleaned up resources")


# Global singleton instance
tts_manager = SingletonHTTPTTSManager()