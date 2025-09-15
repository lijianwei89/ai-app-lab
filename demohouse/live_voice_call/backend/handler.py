# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# Licensed under the 【火山方舟】原型应用软件自用许可协议
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     https://www.volcengine.com/docs/82379/1433703
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import logging
import uuid
import time
from typing import AsyncIterable

import websockets

from arkitect.telemetry.logger import INFO
from arkitect.utils.event_loop import get_event_loop
from service import VoiceBotService, LLMProvider
from utils import *
from event import OpeningGreetingResponsePayload, WebEvent

# replace with your asr API access
ASR_ACCESS_TOKEN = "WDubf8FD7TunKdtBdzMnmLRuEzvximVu"
ASR_APP_ID = "3735242956"
# TTS configuration for internal service
TTS_ACCESS_TOKEN = "200000054:bebc3b8ce075b6fd94d04407e1ed6937"
TTS_APP_ID = "200000054"
# replace with your ark endpoint
LLM_ENDPOINT_ID = "doubao-seed-1-6-250615"
# replace with your dify API access
DIFY_API_KEY = "app-g9uued0gvSWkTfaz7n7Hs0mX"
DIFY_BASE_URL = "https://api.dify.ai"
# Opening greeting dify API access
DIFY_OPENING_API_KEY = "app-nxb7ZW4Uy9DZmeEMoE2ibTDY"
# LLM Provider: "ark" or "dify"
LLM_PROVIDER = "dify"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def handler(websocket: websockets.WebSocketCommonProtocol, path):
    """
    Asynchronous function to handle WebSocket connections.

    Args:
        websocket (websockets.WebSocketCommonProtocol): The client's WebSocket connection.
        path (str): The requested path.
    """
    # Create a VoiceBotService instance and initialize it
    service = VoiceBotService(
        llm_ep_id=LLM_ENDPOINT_ID,
        tts_app_key=TTS_APP_ID,
        tts_access_key=TTS_ACCESS_TOKEN,
        asr_app_key=ASR_APP_ID,
        asr_access_key=ASR_ACCESS_TOKEN,
        llm_provider=LLMProvider.DIFY if LLM_PROVIDER == "dify" else LLMProvider.ARK,
        dify_api_key=DIFY_API_KEY if LLM_PROVIDER == "dify" else None,
        dify_base_url=DIFY_BASE_URL,
        # Opening greeting Dify configuration
        dify_opening_api_key=DIFY_OPENING_API_KEY,
        # Enable HTTP TTS with internal service configuration
        use_http_tts=True,
        tts_cluster="volcengine",
        tts_voice_type="S_dwiOyLR61",
    )
    await service.init()
    # Send a bot ready message
    await websocket.send(
        convert_web_event_to_binary(
            WebEvent.from_payload(BotReadyPayload(session=str(uuid.uuid4())))
        )
    )

    async def async_gen(
        ws: websockets.WebSocketCommonProtocol,
    ) -> AsyncIterable[WebEvent]:
        """
        Asynchronously generate input events from the WebSocket connection.

        Args:
            ws (websockets.WebSocketCommonProtocol): The client's WebSocket connection.

        Returns:
            AsyncIterable[WebEvent]: An asynchronous generator of input events.
        """
        async for m in ws:
            input_event = convert_binary_to_web_event_to_binary(m)
            # Only log non-audio input events to reduce noise
            if input_event.event != "UserAudio":
                INFO(
                    f"[INPUT] 📥 {input_event.event} | data_len:{len(input_event.data) if input_event.data else 0}"
                )
            
            # Handle opening greeting request directly
            if input_event.event == "OpeningGreetingRequest":
                INFO(f"[OPENING_GREETING] 📨 Received opening greeting request")
                try:
                    greeting_text = await service.get_opening_greeting()
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Send the greeting text response
                    response_payload = OpeningGreetingResponsePayload(
                        text=greeting_text,
                        success=True,
                        timestamp=timestamp
                    )
                    response_event = WebEvent.from_payload(response_payload)
                    INFO(f"[OPENING_GREETING] ✅ Sending response: {greeting_text}")
                    await ws.send(convert_web_event_to_binary(response_event))
                    
                    # Also send the greeting through TTS pipeline
                    async def greeting_text_generator():
                        yield greeting_text
                    
                    # Process TTS for opening greeting
                    tts_payloads = service.handle_tts_response(greeting_text_generator())
                    async for tts_payload in tts_payloads:
                        tts_event = WebEvent.from_payload(tts_payload)
                        await ws.send(convert_web_event_to_binary(tts_event))
                        
                except Exception as e:
                    error_msg = str(e)
                    INFO(f"[OPENING_GREETING] ❌ Error: {error_msg}")
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    response_payload = OpeningGreetingResponsePayload(
                        text=f"获取开场白失败：{error_msg}",
                        success=False,
                        error=error_msg,
                        timestamp=timestamp
                    )
                    response_event = WebEvent.from_payload(response_payload)
                    await ws.send(convert_web_event_to_binary(response_event))
                continue
            
            yield input_event

    async def fetch_output(
        ws: websockets.WebSocketCommonProtocol, output_events: AsyncIterable[WebEvent]
    ) -> None:
        """
        Asynchronously fetch and send output events to the WebSocket connection.

        Args:
            ws (websockets.WebSocketCommonProtocol): The client's WebSocket connection.
            output_events (AsyncIterable[WebEvent]): An asynchronous generator of output events.
        """
        async for output_event in output_events:
            # Only log important output events, skip frequent audio events
            if output_event.event not in ['TTSSentenceEnd']:
                INFO(
                    f"[OUTPUT] 📤 {output_event.event} | data_len:{len(output_event.data) if output_event.data else 0}"
                )
            await ws.send(convert_web_event_to_binary(output_event))

    INFO(f"New connection: {websocket.remote_address}")
    try:
        # Start the handler loop and asynchronously fetch output events
        outputs = service.handler_loop(async_gen(websocket))
        await asyncio.create_task(fetch_output(websocket, outputs))
    except websockets.exceptions.ConnectionClosed as e:
        INFO(f"Connection closed: {e}")


async def main():
    """
    Main function to start the WebSocket server.
    """
    # Start the WebSocket server listening on 127.0.0.1:8889
    server = await websockets.serve(handler, host="127.0.0.1", port=8889)
    INFO("WebSocket server is running on ws://127.0.0.1:8889")
    await server.wait_closed()


if __name__ == "__main__":
    get_event_loop(main())
