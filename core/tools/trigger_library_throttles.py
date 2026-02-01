"""Trigger rate-limiter logs for provider-load auditing."""

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.services.rate_limit_helpers import guard_wizard_endpoint
from wizard.services.provider_load_logger import read_recent_provider_events

ENDPOINTS = [
    "/api/v1/library/integration/demo/install",
    "/api/v1/library/parser/execute",
    "/api/v1/library/items/list",
]


def main() -> None:
    print("Triggering library/parsers throttles to populate provider-load.log")
    for endpoint in ENDPOINTS:
        print(f"\nEndpoint {endpoint} (guarding for throttles)")
        for attempt in range(75):
            guard = guard_wizard_endpoint(endpoint)
            status = "allowed" if guard is None else "throttled"
            print(f"  [{attempt + 1:02}] {endpoint} -> {status}")
            if guard:
                break
            time.sleep(0.02)
    print("\nRecent provider load events:")
    for entry in read_recent_provider_events(limit=5):
        ts = entry.get("timestamp")
        provider = entry.get("provider")
        endpoint = entry.get("details", {}).get("endpoint")
        usage = entry.get("details", {}).get("usage")
        limit = entry.get("details", {}).get("limit")
        print(f"  {ts} {provider} {endpoint} usage={usage}/{limit}")


if __name__ == "__main__":
    main()
