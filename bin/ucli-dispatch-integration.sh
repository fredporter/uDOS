#!/bin/bash
# bin/ucli-dispatch-integration.sh
#
# Integration example showing how to wire three-stage dispatcher into bin/ucli
# This demonstrates the dispatch flow without modifying the existing bin/ucli directly
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ─────────────────────────────────────────────────────────────────────────────
# Three-Stage Dispatcher Integration
# ─────────────────────────────────────────────────────────────────────────────

dispatch_with_three_stage_routing() {
  local user_input="$1"
  local debug="${2:-}"

  # Route through Python dispatch service
  PYTHONPATH="$REPO_ROOT:${PYTHONPATH:-}" python3 - <<'PY' "$user_input" "$debug"
import sys
import json
from core.services.command_dispatch_service import CommandDispatchService, DispatchConfig
from core.services.logging_manager import get_logger

logger = get_logger("ucli-dispatch")
user_input = sys.argv[1]
debug = sys.argv[2] if len(sys.argv) > 2 else ""

# Create dispatcher with config
config = DispatchConfig(
    shell_enabled=True,
    shell_timeout_sec=5.0,
    debug=bool(debug)
)
dispatcher = CommandDispatchService(config)

# Dispatch through three-stage chain
result = dispatcher.dispatch(user_input)

# ─────────────────────────────────────────────────────────────────────────────
# Handle dispatch result
# ─────────────────────────────────────────────────────────────────────────────

dispatch_to = result.get("dispatch_to")
stage = result.get("stage")

if debug:
    print(f"[DEBUG] Stage: {stage}")
    print(f"[DEBUG] Dispatch to: {dispatch_to}")
    if "debug" in result:
        print(f"[DEBUG] Debug info: {json.dumps(result['debug'], indent=2)}")

if dispatch_to == "ucode":
    # ─────────────────────────────────────────────────────────────────────────
    # Stage 1: Execute uCODE command
    # ─────────────────────────────────────────────────────────────────────────
    command = result.get("command")
    confidence = result.get("confidence")

    if debug:
        print(f"[STAGE 1] Executing: {command} (confidence: {confidence:.1%})")

    from core.tui.dispatcher import CommandDispatcher
    cmd_dispatcher = CommandDispatcher()
    exec_result = cmd_dispatcher.dispatch(user_input)

    text = (
        exec_result.get("output")
        or exec_result.get("rendered")
        or exec_result.get("message")
        or str(exec_result)
    )
    print(text)

    status = str(exec_result.get("status", "")).lower()
    if status in {"error", "failed"}:
        sys.exit(1)

elif dispatch_to == "confirm":
    # ─────────────────────────────────────────────────────────────────────────
    # Stage 1: Medium confidence, ask for confirmation
    # ─────────────────────────────────────────────────────────────────────────
    command = result.get("command")
    confidence = result.get("confidence")

    # Note: Full confirmation logic would go here
    # For now, print debug info
    print(f"[CONFIRM] Did you mean: {command}? (confidence: {confidence:.1%})")
    print("[CONFIRM] This would normally prompt for y/n/skip")

elif dispatch_to == "shell":
    # ─────────────────────────────────────────────────────────────────────────
    # Stage 2: Shell passthrough
    # ─────────────────────────────────────────────────────────────────────────
    if debug:
        print(f"[STAGE 2] Executing shell: {user_input}")

    import subprocess
    try:
        output = subprocess.run(
            user_input,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5.0
        )
        if output.stdout:
            print(output.stdout, end="")
        if output.stderr:
            print(output.stderr, end="", file=sys.stderr)
        sys.exit(output.returncode)
    except subprocess.TimeoutExpired:
        print("[ERROR] Shell command timed out", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Shell execution failed: {e}", file=sys.stderr)
        sys.exit(1)

elif dispatch_to == "vibe":
    # ─────────────────────────────────────────────────────────────────────────
    # Stage 3: Vibe fallback
    # ─────────────────────────────────────────────────────────────────────────
    skill = result.get("skill", "ask")

    if debug:
        print(f"[STAGE 3] Routing to Vibe skill: {skill}")

    from core.services.vibe_skill_mapper import get_default_mapper
    mapper = get_default_mapper()

    # Format vibe invocation
    vibe_invocation = mapper.invocation_to_string(skill)
    print(f"[VIBE] Would route to: {vibe_invocation}")
    print(f"[VIBE] Input: {user_input}")
    print("[VIBE] This would normally call Wizard Vibe/OK service")

else:
    # Unexpected dispatch target
    print(f"[ERROR] Unknown dispatch target: {dispatch_to}")
    sys.exit(1)

PY
}

# ─────────────────────────────────────────────────────────────────────────────
# Example Usage
# ─────────────────────────────────────────────────────────────────────────────

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <command> [--debug]"
  echo ""
  echo "Examples:"
  echo "  $0 'HELP'"
  echo "  $0 'HELP' --debug"
  echo "  $0 'ls -la /tmp'"
  echo "  $0 'how do I update my password?' --debug"
  exit 0
fi

user_input="$1"
debug="$2"

dispatch_with_three_stage_routing "$user_input" "$debug"
