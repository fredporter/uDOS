"""Quota/cost tracking helpers for gateway telemetry."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict

from core.services.logging_api import get_repo_root
from wizard.services.ok_gateway import AIProvider
from wizard.services.provider_load_logger import read_recent_provider_events

GATEWAY_PATTERN = re.compile(
    r"provider=(?P<provider>[a-zA-Z0-9_-]+)\s+cost=(?P<cost>[0-9]+\.?[0-9]*)\s+tokens=(?P<tokens>[0-9]+)"
)
DEFAULT_DAILY_LIMIT = {
    "openai": 120.0,
    "mistral": 90.0,
    "ollama": 80.0,
    "huggingface": 60.0,
}


def _parse_gateway_logs(log_dir: Path) -> Dict[str, Dict[str, float]]:
    usage: Dict[str, Dict[str, float]] = {}
    if not log_dir.exists():
        return usage

    jsonl_dir = log_dir / "udos" / "wizard"
    jsonl_paths = sorted(jsonl_dir.glob("ok-gateway-*.jsonl")) if jsonl_dir.exists() else []
    legacy_paths = sorted(log_dir.glob("ai-gateway-*.log"))

    for log_path in jsonl_paths:
        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as handle:
                for line in handle:
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    ctx = record.get("ctx", {}) if isinstance(record, dict) else {}
                    provider = ctx.get("provider") or ctx.get("provider_name")
                    cost = ctx.get("cost") or ctx.get("estimated_cost")
                    tokens = ctx.get("tokens") or ctx.get("total_tokens")
                    if not provider or cost is None:
                        continue
                    try:
                        cost_val = float(cost)
                    except (TypeError, ValueError):
                        continue
                    token_val = int(tokens) if tokens is not None and str(tokens).isdigit() else 0
                    entry = usage.setdefault(provider.lower(), {"cost": 0.0, "tokens": 0, "calls": 0})
                    entry["cost"] += cost_val
                    entry["tokens"] += token_val
                    entry["calls"] += 1
        except Exception:
            continue

    for log_path in legacy_paths:
        try:
            with open(log_path, "r") as handle:
                for line in handle:
                    match = GATEWAY_PATTERN.search(line)
                    if not match:
                        continue
                    provider = match.group("provider").lower()
                    cost = float(match.group("cost"))
                    tokens = int(match.group("tokens"))
                    entry = usage.setdefault(provider, {"cost": 0.0, "tokens": 0, "calls": 0})
                    entry["cost"] += cost
                    entry["tokens"] += tokens
                    entry["calls"] += 1
        except Exception:
            continue
    return usage


def _format_provider_summary(provider: str, raw: Dict[str, float]) -> Dict:
    limit = DEFAULT_DAILY_LIMIT.get(provider, 50.0)
    cost = raw.get("cost", 0.0)
    usage_percent = min(100.0, (cost / limit) * 100 if limit else 0)
    status = "healthy"
    if usage_percent >= 100:
        status = "exceeded"
    elif usage_percent >= 90:
        status = "critical"
    elif usage_percent >= 70:
        status = "warning"

    return {
        "daily": {
            "cost": round(cost, 2),
            "limit": limit,
            "usage_percent": round(usage_percent, 1),
        },
        "status": status,
        "tokens": raw.get("tokens", 0),
        "calls": raw.get("calls", 0),
        "cost_trend": "flat" if usage_percent < 50 else "elevated",
    }


def get_quotas_summary() -> Dict:
    repo_root = get_repo_root()
    log_dir = repo_root / "memory" / "logs"
    usage = _parse_gateway_logs(log_dir)
    providers: Dict[str, Dict] = {}
    for provider in AIProvider:
        raw = usage.get(provider.value, usage.get(provider.value.lower(), {}))
        providers[provider.value] = _format_provider_summary(provider.value, raw)

    events = read_recent_provider_events(limit=5)

    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "providers": providers,
        "events": events,
    }
    return summary
