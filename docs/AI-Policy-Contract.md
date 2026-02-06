# AI Policy Contract

This contract captures the local-first AI rules from `docs/uDOS-v1-3.md` section 8 and the Ghost Mode policy in `docs/specs/AI-OK-GHOST-MODE-POLICY.md`.

## Model tiers
1. **Local lanes (Ollama pool)**
   - `mistral-small`, `mistral-large`, `devstral-small-2` (default set)
   - Optional: `codellama`, `llama2`, `mistral`, `neural-chat`, `openchat`, `zephyr`, `orca-mini` (or equivalents)
   - Preferred for routine tasks, missions, and indexing to avoid network dependencies.

2. **Online lanes (policy-triggered)**
   - `OpenRouter`, `OpenAI`, `Gemini` (or other approved services)
   - Allowed only when:
     - “Publish-grade” quality is required
     - Context window exceeds local model capability
     - Vision/long-context/tooling is necessary
     - Mission policy explicitly allows it
     - Time/compute constraints demand it

## Logging + compliance
Every AI call must log:
- Model and provider
- Input hashes (never raw secrets)
- Output files and destinations
- Estimated cost (if online)
- Timestamps and mission/job IDs

## Governance
- AI behaves like a contributor: it proposes edits via patch bundles and run reports.
- The control plane (Wizard + Vibe CLI) enforces quotas and policy before allowing online fallbacks.
 - `/core` and `/dev` must not make direct online requests; all online access goes through `wizard-server`.
 - Ghost Mode forces offline-only behavior and dry-run for destructive commands.
