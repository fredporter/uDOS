from core.services.dev_tool_registry import build_dev_tool_command, list_dev_tools


def test_dev_tool_registry_has_expected_subset() -> None:
    names = [tool.name for tool in list_dev_tools()]
    assert names == [
        "ucode_config",
        "ucode_health",
        "ucode_help",
        "ucode_read",
        "ucode_repair",
        "ucode_run",
        "ucode_seed",
        "ucode_setup",
        "ucode_token",
        "ucode_verify",
    ]


def test_dev_tool_registry_builds_canonical_commands() -> None:
    assert build_dev_tool_command("ucode_health", {"check": "disk"}) == "HEALTH disk"
    assert build_dev_tool_command("ucode_verify", {"target": "core"}) == "VERIFY core"
    assert (
        build_dev_tool_command("ucode_run", {"script": "demo.md", "dry_run": True})
        == "RUN demo.md --dry-run"
    )
    assert build_dev_tool_command("ucode_read", {"path": "README.md"}) == "READ README.md"
