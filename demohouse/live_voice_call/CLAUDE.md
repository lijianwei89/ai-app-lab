# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a live voice call application built with Python backend and React/TypeScript frontend. It enables real-time voice conversations with an AI character named "乔青青" (Qiao Qingqing) using ByteDance's Doubao AI models.

**Key Technologies:**
- Backend: Python with arkitect framework, WebSocket server, ASR/TTS/LLM integration
- Frontend: React/TypeScript with Modern.js framework, WebSocket client, audio processing
- AI Services: Doubao ASR (speech recognition), Doubao TTS (text-to-speech), Doubao LLM or Dify workflow

## Common Development Commands

### Backend (Python)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install poetry==1.6.1
poetry install
poetry run python -m handler  # Start WebSocket server on ws://127.0.0.1:8888
```

### Frontend (React/TypeScript)
```bash
cd frontend
pnpm install
pnpm run dev      # Start development server on http://localhost:8080
pnpm run build    # Build for production
pnpm run lint     # Run Biome linter
pnpm run lint:fix # Fix linting issues
```

### Testing
```bash
# Backend tests
cd backend
poetry run python -m pytest

# Frontend tests (if available)
cd frontend
pnpm test
```

## Architecture Overview

### Backend Architecture
- **handler.py**: WebSocket server entry point, handles connections and message routing
- **service.py**: Core `VoiceBotService` class managing the conversation flow
- **event.py**: Pydantic models for WebSocket events and payloads
- **dify_client.py**: HTTP client for Dify workflow API integration
- **utils.py**: Binary protocol encoding/decoding utilities
- **prompt.py**: LLM prompt templates

### Frontend Architecture
- **Modern.js framework**: React SSR/SPA framework with Rspack bundler
- **src/utils/voice_bot_service.ts**: WebSocket client with audio processing
- **src/components/**: React components organized by feature
  - `AudioChatProvider/`: Audio recording and playback state management
  - `AudioChatServiceProvider/`: WebSocket service and configuration
- **src/types.ts**: TypeScript type definitions for WebSocket protocol

### WebSocket Protocol
The application uses a custom binary protocol over WebSocket:
- **Header**: 4 bytes (protocol version, message type, serialization, compression)
- **Payload**: JSON or binary data depending on message type
- **Message Types**:
  - `0b0001`: Full client request (JSON)
  - `0b0010`: Audio only request (binary)
  - `0b1001`: Full server response (JSON)

### Key Event Flow
1. **Connection**: Client connects → Server sends `BotReady`
2. **Configuration**: Client sends `BotUpdateConfig` (speaker selection)
3. **Parameters**: Client sends `UserParameters` (question context)
4. **Audio Input**: Client streams audio → Server processes via ASR
5. **Recognition**: Server sends `SentenceRecognized` → enters `InProgress` state
6. **LLM Processing**: Server calls LLM/Dify → generates response
7. **Audio Output**: Server sends `TTSSentenceStart` → audio chunks → `TTSDone`
8. **Reset**: Server returns to `Idle` state

## Configuration Requirements

### Backend Environment Variables
```bash
export ARK_API_KEY={YOUR_API_KEY}
```

### Backend Configuration (handler.py)
```python
ASR_ACCESS_TOKEN = "{YOUR_ASR_ACCESS_TOKEN}"
ASR_APP_ID = "{YOUR_ASR_APP_ID}"
TTS_ACCESS_TOKEN = "{YOUR_TTS_ACCESS_TOKEN}"
TTS_APP_ID = "{YOUR_TTS_APP_ID}"
LLM_ENDPOINT_ID = "{YOUR_ARK_LLM_ENDPOINT_ID}"
DIFY_API_KEY = "app-..."  # If using Dify provider
DIFY_BASE_URL = "https://api.dify.ai"
LLM_PROVIDER = "dify"  # or "ark"
```

## Development Notes

### State Management
- Backend service has two states: `Idle` and `InProgress`
- Audio input is blocked during `InProgress` state
- Configuration events (`BotUpdateConfig`, `UserParameters`) are processed regardless of state

### Audio Processing
- Frontend uses Web Audio API for real-time audio playback
- Backend buffers audio chunks and plays them sequentially
- TTS audio is streamed in chunks to minimize latency

### LLM Integration
- Supports both ARK LLM and Dify workflow providers
- Dify integration includes parameter passing and streaming response handling
- ARK integration maintains conversation history

### Error Handling
- WebSocket connection errors trigger automatic cleanup
- LLM failures fall back to error responses
- Audio processing errors reset the audio pipeline

## Important Files to Understand

- **backend/service.py:110-127**: Main event loop handling input/output flow
- **backend/handler.py:44-131**: WebSocket connection management
- **frontend/src/utils/voice_bot_service.ts**: Client-side WebSocket and audio handling
- **backend/event.py**: Complete event type definitions
- **backend/dify_client.py**: Dify API streaming implementation