# JARVIS AI Assistant V3 — Project State

## Current phase
**Phase 5 — Full-history model context (COMPLETED)**

Phase 5 adds persisted multi-turn conversation context to provider requests while preserving the completed Phase 1–4 API, frontend, streaming, and persistence behavior.

## Branch baseline
- Branch: `phase-5-full-history-context`
- Created directly from `phase-4-web-frontend` at `6c887c6a671f4a34fc99ba912d604cb9611c7367`
- Earlier phase branches remain unmerged into `main`.

## Implemented in Phase 5
- Minimal provider-neutral history messages with `user` and `assistant` roles
- Chronological persisted history supplied for conversation-backed chat
- Current user message added to provider context exactly once
- NVIDIA serialization into the OpenAI-compatible `messages` array
- Stateless chat remains a single current-user message
- Focused service and NVIDIA adapter regression coverage

## Preserved behavior and boundaries
- User messages persist before provider streaming starts
- Assistant messages persist only after successful, non-empty completion
- Cancellation and provider failures leave no partial assistant message in history
- Existing request validation and SSE wire format
- Exactly one `[DONE]` marker per started stream
- Provider/service abstractions and sanitized provider errors
- SQLite schema and conversation APIs
- Responsive dependency-free Phase 4 frontend

## Verification
- Phase 4 baseline: 49/49 local tests passing with browser verification completed
- Complete automated suite must pass after the Phase 5 additions
- Manual browser verification is not required for the backend-only context change; an optional live NVIDIA multi-turn smoke test can confirm remote model behavior

## Explicit scope boundary
No frontend redesign, database migration, authentication, voice, tools, browser automation, desktop packaging, Phase 6 work, or later-phase work is included.
