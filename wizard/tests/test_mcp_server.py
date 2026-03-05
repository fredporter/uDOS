import importlib
import asyncio
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def mcp_server_module():
    try:
        importlib.import_module("mcp.server.fastmcp")
    except ModuleNotFoundError:
        mcp_server_mod = pytest.importorskip("mcp.server")
        if not hasattr(mcp_server_mod, "FastMCP"):
            pytest.skip("mcp.server.FastMCP is unavailable in this MCP installation")
    module_dir = Path(__file__).resolve().parents[1] / "mcp"
    sys.path.insert(0, str(module_dir))
    try:
        return importlib.import_module("mcp_server")
    finally:
        if str(module_dir) in sys.path:
            sys.path.remove(str(module_dir))


def test_load_tool_index_reads_tools(tmp_path, mcp_server_module, monkeypatch):
    tools_path = tmp_path / "api" / "wizard" / "tools"
    tools_path.mkdir(parents=True)
    (tools_path / "mcp-tools.md").write_text(
        "- `wizard_health`\n- `ucode_dispatch`\n- `wizard_tools_list`\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mcp_server_module, "REPO_ROOT", tmp_path)
    assert mcp_server_module._load_tool_index() == [
        "wizard_health",
        "ucode_dispatch",
        "wizard_tools_list",
    ]


def test_load_tool_index_fallback_docs_path(tmp_path, mcp_server_module, monkeypatch):
    tools_path = tmp_path / "docs" / "api" / "tools"
    tools_path.mkdir(parents=True)
    (tools_path / "mcp-tools.md").write_text(
        "- `wizard_health`\n- `wizard_tools_registration_status`\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mcp_server_module, "THIS_DIR", tmp_path / "mcp")
    monkeypatch.setattr(mcp_server_module, "REPO_ROOT", tmp_path / "repo_without_api")
    assert mcp_server_module._load_tool_index() == [
        "wizard_health",
        "wizard_tools_registration_status",
    ]


def test_load_tool_index_normalizes_dotted_tool_names(tmp_path, mcp_server_module, monkeypatch):
    tools_path = tmp_path / "api" / "wizard" / "tools"
    tools_path.mkdir(parents=True)
    (tools_path / "mcp-tools.md").write_text(
        "- `wizard.health`\n- `wizard.tools.list`\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mcp_server_module, "REPO_ROOT", tmp_path)
    assert mcp_server_module._load_tool_index() == [
        "wizard_health",
        "wizard_tools_list",
    ]


def test_load_tool_index_ignores_malformed_and_noncanonical_tokens(tmp_path, mcp_server_module, monkeypatch):
    tools_path = tmp_path / "api" / "wizard" / "tools"
    tools_path.mkdir(parents=True)
    (tools_path / "mcp-tools.md").write_text(
        "\n".join(
            [
                "- `wizard_health`",
                "- `wizard.tools.list`",
                "- `WIZARD_BASE_URL`",
                "- `wizard_health` trailing",
                "wizard_config_get",
                "- wizard_config_set",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(mcp_server_module, "REPO_ROOT", tmp_path)
    assert mcp_server_module._load_tool_index() == [
        "wizard_health",
        "wizard_tools_list",
    ]


def test_extract_ucode_output_prefers_result(mcp_server_module):
    payload = {"result": {"output": "hi"}, "output": "no"}
    assert mcp_server_module._extract_ucode_output(payload) == "hi"


def test_ucode_command_wraps_display(mcp_server_module, monkeypatch):
    """Test that ucode_command wraps output with status/toolbar display.

    Note: @mcp.tool() decorated functions return string content for MCP protocol.
    """
    class DummyClient:
        def ucode_dispatch(self, command: str):
            return {"result": {"output": f"ran {command}"}}

    monkeypatch.setattr(mcp_server_module, "_client", lambda: DummyClient())
    monkeypatch.setattr(mcp_server_module, "_status_line", lambda: "[STATUS]")
    monkeypatch.setattr(mcp_server_module, "_emoji_indicator", lambda: ":)")
    monkeypatch.setattr(mcp_server_module, "_toolbar_block", lambda: "[TOOLBAR]")

    # The decorated MCP tool returns string content
    result = mcp_server_module.ucode_command("OK")
    assert isinstance(result, str)
    assert "[STATUS]" in result
    assert "[TOOLBAR]" in result
    assert "ran OK" in result


def test_ucode_dispatch_alias_delegates_to_shared_handler(mcp_server_module, monkeypatch):
    calls: list[str] = []

    def _fake_run(command: str) -> str:
        calls.append(command)
        return f"ran {command}"

    monkeypatch.setattr(mcp_server_module, "_run_ucode_command", _fake_run)
    result = mcp_server_module.ucode_dispatch("HELP")
    assert result == "ran HELP"
    assert calls == ["HELP"]


def test_wizard_tools_list_uses_index(mcp_server_module, monkeypatch):
    monkeypatch.setattr(mcp_server_module, "_load_tool_index", lambda: ["a", "b"])
    payload = mcp_server_module.wizard_tools_list()
    assert payload == {"count": 2, "tools": ["a", "b"]}


def test_wizard_tools_registration_status(mcp_server_module, monkeypatch):
    monkeypatch.setattr(mcp_server_module, "_load_tool_index", lambda: ["a", "b"])

    class DummyMCP:
        def list_tools(self):
            return [type("_Tool", (), {"name": "a"})(), type("_Tool", (), {"name": "c"})()]

    monkeypatch.setattr(mcp_server_module, "mcp", DummyMCP())
    payload = mcp_server_module.wizard_tools_registration_status()
    assert payload["protocol_version"] == "1.0.0"
    assert payload["indexed_count"] == 2
    assert payload["server_count"] == 2
    assert payload["missing_from_server"] == ["b"]
    assert payload["missing_from_index"] == ["c"]
    assert payload["valid"] is False


def test_wizard_tools_registration_status_applies_aliases_and_filters_non_tool_tokens(
    mcp_server_module, monkeypatch
):
    monkeypatch.setattr(
        mcp_server_module,
        "_load_tool_index",
        lambda: [
            "wizard_monitoring_logs_tail",
            "wizard_monitoring_logs_stats",
            "wizard_monitoring_alerts_ack",
            "wizard_monitoring_alerts_resolve",
            "WIZARD_BASE_URL",
        ],
    )

    class DummyMCP:
        def list_tools(self):
            return [
                type("_Tool", (), {"name": "wizard_monitoring_log_tail"})(),
                type("_Tool", (), {"name": "wizard_monitoring_log_stats"})(),
                type("_Tool", (), {"name": "wizard_monitoring_alert_ack"})(),
                type("_Tool", (), {"name": "wizard_monitoring_alert_resolve"})(),
            ]

    monkeypatch.setattr(mcp_server_module, "mcp", DummyMCP())
    payload = mcp_server_module.wizard_tools_registration_status()
    assert payload["indexed_count"] == 4
    assert payload["missing_from_server"] == []
    assert payload["valid"] is True


def test_enforce_mcp_security_requires_admin_token(mcp_server_module, monkeypatch):
    monkeypatch.setenv("WIZARD_MCP_REQUIRE_ADMIN_TOKEN", "1")
    monkeypatch.delenv("WIZARD_ADMIN_TOKEN", raising=False)
    mcp_server_module._MCP_LAST_CALL_TS = 0.0
    mcp_server_module._MCP_CALL_TIMESTAMPS.clear()

    with pytest.raises(RuntimeError, match="MCP admin token required"):
        mcp_server_module._enforce_mcp_security()


def test_enforce_mcp_security_per_minute_limit(mcp_server_module, monkeypatch):
    monkeypatch.setenv("WIZARD_MCP_REQUIRE_ADMIN_TOKEN", "0")
    monkeypatch.setenv("WIZARD_MCP_RATE_LIMIT_PER_MIN", "1")
    monkeypatch.setenv("WIZARD_MCP_MIN_INTERVAL_SECONDS", "0")
    mcp_server_module._MCP_LAST_CALL_TS = 0.0
    mcp_server_module._MCP_CALL_TIMESTAMPS.clear()
    monkeypatch.setattr(mcp_server_module.time, "time", lambda: 1000.0)

    mcp_server_module._enforce_mcp_security()
    with pytest.raises(RuntimeError, match="per-minute limit exceeded"):
        mcp_server_module._enforce_mcp_security()


def test_enforce_mcp_security_cooldown_active(mcp_server_module, monkeypatch):
    monkeypatch.setenv("WIZARD_MCP_REQUIRE_ADMIN_TOKEN", "0")
    monkeypatch.setenv("WIZARD_MCP_RATE_LIMIT_PER_MIN", "120")
    monkeypatch.setenv("WIZARD_MCP_MIN_INTERVAL_SECONDS", "0.05")
    mcp_server_module._MCP_LAST_CALL_TS = 0.0
    mcp_server_module._MCP_CALL_TIMESTAMPS.clear()

    now = iter([1000.0, 1000.01])
    monkeypatch.setattr(mcp_server_module.time, "time", lambda: next(now))

    mcp_server_module._enforce_mcp_security()
    with pytest.raises(RuntimeError, match="cooldown active"):
        mcp_server_module._enforce_mcp_security()


def test_mcp_limits_invalid_env_falls_back_to_defaults(mcp_server_module, monkeypatch):
    monkeypatch.setenv("WIZARD_MCP_RATE_LIMIT_PER_MIN", "not-a-number")
    monkeypatch.setenv("WIZARD_MCP_MIN_INTERVAL_SECONDS", "bad")
    assert mcp_server_module._mcp_limits() == (120, 0.05)


def test_extract_ucode_output_handles_rendered(mcp_server_module):
    """Test _extract_ucode_output extracts 'rendered' key."""
    payload = {"rendered": "formatted output"}
    assert mcp_server_module._extract_ucode_output(payload) == "formatted output"


def test_extract_ucode_output_handles_string_input(mcp_server_module):
    """Test _extract_ucode_output handles non-dict input."""
    assert mcp_server_module._extract_ucode_output("plain string") == "plain string"


def test_wrap_display_includes_all_sections(mcp_server_module, monkeypatch):
    """Test _wrap_display includes status, emoji, toolbar, and content."""
    monkeypatch.setattr(mcp_server_module, "_status_line", lambda: "[STATUS]")
    monkeypatch.setattr(mcp_server_module, "_emoji_indicator", lambda: "🙂")
    monkeypatch.setattr(mcp_server_module, "_toolbar_block", lambda: "[TOOLBAR]")

    result = mcp_server_module._wrap_display("content here")
    assert "[STATUS]" in result
    assert "🙂" in result
    assert "[TOOLBAR]" in result
    assert "content here" in result


def test_mcp_server_has_expected_tools(mcp_server_module):
    """Verify MCP server registers expected core tools."""
    tools = {tool.name for tool in asyncio.run(mcp_server_module.mcp.list_tools())}
    expected_tools = [
        "wizard_health",
        "wizard_config_get",
        "wizard_tools_list",
        "wizard_tools_registration_status",
        "ucode_command",
        "ucode_dispatch",
    ]
    for tool in expected_tools:
        assert tool in tools, f"Expected tool {tool} not found"
