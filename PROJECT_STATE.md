# JARVIS AI Assistant V3 — Project State

## Current phase
**Phase 6 — Voice Mode MVP (IMPLEMENTED; LOCAL SUITE VERIFICATION PENDING)**

Controlled push-to-talk now runs transient microphone audio through OpenAI STT, the existing full-history ChatService/NVIDIA LLM, sentence/phrase buffered OpenAI TTS, and ordered browser playback.

## Branch baseline
- Branch: `phase-6-voice-mode-mvp`
- Created from `phase-5-full-history-context` at `80661c04fc013bf805965c9013dd58d0e3d4bf6d`
- Phase 5 baseline: 49/49 local tests and successful live multi-turn history smoke test

## Implemented
- Dedicated multipart `POST /api/voice` SSE pipeline
- Provider-neutral STT/TTS boundaries and OpenAI adapters using `httpx`
- Existing ChatService reuse for conversations, persistence, and full-history model context
- Push-and-hold recording with a 60-second client/server limit
- 25 MB upload limit and no raw-audio persistence
- Sequential sentence/bounded-phrase synthesis and ordered playback
- Cancellation propagation and sanitized stage errors
- Text/history preservation when TTS fails
- Focused adapter, orchestration, route, and frontend coverage

## Preserved behavior
- Existing `/api/chat` route and text-only Chat mode
- Phase 1–5 APIs, SSE contract, history, provider, persistence, and full-context behavior

## Verification
- Python source/test compilation passed in the available sandbox
- Frontend JavaScript syntax check passed
- Full pytest execution remains required locally because the sandbox lacks project dependencies

## Scope boundary
No wake word, always-listening, VAD/realtime voice, tools, authentication, browser automation, desktop packaging, or Phase 7+ behavior is included.
