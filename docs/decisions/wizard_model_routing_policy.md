# Wizard Model Routing Policy

This document defines how the **Wizard Server** selects and uses local/offline and cloud-based model backends for Agent tasks.

---

## 1. Goals

- **Offline-first**: default to local inference (Ollama + Devstral) whenever feasible.
- **Deterministic escalation**: only use cloud when policy allows it.
- **Cost + privacy controls**: track spend, minimise data exposure, and redact secrets.
- **Stable developer experience**: a single internal interface, multiple backends.

---

## 2. Definitions

- **Task**: a single request from an Agent/client (eg “refactor module”, “write tests”).
- **Backend**: a model provider endpoint (local or cloud).
- **Route**: the chosen backend + model + parameters.
- **Budget**: spend and/or token limits applied to cloud backends.

---

## 3. Backends

### 3.1 Local (default)

- Provider: Ollama
- Default model: `devstral-small-2`
- Intended use: code changes, refactors, tests, docs drafting, quick analyses.

### 3.2 Cloud (burst, optional)

- Provider: OpenRouter (optional)
- Intended use:
  - tasks exceeding local capacity (context size, runtime)
  - specialised models (eg reasoning, long-context)
  - parallelism / peak-load bursts

---

## 4. Routing Strategy

### 4.1 Policy summary

1. **Local-first**: attempt local route unless explicitly blocked.
2. **Escalate only when**:
   - the task is tagged `burst` OR
   - local route fails twice OR
   - policy classification requires a cloud-only capability.
3. **Never escalate** if any of:
   - task is tagged `private`
   - task includes secrets (detected)
   - cloud budget is exhausted
   - user has disabled cloud.

---

## 5. Task Classification

Wizard classifies each task before routing.

### 5.1 Required fields (internal)

- `task_id`
- `actor` (who requested it)
- `workspace` (`core` | `app` | `wizard` | `extensions` | `docs`)
- `intent` (`code` | `test` | `docs` | `design` | `ops`)
- `privacy` (`private` | `internal` | `public`)
- `urgency` (`low` | `normal` | `high`)

### 5.2 Optional tags

- `burst` (allow cloud)
- `long_context`
- `tooling_heavy` (lots of file ops)
- `offline_required` (force local)

---

## 6. Decision Algorithm

### 6.1 Local eligibility

Local is eligible when:
- Ollama is reachable
- requested model is installed
- estimated context fits local constraints

### 6.2 Cloud eligibility

Cloud is eligible when:
- cloud is enabled
- task privacy is not `private`
- budget remaining is above thresholds
- secrets scan passes (no secrets detected)

### 6.3 Route scoring

Select the route with the best score.

Score inputs (examples):
- **privacy risk** (highest weight)
- **cost estimate**
- **expected latency**
- **context fit**
- **tool support**

Routing preference order (default):
1. Local Devstral
2. Cloud “auto/router” (if enabled)
3. Cloud specialised model (only if explicitly requested)

---

## 7. Failure Handling

### 7.1 Retries

- Local: retry up to **2** times (with simplified prompt on retry)
- Cloud: retry up to **1** time (provider failover if supported)

### 7.2 Fallback rules

- If local fails and cloud is eligible: escalate only if task is not `private` and budget allows.
- If cloud fails: fall back to local with a reduced plan (smaller chunk size, smaller diff).

---

## 8. Safety and Redaction

### 8.1 Secret detection

Before any cloud call:
- scan prompt + attached context for:
  - API keys
  - OAuth secrets
  - private tokens
  - credential files

If detected:
- block cloud
- route local
- log a `secrets_detected` event

### 8.2 Data minimisation

- Send only the smallest necessary context window to cloud.
- Prefer **summaries** over raw files.
- Never send `memory/private/` content.

---

## 9. Auditing and Cost Tracking

Wizard must record for each task:
- chosen backend + model
- prompt size + completion size
- estimated/actual cost (cloud)
- latency
- success/failure
- escalation reason (if any)

Store logs in:
- `memory/logs/` (runtime)
- promote monthly summaries to `docs/devlog/YYYY-MM.md`

---

## 10. Configuration

### 10.1 Environment / config inputs

- `MODEL_ROUTING_ENABLED=true|false`
- `MODEL_CLOUD_ENABLED=true|false`
- `MODEL_LOCAL_ENDPOINT=http://127.0.0.1:11434` (example)
- `MODEL_CLOUD_ENDPOINT=https://openrouter.ai/api/v1` (example)
- `MODEL_DEFAULT_LOCAL=devstral-small-2`
- `MODEL_DEFAULT_CLOUD=auto` (or a chosen default)

### 10.2 Budget

- Daily and monthly cloud budgets
- Per-task maximum tokens
- Optional per-workspace budgets (core/app/wizard)

---

## 11. Developer UX

### 11.1 Single internal interface

All clients call Wizard with a stable request schema.
Wizard decides routing and returns:
- final answer
- route metadata (backend, model)
- audit id

### 11.2 Reproducibility

Wizard should support `route=local` or `route=cloud` overrides for debugging.

---

## 12. Defaults

- Default route: **Local Devstral**
- Cloud: **disabled by default** unless explicitly enabled
- Escalation: **off** unless `burst` tag or local failure triggers and policy allows

---

_End of policy._