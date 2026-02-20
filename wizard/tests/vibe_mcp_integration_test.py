"""Tests for Vibe MCP Integration

Verifies:
- Vibe MCP module loads correctly
- Skill discovery works
- MCP tool registration succeeds
- Skills can be queried
"""

import pytest
from pathlib import Path
import sys

# Add wizard module to path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "wizard" / "mcp"))

from vibe_mcp_integration import (
    VibeMCPIntegration,
    get_vibe_mcp,
)


class TestVibeMCPIntegration:
    """Test Vibe MCP integration."""

    def test_vibe_mcp_instantiation(self):
        """VibeMCPIntegration should instantiate correctly."""
        vibe = VibeMCPIntegration()
        assert vibe is not None
        assert vibe.mapper is not None

    def test_skill_index(self):
        """skill_index() should return list of all skills."""
        vibe = get_vibe_mcp()
        result = vibe.skill_index()

        assert result["status"] == "success"
        assert "skills" in result
        assert len(result["skills"]) == 9  # 9 built-in skills
        assert result["total_skills"] == 9

        # Check skill names
        skill_names = {skill["name"] for skill in result["skills"]}
        expected_skills = {
            "device", "vault", "workspace", "wizard",
            "ask", "network", "script", "user", "help"
        }
        assert skill_names == expected_skills

    def test_skill_contract_device(self):
        """skill_contract() should return full device skill contract."""
        vibe = get_vibe_mcp()
        result = vibe.skill_contract("device")

        assert result["status"] == "success"
        assert "contract" in result

        contract = result["contract"]
        assert contract["name"] == "device"
        assert "actions" in contract
        assert "list" in contract["actions"]
        assert "status" in contract["actions"]

    def test_skill_contract_vault(self):
        """skill_contract() should return full vault skill contract."""
        vibe = get_vibe_mcp()
        result = vibe.skill_contract("vault")

        assert result["status"] == "success"
        contract = result["contract"]
        assert contract["name"] == "vault"
        assert "list" in contract["actions"]
        assert "get" in contract["actions"]
        assert "set" in contract["actions"]
        assert "delete" in contract["actions"]

    def test_skill_contract_workspace(self):
        """skill_contract() should return full workspace skill contract."""
        vibe = get_vibe_mcp()
        result = vibe.skill_contract("workspace")

        assert result["status"] == "success"
        contract = result["contract"]
        assert contract["name"] == "workspace"
        assert "list" in contract["actions"]
        assert "switch" in contract["actions"]

    def test_skill_contract_unknown_skill(self):
        """skill_contract() should handle unknown skills gracefully."""
        vibe = get_vibe_mcp()
        result = vibe.skill_contract("nonexistent_skill")

        assert result["status"] == "error"
        assert "Unknown skill" in result["message"]

    def test_device_list(self):
        """device_list() should return device list (backend pending)."""
        vibe = get_vibe_mcp()
        result = vibe.device_list(filter="active", location="Brisbane")

        assert "status" in result
        assert "message" in result

    def test_vault_get(self):
        """vault_get() should handle vault operations."""
        vibe = get_vibe_mcp()
        result = vibe.vault_get("test_key")

        assert result["key"] == "test_key"
        assert "***" in result["value"]  # Value should be redacted

    def test_workspace_list(self):
        """workspace_list() should return workspace list."""
        vibe = get_vibe_mcp()
        result = vibe.workspace_list()

        assert "status" in result

    def test_wizard_start(self):
        """wizard_start() should handle automation launch."""
        vibe = get_vibe_mcp()
        result = vibe.wizard_start(project="test_project", task="test_task")

        assert result["project"] == "test_project"
        assert result["task"] == "test_task"

    def test_get_vibe_mcp_singleton(self):
        """get_vibe_mcp() should return singleton instance."""
        vibe1 = get_vibe_mcp()
        vibe2 = get_vibe_mcp()

        assert vibe1 is vibe2

    def test_all_skills_in_index(self):
        """All skills should appear in index."""
        vibe = get_vibe_mcp()
        index = vibe.skill_index()
        all_skill_names = [skill["name"] for skill in index["skills"]]

        # Test we can get contract for each skill
        for skill_name in all_skill_names:
            result = vibe.skill_contract(skill_name)
            assert result["status"] == "success", f"Failed to get contract for {skill_name}"

    def test_skill_actions_documented(self):
        """Each skill should have documented actions."""
        vibe = get_vibe_mcp()
        index = vibe.skill_index()

        for skill in index["skills"]:
            assert "actions" in skill
            assert len(skill["actions"]) > 0, f"Skill {skill['name']} has no actions"
            assert "action_count" in skill
            assert skill["action_count"] == len(skill["actions"])


class TestVibeMCPToolRegistration:
    """Test that Vibe MCP tools can be registered with FastMCP."""

    def test_can_create_mock_mcp_server(self):
        """Should be able to create a mock MCP server for testing."""
        # Mock FastMCP server
        class MockMCP:
            def __init__(self):
                self.tools = {}

            def tool(self):
                def decorator(func):
                    self.tools[func.__name__] = func
                    return func
                return decorator

        mcp_server = MockMCP()

        # This would import and register in real scenario
        from vibe_mcp_integration import register_vibe_mcp_tools
        register_vibe_mcp_tools(mcp_server)

        # Check that tools were registered
        assert len(mcp_server.tools) > 0
        assert "vibe_skill_index" in mcp_server.tools
        assert "vibe_device_list" in mcp_server.tools
        assert "vibe_vault_get" in mcp_server.tools

    def test_registered_tools_callable(self):
        """Registered tools should be callable."""
        class MockMCP:
            def __init__(self):
                self.tools = {}

            def tool(self):
                def decorator(func):
                    self.tools[func.__name__] = func
                    return func
                return decorator

        mcp_server = MockMCP()
        from vibe_mcp_integration import register_vibe_mcp_tools
        register_vibe_mcp_tools(mcp_server)

        # Test calling a tool
        skill_index_tool = mcp_server.tools["vibe_skill_index"]
        result = skill_index_tool()

        assert result["status"] == "success"
        assert len(result["skills"]) == 9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
