from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.services.error_contract import CommandError
from core.commands.ucode_handler import UcodeHandler
from core.tui.dispatcher import CommandDispatcher


def _handler_with_home(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("UDOS_UCODE_ROOT", str(tmp_path / "ucode-cache"))
    return UcodeHandler()


def test_ucode_help_surface(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)
    result = handler.handle("UCODE", [])
    assert result["status"] == "success"
    assert "UCODE DEMO LIST" in result["output"]
    assert "UCODE PROFILE <LIST|SHOW|INSTALL|ENABLE|DISABLE|VERIFY>" in result["output"]


def test_ucode_demo_list_and_run(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)

    listed = handler.handle("UCODE", ["DEMO", "LIST"])
    assert listed["status"] == "success"
    assert "parse_file" in listed["output"]

    ran = handler.handle("UCODE", ["DEMO", "RUN", "parse_file"])
    assert ran["status"] == "success"
    assert "Demo: parse_file" in ran["output"]


def test_ucode_docs_query(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)
    result = handler.handle("UCODE", ["DOCS", "--query", "reference"])
    assert result["status"] == "success"
    assert "ucode-reference.md" in result["output"]


def test_ucode_system_info(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)
    result = handler.handle("UCODE", ["SYSTEM", "INFO"])
    assert result["status"] == "success"
    assert "CPU cores" in result["output"]
    assert "Storage" in result["output"]
    assert "Minimum spec" in result["output"]
    assert "Field validation" in result["output"]


def test_ucode_system_info_minimum_spec_status(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)
    monkeypatch.setattr("core.commands.ucode_handler.os.cpu_count", lambda: 4)
    monkeypatch.setattr(handler, "_detect_ram_gb", lambda: 8.0)
    monkeypatch.setattr(
        "core.commands.ucode_handler.shutil.disk_usage",
        lambda _path: SimpleNamespace(
            free=10 * (1024 ** 3),
            total=100 * (1024 ** 3),
        ),
    )
    result = handler.handle("UCODE", ["SYSTEM", "INFO"])
    minimum_spec = result["system"]["minimum_spec"]["result"]
    assert minimum_spec["overall"] is True
    assert minimum_spec["cpu"] is True
    assert minimum_spec["ram"] is True
    assert minimum_spec["storage"] is True


def test_ucode_capabilities_filter(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)
    monkeypatch.setattr(handler, "_network_reachable", lambda: False)
    result = handler.handle("UCODE", ["CAPABILITIES", "--filter", "wizard"])
    assert result["status"] == "success"
    assert "wizard.server" in result["output"]


def test_ucode_capabilities_profile_filter(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)
    monkeypatch.setattr(handler, "_network_reachable", lambda: True)
    result = handler.handle("UCODE", ["CAPABILITIES", "--filter", "profile:core"])
    assert result["status"] == "success"
    assert result["filter_profile"] == "core"
    assert "wizard.server" not in result["output"]
    assert "demo.scripts" in result["output"]


def test_ucode_update_offline_reports_fallback_order(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)
    monkeypatch.setattr(handler, "_network_reachable", lambda: False)
    result = handler.handle("UCODE", ["UPDATE"])
    assert result["status"] == "warning"
    assert result["fallback_order"] == [
        "UCODE DEMO LIST",
        "UCODE DOCS --query <text>",
        "UCODE SYSTEM INFO",
        "UCODE CAPABILITIES --filter <text>",
    ]


def test_ucode_update_online_refreshes_manifest(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)
    monkeypatch.setattr(handler, "_network_reachable", lambda: True)
    stale_demo = Path(handler.demos_root / "parse_file.txt")
    stale_demo.parent.mkdir(parents=True, exist_ok=True)
    stale_demo.write_text("stale", encoding="utf-8")

    result = handler.handle("UCODE", ["UPDATE"])
    assert result["status"] == "success"
    assert "refreshed" in result["output"]
    assert "Demo: parse_file" in stale_demo.read_text(encoding="utf-8")

    manifest_path = Path(handler.ucode_root / "update-manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["network"] == "online"
    assert "updated_at" in manifest

    bundle_path = Path(handler.ucode_root / "bundles" / "offline-content-bundle.json")
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert bundle["algorithm"] == "sha256+hmac-sha256"
    assert bundle["verification"]["verified"] is True
    assert bundle["files"]


def test_ucode_plugin_list_initially_empty(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)
    result = handler.handle("UCODE", ["PLUGIN", "LIST"])
    assert result["status"] == "success"
    assert result["plugins"] == []
    assert "No plugins installed" in result["output"]


def test_ucode_plugin_install_and_capabilities(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)
    installed = handler.handle("UCODE", ["PLUGIN", "INSTALL", "sample-plugin"])
    assert installed["status"] == "success"
    assert installed["plugin"]["name"] == "sample-plugin"

    listed = handler.handle("UCODE", ["PLUGIN", "LIST"])
    assert listed["status"] == "success"
    assert listed["plugins"][0]["name"] == "sample-plugin"

    capabilities = handler.handle("UCODE", ["CAPABILITIES", "--filter", "sample-plugin"])
    assert capabilities["status"] == "success"
    assert "plugin.sample-plugin" in capabilities["output"]


def test_ucode_plugin_install_rejects_invalid_name(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)
    with pytest.raises(CommandError):
        handler.handle("UCODE", ["PLUGIN", "INSTALL", "Invalid Name"])


def test_ucode_metrics_summary_tracks_local_usage(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)
    handler.handle("UCODE", ["DEMO", "LIST"])
    monkeypatch.setattr(handler, "_network_reachable", lambda: False)
    handler.handle("UCODE", ["CAPABILITIES"])

    metrics = handler.handle("UCODE", ["METRICS"])
    assert metrics["status"] == "success"
    assert metrics["metrics"]["total_events"] >= 2
    assert metrics["metrics"]["fallback_events"] >= 1
    assert metrics["metrics"]["offline_events"] >= 1
    assert "demo" in metrics["metrics"]["actions"]
    assert "capabilities" in metrics["metrics"]["actions"]

    events_path = Path(handler.ucode_root / "metrics" / "usage-events.jsonl")
    summary_path = Path(handler.ucode_root / "metrics" / "usage-summary.json")
    assert events_path.exists()
    assert summary_path.exists()


def test_dispatcher_accepts_ucli_alias(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch("UCLI DEMO LIST")
    assert result["status"] == "success"
    assert "parse_file" in result["output"]


def test_ucode_profile_lifecycle(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)

    listed = handler.handle("UCODE", ["PROFILE", "LIST"])
    assert listed["status"] == "success"
    assert "core" in listed["output"]

    installed = handler.handle("UCODE", ["PROFILE", "INSTALL", "home"])
    assert installed["status"] == "success"
    assert "home" in installed["output"]

    shown = handler.handle("UCODE", ["PROFILE", "SHOW", "home"])
    assert shown["status"] == "success"
    assert "Profile: Home (home)" in shown["output"]

    verified = handler.handle("UCODE", ["PROFILE", "VERIFY", "core"])
    assert verified["status"] == "success"
    assert "Profile verify: core" in verified["output"]


def test_ucode_operator_status_and_plan(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)

    status = handler.handle("UCODE", ["OPERATOR", "STATUS"])
    assert status["status"] == "success"
    assert "Operator mode:" in status["output"]

    plan = handler.handle("UCODE", ["OPERATOR", "PLAN", "install", "creator", "profile"])
    assert plan["status"] == "success"
    assert "Intent: profiles" in plan["output"]
    assert "UCODE PROFILE INSTALL creator" in plan["output"]


def test_ucode_extension_and_package_views(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)

    extensions = handler.handle("UCODE", ["EXTENSION", "LIST"])
    assert extensions["status"] == "success"
    assert "groovebox" in extensions["output"]

    package_groups = handler.handle("UCODE", ["PACKAGE", "VERIFY", "utilities"])
    assert package_groups["status"] == "success"
    assert "Package group: Utilities (utilities)" in package_groups["output"]


def test_ucode_repair_status(monkeypatch, tmp_path):
    handler = _handler_with_home(monkeypatch, tmp_path)
    result = handler.handle("UCODE", ["REPAIR", "STATUS"])
    assert result["status"] == "success"
    assert "Rebaseline repair contracts:" in result["output"]
