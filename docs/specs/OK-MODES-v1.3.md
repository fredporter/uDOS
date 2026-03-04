# Wizard OK Modes + Local Model Defaults

**Status:** Implemented
**Scope:** Wizard OK gateway + Core access

## 1) Goals
- Standardize **OK modes** for consistent behavior across TUI, App, and extensions.
- Keep **offline-first** routing as the default (local GPT4All models).
- Provide Core access via the Wizard completion endpoint with strict policy controls.
- Enforce Ghost Mode policy in `docs/specs/GHOST-MODE-POLICY.md`.

## 2) OK Modes (Contract)

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

## 3) Local Model Defaults (GPT4All)

Default local set for OK operation:
- **Chat / summaries:** `mistral-small`
- **Reasoning / scheduler:** `mistral-large`
- **Code / repo work:** `devstral-small-2`

Optional local alternatives:
- **General fast:** `llama3.2:3b`
- **Tiny / minimal:** `gemma2:2b`
- **Coding:** `starcoder2:3b` or `qwen2.5-coder:7b` (if available)

Defaults map to the configured local runtime profile and are enforced as **local-first**.

## 4) Core Access (Wizard API)

Core accesses Wizard via the completion endpoint.
Legacy route names may still exist in implementation, but user-facing terminology should use OK Assistant / OK Model wording.

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
- `privacy=private` must never route to cloud providers.

## 5) Offline-First Policy (Required)

Routing priority:
1. **Local GPT4All** (default, always try first)
2. **Cloud burst** (optional, only when explicitly allowed by policy)

Hard rules:
- `privacy=private` → local only.
- `offline_required` tag → local only.
- If local model unavailable → return clear error with install prompt.
- Ghost Mode → local only, destructive commands dry-run only.

## 6) Deliverables
- the completion endpoint supports `mode` + `conversation_id`.
- Wizard applies prompt templates + temperature presets.
- Core uses the Wizard completion endpoint for assistant calls instead of direct cloud routing.
