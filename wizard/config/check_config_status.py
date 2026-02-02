#!/usr/bin/env python3
"""
Local config sanity checker (no secrets printed).

Checks expected Wizard config files in this folder and reports missing keys
without revealing values. Intended for dev/test readiness after v1.0.6.0.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

CONFIG_DIR = Path(__file__).parent

# Required keys per file (nested paths expressed as tuples)
REQUIRED_KEYS: Dict[str, List[Tuple[str, ...]]] = {
    "ai_keys.json": [
        ("GEMINI_API_KEY",),
        ("OPENAI_API_KEY",),
        ("MISTRAL_API_KEY",),
        ("OLLAMA_HOST",),
    ],
    "oauth_providers.json": [
        ("google", "client_id"),
        ("google", "client_secret"),
        ("github", "client_id"),
        ("github", "client_secret"),
    ],
    "github_keys.json": [
        ("tokens", "default", "key_id"),
    ],
    "notion_keys.json": [
        ("integration", "key_id"),
    ],
    "port_registry.json": [],
}


def get_nested(data: dict, path: Tuple[str, ...]):
    current = data
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def check_file(file_name: str, required: Iterable[Tuple[str, ...]]):
    path = CONFIG_DIR / file_name
    if not path.exists():
        return {"exists": False, "missing": list(required)}

    try:
        data = json.loads(path.read_text())
    except Exception:
        return {"exists": True, "invalid_json": True, "missing": list(required)}

    missing: List[Tuple[str, ...]] = []
    for path_tuple in required:
        if get_nested(data, path_tuple) in (None, ""):
            missing.append(path_tuple)

    return {"exists": True, "missing": missing, "invalid_json": False}


def main():
    print("Wizard config status (no secrets shown)\n")
    for file_name, required in REQUIRED_KEYS.items():
        result = check_file(file_name, required)
        status = []

        if not result.get("exists"):
            status.append("MISSING FILE")
        elif result.get("invalid_json"):
            status.append("INVALID JSON")
        else:
            missing = result.get("missing", [])
            status.append("OK" if not missing else f"missing {len(missing)} keys")

        print(f"- {file_name}: {'; '.join(status)}")
        missing_keys = result.get("missing", [])
        if missing_keys:
            joined = [".".join(parts) for parts in missing_keys]
            print(f"  -> add: {', '.join(joined)}")
    print("\nNote: values are intentionally hidden; populate files from the templates in this folder.")


if __name__ == "__main__":
    main()
