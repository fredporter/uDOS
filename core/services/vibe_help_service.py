"""
Dev Mode tool help service.

Provides contributor-tool documentation, command references, and tutorial guidance.
"""

from typing import Dict, List, Any, Optional

from core.services.logging_manager import get_logger


class DevModeToolHelpService:
    """Provide Dev Mode contributor-tool help and learning resources."""

    def __init__(self):
        """Initialize help service."""
        self.logger = get_logger("dev-mode-tool-help-service")
        self.help_topics = self._build_help_index()

    def _build_help_index(self) -> Dict[str, Dict[str, str]]:
        """Build help topic index."""
        return {
            "getting_started": {
                "title": "Getting Started with uDOS",
                "description": "Introduction to uDOS and basic operations",
                "url": "docs/guides/getting-started.md",
            },
            "commands": {
                "title": "uCODE Command Reference",
                "description": "Complete list of available uCODE commands",
                "url": "docs/reference/commands.md",
            },
            "skills": {
                "title": "Dev Mode Tool Skills Guide",
                "description": "Guide to using Dev Mode contributor-tool skills (device, vault, workspace, etc.)",
                "url": "docs/howto/HOW-TO-USE-SKILLS.md",
            },
            "troubleshooting": {
                "title": "Troubleshooting Guide",
                "description": "Solutions for common problems and errors",
                "url": "docs/guides/troubleshooting.md",
            },
            "automation": {
                "title": "Automation Workflows",
                "description": "Creating and managing automated tasks",
                "url": "docs/guides/automation.md",
            },
        }

    def list_commands(self) -> Dict[str, Any]:
        """List all available commands."""
        commands = [
            ("MAP", "Display current location map"),
            ("HELP", "Show help information"),
            ("GRAB", "Pick up or take an item"),
            ("BAG", "View inventory"),
            ("VERIFY", "System health check"),
            ("HEALTH", "Show system status"),
            ("DEVICE", "Manage devices"),
            ("VAULT", "Manage secrets"),
            ("WORKSPACE", "Manage workspaces"),
            ("WIZARD", "Automation tasks"),
        ]

        return {
            "status": "success",
            "commands": [
                {"name": name, "description": desc}
                for name, desc in commands
            ],
            "count": len(commands),
        }

    def get_guide(self, topic: str) -> Dict[str, Any]:
        """
        Get detailed guide for a help topic.

        Args:
            topic: Help topic (getting_started|commands|skills|troubleshooting|automation)

        Returns:
            Dict with guide content
        """
        if topic not in self.help_topics:
            return {
                "status": "error",
                "message": f"Help topic not found: {topic}",
                "available_topics": list(self.help_topics.keys()),
            }

        help_item = self.help_topics[topic]

        return {
            "status": "success",
            "topic": topic,
            "title": help_item["title"],
            "description": help_item["description"],
            "url": help_item["url"],
            "content": f"[Help content for {topic} loaded from {help_item['url']}]",
        }


# Global singleton
VibeHelpService = DevModeToolHelpService

_help_service: Optional[DevModeToolHelpService] = None


def get_help_service() -> DevModeToolHelpService:
    """Get or create the global help service."""
    global _help_service
    if _help_service is None:
        _help_service = DevModeToolHelpService()
    return _help_service
