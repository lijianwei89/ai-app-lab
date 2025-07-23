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

import struct

from arkitect.utils.binary_protocol import (
    AUDIO_ONLY_SERVER,
    FULL_SERVER_RESPONSE,
    NO_COMPRESSION,
    NO_SEQUENCE,
    NO_SERIALIZATION,
    generate_header,
    parse_request,
)
from event import *
from event import OPENING_GREETING_REQUEST


def json_payload_to_binary_response(event: WebEvent) -> bytes:
    """
    Convert a JSON-formatted WebEvent event into a binary response.

    Args:
        event (WebEvent): The WebEvent event to be converted.

    Returns:
        bytes: The generated binary response.
    """
    # Convert the event object to a JSON string and encode it as bytes
    payload_bytes = str.encode(
        event.model_dump_json(exclude_none=True, exclude_unset=True)
    )
    # Generate the response header
    rsp_bytes = bytearray(
        generate_header(
            message_type=FULL_SERVER_RESPONSE,
            message_type_specific_flags=NO_SEQUENCE,
            compression_type=NO_COMPRESSION,
        )
    )
    # Pack the payload length as a 4-byte big-endian integer and add it to the response
    rsp_bytes.extend(struct.pack(">I", len(payload_bytes)))
    # Add the payload to the response
    rsp_bytes.extend(payload_bytes)
    return rsp_bytes


def audio_to_binary_response(audio_data: bytes) -> bytes:
    """
    Convert audio data into a binary response.

    Args:
        audio_data (bytes): The audio data to be converted.

    Returns:
        bytes: The generated binary response.
    """
    # Generate the audio response header
    rsp_bytes = bytearray(
        generate_header(
            message_type=AUDIO_ONLY_SERVER,
            message_type_specific_flags=NO_SEQUENCE,
            compression_type=NO_COMPRESSION,
            serial_method=NO_SERIALIZATION,
        )
    )
    # Pack the audio data length as a 4-byte big-endian integer and add it to the response
    rsp_bytes.extend(struct.pack(">I", len(audio_data)))  # payload size(4 bytes)
    # Add the audio data to the response
    rsp_bytes.extend(audio_data)
    return rsp_bytes


# Downlink message conversion
def convert_web_event_to_binary(event: WebEvent) -> bytes:
    """
    Convert a WebEvent event into a binary response.

    Args:
        event (WebEvent): The WebEvent event to be converted.

    Returns:
        bytes: The generated binary response.
    """
    # If the event contains data, convert it to an audio binary response
    if event.data:
        return audio_to_binary_response(event.data)
    # Otherwise, convert it to a JSON binary response
    else:
        return json_payload_to_binary_response(event)


# Uplink message conversion
def convert_binary_to_web_event_to_binary(data: bytes) -> WebEvent:
    """
    Parse binary data into a WebEvent event.

    Args:
        data (bytes): The binary data to be parsed.

    Returns:
        WebEvent: The parsed WebEvent event.
    """
    from arkitect.telemetry.logger import INFO
    
    # Parse the request
    req = parse_request(data)
    INFO(f"[PARSE_DEBUG] 🔍 parse_request result type: {type(req)}")
    
    # If the parsing result is a dictionary, convert it to a WebEvent object
    if isinstance(req, dict):
        INFO(f"[PARSE_DEBUG] 📋 Dictionary parsed: {req}")
        try:
            # Extract event type and payload
            event_type = req.get('event')
            payload_data = req.get('payload', {})
            
            INFO(f"[PARSE_DEBUG] 🔍 Event type: {event_type}, payload_data: {payload_data}")
            
            # Convert payload dict to appropriate payload object based on event type
            if event_type == USER_PARAMETERS:
                from event import UserParametersPayload
                payload = UserParametersPayload(**payload_data)
                web_event = WebEvent(event=event_type, payload=payload)
            elif event_type == BOT_UPDATE_CONFIG:
                from event import BotUpdateConfigPayload
                payload = BotUpdateConfigPayload(**payload_data)
                web_event = WebEvent(event=event_type, payload=payload)
            elif event_type == OPENING_GREETING_REQUEST:
                from event import OpeningGreetingRequestPayload
                payload = OpeningGreetingRequestPayload()
                web_event = WebEvent(event=event_type, payload=payload)
            else:
                # For other events, try direct parsing
                web_event = WebEvent.parse_obj(req)
            
            INFO(f"[PARSE_DEBUG] ✅ WebEvent created: event={web_event.event}, payload_type={type(web_event.payload)}")
            return web_event
        except Exception as e:
            INFO(f"[PARSE_DEBUG] ❌ Failed to parse WebEvent: {e}")
            raise e
    # Otherwise, create a new WebEvent object containing the audio data
    else:
        INFO(f"[PARSE_DEBUG] 🎵 Creating USER_AUDIO event, data len: {len(req) if req else 0}")
        return WebEvent(event=USER_AUDIO, data=req)
