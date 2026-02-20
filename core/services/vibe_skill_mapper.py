"""Vibe skill mapper for uCLI Vibe protocol.

Maps uCLI commands to Vibe skills and handles skill invocation.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
import json

from core.services.logging_manager import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Skill Contracts
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SkillAction:
    """Definition of a Vibe skill action."""
    name: str
    description: str
    args: List[str]  # Argument names
    optional_args: List[str] = None  # Optional argument names
    returns_type: str = "object"

    def __post_init__(self):
        if self.optional_args is None:
            self.optional_args = []


@dataclass
class SkillContract:
    """Contract for a Vibe skill."""
    name: str
    description: str
    actions: Dict[str, SkillAction]
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "actions": {
                k: {
                    "description": v.description,
                    "args": v.args,
                    "optional_args": v.optional_args,
                    "returns": v.returns_type,
                }
                for k, v in self.actions.items()
            },
        }


# ─────────────────────────────────────────────────────────────────────────────
# Built-in Skill Contracts
# ─────────────────────────────────────────────────────────────────────────────

DEVICE_SKILL = SkillContract(
    name="device",
    description="Device and machine management",
    actions={
        "list": SkillAction(
            name="list",
            description="Enumerate devices with optional filtering",
            args=[],
            optional_args=["filter", "location", "status"],
            returns_type="list[device]",
        ),
        "status": SkillAction(
            name="status",
            description="Check device health and status",
            args=["device_id"],
            optional_args=[],
            returns_type="device_status",
        ),
        "update": SkillAction(
            name="update",
            description="Modify device configuration",
            args=["device_id"],
            optional_args=["location", "config"],
            returns_type="device",
        ),
        "add": SkillAction(
            name="add",
            description="Register new device",
            args=["name"],
            optional_args=["location", "config"],
            returns_type="device",
        ),
    },
)

VAULT_SKILL = SkillContract(
    name="vault",
    description="Secret and credential management",
    actions={
        "list": SkillAction(
            name="list",
            description="Show all vault keys",
            args=[],
            optional_args=[],
            returns_type="list[string]",
        ),
        "get": SkillAction(
            name="get",
            description="Retrieve secret value",
            args=["key"],
            optional_args=[],
            returns_type="secret_value",
        ),
        "set": SkillAction(
            name="set",
            description="Store or update secret",
            args=["key", "value"],
            optional_args=[],
            returns_type="void",
        ),
        "delete": SkillAction(
            name="delete",
            description="Remove secret from vault",
            args=["key"],
            optional_args=[],
            returns_type="void",
        ),
    },
)

WORKSPACE_SKILL = SkillContract(
    name="workspace",
    description="Workspace and environment management",
    actions={
        "list": SkillAction(
            name="list",
            description="Enumerate workspaces",
            args=[],
            optional_args=[],
            returns_type="list[workspace]",
        ),
        "switch": SkillAction(
            name="switch",
            description="Switch active workspace",
            args=["name"],
            optional_args=[],
            returns_type="workspace",
        ),
        "create": SkillAction(
            name="create",
            description="Create new workspace",
            args=["name"],
            optional_args=["template"],
            returns_type="workspace",
        ),
        "delete": SkillAction(
            name="delete",
            description="Remove workspace",
            args=["name"],
            optional_args=[],
            returns_type="void",
        ),
    },
)

WIZARD_SKILL = SkillContract(
    name="wizard",
    description="Wizard automation and task management",
    actions={
        "start": SkillAction(
            name="start",
            description="Launch automation or task",
            args=[],
            optional_args=["project", "task", "config"],
            returns_type="task",
        ),
        "stop": SkillAction(
            name="stop",
            description="Halt running automation",
            args=["task_id"],
            optional_args=[],
            returns_type="void",
        ),
        "status": SkillAction(
            name="status",
            description="Check automation status",
            args=[],
            optional_args=["task_id"],
            returns_type="task_status",
        ),
        "list": SkillAction(
            name="list",
            description="Show available automations",
            args=[],
            optional_args=[],
            returns_type="list[automation]",
        ),
    },
)

ASK_SKILL = SkillContract(
    name="ask",
    description="General natural language query handling",
    actions={
        "query": SkillAction(
            name="query",
            description="Handle natural language question",
            args=["question"],
            optional_args=["context", "model"],
            returns_type="response",
        ),
    },
)

NETWORK_SKILL = SkillContract(
    name="network",
    description="Network connectivity and diagnostics",
    actions={
        "scan": SkillAction(
            name="scan",
            description="Scan network resources",
            args=[],
            optional_args=[],
            returns_type="list[network_resource]",
        ),
        "connect": SkillAction(
            name="connect",
            description="Establish network connection",
            args=["host"],
            optional_args=["port", "protocol"],
            returns_type="connection",
        ),
        "check": SkillAction(
            name="check",
            description="Diagnose network connectivity",
            args=["host"],
            optional_args=[],
            returns_type="diagnostics",
        ),
    },
)

SCRIPT_SKILL = SkillContract(
    name="script",
    description="Scripting and flow automation",
    actions={
        "run": SkillAction(
            name="run",
            description="Execute script or flow",
            args=["script_name"],
            optional_args=["args", "timeout"],
            returns_type="execution_result",
        ),
        "edit": SkillAction(
            name="edit",
            description="Edit script content",
            args=["script_name"],
            optional_args=[],
            returns_type="void",
        ),
        "list": SkillAction(
            name="list",
            description="List available scripts",
            args=[],
            optional_args=[],
            returns_type="list[script]",
        ),
    },
)

USER_SKILL = SkillContract(
    name="user",
    description="User and account management",
    actions={
        "add": SkillAction(
            name="add",
            description="Create new user",
            args=["username"],
            optional_args=["email", "role"],
            returns_type="user",
        ),
        "remove": SkillAction(
            name="remove",
            description="Delete user account",
            args=["username"],
            optional_args=[],
            returns_type="void",
        ),
        "update": SkillAction(
            name="update",
            description="Modify user properties",
            args=["username"],
            optional_args=["email", "role", "permissions"],
            returns_type="user",
        ),
        "list": SkillAction(
            name="list",
            description="Enumerate users",
            args=[],
            optional_args=[],
            returns_type="list[user]",
        ),
    },
)

HELP_SKILL = SkillContract(
    name="help",
    description="Help and documentation",
    actions={
        "commands": SkillAction(
            name="commands",
            description="Show available commands",
            args=[],
            optional_args=["filter"],
            returns_type="list[command]",
        ),
        "guide": SkillAction(
            name="guide",
            description="Show guide or tutorial",
            args=["topic"],
            optional_args=[],
            returns_type="guide_content",
        ),
    },
)

# Skill registry
SKILL_REGISTRY = {
    "device": DEVICE_SKILL,
    "vault": VAULT_SKILL,
    "workspace": WORKSPACE_SKILL,
    "wizard": WIZARD_SKILL,
    "ask": ASK_SKILL,
    "network": NETWORK_SKILL,
    "script": SCRIPT_SKILL,
    "user": USER_SKILL,
    "help": HELP_SKILL,
}


# ─────────────────────────────────────────────────────────────────────────────
# Skill Mapper
# ─────────────────────────────────────────────────────────────────────────────

class VibeSkillMapper:
    """Maps uCLI input to Vibe skills."""

    def __init__(self):
        """Initialize skill mapper."""
        self.logger = get_logger("vibe-skill-mapper")
        self.registry = SKILL_REGISTRY

    def get_skill(self, skill_name: str) -> Optional[SkillContract]:
        """Get skill contract by name."""
        return self.registry.get(skill_name.lower())

    def list_skills(self) -> List[str]:
        """List all available skills."""
        return list(self.registry.keys())

    def get_all_skills(self) -> Dict[str, SkillContract]:
        """Get all skill contracts."""
        return self.registry.copy()

    def validate_invocation(self, skill_name: str, action: str, args: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate skill action invocation.

        Args:
            skill_name: Name of skill
            action: Action name
            args: Arguments dict

        Returns:
            (is_valid, error_message)
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return False, f"Unknown skill: {skill_name}"

        if action not in skill.actions:
            valid_actions = ", ".join(skill.actions.keys())
            return False, f"Unknown action '{action}' for skill '{skill_name}'. Valid actions: {valid_actions}"

        # Validate required arguments
        skill_action = skill.actions[action]
        for required_arg in skill_action.args:
            if required_arg not in args:
                return False, f"Missing required argument: {required_arg}"

        return True, None

    def invocation_to_string(self, skill_name: str, action: Optional[str] = None, args: Optional[Dict[str, Any]] = None) -> str:
        """
        Format skill invocation as string.

        Args:
            skill_name: Skill name
            action: Action name (optional)
            args: Arguments dict (optional)

        Returns:
            Formatted invocation string (e.g., "vibe device list --filter active")
        """
        invocation = f"vibe {skill_name}"

        if action:
            invocation += f" {action}"

        if args:
            for key, value in args.items():
                if value is not None:
                    invocation += f" --{key} {value}"

        return invocation


# ─────────────────────────────────────────────────────────────────────────────
# Convenience Functions
# ─────────────────────────────────────────────────────────────────────────────

_default_mapper: Optional[VibeSkillMapper] = None


def get_default_mapper() -> VibeSkillMapper:
    """Get or create default skill mapper."""
    global _default_mapper
    if _default_mapper is None:
        _default_mapper = VibeSkillMapper()
    return _default_mapper


def list_all_skills() -> List[str]:
    """List all available Vibe skills."""
    return get_default_mapper().list_skills()


def get_skill_contract(skill_name: str) -> Optional[SkillContract]:
    """Get skill contract by name."""
    return get_default_mapper().get_skill(skill_name)


def format_skill_invocation(skill_name: str, action: str = None, args: Dict[str, Any] = None) -> str:
    """Format skill invocation as string."""
    return get_default_mapper().invocation_to_string(skill_name, action, args)
