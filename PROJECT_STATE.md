# JARVIS AI Assistant V3 — Project State

## Current phase

**Phase 3 — Conversation history (COMPLETED)**

Phase 3 adds durable, local conversation history while preserving the Phase 1 streaming API and the Phase 2 provider/service boundaries.

## Repository state found before Phase 3 work

- `phase-3-conversation-history` existed but pointed to the exact Phase 2 head (`60cd815`).
- There were no Phase 3 commits or partial Phase 3 source files on the branch.
- `PROJECT_STATE.md` and `README.md` still described Phase 1, despite the completed Phase 2 provider and service boundaries.

## Implemented in Phase 3

- SQLite-backed conversation and message storage
- Conversation create, list, detail, and delete endpoints
- Optional `conversation_id` on `POST /api/chat`
- Full prior message history passed through the provider-neutral request model
- Successful user/assistant exchanges persisted atomically after streaming completes
- NVIDIA adapter support for multi-message context
- Stateless chat behavior remains backward compatible when `conversation_id` is omitted
- Provider failures and cancelled streams do not persist incomplete assistant exchanges

## API additions

- `POST /api/conversations`
- `GET /api/conversations`
- `GET /api/conversations/{conversation_id}`
- `DELETE /api/conversations/{conversation_id}`

`POST /api/chat` accepts the existing request plus optional `conversation_id`.

## Configuration

- `HISTORY_DB_PATH` controls the SQLite database path and defaults to `jarvis_history.db`.

## Verification

- Conversation storage was smoke-tested across store re-instantiation.
- History ordering, provider context construction, successful exchange persistence, and legacy stateless request compatibility were verified.
- Source compilation passed.
- The execution sandbox did not contain the repository's pytest/httpx development dependencies, so the full automated suite could not be executed there.

## Preserved behavior

- Existing health response and application version
- Existing stateless `POST /api/chat` input and SSE output
- Exactly one `[DONE]` marker per started stream
- Sanitized provider errors
- NVIDIA NIM default provider and Phase 2 provider/service abstractions

## Remaining limitations

- No frontend, voice, tools, authentication, CI, or desktop packaging
- No Phase 4 work has been started
