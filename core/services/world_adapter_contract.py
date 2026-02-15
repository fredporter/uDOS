"""Utilities for v1.3.21 world/adapter contract validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from core.services.logging_api import get_repo_root


def _contract_path() -> Path:
    return get_repo_root() / "core" / "config" / "world_adapter_contract_v1_3_21.json"


def load_world_adapter_contract() -> Dict[str, Any]:
    return json.loads(_contract_path().read_text(encoding="utf-8"))


def validate_canonical_event(event: Dict[str, Any], contract: Dict[str, Any] | None = None) -> Tuple[bool, List[str]]:
    """Validate canonical map event shape against v1.3.21 contract."""

    contract = contract or load_world_adapter_contract()
    errors: List[str] = []

    required_fields = contract.get("events", {}).get("required_fields", [])
    for field in required_fields:
        if field not in event:
            errors.append(f"missing event field: {field}")

    event_type = str(event.get("type", "")).upper()
    canonical_types = {str(x).upper() for x in contract.get("events", {}).get("canonical_types", [])}
    if event_type not in canonical_types:
        errors.append(f"non-canonical event type: {event_type}")

    payload = event.get("payload", {})
    if not isinstance(payload, dict):
        errors.append("payload must be an object")
        return False, errors

    required_payload = contract.get("events", {}).get("required_payload_fields", {}).get(event_type, [])
    for field in required_payload:
        if field not in payload:
            errors.append(f"missing payload field for {event_type}: {field}")

    return len(errors) == 0, errors
