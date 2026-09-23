# JARVIS AI Assistant V3 — Project State

## Current phase

**Phase 1 — Stabilize and establish an executable baseline**

Phase 1 establishes a consistent, testable FastAPI backend while preserving the existing NVIDIA NIM streaming path.

## Implemented baseline

- FastAPI application with `GET /`, `GET /api/health`, and `POST /api/chat`
- Environment configuration through Pydantic Settings
- Fail-fast validation for a missing, blank, or placeholder NVIDIA API key
- NVIDIA NIM integration through its OpenAI-compatible endpoint
- Stateless SSE chat streaming with JSON content deltas and one `[DONE]` marker
- Typed validation for message, temperature, and token limits
- Sanitized client-facing provider errors
- Configurable Uvicorn host and port
- Automated tests with mocked provider traffic

## Runtime requirements

- Python 3.10+
- FastAPI
- Uvicorn
- HTTPX
- Pydantic Settings

Development tests use pytest, pytest-asyncio, and respx.

## API contract

### `GET /api/health`

Returns application identity, version, `healthy` status, and `nvidia_configured`.

### `POST /api/chat`

Accepts one stateless message with optional temperature and maximum-token values. Successful provider deltas are returned as SSE `data:` records containing `{"content": "..."}`. Sanitized provider failures use `{"error": "AI provider request failed"}`. Every started stream ends with exactly one `[DONE]` marker.

## Verification

The committed test suite covers configuration, health, request validation, mocked NVIDIA streams, sanitized failures, SSE framing, and terminal-marker behavior. Live-provider tests remain intentionally excluded from ordinary test runs.

## Known limitations

- No frontend
- No conversation history or persistence
- No STT, TTS, microphone, or voice session
- No provider abstraction beyond the concrete NVIDIA client
- No tools, authentication, CI, or desktop packaging

These limitations belong to later roadmap phases and are not part of Phase 1.
