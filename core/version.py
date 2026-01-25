#!/usr/bin/env python3
"""
uDOS Version Manager
Centralised version control for all uDOS components

Usage:
    python -m core.version                    # Show all versions
    python -m core.version check              # Validate all version.json files
    python -m core.version bump core patch    # Bump core patch version
    python -m core.version set core 1.0.1.0   # Set core to specific version
    python -m core.version export             # Export all versions as JSON

Alpha v1.0.0.0 - Fresh start, no legacy versions
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Component paths relative to project root
COMPONENT_PATHS = {
    "core": "core/version.json",
    "api": "extensions/api/version.json",
    "app": "app/version.json",
    "wizard": "wizard/version.json",
    "knowledge": "knowledge/version.json",
    "transport": "extensions/transport/version.json",
    "sonic": "sonic/version.json",
}

# Legacy paths - ARCHIVED 2026-01-05 (no longer used)
# These have been moved/consolidated:
#   - tauri-udos -> .archive/ (replaced by system-app)
#   - tauri-typo -> .archive/ (replaced by system-app)
#   - cloud -> .archive/ (folded into wizard)
LEGACY_PATHS = {}

# Cache for loaded versions
_version_cache: Dict[str, Dict] = {}


def get_project_root() -> Path:
    """Get project root from this file's location."""
    return Path(__file__).parent.parent


def load_version(component: str) -> Optional[Dict[str, Any]]:
    """
    Load version.json for a component.

    Args:
        component: Component identifier (core, api, tauri-udos, etc.)

    Returns:
        Version dict or None if not found
    """
    if component in _version_cache:
        return _version_cache[component]

    if component not in COMPONENT_PATHS:
        return None

    version_path = get_project_root() / COMPONENT_PATHS[component]

    if not version_path.exists():
        return None

    try:
        with open(version_path, "r") as f:
            data = json.load(f)
            _version_cache[component] = data
            return data
    except (json.JSONDecodeError, IOError):
        return None


def _parse_version_value(version_value: Any) -> Dict[str, int]:
    if isinstance(version_value, dict):
        return {
            "major": int(version_value.get("major", 0)),
            "minor": int(version_value.get("minor", 0)),
            "patch": int(version_value.get("patch", 0)),
            "build": int(version_value.get("build", 0)),
        }
    if isinstance(version_value, str):
        parts = version_value.replace("v", "").split(".")
        while len(parts) < 4:
            parts.append("0")
        try:
            major, minor, patch, build = (int(p) for p in parts[:4])
        except ValueError:
            major = minor = patch = build = 0
        return {"major": major, "minor": minor, "patch": patch, "build": build}
    return {"major": 0, "minor": 0, "patch": 0, "build": 0}


def _coerce_schema(data: Dict[str, Any], component: str) -> Dict[str, Any]:
    version_dict = _parse_version_value(data.get("version"))
    data["version"] = version_dict

    if "name" not in data:
        data["name"] = component
    if "channel" not in data:
        data["channel"] = "dev"
    if "display" not in data:
        data["display"] = (
            f"v{version_dict['major']}."
            f"{version_dict['minor']}."
            f"{version_dict['patch']}."
            f"{version_dict['build']}"
        )

    return data


def get_version_string(component: str) -> str:
    """
    Get display version string for a component.

    Args:
        component: Component identifier

    Returns:
        Version string (e.g., "v1.0.0.0") or "unknown"
    """
    data = load_version(component)
    if not data:
        return "unknown"
    if "display" in data:
        return data["display"]
    v = _parse_version_value(data.get("version"))
    return f"v{v['major']}.{v['minor']}.{v['patch']}.{v['build']}"


def get_version_tuple(component: str) -> tuple:
    """
    Get version as tuple (major, minor, patch, build).

    Args:
        component: Component identifier

    Returns:
        Version tuple or (0, 0, 0, 0) if not found
    """
    data = load_version(component)
    if not data:
        return (0, 0, 0, 0)

    v = _parse_version_value(data.get("version"))
    return (v["major"], v["minor"], v["patch"], v["build"])


def bump_version(component: str, part: str = "build") -> bool:
    """
    Bump version for a component.

    Args:
        component: Component identifier
        part: Version part to bump (major, minor, patch, build)

    Returns:
        True if successful
    """
    if component not in COMPONENT_PATHS:
        print(f"Unknown component: {component}")
        return False

    version_path = get_project_root() / COMPONENT_PATHS[component]

    try:
        with open(version_path, "r") as f:
            data = json.load(f)

        data = _coerce_schema(data, component)
        v = data["version"]

        if part == "major":
            v["major"] += 1
            v["minor"] = 0
            v["patch"] = 0
            v["build"] = 0
        elif part == "minor":
            v["minor"] += 1
            v["patch"] = 0
            v["build"] = 0
        elif part == "patch":
            v["patch"] += 1
            v["build"] = 0
        elif part == "build":
            v["build"] += 1
        else:
            print(f"Unknown version part: {part}")
            return False

        # Update display string
        data["display"] = f"v{v['major']}.{v['minor']}.{v['patch']}.{v['build']}"
        data["released"] = datetime.now().strftime("%Y-%m-%d")

        with open(version_path, "w") as f:
            json.dump(data, f, indent=2)

        # Clear cache
        _version_cache.pop(component, None)

        print(f"OK {component}: {data['display']}")
        return True

    except (json.JSONDecodeError, IOError, KeyError) as e:
        print(f"ERROR Error bumping {component}: {e}")
        return False


