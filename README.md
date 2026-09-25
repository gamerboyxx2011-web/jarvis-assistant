# JARVIS AI Assistant V3

A local FastAPI personal assistant with NVIDIA NIM streaming chat, SQLite full-history conversations, a same-origin web interface, and controlled push-to-talk voice mode.

## Requirements
- Python 3.10+
- NVIDIA NIM API key
- OpenAI API key for hosted STT/TTS
- Browser support for `getUserMedia` and `MediaRecorder`

## Setup and run
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python server.py
```
Set `NVIDIA_API_KEY` and `OPENAI_API_KEY`. Speech defaults are `whisper-1`, `tts-1`, voice `alloy`, and MP3 output; the `OPENAI_*` variables are configurable.

Open `http://localhost:8000/app`. Chat mode retains the text-only `POST /api/chat` flow. Voice mode records only while push-to-talk is held, stops at 60 seconds, and sends one finalized recording to the dedicated multipart `POST /api/voice` SSE pipeline.

Recordings are limited to 25 MB, held only for the request, and never persisted. The finalized transcript and completed assistant text use the existing ChatService conversation/full-history behavior. TTS emits ordered sentence or bounded-phrase audio; TTS failure preserves generated text and history.

## Test
```bash
pip install -r requirements-dev.txt
pytest
```

Implemented through Phase 6. Wake words, always-listening/VAD, realtime voice, tools, desktop packaging, and Phase 7+ behavior are out of scope.
