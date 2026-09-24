# JARVIS AI Assistant V3

A local FastAPI backend for a personal AI assistant with NVIDIA NIM streaming chat and SQLite conversation history.

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

## API

- `GET /`
- `GET /api/health`
- `POST /api/conversations`
- `GET /api/conversations`
- `GET /api/conversations/{conversation_id}`
- `DELETE /api/conversations/{conversation_id}`
- `POST /api/chat`

Create a conversation, then pass its ID to chat:

```json
{
  "message": "Hello, JARVIS!",
  "conversation_id": "3d90e211-377c-486d-a23a-7c01b9b4a555",
  "temperature": 0.7,
  "max_tokens": 150
}
```

In Phase 3, `conversation_id` selects where the completed user/assistant exchange is persisted. Stored history is available through the conversation detail endpoint, but prior messages are not sent to NVIDIA; provider requests contain only the current `message`. Full-history context assembly is reserved for Phase 5.

Omit `conversation_id` for the original stateless behavior. Chat responses keep the existing SSE contract:

```text
data: {"content": "Hello"}

data: [DONE]
```

Provider failures remain sanitized and finish with one `[DONE]` marker.

## Current scope

Implemented through Phase 3: stable FastAPI backend, provider/service boundaries, NVIDIA NIM streaming, and durable local conversation history.

Not implemented: frontend, voice, full-history model context, tools, authentication, CI, or desktop packaging.
