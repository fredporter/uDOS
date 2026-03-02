from __future__ import annotations

from wizard.services.monitoring_manager import MonitoringManager


def main() -> int:
    manager = MonitoringManager()
    manager.run_default_checks()
    payload = manager.log_training_summary()
    print(payload["summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
