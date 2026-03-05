# Demo 01: Local Assist and Knowledge

## Goal

Show the offline-first local assist lane with active governance context, then prove the same runtime can report knowledge-aware readiness through the operator surfaces.

## Target Profiles

- `core`
- `home`
- `dev`

## Transcript

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_01_local_assist_and_knowledge.py
ucode READ AGENTS.md
curl -s http://127.0.0.1:8000/api/ucode/logic/status
curl -s http://127.0.0.1:8000/api/providers/gpt4all/status
curl -s http://127.0.0.1:8000/api/self-heal/recovery/status
```

If local runtime setup is required:

```bash
curl -N http://127.0.0.1:8000/api/self-heal/recovery/run/logic-assist-setup
```

## Expected Output

- `logic/status` reports local runtime readiness, context hash, conversation store, and cache metadata
- provider health reports GPT4All model/install evidence
- self-heal recovery reports local setup guidance using the canonical model and guidance paths
- local assist remains the first lane and Wizard network escalation remains policy-bound

## Expected Artifacts

- `.artifacts/release-demos/demo-01-local-assist-and-knowledge.json`
- `memory/wizard/logic_conversations/` may gain conversation history
- `memory/models/gpt4all/` may gain model guidance artifacts after setup

## Validation

```bash
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python docs/examples/ucode_v1_5_release_pack/scripts/run_demo_01_local_assist_and_knowledge.py
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest \
  core/tests/ucode_release_demo_scripts_test.py \
  wizard/tests/logic_assist_service_test.py \
  wizard/tests/provider_health_routes_test.py \
  wizard/tests/self_heal_routes_recovery_test.py \
  wizard/tests/ucode_ok_mode_utils_test.py \
  wizard/tests/ucode_ok_routes_test.py
```
