# JARVIS AI Assistant V3 — Project State

## Current phase
**Phase 4 — Text web interface (COMPLETED)**

Phase 4 adds a same-origin browser interface over the completed Phase 3 backend while preserving all Phase 1–3 API and persistence behavior.

## Branch baseline
- Branch: `phase-4-web-frontend`
- Created directly from `phase-3-conversation-history` at `bc4f8b16e8224e152fd5d0f289e639e0fb90bc73`
- Phase 3 was not merged into `main`.

## Implemented in Phase 4
- Responsive, accessible text chat interface at `/app`
- Conversation create, list, select, reload, and delete flows
- Incremental parsing of the existing `POST /api/chat` SSE response
- Stream cancellation and stale-update protection when switching conversations
- Safe message rendering with text content rather than HTML injection
- Same-origin static delivery through FastAPI
- Static/API regression tests without browser automation dependencies
- User messages persist before provider streaming; assistant messages persist only after successful, non-empty completion
- Cancellation and provider failures leave no partial assistant message in history

## Deliberate frontend-stack deviation
Phase 4 deliberately uses vanilla HTML, CSS, and JavaScript instead of React/Vite. This keeps the phase dependency-free, avoids a separate build pipeline, and matches the approved text-only scope. A framework migration is not part of Phase 4.

## Preserved behavior and boundaries
- Original `GET /` JSON response
- Existing health and conversation APIs
- Existing `/api/chat` request validation and SSE wire format
- Exactly one `[DONE]` marker per started stream
- Provider/service abstractions and sanitized provider errors
- SQLite conversation persistence and stateless chat compatibility
- Frontend sends only the current message and optional `conversation_id`; previous messages are not sent to NVIDIA

## Verification
- User-provided Phase 3 baseline: 38/38 tests passing locally
- Python source compilation passed
- JavaScript syntax check passed
- Desktop frontend render completed without console or resource errors
- The sandbox lacked the repository's pytest/httpx development dependencies, so the full automated suite and new static/API tests must be run in the project environment
- Manual browser verification remains required for desktop/mobile layout, real streaming, reload persistence, deletion, dark mode, and keyboard interaction

## Explicit scope boundary
No voice, tools, authentication, browser automation, desktop packaging, or Phase 5 work is included. Full-history model context remains Phase 5.
