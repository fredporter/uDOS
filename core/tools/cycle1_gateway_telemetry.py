#!/usr/bin/env python3
import json
import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.services.health_training import get_health_log_path
from core.services.hotkey_map import write_hotkey_payload
from core.services.self_healer import collect_self_heal_summary
from wizard.services.ai_gateway import AIProvider
from wizard.services.monitoring_manager import MonitoringManager, HealthStatus


def _latest_gateway_log(memory_root: Path) -> Path:
    logs_dir = memory_root / "logs"
    candidates = sorted(
        logs_dir.glob("ai-gateway-*.log"), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True
    )
    return candidates[0] if candidates else None


def _gateway_health_check(latest_log: Path):
    """Return a tuple suitable for `MonitoringManager.check_health`."""
    if latest_log:
        age_secs = time.time() - latest_log.stat().st_mtime
        status = HealthStatus.HEALTHY if age_secs < 3600 else HealthStatus.DEGRADED
        message = (
            f"Latest gateway log {latest_log.name} (age {age_secs/60:0.1f}m)"
        )
        metadata = {"log": str(latest_log), "age_secs": round(age_secs, 2)}
    else:
        status = HealthStatus.UNHEALTHY
        message = "No ai-gateway logs recorded yet"
        metadata = {}
    return status, message, metadata


def _provider_fingerprint():
    providers = [provider.value for provider in AIProvider]
    source = {"providers": providers, "timestamp": datetime.utcnow().isoformat()}
    fingerprint = hashlib.sha256(json.dumps(source, sort_keys=True).encode()).hexdigest()
    return fingerprint, providers


def main():
    memory_root = ROOT / "memory"
    memory_root.mkdir(parents=True, exist_ok=True)
    logs_dir = memory_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    monitoring = MonitoringManager(data_dir=memory_root / "monitoring", check_interval=60)
    latest_log = _latest_gateway_log(memory_root)
    status, message, metadata = _gateway_health_check(latest_log)
    health_record = monitoring.check_health(
        "gateway_telemetry",
        lambda: (status, message, metadata),
    )

    fingerprint, providers = _provider_fingerprint()

    self_heal_summary = collect_self_heal_summary(component="wizard", auto_repair=False)

    hotkey_payload = write_hotkey_payload(memory_root)

    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "self_heal": self_heal_summary,
        "gateway_telemetry": {
            "health": health_record.to_dict(),
            "provider_fingerprint": fingerprint,
            "providers": providers,
        },
        "hotkeys": hotkey_payload,
    }

    health_log_path = get_health_log_path()
    health_log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(health_log_path, "a") as log_file:
        log_file.write(json.dumps(payload) + "\n")

    print("Cycle 1 gateway telemetry snapshot recorded.")
    print(f"  Health log: {health_log_path}")
    print(f"  Gateway health: {health_record.status} ({health_record.message})")
    print(f"  Providers: {providers}")
    print(f"  Fingerprint: {fingerprint}")
    print(f"  Self-Heal remaining issues: {self_heal_summary.get('remaining')}")


if __name__ == "__main__":
    main()
