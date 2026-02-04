# Vibe NL Routing and Code Assistance Prototype Plan

**Date:** February 4, 2026
**Status:** Draft prototype plan

## Goals
- Add a natural language (NL) entry point to the uCODE TUI.
- Provide code assistance commands (analyze, explain, suggest) that use Vibe services.
- Keep routing deterministic and testable with explicit, documented hooks.
- Preserve the current Vibe command surface and avoid breaking changes.

## Non-Goals (for prototype)
- No full agent loop or autonomous actions.
- No automatic code changes without user confirmation.
- No cloud-only features that break offline-first workflows.

## Command Surface (prototype)

### New NL routing
- `NL ROUTE <prompt>`
  - Interprets NL and maps to a concrete uCODE command.
  - Outputs a structured route plan before execution.
  - Supports `--dry-run` to return the plan only.

### Vibe assistance
- `VIBE ANALYZE <path>`
  - Summarize a module or folder.
  - Output risks, dependencies, and suggested next steps.
- `VIBE EXPLAIN <symbol>`
  - Explain a function/class or file section.
- `VIBE SUGGEST <task>`
  - Generate suggestions and recommended commands.

### Existing Vibe commands (keep)
- `VIBE CHAT`, `VIBE CONTEXT`, `VIBE HISTORY`, `VIBE CONFIG`

## Routing Pipeline (prototype)

1. **Input capture**
   - Accept raw NL input from `NL ROUTE`.

2. **Intent extraction**
   - Identify intent category (analyze, explain, suggest, execute, sync, schedule).
   - Extract entities (paths, symbols, timeframe, scope).

3. **Route plan**
   - Build a structured plan:
     - `intent`
     - `target`
     - `commands[]`
     - `context_scope`
     - `risk_level`

4. **Execution**
   - If not `--dry-run`, execute the mapped commands.
   - Use the same Vibe transport logic as `VIBE CHAT`.

5. **Output**
   - Print the plan (always).
   - Stream results with the `vibe>` prefix.

## Context Scoping
- Default scope: repository root + active vault.
- Allow overrides:
  - `--context repo|vault|files` (one or more)
  - `--files a,b,c` (explicit file list)
  - `--no-context`
- Enforce size limits and allowlist extensions.

## Transport and Services
- Prefer Goblin endpoints for local development.
- Fallback to Wizard endpoints when available.
- Do not enable cloud-only features without explicit user opt-in.

## Prototype Phases

### Phase 0: Plan + hooks (now)
- Document the NL routing pipeline.
- Add test hooks for Vibe requests.

### Phase 1: Minimal NL router
- Implement `NL ROUTE` with a rule-based router.
- Add `--dry-run` and structured plan output.

### Phase 2: Assistance commands
- Implement `VIBE ANALYZE`, `VIBE EXPLAIN`, `VIBE SUGGEST`.
- Route to Goblin/Wizard Vibe endpoints.

### Phase 3: Context gating and policies
- Add context scope flags.
- Add output redaction for secrets and tokens.

## Test Hooks (added)

These are intended for deterministic tests of the Vibe commands and future NL routing.

- `UDOS_VIBE_TEST_MODE=1`
  - Forces uCODE to bypass live network calls.
- `UDOS_VIBE_TEST_PROVIDER=goblin|wizard`
  - Emulates a provider for branching logic.
- `UDOS_VIBE_TEST_URL=http://localhost:8767`
  - Base URL shown in config output.
- `UDOS_VIBE_TEST_RESPONSE='{ "response": "ok" }'`
  - Inline JSON response for all Vibe requests.
- `UDOS_VIBE_TEST_RESPONSE_FILE=/path/to/response.json`
  - File-based JSON response payload.
- `UDOS_VIBE_TEST_CAPTURE_FILE=/tmp/vibe_request.json`
  - Captures the last request payload for assertions.

## Test Strategy

- **Unit tests**:
  - NL routing parser (intent and entity extraction).
  - Route plan formatting and `--dry-run` output.
- **Integration tests**:
  - uCODE Vibe commands with `UDOS_VIBE_TEST_MODE=1`.
  - Verify routing output for `NL ROUTE` maps to correct command tokens.

## Acceptance Criteria (prototype)
- `NL ROUTE` returns a structured plan and can run in `--dry-run` mode.
- `VIBE ANALYZE/EXPLAIN/SUGGEST` return responses from stubbed hooks.
- No live network calls occur when test mode is enabled.
- Commands are documented in `docs/specs/uCODE-v1.3.md` after implementation.
