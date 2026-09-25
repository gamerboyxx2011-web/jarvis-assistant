# JARVIS AI Assistant V3 — Project State

## Current phase
**Phase 6 — Voice Mode MVP + NVIDIA chat model selection**

The existing text chat pipeline now supports four validated NVIDIA NIM models without changing conversation history, SSE streaming, or the voice pipeline.

## Branch baseline
- Branch: `phase-model-selection`
- Created from `phase-6-voice-mode-mvp` at `b8224ae68ed071c6c22210ffafc2abf6fe73863e`

## Model selection
- Default: `z-ai/glm-5-3-flash` (GLM-5.3 Flash, Fast)
- Fast: GLM-5.3 Flash; Nemotron 3.5 Lightning
- Deep: GLM-5.3; Nemotron 3 Ultra
- The frontend sends the exact selected model through the existing Chat API and ChatService to the NVIDIA provider.
- Selection is stored only in browser `sessionStorage`; fresh sessions return to GLM-5.3 Flash.
- Chat clients that omit `model` retain compatible behavior through the default; unsupported IDs receive request validation errors.

## Preserved behavior
- Existing `/api/chat` SSE contract, ChatService orchestration, full-history context, and persistence
- Existing conversation/history APIs
- Existing push-to-talk, VoiceService, STT, TTS, and speech-provider behavior

## Scope boundary
No wake word, always-listening, VAD/realtime voice, tools, authentication, browser automation, desktop packaging, or Phase 7+ behavior is included.
