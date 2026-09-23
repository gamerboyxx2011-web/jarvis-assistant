# JARVIS AI Assistant V3

A local, backend-only prototype for a personal AI assistant. Phase 1 provides a stable FastAPI API and NVIDIA NIM streaming chat integration. A frontend, persistence, and voice features are not implemented yet.

## Requirements

- Python 3.10 or newer
- A valid NVIDIA NIM API key from [NVIDIA Build](https://build.nvidia.com/)

## Installation

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Replace `your_nvidia_api_key_here` in `.env`. The application intentionally fails startup with a clear configuration error if the key is absent, blank, or still the placeholder.

Optional server settings are `HOST` and `PORT`. `server.py` honors both values.

## Running

```bash
python server.py
```

With the example server settings, the API is available at `http://localhost:8000`.

## API

### `GET /`

Returns a basic application status message.

### `GET /api/health`

Returns the application name, version, health status, and whether NVIDIA NIM is configured.

### `POST /api/chat`

Accepts:

```json
{
  "message": "Hello, JARVIS!",
  "temperature": 0.7,
  "max_tokens": 150
}
```

Validation rules:

- `message`: nonblank string, up to 32,000 characters
- `temperature`: number from `0.0` through `2.0`; default `0.7`
- `max_tokens`: optional integer from `1` through `8192`
- unknown request fields are rejected

Successful output remains an SSE stream of JSON content deltas:

```text
data: {"content": "Hello"}

data: [DONE]
```

Provider failures use a sanitized error event and the same single terminal marker:

```text
data: {"error": "AI provider request failed"}

data: [DONE]
```

## Development and tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests use mocked NVIDIA responses and do not require or spend a real provider key.

## Current scope

Implemented: FastAPI, configuration, health API, stateless streaming chat, and NVIDIA NIM integration.

Not implemented: frontend, conversation history, storage, STT, TTS, voice interaction, tools, authentication, CI, or desktop packaging.
