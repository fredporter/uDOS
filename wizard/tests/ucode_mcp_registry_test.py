from wizard.mcp.tools.ucode_mcp_registry import (
    MCPToolLane,
    tool_names,
    tool_registry_records,
)


def test_ucode_mcp_registry_generic_and_proxy_sets_are_canonical() -> None:
    assert set(tool_names(MCPToolLane.GENERIC)) == {"ucode_tools_list", "ucode_tools_call"}
    assert set(tool_names(MCPToolLane.PROXY)) == {
        "ucode_health",
        "ucode_token",
        "ucode_help",
        "ucode_verify",
        "ucode_repair",
        "ucode_config",
        "ucode_run",
        "ucode_read",
    }


def test_ucode_mcp_registry_has_unique_names() -> None:
    names = tool_names()
    assert len(names) == len(set(names))


def test_ucode_mcp_registry_records_include_ownership_fields() -> None:
    records = tool_registry_records()
    assert records
    for record in records:
        assert record["name"]
        assert record["lane"] in {"generic", "proxy"}
        assert record["owner_module"]
        assert record["rationale"]
