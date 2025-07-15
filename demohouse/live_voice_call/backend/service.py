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

from typing import AsyncIterable, List, Union, Optional
from enum import Enum

from pydantic import BaseModel
from arkitect.core.component.asr import ASRFullServerResponse, AsyncASRClient
from arkitect.core.component.llm import BaseChatLanguageModel
from arkitect.core.component.llm.model import ArkMessage
from arkitect.core.component.tts import AsyncTTSClient, AudioParams, ConnectionParams
from arkitect.core.component.tts.constants import (
    EventSessionFinished,
    EventTTSSentenceEnd,
    EventTTSSentenceStart,
)
from tts_http_client import SingletonHTTPTTSManager, TTSConfig, tts_manager
from arkitect.telemetry.logger import INFO, ERROR
from event import *
from prompt import VoiceBotPrompt
from dify_client import DifyClient
import time

StateInProgress = "InProgress"
StateIdle = "Idle"
StateOpening = "Opening"
# asr continuous detection no input duration, empirical value
ASRInterval = 2000
# Default tts live_voice_call
DEFAULT_SPEAKER = "zh_female_sajiaonvyou_moon_bigtts"


class LLMProvider(Enum):
    """Enumeration of available LLM providers."""
    ARK = "ark"
    DIFY = "dify"


