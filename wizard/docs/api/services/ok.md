# Logic Assist Service

Wizard exposes the v1.5 logic-assist runtime: GPT4All local advisory output plus Wizard-only network escalation and budget control.

## Defaults

Active settings live in [logic-assist.md](/Users/fredbook/Code/uDOS/core/framework/seed/bank/typo-workspace/settings/logic-assist.md) and the user override at [logic-assist.md](/Users/fredbook/Code/uDOS/memory/bank/typo-workspace/user/settings/logic-assist.md).

## Routes

- `GET /api/logic/health`
- `GET /api/logic/config`
- `GET /api/logic/status`
- `GET /api/logic/models`
- `POST /api/logic/complete`
- `POST /api/logic/explain-code`
- `GET /api/ucode/logic/status`
- `GET /api/ucode/logic/history`
- `POST /api/ucode/logic/model`
- `POST /api/ucode/logic/network`
