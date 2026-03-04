# uDOS Creative Execution Library + Prompt Pack (v1.0)

This zip contains:

1. **Python stubs** for creative adapters (writing, image, video, music) and packaging hooks.
2. **Provider rotation** module (tier selection, escalation rules, cooldowns, budget caps).
3. **End-to-end example workflow** that uses the framework across writing + image + video + music.
4. **Markdown workflow template pack** (ready-to-copy) for common creative tasks.
5. **Cost control / budgeting subsystem** (per-phase caps, estimation, and enforcement).

## Quick start (developer)
- Copy `core/` into your uDOS repo (or merge selectively).
- Start with `examples/run_workflow_demo.py` to see the orchestration flow.
- Prompts live in `core/creative/**/prompts/*.md` and `templates/workflows/*.md`.

## Design notes
- Markdown is the canonical artifact format.
- Every phase writes to `vault/workflows/<workflow-id>/...`
- Providers are abstracted behind `providers/base.py` and can be implemented for OpenAI, Anthropic, OpenRouter, GPT4All, etc.
- Rotation is deterministic: choose tier by policy, validate output, escalate if needed.

## This is scaffolding
This pack is intentionally "safe stubs":
- The provider integrations are placeholders you wire to your existing uDOS provider stack.
- Packaging steps are stubs (pptx/pdf/audio) you can connect to your packaging pipeline.
