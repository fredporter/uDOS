"""Tests for the v1.5 Dev Mode tool-backed ucode registry."""

from __future__ import annotations

from wizard.mcp.tools.ucode_registry import (
    discover_ucode_tools,
    get_tool_by_name,
    get_tool_description,
    get_tool_schema,
    list_all_tools,
)


def test_discover_ucode_tools_returns_dict() -> None:
    tools = discover_ucode_tools()
    assert isinstance(tools, dict)


def test_list_all_tools_matches_discover() -> None:
    assert list_all_tools() == discover_ucode_tools()


def test_get_tool_schema_and_description_defaults() -> None:
    assert get_tool_schema({}) == {"type": "object", "properties": {}}
    assert get_tool_description({}) == ""


def test_get_tool_schema_and_description_from_metadata() -> None:
    meta = {
        "schema": {"type": "object", "properties": {"path": {"type": "string"}}},
        "description": "Read a local file",
    }
    assert get_tool_schema(meta) == meta["schema"]
    assert get_tool_description(meta) == "Read a local file"


def test_get_tool_by_name_handles_missing_and_known_tools() -> None:
    assert get_tool_by_name("__does_not_exist__") is None

    tools = list_all_tools()
    if tools:
        first_name = next(iter(tools.keys()))
        resolved = get_tool_by_name(first_name)
        assert resolved is not None
        assert resolved["name"] == first_name
        assert isinstance(resolved.get("schema"), dict)
