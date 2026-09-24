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
- Conversation lookup before a history-associated chat request
- Successful user/assistant exchanges persisted atomically after streaming completes
- Stored messages returned through the conversation detail endpoint
- Stateless chat behavior remains backward compatible when `conversation_id` is omitted
- Provider failures and cancelled streams do not persist incomplete assistant exchanges

## Explicit scope boundary

Phase 3 persists and returns conversation history but does not send prior messages to NVIDIA. Every provider request retains the Phase 2 single-current-message contract. Full-history context assembly is reserved for Phase 5.

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
- Conversation lookup, successful exchange persistence, single-current-message provider requests, and legacy stateless request compatibility were verified.
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
