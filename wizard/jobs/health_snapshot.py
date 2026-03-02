from __future__ import annotations

import time

from wizard.services.monitoring_manager import MonitoringManager


def main() -> int:
    started = time.time()
    manager = MonitoringManager()
    try:
        manager.run_default_checks()
        payload = manager.log_training_summary()
        manager.record_automation_run(
            "health_snapshot",
            success=True,
            duration_ms=(time.time() - started) * 1000,
            metadata={"summary": payload["summary"]},
        )
        print(payload["summary"])
        return 0
    except Exception as exc:
        manager.record_automation_run(
            "health_snapshot",
            success=False,
            duration_ms=(time.time() - started) * 1000,
            error=str(exc),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
