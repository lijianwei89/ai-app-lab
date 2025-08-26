#!/usr/bin/env python3
"""
Debug the TTS response format
"""
import asyncio
import aiohttp
import json
import base64

async def debug_tts():
    """Debug the exact response format"""
    
    url = "https://speech-internal.tal.com/v1/tts"
    headers = {
        "Authorization": "Bearer 200000054:bebc3b8ce075b6fd94d04407e1ed6937",
        "Content-Type": "application/json"
    }
    
    payload = {
        "voice": "volcengine:S_dwiOyLR61",
        "text": "你好，测试",
        "format": "mp3",
        "sample_rate": 24000,
        "speed": 1,
        "volume": 1,
        "pitch": 1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                
                text_content = await response.text()
                print(f"Raw response: {text_content}")
                
                if response.status == 200:
                    try:
                        data = json.loads(text_content)
                        print(f"Parsed JSON keys: {list(data.keys())}")
                        
                        # Try to find audio data
                        if "audio" in data:
                            audio = base64.b64decode(data["audio"])
                            print(f"✅ Found audio in 'audio' field: {len(audio)} bytes")
                        elif "data" in data:
                            audio = base64.b64decode(data["data"])
                            print(f"✅ Found audio in 'data' field: {len(audio)} bytes")
                        else:
                            print(f"❌ No audio field found. Available: {list(data.keys())}")
                            
                    except Exception as e:
                        print(f"❌ JSON parse error: {e}")
                        # Try as base64 string directly
                        try:
                            audio = base64.b64decode(text_content)
                            print(f"✅ Response is base64 audio: {len(audio)} bytes")
                        except:
                            print("❌ Response is neither JSON nor base64")
                else:
                    print(f"❌ HTTP error: {response.status} - {text_content}")
                    
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_tts())