# JARVIS AI Assistant V3

A local FastAPI personal assistant with NVIDIA NIM streaming chat, SQLite conversation history, and a same-origin text web interface.

## Requirements
- Python 3.10+
- NVIDIA NIM API key

## Installation
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```
Replace the placeholder API key in `.env`. Optional settings are `HOST`, `PORT`, and `HISTORY_DB_PATH`.

## Running and tests
```bash
python server.py
pip install -r requirements-dev.txt
pytest
```
Open `http://localhost:8000/app` for the Phase 4 web interface. The original `GET /` JSON response remains available.

## API
- `GET /`
- `GET /app`
- `GET /api/health`
- `POST /api/conversations`
- `GET /api/conversations`
- `GET /api/conversations/{conversation_id}`
- `DELETE /api/conversations/{conversation_id}`
- `POST /api/chat`

The frontend creates and selects conversations, loads persisted messages, consumes the existing SSE stream, and deletes conversations. It sends only the current message plus optional `conversation_id`:
```json
{"message":"Hello, JARVIS!","conversation_id":"3d90e211-377c-486d-a23a-7c01b9b4a555"}
```
The SSE contract remains:
```text
data: {"content": "Hello"}

data: [DONE]
```
Prior messages are stored and displayed but are not sent to NVIDIA. Full-history model context remains reserved for Phase 5.

## Current scope
Implemented through Phase 4: stable provider/service boundaries, NVIDIA NIM streaming, durable local conversation history, and a dependency-free vanilla HTML/CSS/JavaScript text interface.

Not implemented: voice, full-history model context, tools, authentication, browser automation, CI, or desktop packaging.