def set_version(component: str, version_str: str) -> bool:
    """
    Set version for a component.

    Args:
        component: Component identifier
        version_str: Version string (e.g., "1.0.1.0")

    Returns:
        True if successful
    """
    if component not in COMPONENT_PATHS:
        print(f"Unknown component: {component}")
        return False

    parts = version_str.replace("v", "").split(".")
    if len(parts) not in (3, 4):
        print(f"Invalid version format: {version_str} (expected X.X.X[.X])")
        return False
    if len(parts) == 3:
        parts.append("0")

    try:
        version_tuple = tuple(int(p) for p in parts)
    except ValueError:
        print(f"Invalid version numbers: {version_str}")
        return False

    version_path = get_project_root() / COMPONENT_PATHS[component]

    try:
        with open(version_path, "r") as f:
            data = json.load(f)

        data = _coerce_schema(data, component)
        data["version"] = {
            "major": version_tuple[0],
            "minor": version_tuple[1],
            "patch": version_tuple[2],
            "build": version_tuple[3],
        }
        data["display"] = f"v{'.'.join(parts)}"
        data["released"] = datetime.now().strftime("%Y-%m-%d")

        with open(version_path, "w") as f:
            json.dump(data, f, indent=2)

        _version_cache.pop(component, None)

        print(f"OK {component}: {data['display']}")
        return True

    except (json.JSONDecodeError, IOError, KeyError) as e:
        print(f"ERROR Error setting {component}: {e}")
        return False


def check_all() -> bool:
    """
    Validate all version.json files.

    Returns:
        True if all valid
    """
    all_valid = True
    print("CHECK Checking all version.json files...\n")

    for component, path in COMPONENT_PATHS.items():
        version_path = get_project_root() / path

        if not version_path.exists():
            print(f"ERROR {component}: {path} NOT FOUND")
            all_valid = False
            continue

        data = load_version(component)
        if not data:
            print(f"ERROR {component}: Invalid JSON")
            all_valid = False
            continue

        # Check required fields
        required = ["component", "name", "version", "display", "channel"]
        missing = [f for f in required if f not in data]

        if missing:
            print(f"WARN  {component}: Missing fields: {missing}")
            all_valid = False
        else:
            print(f"OK {component}: {data['display']} ({data['channel']})")

    return all_valid


def show_all() -> None:
    """Display all component versions."""
    print("\n+------------------------------------------------------------+")
    print("|                    uDOS Component Versions                  |")
    print("+------------------------------------------------------------+")

    for component in COMPONENT_PATHS:
        data = load_version(component)
        if data:
            name = data.get("name", component)[:35]
            version = data.get("display", "unknown")
            channel = data.get("channel", "alpha")
            print(f"|  {name:<35} {version:>12} [{channel:^6}] |")
        else:
            print(f"|  {component:<35} {'NOT FOUND':>12} [{'?':^6}] |")

    print("+------------------------------------------------------------+\n")


def export_all() -> Dict[str, Any]:
    """
    Export all versions as JSON.

    Returns:
        Dict with all component versions
    """
    result = {"exported": datetime.now().isoformat(), "components": {}}

    for component in COMPONENT_PATHS:
        data = load_version(component)
        if data:
            result["components"][component] = {
                "display": data.get("display"),
                "channel": data.get("channel"),
                "released": data.get("released"),
            }

    return result


# Convenience functions for common use cases
def get_core_version() -> str:
    """Get core version string."""
    return get_version_string("core")


def get_api_version() -> str:
    """Get API version string."""
    return get_version_string("api")


def get_all_versions() -> Dict[str, str]:
    """Get all component versions as dict."""
    return {c: get_version_string(c) for c in COMPONENT_PATHS}


# CLI interface
if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "show":
        show_all()
    elif args[0] == "check":
        sys.exit(0 if check_all() else 1)
    elif args[0] == "bump" and len(args) >= 2:
        component = args[1]
        part = args[2] if len(args) > 2 else "build"
        sys.exit(0 if bump_version(component, part) else 1)
    elif args[0] == "set" and len(args) >= 3:
        sys.exit(0 if set_version(args[1], args[2]) else 1)
    elif args[0] == "export":
        print(json.dumps(export_all(), indent=2))
    elif args[0] == "get" and len(args) >= 2:
        print(get_version_string(args[1]))
    else:
        print(
            """
uDOS Version Manager

Usage:
    python -m core.version              Show all versions
    python -m core.version check        Validate all version.json files
    python -m core.version bump <comp> [part]  Bump version (part: major/minor/patch/build)
    python -m core.version set <comp> <ver>    Set specific version (e.g., 1.0.1.0)
    python -m core.version export       Export all versions as JSON
    python -m core.version get <comp>   Get single component version

Components: core, api, app, wizard, knowledge, transport
"""
        )
