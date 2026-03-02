#!/usr/bin/env bash
set -euo pipefail

profile="${1:-full}"
shift || true

case "${profile}" in
  core)
    targets=(core/tests tests)
    ;;
  wizard|full|roadmap)
    targets=(wizard/tests core/tests tests)
    ;;
  *)
    echo "Unknown profile: ${profile}" >&2
    echo "Usage: scripts/run_pytest_profile.sh [core|wizard|full|roadmap] [extra pytest args...]" >&2
    exit 2
    ;;
esac

./scripts/run_pytest.sh "${targets[@]}" "$@"
