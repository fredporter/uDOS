"""Vibe Skills MCP Integration

Exposes Vibe skills as MCP tools through Wizard MCP server.
Provides tool wrappers for device, vault, workspace, wizard, network,
script, user, and help skills.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, List
from pathlib import Path
import sys

# Import Vibe skill mapper from Core
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.services.vibe_skill_mapper import (
    VibeSkillMapper,
    get_default_mapper,
    SkillContract,
)
from core.services.logging_manager import get_logger
from core.services.vibe_device_service import get_device_service
from core.services.vibe_vault_service import get_vault_service
from core.services.vibe_workspace_service import get_workspace_service
from core.services.vibe_network_service import get_network_service
from core.services.vibe_script_service import get_script_service
from core.services.vibe_user_service import get_user_service
from core.services.vibe_wizard_service import get_wizard_service
from core.services.vibe_help_service import get_help_service
from core.services.vibe_ask_service import get_ask_service

logger = get_logger("vibe-mcp")


class VibeMCPIntegration:
    """Integration layer between Vibe skills and MCP tools."""

    def __init__(self):
        """Initialize Vibe MCP integration."""
        self.mapper = get_default_mapper()
        self.logger = logger

    def skill_index(self) -> Dict[str, Any]:
        """Return Vibe skill index for MCP discovery."""
        skills = self.mapper.get_all_skills()
        return {
            "status": "success",
            "skills": [
                {
                    "name": skill.name,
                    "description": skill.description,
                    "version": skill.version,
                    "actions": list(skill.actions.keys()),
                    "action_count": len(skill.actions),
                }
                for skill in skills.values()
            ],
            "total_skills": len(skills),
        }

    def skill_contract(self, skill_name: str) -> Dict[str, Any]:
        """Get full contract for a skill."""
        skill = self.mapper.get_skill(skill_name)
        if not skill:
            return {
                "status": "error",
                "message": f"Unknown skill: {skill_name}",
            }
        return {
            "status": "success",
            "contract": skill.to_dict(),
        }

    def device_list(
        self, filter: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List devices with optional filtering."""
        try:
            service = get_device_service()
            return service.list_devices(
                filter_name=filter,
                location=location,
                status=status,
            )
        except Exception as e:
            self.logger.error(f"Device list failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to list devices: {e}",
            }

    def device_status(self, device_id: str) -> Dict[str, Any]:
        """Check device health and status."""
        try:
            service = get_device_service()
            return service.device_status(device_id)
        except Exception as e:
            self.logger.error(f"Device status failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to get device status: {e}",
            }

    def vault_list(self) -> Dict[str, Any]:
        """List all vault keys."""
        try:
            service = get_vault_service()
            return service.list_keys()
        except Exception as e:
            self.logger.error(f"Vault list failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to list vault keys: {e}",
            }

    def vault_get(self, key: str) -> Dict[str, Any]:
        """Retrieve secret value."""
        try:
            service = get_vault_service()
            return service.get_secret(key)
        except Exception as e:
            self.logger.error(f"Vault get failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to retrieve secret: {e}",
            }

    def vault_set(self, key: str, value: str) -> Dict[str, Any]:
        """Store secret value."""
        try:
            service = get_vault_service()
            return service.set_secret(key, value)
        except Exception as e:
            self.logger.error(f"Vault set failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to store secret: {e}",
            }

    def workspace_list(self) -> Dict[str, Any]:
        """Enumerate workspaces."""
        try:
            service = get_workspace_service()
            return service.list_workspaces()
        except Exception as e:
            self.logger.error(f"Workspace list failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to list workspaces: {e}",
            }

    def workspace_switch(self, name: str) -> Dict[str, Any]:
        """Switch active workspace."""
        try:
            service = get_workspace_service()
            return service.switch_workspace(name)
        except Exception as e:
            self.logger.error(f"Workspace switch failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to switch workspace: {e}",
            }

    def wizard_list(self) -> Dict[str, Any]:
        """List available automations."""
        try:
            service = get_wizard_service()
            return service.list_tasks()
        except Exception as e:
            self.logger.error(f"Wizard list failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to list automations: {e}",
            }

    def wizard_start(
        self,
        project: Optional[str] = None,
        task: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Launch automation or task."""
        try:
            if not task:
                return {
                    "status": "error",
                    "message": "Task name required",
                }
            service = get_wizard_service()
            return service.start_task(task)
        except Exception as e:
            self.logger.error(f"Wizard start failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to start automation: {e}",
            }

    def network_scan(self) -> Dict[str, Any]:
        """Scan network resources."""
        try:
            service = get_network_service()
            return service.scan_network()
        except Exception as e:
            self.logger.error(f"Network scan failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to scan network: {e}",
            }

    def script_list(self) -> Dict[str, Any]:
        """List available scripts."""
        try:
            service = get_script_service()
            return service.list_scripts()
        except Exception as e:
            self.logger.error(f"Script list failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to list scripts: {e}",
            }

    def script_run(
        self,
        script_name: str,
        args: Optional[List[str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Execute script or flow."""
        try:
            service = get_script_service()
            return service.run_script(script_name, args or [])
        except Exception as e:
            self.logger.error(f"Script run failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to run script: {e}",
            }

    def user_list(self) -> Dict[str, Any]:
        """Enumerate users."""
        try:
            service = get_user_service()
            return service.list_users()
        except Exception as e:
            self.logger.error(f"User list failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to list users: {e}",
            }

    def user_add(
        self,
        username: str,
        email: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create new user."""
        try:
            service = get_user_service()
            return service.add_user(username, email, role or "user")
        except Exception as e:
            self.logger.error(f"User add failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to add user: {e}",
            }

    def help_commands(self, filter: Optional[str] = None) -> Dict[str, Any]:
        """Show available commands."""
        try:
            service = get_help_service()
            result = service.list_commands()
            # Filter results if requested
            if filter and "commands" in result:
                filtered = [
                    cmd for cmd in result["commands"]
                    if filter.lower() in cmd.get("name", "").lower() or
                    filter.lower() in cmd.get("description", "").lower()
                ]
                return {
                    **result,
                    "commands": filtered,
                    "count": len(filtered),
                }
            return result
        except Exception as e:
            self.logger.error(f"Help commands failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to retrieve help: {e}",
            }

    def ask_query(self, prompt: str) -> Dict[str, Any]:
        """Process natural language query."""
        try:
            service = get_ask_service()
            return service.query(prompt)
        except Exception as e:
            self.logger.error(f"Ask query failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to process query: {e}",
            }

    def ask_explain(
        self,
        topic: str,
        detail_level: str = "medium",
    ) -> Dict[str, Any]:
        """Get explanation of a topic."""
        try:
            service = get_ask_service()
            return service.explain(topic, detail_level)
        except Exception as e:
            self.logger.error(f"Ask explain failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to explain topic: {e}",
            }

    def ask_suggest(self, context: str) -> Dict[str, Any]:
        """Get suggestions based on context."""
        try:
            service = get_ask_service()
            return service.suggest(context)
        except Exception as e:
            self.logger.error(f"Ask suggest failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to get suggestions: {e}",
            }


# Global integration instance
_vibe_mcp: Optional[VibeMCPIntegration] = None


def get_vibe_mcp() -> VibeMCPIntegration:
    """Get or create Vibe MCP integration instance."""
    global _vibe_mcp
    if _vibe_mcp is None:
        _vibe_mcp = VibeMCPIntegration()
    return _vibe_mcp


def register_vibe_mcp_tools(mcp_server) -> None:
    """
    Register Vibe skill tools with MCP server.

    Args:
        mcp_server: FastMCP server instance
    """
    vibe = get_vibe_mcp()

    # Skill discovery and metadata
    @mcp_server.tool()
    def vibe_skill_index() -> Dict[str, Any]:
        """List all available Vibe skills."""
        return vibe.skill_index()

    @mcp_server.tool()
    def vibe_skill_contract(skill_name: str) -> Dict[str, Any]:
        """Get full contract for a Vibe skill."""
        return vibe.skill_contract(skill_name)

    # Device skill
    @mcp_server.tool()
    def vibe_device_list(
        filter: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List devices with optional filtering."""
        return vibe.device_list(filter, location, status)

    @mcp_server.tool()
    def vibe_device_status(device_id: str) -> Dict[str, Any]:
        """Check device health and status."""
        return vibe.device_status(device_id)

    # Vault skill
    @mcp_server.tool()
    def vibe_vault_list() -> Dict[str, Any]:
        """List all vault keys."""
        return vibe.vault_list()

    @mcp_server.tool()
    def vibe_vault_get(key: str) -> Dict[str, Any]:
        """Retrieve secret value."""
        return vibe.vault_get(key)

    @mcp_server.tool()
    def vibe_vault_set(key: str, value: str) -> Dict[str, Any]:
        """Store secret value."""
        return vibe.vault_set(key, value)

    # Workspace skill
    @mcp_server.tool()
    def vibe_workspace_list() -> Dict[str, Any]:
        """Enumerate workspaces."""
        return vibe.workspace_list()

    @mcp_server.tool()
    def vibe_workspace_switch(name: str) -> Dict[str, Any]:
        """Switch active workspace."""
        return vibe.workspace_switch(name)

    # Wizard skill
    @mcp_server.tool()
    def vibe_wizard_list() -> Dict[str, Any]:
        """List available automations."""
        return vibe.wizard_list()

    @mcp_server.tool()
    def vibe_wizard_start(
        project: Optional[str] = None,
        task: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Launch automation or task."""
        return vibe.wizard_start(project, task, config)

    # Network skill
    @mcp_server.tool()
    def vibe_network_scan() -> Dict[str, Any]:
        """Scan network resources."""
        return vibe.network_scan()

    # Script skill
    @mcp_server.tool()
    def vibe_script_list() -> Dict[str, Any]:
        """List available scripts."""
        return vibe.script_list()

    @mcp_server.tool()
    def vibe_script_run(
        script_name: str,
        args: Optional[List[str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Execute script or flow."""
        return vibe.script_run(script_name, args, timeout)

    # User skill
    @mcp_server.tool()
    def vibe_user_list() -> Dict[str, Any]:
        """Enumerate users."""
        return vibe.user_list()

    @mcp_server.tool()
    def vibe_user_add(
        username: str,
        email: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create new user."""
        return vibe.user_add(username, email, role)

    # Help skill
    @mcp_server.tool()
    def vibe_help_commands(filter: Optional[str] = None) -> Dict[str, Any]:
        """Show available commands."""
        return vibe.help_commands(filter)

    # Ask skill
    @mcp_server.tool()
    def vibe_ask_query(prompt: str) -> Dict[str, Any]:
        """Process natural language query."""
        return vibe.ask_query(prompt)

    @mcp_server.tool()
    def vibe_ask_explain(
        topic: str,
        detail_level: str = "medium",
    ) -> Dict[str, Any]:
        """Get explanation of a topic."""
        return vibe.ask_explain(topic, detail_level)

    @mcp_server.tool()
    def vibe_ask_suggest(context: str) -> Dict[str, Any]:
        """Get suggestions based on context."""
        return vibe.ask_suggest(context)
