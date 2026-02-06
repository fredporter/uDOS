# uDOS v1.3 — Wizard AI Modes + Local Model Defaults (Short Spec)

**Status:** Implemented
**Scope:** Wizard AI gateway + Core access

## 1) Goals
- Standardize **AI modes** for consistent behavior across TUI, App, and extensions.
- Keep **offline-first** routing as the default (Ollama local models).
- Provide **Core access** via `/api/ai/complete` with strict policy controls.

## 2) AI Modes (Contract)

### Conversation mode
- **Purpose:** conversational UX in TUI / App
- **Behavior:** clarifying questions, concise answers
- **Preset:** `temperature ~0.7`
- **Required fields:** `conversation_id` (stable session id)

### Creative mode
- **Purpose:** idea generation, content drafting
- **Behavior:** multiple options, more varied output
- **Preset:** `temperature ~1.0`

### Code mode
- **Purpose:** deterministic engineering help
- **Behavior:** concise, precise, low randomness
- **Preset:** `temperature ~0.2`

## 3) Local Model Defaults (Ollama)

Default small/fast models for local-only:
- **General fast:** `llama3.2:3b`
- **Tiny / minimal:** `gemma2:2b`
- **Coding:** `starcoder2:3b` or `qwen2.5-coder:7b` (if available)

These map to `library/ollama/container.json` and are enforced as **local-first**.

## 4) Core Access (Wizard API)

Core accesses Wizard via **`/api/ai/complete`**.

Request contract (minimal):
```json
{
  "prompt": "Summarize today’s tasks",
  "mode": "conversation",
  "conversation_id": "vault-2026-02-04",
  "max_tokens": 512,
  "workspace": "core",
  "privacy": "internal"
}
```

Notes:
- `mode` selects the preset template + temperature.
- `conversation_id` enables threaded context.
- `privacy=private` **must never** route to cloud providers.

## 5) Offline-First Policy (Required)

Routing priority:
1. **Local Ollama** (default, always try first)
2. **Cloud burst** (optional, only when explicitly allowed by policy)

Hard rules:
- `privacy=private` → local only.
- `offline_required` tag → local only.
- If local model unavailable → return clear error with install prompt.

## 6) Deliverables
- `/api/ai/complete` supports `mode` + `conversation_id`.
- Wizard applies prompt templates + temperature presets.
- Core uses `/api/ai/complete` for all assistant calls (no direct cloud).
