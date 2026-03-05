from wizard.mcp.tools import ucode_proxies, ucode_tools


class _Gateway:
    def ucode_dispatch(self, command: str):
        return {
            "result": {"status": "success", "output": f"ran {command}"},
            "routing_contract": {"tool_gateway": "wizard-mcp"},
        }


def test_ucode_tool_list_exposes_udos_owned_registry(monkeypatch):
    monkeypatch.setattr(ucode_tools, "_dev_tool_error", lambda: None)
    payload = ucode_tools.ucode_tool_list()
    assert payload["status"] == "success"
    assert payload["count"] >= 10
    assert any(tool["name"] == "ucode_health" for tool in payload["tools"])


def test_ucode_tool_call_dispatches_canonical_command(monkeypatch):
    monkeypatch.setattr(ucode_tools, "_dev_tool_error", lambda: None)
    monkeypatch.setattr(ucode_tools, "WizardGateway", lambda: _Gateway())
    payload = ucode_tools.ucode_tool_call("ucode_verify", {"target": "core"})
    assert payload["status"] == "success"
    assert payload["command"] == "VERIFY core"
    assert payload["result"]["output"] == "ran VERIFY core"


def test_ucode_proxy_uses_generic_dev_tool_dispatch(monkeypatch):
    monkeypatch.setattr(ucode_tools, "_dev_tool_error", lambda: None)
    monkeypatch.setattr(ucode_tools, "WizardGateway", lambda: _Gateway())
    payload = ucode_proxies.proxy_read("README.md")
    assert payload["status"] == "success"
    assert payload["command"] == "READ README.md"
