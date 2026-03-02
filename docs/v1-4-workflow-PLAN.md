# Workflow Plan Archive Note

Status: Superseded  
Last updated: 2026-03-03

This file is retained only as a redirect stub.

The active workflow architecture and implementation direction now live in:

- [v1-5-workflow.md](/Users/fredbook/Code/uDOS/docs/decisions/v1-5-workflow.md)
- [roadmap.md](/Users/fredbook/Code/uDOS/docs/roadmap.md)

## Reason for Supersession

The previous workflow plan content overlapped with newer v1.5 workflow planning and risked creating multiple active-looking sources of truth.

Workflow planning is now split deliberately into:

- Core lane:
  deterministic markdown-first workflow parsing, state, artifacts, and `WORKFLOW` command execution
- Wizard lane:
  future control-plane scheduling windows, GUI, MCP/API orchestration, and budget-aware runtime integration
- Extension lane:
  Empire, Typo, and domain-specific workflow enrichment

## Current Rule

Use:

- [v1-5-workflow.md](/Users/fredbook/Code/uDOS/docs/decisions/v1-5-workflow.md) for workflow architecture decisions
- [roadmap.md](/Users/fredbook/Code/uDOS/docs/roadmap.md) for workflow progress, sequencing, and remaining delivery lanes

Do not extend this file with new workflow requirements.