class VoiceBotService(BaseModel):
    asr_client: Optional[AsyncASRClient] = None
    tts_client: Optional[AsyncTTSClient] = None
    http_tts_manager: Optional[SingletonHTTPTTSManager] = None
    use_http_tts: bool = True  # Flag to use HTTP TTS instead of WebSocket
    llm_ep_id: str
    state: str = StateIdle
    tts_speaker: str = DEFAULT_SPEAKER  # TTS speaker
    tts_cluster: Optional[str] = None  # TTS cluster for load balancing
    tts_voice_type: Optional[str] = None  # TTS voice type

    """
    config vars
    """
    asr_app_key: str
    asr_access_key: str
    tts_app_key: str
    tts_access_key: str
    
    # LLM Provider Configuration
    llm_provider: LLMProvider = LLMProvider.ARK
    dify_api_key: Optional[str] = None
    dify_base_url: str = "https://api.dify.ai"
    dify_client: Optional[DifyClient] = None

    history_messages: List[ArkMessage] = []  # Store historical dialogue information

    asr_buffer: str = ""  # Reservoir asr recognition result
    asr_no_input_duration: int = 0  # Cumulated no live_voice_call recognition duration
    asr_last_duration: int = 0  # Last asr recognition duration

    # Store user parameters
    current_question: str = ""
    current_answer: str = ""
    current_user_responds: str = ""
    current_question_stem: str = ""
    current_student_name: str = ""
    current_question_category: str = ""
    
    # Opening related configuration
    enable_opening: bool = True
    opening_timeout: int = 5
    opening_generated: bool = False
    _should_generate_opening: bool = False

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    async def init(self):
        """
        Initialize the TTS, ASR, and LLM clients.
        """
        # Initialize ASR client
        self.asr_client = AsyncASRClient(
            app_key=self.asr_app_key, access_key=self.asr_access_key
        )
        await self.asr_client.init()
        
        if self.use_http_tts:
            # Initialize HTTP TTS manager (singleton)
            self.http_tts_manager = tts_manager
            await self.http_tts_manager.initialize(
                app_id=self.tts_app_key,
                access_token=self.tts_access_key,
                cluster=self.tts_cluster or "volcano_icl",
                voice_type=self.tts_voice_type or "S_pic297Bs1"
            )
            INFO(f"[INIT] ✅ HTTP TTS initialized with cluster={self.tts_cluster}, voice_type={self.tts_voice_type}")
        else:
            # Fallback to WebSocket TTS (original implementation)
            connection_params = ConnectionParams(
                speaker=self.tts_speaker, 
                audio_params=AudioParams()
            )
            
            # Add cluster and voice_type if provided
            if self.tts_cluster:
                connection_params.cluster = self.tts_cluster
            if self.tts_voice_type:
                connection_params.voice_type = self.tts_voice_type
                
            self.tts_client = AsyncTTSClient(
                app_key=self.tts_app_key,
                access_key=self.tts_access_key,
                connection_params=connection_params,
            )
            await self.tts_client.init()
        
        # Initialize Dify client if using Dify provider
        if self.llm_provider == LLMProvider.DIFY and self.dify_api_key:
            self.dify_client = DifyClient(
                api_key=self.dify_api_key,
                base_url=self.dify_base_url
            )
            INFO(f"Initialized Dify client with base URL: {self.dify_base_url}")

    async def handler_loop(
        self, inputs: AsyncIterable[WebEvent]
    ) -> AsyncIterable[WebEvent]:
        """
        Main loop for handling input events and generating responses.
        """
        asr_responses = await self.handle_input_event(inputs)
        
        # Create an async iterator for handling both ASR and opening generation
        async def combined_handler():
            async for asr_recognized in self.handle_asr_response(asr_responses):
                # Check if we should generate opening first
                if self._should_generate_opening:
                    self._should_generate_opening = False
                    INFO("[HANDLER] 🎬 Triggering opening generation")
                    async for opening_event in self.generate_opening():
                        yield opening_event
                
                # set state into InProgress
                self.state = StateInProgress
                yield WebEvent.from_payload(asr_recognized)
                
                llm_stream_rsp = self.stream_llm_chat(asr_recognized.sentence)
                async for payload in self.handle_tts_response(llm_stream_rsp):
                    yield WebEvent.from_payload(payload)
                # recreate the asr and tts client
                self.state = StateIdle
        
        # Start the combined handler
        async for event in combined_handler():
            yield event
            
    async def generate_opening(self) -> AsyncIterable[WebEvent]:
        """
        Generate opening greeting based on question and student name.
        """
        if not self.enable_opening or self.opening_generated:
            return
        
        if not self.current_question or not self.current_student_name:
            INFO("[OPENING] ⚠️ Missing required parameters for opening generation")
            return
            
        INFO(f"[OPENING] 🎬 Starting opening generation for student: {self.current_student_name}")
        
        # Set state to Opening
        self.state = StateOpening
        self.opening_generated = True
        
        # Send opening start event
        yield WebEvent.from_payload(OpeningStartPayload(
            question=self.current_question,
            student_name=self.current_student_name
        ))
        
        try:
            # Generate opening text using Dify workflow
            opening_text = await self._generate_opening_text()
            
            if opening_text:
                # Convert opening text to speech
                async for payload in self.handle_tts_response(self._async_text_generator(opening_text)):
                    yield WebEvent.from_payload(payload)
                    
                # Send opening done event
                yield WebEvent.from_payload(OpeningDonePayload(success=True))
                INFO(f"[OPENING] ✅ Opening generation completed successfully")
            else:
                # Use default opening if generation fails
                default_opening = f"你好{self.current_student_name}，我是你的学习助手乔青青，让我们一起来解决这个问题吧！"
                async for payload in self.handle_tts_response(self._async_text_generator(default_opening)):
                    yield WebEvent.from_payload(payload)
                yield WebEvent.from_payload(OpeningDonePayload(success=False, error="Using default opening"))
                INFO(f"[OPENING] ⚠️ Using default opening due to generation failure")
                
        except Exception as e:
            INFO(f"[OPENING] ❌ Opening generation failed: {str(e)}")
            yield WebEvent.from_payload(OpeningDonePayload(success=False, error=str(e)))
        
        finally:
            # Return to idle state
            self.state = StateIdle

    async def handle_input_event(
        self, inputs: AsyncIterable[WebEvent]
    ) -> AsyncIterable[ASRFullServerResponse]:
        """
        Handle input events and generate ASR responses.
        """

        async def async_gen() -> AsyncIterable[bytes]:
            async for input_event in inputs:
                # Only log non-audio events to reduce noise
                if input_event.event != USER_AUDIO:
                    INFO(
                        f"[EVENT_RECEIVED] 📨 {input_event.event} | payload_type={type(input_event.payload).__name__}"
                    )
                
                
                # Handle configuration events even when service is InProgress
                if input_event.event == BOT_UPDATE_CONFIG and isinstance(
                    input_event.payload, BotUpdateConfigPayload
                ):
                    config_updated = False
                    
                    # Update speaker if provided
                    if input_event.payload.speaker is not None:
                        INFO(f"[CONFIG] 🔧 Updating TTS speaker: {input_event.payload.speaker}")
                        self.tts_speaker = input_event.payload.speaker
                        config_updated = True
                    
                    # Update cluster if provided
                    if input_event.payload.cluster is not None:
                        INFO(f"[CONFIG] 🔧 Updating TTS cluster: {input_event.payload.cluster}")
                        self.tts_cluster = input_event.payload.cluster
                        config_updated = True
                    
                    # Update voice_type if provided
                    if input_event.payload.voice_type is not None:
                        INFO(f"[CONFIG] 🔧 Updating TTS voice_type: {input_event.payload.voice_type}")
                        self.tts_voice_type = input_event.payload.voice_type
                        config_updated = True
                    
                    # Reinitialize TTS client if any config was updated
                    if config_updated:
                        INFO("[CONFIG] 🔄 Reinitializing TTS client with new configuration")
                        
                        if self.use_http_tts and self.http_tts_manager:
                            # Update HTTP TTS configuration
                            await self.http_tts_manager.update_voice_config(
                                cluster=self.tts_cluster,
                                voice_type=self.tts_voice_type
                            )
                            INFO(f"[CONFIG] ✅ HTTP TTS updated: cluster={self.tts_cluster}, voice_type={self.tts_voice_type}")
                        else:
                            # Fallback to WebSocket TTS update
                            if self.tts_client and getattr(self.tts_client, 'inited', False):
                                await self.tts_client.close()
                            
                            connection_params = ConnectionParams(
                                speaker=self.tts_speaker,
                                audio_params=AudioParams()
                            )
                            
                            if self.tts_cluster:
                                connection_params.cluster = self.tts_cluster
                            if self.tts_voice_type:
                                connection_params.voice_type = self.tts_voice_type
                                
                            self.tts_client = AsyncTTSClient(
                                app_key=self.tts_app_key,
                                access_key=self.tts_access_key,
                                connection_params=connection_params,
                            )
                            await self.tts_client.init()
                    
                    continue
                elif input_event.event == USER_PARAMETERS and isinstance(
                    input_event.payload, UserParametersPayload
                ):
                    # Store the six parameters - allowed even when InProgress
                    INFO(f"[PARAM_DEBUG] Before update - current_user_responds: '{self.current_user_responds}'")
                    self.current_question = input_event.payload.question
                    self.current_answer = input_event.payload.answer
                    self.current_user_responds = input_event.payload.user_responds
                    self.current_question_stem = input_event.payload.question_stem
                    self.current_student_name = input_event.payload.student_name
                    self.current_question_category = input_event.payload.question_category
                    INFO(f"[PARAM_RECEIVED] ✅ User parameters stored successfully:")
                    INFO(f"  📝 question: '{self.current_question}'")
                    INFO(f"  ✅ answer: '{self.current_answer}'")
                    INFO(f"  🗣️ user_responds: '{self.current_user_responds}'")
                    INFO(f"  📋 question_stem: '{self.current_question_stem}'")
                    INFO(f"  👤 student_name: '{self.current_student_name}'")
                    INFO(f"  🏷️ question_category: '{self.current_question_category}'")
                    
                    # Check if we should trigger opening generation
                    if (self.enable_opening and not self.opening_generated and 
                        self.current_question and self.current_student_name and 
                        self.state == StateIdle):
                        INFO("[PARAM_RECEIVED] 🎬 Parameters complete, will generate opening")
                        self._should_generate_opening = True
                    
                    continue
                
                # For audio processing, check if service is busy (including Opening state)
                if self.state not in [StateIdle]:
                    INFO(f"[AUDIO_BLOCKED] 🚫 Service is {self.state}, ignoring audio input")
                    continue
                elif not self.asr_client.inited:
                    INFO("need recreate asr conn")
                    await self.asr_client.init()
                
                # Process audio data
                if input_event.event == USER_AUDIO and input_event.data:
                    yield input_event.data

        return self.asr_client.stream_asr(async_gen())

    async def handle_asr_response(
        self, asr_responses: AsyncIterable[ASRFullServerResponse]
    ) -> AsyncIterable[SentenceRecognizedPayload]:
        """
        Handle ASR responses and generate recognized sentences.
        """
        async for response in asr_responses:
            if self.state == StateIdle:
                if self.asr_buffer and self.asr_no_input_duration > ASRInterval:
                    # Update user_responds with ASR result
                    INFO(f"[ASR_OVERRIDE] ⚠️ ASR will override user_responds:")
                    INFO(f"  OLD user_responds: '{self.current_user_responds}'")
                    INFO(f"  NEW user_responds: '{self.asr_buffer}'")
                    self.current_user_responds = self.asr_buffer
                    yield SentenceRecognizedPayload(sentence=self.asr_buffer)
                    self.asr_buffer = ""
                    self.asr_no_input_duration = 0
                    self.asr_last_duration = 0
                    await self.asr_client.close()
                elif response.result and response.result.text:
                    # buffering
                    increment_len = len(response.result.text) - len(self.asr_buffer)
                    self.asr_buffer = response.result.text
                    if increment_len > 0:
                        self.asr_last_duration = response.audio.duration
                    else:
                        self.asr_no_input_duration = (
                            response.audio.duration - self.asr_last_duration
                        )
                    # Only log when there's actual content change
                    if increment_len > 0:
                        INFO(f"[ASR] 🎤 Speech recognized: '{response.result.text}'")
                    # Skip logging for no-change ASR responses to reduce noise
            else:
                INFO("service is InProgress, will ignore the newer asr response")
                continue

    async def handle_tts_response(
        self, llm_output: AsyncIterable[str]
    ) -> AsyncIterable[
        Union[TTSSentenceStartPayload, TTSSentenceEndPayload, TTSDonePayload]
    ]:
        """
        Handle TTS responses and generate TTS events.
        """
        if self.use_http_tts and self.http_tts_manager:
            # Use HTTP TTS implementation
            async for payload in self._handle_http_tts_response(llm_output):
                yield payload
        else:
            # Use WebSocket TTS implementation (fallback)
            async for payload in self._handle_websocket_tts_response(llm_output):
                yield payload
    
    async def _handle_http_tts_response(
        self, llm_output: AsyncIterable[str]
    ) -> AsyncIterable[
        Union[TTSSentenceStartPayload, TTSSentenceEndPayload, TTSDonePayload]
    ]:
        """Handle TTS responses using HTTP client."""
        full_text = ""
        
        # Collect all LLM output chunks into a single text
        async for chunk in llm_output:
            if chunk:
                full_text += chunk
        
        if not full_text.strip():
            INFO("[HTTP_TTS] ⚠️ No text to synthesize")
            yield TTSDonePayload()
            return
        
        # Send sentence start event
        INFO(f"[HTTP_TTS] 🎤 Sentence start: '{full_text[:50]}{'...' if len(full_text) > 50 else ''}'")
        yield TTSSentenceStartPayload(sentence=full_text)
        
        try:
            # Synthesize the full text
            tts_response = await self.http_tts_manager.synthesize(full_text)
            
            if tts_response.success and tts_response.audio_data:
                INFO(f"[HTTP_TTS] ✅ Synthesis successful: {len(tts_response.audio_data)} bytes")
                yield TTSSentenceEndPayload(data=tts_response.audio_data)
            else:
                ERROR(f"[HTTP_TTS] ❌ Synthesis failed: {tts_response.error_message}")
                # Send empty audio data to avoid blocking the client
                yield TTSSentenceEndPayload(data=b"")
        
        except Exception as e:
            ERROR(f"[HTTP_TTS] 💥 Exception during synthesis: {str(e)}")
            yield TTSSentenceEndPayload(data=b"")
        
        finally:
            INFO("[HTTP_TTS] 🏁 TTS session finished")
            yield TTSDonePayload()
    
    async def _handle_websocket_tts_response(
        self, llm_output: AsyncIterable[str]
    ) -> AsyncIterable[
        Union[TTSSentenceStartPayload, TTSSentenceEndPayload, TTSDonePayload]
    ]:
        """Handle TTS responses using WebSocket client (original implementation)."""
        buffer = bytearray()
        total_audio_chunks = 0
        total_audio_bytes = 0
        
        if not self.tts_client or not getattr(self.tts_client, 'inited', False):
            INFO("[TTS] 🔄 Recreating TTS client")
            connection_params = ConnectionParams(
                speaker=self.tts_speaker,
                audio_params=AudioParams()
            )
            
            if self.tts_cluster:
                connection_params.cluster = self.tts_cluster
            if self.tts_voice_type:
                connection_params.voice_type = self.tts_voice_type
                
            self.tts_client = AsyncTTSClient(
                app_key=self.tts_app_key,
                access_key=self.tts_access_key,
                connection_params=connection_params,
            )
            await self.tts_client.init()
            
        async for tts_rsp in self.tts_client.tts(
            source=llm_output, include_transcript=True
        ):
            # Only log important TTS events, not every audio chunk
            if tts_rsp.event == EventTTSSentenceStart:
                INFO(f"[TTS] 🎤 Sentence start: '{tts_rsp.transcript}'")
                yield TTSSentenceStartPayload(sentence=tts_rsp.transcript)
            elif tts_rsp.event == EventTTSSentenceEnd:
                INFO(f"[TTS] ✅ Sentence end: {len(buffer)} bytes total, {total_audio_chunks} chunks")
                yield TTSSentenceEndPayload(data=buffer)
                buffer.clear()
                total_audio_chunks = 0
                total_audio_bytes = 0
            elif tts_rsp.audio:
                buffer.extend(tts_rsp.audio)
                total_audio_chunks += 1
                total_audio_bytes += len(tts_rsp.audio)

            if tts_rsp.event == EventSessionFinished:
                INFO(f"[TTS] 🏁 Session finished")
                yield TTSDonePayload()
                await self.tts_client.close()
                break

    async def stream_llm_chat(self, text: str) -> AsyncIterable[str]:
        """
        Stream chat with the LLM and generate responses.
        """
        INFO(f"[LLM_CALL] 🚀 Starting LLM chat with provider: {self.llm_provider.value}")
        INFO(f"[LLM_CALL] 📝 ASR text input: '{text}'")
        
        if self.llm_provider == LLMProvider.DIFY:
            # Use Dify workflow
            INFO(f"[LLM_CALL] 🔄 Calling Dify workflow...")
            async for chunk in self._stream_dify_chat(text):
                yield chunk
        else:
            # Use ARK LLM (default)
            async for chunk in self._stream_ark_chat(text):
                yield chunk
    
    async def _stream_ark_chat(self, text: str) -> AsyncIterable[str]:
        """
        Stream chat with ARK LLM.
        """
        self.history_messages.append(ArkMessage(**{"role": "user", "content": text}))

        llm = BaseChatLanguageModel(
            template=VoiceBotPrompt(),
            messages=self.history_messages,
            endpoint_id=self.llm_ep_id,
        )
        completion_buffer = ""

        async for chunk in llm.astream():
            if chunk.choices and chunk.choices[0].delta:
                yield chunk.choices[0].delta.content
                completion_buffer += chunk.choices[0].delta.content

        if completion_buffer:
            self.history_messages.append(
                ArkMessage(**{"role": "assistant", "content": completion_buffer})
            )
    
    async def _stream_dify_chat(self, text: str) -> AsyncIterable[str]:
        """
        Stream chat with Dify workflow.
        """
        if not self.dify_client:
            raise ValueError("Dify client not initialized")
        
        # Prepare inputs with all user parameters
        INFO(f"[DIFY_PREPARE] 🔍 Checking current parameter state before Dify call:")
        INFO(f"  📝 question: '{self.current_question}' (len: {len(self.current_question)})")
        INFO(f"  ✅ answer: '{self.current_answer}' (len: {len(self.current_answer)})")
        INFO(f"  🗣️ user_responds: '{self.current_user_responds}' (len: {len(self.current_user_responds)})")
        INFO(f"  📋 question_stem: '{self.current_question_stem}' (len: {len(self.current_question_stem)})")
        INFO(f"  👤 student_name: '{self.current_student_name}' (len: {len(self.current_student_name)})")
        INFO(f"  🏷️ question_category: '{self.current_question_category}' (len: {len(self.current_question_category)})")
        
        inputs = {
            "question": self.current_question,
            "answer": self.current_answer,
            "user_responds": self.current_user_responds,
            "question_stem": self.current_question_stem,
            "student_name": self.current_student_name,
            "question_category": self.current_question_category,
        }
        
        # Validate inputs for empty values
        empty_params = [k for k, v in inputs.items() if not v or v.strip() == ""]
        if empty_params:
            INFO(f"[DIFY_WARNING] ⚠️ Empty parameters detected: {empty_params}")
        else:
            INFO(f"[DIFY_VALIDATION] ✅ All parameters have values")
        
        # Generate timestamp for logging
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        INFO(f"[DIFY_REQUEST] {timestamp} | 🚀 Sending to Dify with inputs: {inputs}")
        
        completion_buffer = ""
        final_result = ""  # Store the final result from workflow_finished event
        
        try:
            async for chunk in self.dify_client.stream_workflow_run(
                inputs=inputs,
                user_id=f"user-{self.current_student_name or 'anonymous'}"
            ):
                if chunk:
                    # Check if this is the final result (from workflow_finished event)
                    # The Dify client now prioritizes 'result' field content
                    final_result = chunk
                    completion_buffer += chunk
            
            # Only yield the final result for TTS, not intermediate chunks
            if final_result:
                response_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                INFO(f"[DIFY_RESPONSE] {response_timestamp} | SUCCESS | Result: {final_result}")
                yield final_result
            else:
                # Fallback if no final result
                response_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                INFO(f"[DIFY_RESPONSE] {response_timestamp} | SUCCESS | Fallback result: {completion_buffer}")
                yield completion_buffer
                    
        except Exception as e:
            error_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            INFO(f"[DIFY_RESPONSE] {error_timestamp} | ERROR | {str(e)}")
            # Fallback to a simple response
            error_response = f"抱歉，我遇到了一些问题：{str(e)}"
            yield error_response
            completion_buffer = error_response
        
        # Store the conversation for context (optional)
        if completion_buffer:
            self.history_messages.append(
                ArkMessage(**{"role": "user", "content": text})
            )
            self.history_messages.append(
                ArkMessage(**{"role": "assistant", "content": completion_buffer})
            )
    
    async def _generate_opening_text(self) -> str:
        """
        Generate opening text using Dify workflow.
        """
        if not self.dify_client:
            INFO("[OPENING] ⚠️ Dify client not available, using default opening")
            return ""
        
        try:
            # Prepare inputs for opening generation
            inputs = {
                "question": self.current_question,
                "student_name": self.current_student_name,
            }
            
            INFO(f"[OPENING] 🚀 Generating opening with inputs: {inputs}")
            
            opening_text = ""
            async for chunk in self.dify_client.stream_workflow_run(
                inputs=inputs,
                user_id=f"opening-{self.current_student_name or 'anonymous'}"
            ):
                if chunk:
                    opening_text += chunk
            
            INFO(f"[OPENING] ✅ Generated opening text: '{opening_text}'")
            return opening_text.strip()
            
        except Exception as e:
            INFO(f"[OPENING] ❌ Failed to generate opening: {str(e)}")
            return ""
    
    async def _async_text_generator(self, text: str) -> AsyncIterable[str]:
        """
        Convert a single text string into an async generator for TTS processing.
        """
        yield text
        
    def should_generate_opening(self) -> bool:
        """
        Check if opening should be generated based on current state and parameters.
        """
        return (
            self.enable_opening and 
            not self.opening_generated and 
            bool(self.current_question) and 
            bool(self.current_student_name) and 
            self.state == StateIdle
        )
