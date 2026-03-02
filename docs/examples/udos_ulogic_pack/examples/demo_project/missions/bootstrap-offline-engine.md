# MISSION: bootstrap-offline-engine

## Goal
Run a tiny end-to-end mission through uLogic and capture evidence.

## Constraints
- offline_only: true
- destructive_commands: forbidden

## Steps
1. CREATE core/ulogic/engine/runtime.py
   - output: artifacts/s1-create-runtime.md

2. RUN UCODE STATUS
   - output: logs/s2-status.md

3. RUN scripts/check_env.py
   - output: logs/s3-check-env.md

4. CALL mcp:local.tools.echo
   - output: logs/s4-mcp.json

5. CALL ok:assets.render
   - output: logs/s5-ok.json

## Rewards
- xp: 50
- unlock: mission:provider_integration
