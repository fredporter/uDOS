# uLogic Offline Logic Engine Scaffold (uDOS / uCode-first)

Offline-first logic engine scaffolding for uDOS.

Features:
- **uCode-first** command + loop execution model
- **Sandboxed script runner** (python/bash stub)
- **MCP + OK API** wrappers with **offline deferred queue**
- **Workflow/Mission Markdown contracts**
- **Gameplay lens**: metrics + gates + effects (unlock/reveal/decode-ready)
- Reads/writes: `project.json`, `agents.md`, `tasks.json`, `completed.json`

## Run demo
```bash
python examples/run_mission_demo.py
```
Writes artifacts under `demo_vault/` and updates `examples/demo_project/completed.json`
and `examples/demo_project/memory/ulogic/*`.

## Integrate into uDOS
- Replace `ucode/dispatcher.py` stub to call your uDOS CommandDispatcher.
- Replace `providers/*` stubs to call your real MCP/OK provider layer when available.
