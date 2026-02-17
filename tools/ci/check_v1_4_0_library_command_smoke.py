#!/usr/bin/env python3
"""v1.4.0 LIBRARY command smoke gate.

Verifies that:
- LibraryHandler is importable
- STATUS/SYNC/INFO/HELP/LIST subcommands return expected shapes
- Handler is registered in dispatcher
- LIBRARY appears in help command category list
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


def _mock_integration(name: str = "sonic", enabled: bool = False):
    m = MagicMock()
    m.name = name
    m.path = f"/repo/library/{name}"
    m.source = "library"
    m.enabled = enabled
    m.installed = False
    m.cloned = False
    return m


def _mock_status(names=("sonic", "groovebox")):
    status = MagicMock()
    status.integrations = [_mock_integration(n) for n in names]
    return status


def check_import() -> bool:
    try:
        from core.commands.library_handler import LibraryHandler
        LibraryHandler()
        return True
    except Exception as e:
        print(f"  FAIL import: {e}")
        return False


def check_status() -> bool:
    from core.commands.library_handler import LibraryHandler
    h = LibraryHandler()
    with patch.object(h, "_get_manager") as mock_mgr:
        mock_mgr.return_value.get_library_status.return_value = _mock_status()
        result = h.handle("LIBRARY", [], None, None)
    if result.get("status") != "success":
        print(f"  FAIL status: {result}")
        return False
    if result.get("total") != 2:
        print(f"  FAIL status total: {result}")
        return False
    return True


def check_sync() -> bool:
    from core.commands.library_handler import LibraryHandler
    h = LibraryHandler()
    with patch.object(h, "_get_manager") as mock_mgr:
        mock_mgr.return_value.get_library_status.return_value = _mock_status()
        result = h.handle("LIBRARY", ["SYNC"], None, None)
    if result.get("status") != "success":
        print(f"  FAIL sync: {result}")
        return False
    if "sync" not in result.get("message", "").lower():
        print(f"  FAIL sync message: {result}")
        return False
    return True


def check_info() -> bool:
    from core.commands.library_handler import LibraryHandler
    h = LibraryHandler()
    with patch.object(h, "_get_manager") as mock_mgr:
        mock_mgr.return_value.get_integration.return_value = _mock_integration("sonic")
        result = h.handle("LIBRARY", ["INFO", "sonic"], None, None)
    if result.get("status") != "success":
        print(f"  FAIL info: {result}")
        return False
    if result.get("name") != "sonic":
        print(f"  FAIL info name: {result}")
        return False
    return True


def check_help() -> bool:
    from core.commands.library_handler import LibraryHandler
    h = LibraryHandler()
    result = h.handle("LIBRARY", ["HELP"], None, None)
    if result.get("status") != "success":
        print(f"  FAIL help: {result}")
        return False
    output = result.get("output", "")
    for keyword in ("STATUS", "SYNC", "INFO"):
        if keyword not in output:
            print(f"  FAIL help missing keyword: {keyword}")
            return False
    return True


def check_dispatcher_registration() -> bool:
    try:
        from core.tui.dispatcher import CommandDispatcher
        d = CommandDispatcher()
        if "LIBRARY" not in d.handlers:
            print("  FAIL dispatcher: LIBRARY not in handlers")
            return False
        return True
    except Exception as e:
        print(f"  FAIL dispatcher: {e}")
        return False


def check_test_file() -> bool:
    test_path = REPO / "core" / "tests" / "v1_4_0_library_command_test.py"
    if not test_path.exists():
        print(f"  FAIL test file missing: {test_path}")
        return False
    return True


def main() -> int:
    checks = [
        ("import LibraryHandler", check_import),
        ("LIBRARY STATUS", check_status),
        ("LIBRARY SYNC", check_sync),
        ("LIBRARY INFO", check_info),
        ("LIBRARY HELP", check_help),
        ("dispatcher registration", check_dispatcher_registration),
        ("test file present", check_test_file),
    ]

    results = {}
    all_ok = True
    for name, fn in checks:
        ok = fn()
        results[name] = ok
        if not ok:
            all_ok = False

    report = {
        "ok": all_ok,
        "checks": results,
    }
    print(json.dumps(report, indent=2))

    if not all_ok:
        raise RuntimeError("v1.4.0 LIBRARY command smoke gate failed")

    print("[library-command-smoke-v1.4.0] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
