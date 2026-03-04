# Workflow Management Archive Note

Status: Superseded  
Updated: 2026-03-03

This file is retained only as a redirect note.

The active v1.5 workflow-management standard now lives in:

- [WORKFLOW-SCHEDULER-v1.5.md](/Users/fredbook/Code/uDOS/docs/specs/WORKFLOW-SCHEDULER-v1.5.md)
- [v1-5-workflow.md](/Users/fredbook/Code/uDOS/docs/decisions/v1-5-workflow.md)
- [WORKFLOW-SCHEDULER-QUICKSTART.md](/Users/fredbook/Code/uDOS/docs/howto/WORKFLOW-SCHEDULER-QUICKSTART.md)
- [STATUS.md](/Users/fredbook/Code/uDOS/docs/STATUS.md)

## Reason for Supersession

The earlier workflow-management document described a broader project/mission concept that overlapped with the v1.5 workflow scheduler direction.

That older concept is now split into explicit lanes:
- core workflow execution and artifact contracts
- Wizard control-plane scheduling and orchestration
- extension-specific enrichment for contacts, research, content, and editing flows

## Current Rule

Use the v1.5 workflow scheduler spec as the canonical workflow runtime contract.

Do not extend this file with new workflow behavior.
