"""
Vibe Workspace Service

Manages workspace environments, context switching, and workspace-specific configurations.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from core.services.logging_manager import get_logger
from core.services.persistence_service import get_persistence_service


@dataclass
class Workspace:
    """Workspace representation."""
    id: str
    name: str
    description: str
    created: str
    updated: str
    is_active: bool = False


class VibeWorkspaceService:
    """Manage workspaces and workspace context."""

    _DATA_FILE = "workspaces"

    def __init__(self):
        """Initialize workspace service."""
        self.logger = get_logger("vibe-workspace-service")
        self.persistence_service = get_persistence_service()
        self.workspaces: Dict[str, Workspace] = {}
        self.current_workspace: Optional[str] = None
        self._load_workspaces()

    def _load_workspaces(self) -> None:
        """Load workspaces from persistent storage."""
        self.logger.debug("Loading workspaces from persistence...")
        data = self.persistence_service.read_data(self._DATA_FILE)
        if data and "workspaces" in data:
            self.workspaces = {
                ws_id: Workspace(**ws_data)
                for ws_id, ws_data in data["workspaces"].items()
            }
            self.current_workspace = data.get("current_workspace")
            self.logger.info(f"Loaded {len(self.workspaces)} workspaces.")
        else:
            self.logger.warning("No persistent workspace data found. Creating default.")
            self.create_workspace("default", "Default workspace")
            self.switch_workspace("default")

    def _save_workspaces(self) -> None:
        """Save workspaces to persistent storage."""
        self.logger.debug("Saving workspaces to persistence...")
        data = {
            "workspaces": {
                ws_id: asdict(ws) for ws_id, ws in self.workspaces.items()
            },
            "current_workspace": self.current_workspace,
        }
        self.persistence_service.write_data(self._DATA_FILE, data)

    def list_workspaces(self) -> Dict[str, Any]:
        """List all workspaces."""
        workspaces = [asdict(w) for w in self.workspaces.values()]
        # Dynamically set is_active for the response
        for ws in workspaces:
            ws['is_active'] = ws['id'] == self.current_workspace

        return {
            "status": "success",
            "workspaces": workspaces,
            "count": len(workspaces),
            "current": self.current_workspace,
        }

    def switch_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Switch to a different workspace."""
        if workspace_id not in self.workspaces:
            return {
                "status": "error",
                "message": f"Workspace not found: {workspace_id}",
            }

        # Deactivate old workspace if one was active
        if self.current_workspace and self.current_workspace in self.workspaces:
            self.workspaces[self.current_workspace].is_active = False

        self.current_workspace = workspace_id
        workspace = self.workspaces[workspace_id]
        workspace.is_active = True
        self._save_workspaces()

        self.logger.info(f"Switched to workspace: {workspace_id}")

        return {
            "status": "success",
            "message": f"Workspace switched: {workspace.name}",
            "workspace": asdict(workspace),
        }

    def create_workspace(
        self,
        name: str,
        description: str = "",
    ) -> Dict[str, Any]:
        """Create a new workspace."""
        workspace_id = name.lower().replace(" ", "_")

        if workspace_id in self.workspaces:
            return {
                "status": "error",
                "message": f"Workspace already exists: {workspace_id}",
            }

        now = datetime.now().isoformat()
        workspace = Workspace(
            id=workspace_id,
            name=name,
            description=description,
            created=now,
            updated=now,
            is_active=False,  # New workspaces are not active by default
        )

        self.workspaces[workspace_id] = workspace
        self._save_workspaces()
        self.logger.info(f"Created workspace: {workspace_id}")

        return {
            "status": "success",
            "message": f"Workspace created: {name}",
            "workspace": asdict(workspace),
        }

    def delete_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Delete a workspace."""
        if workspace_id not in self.workspaces:
            return {
                "status": "error",
                "message": f"Workspace not found: {workspace_id}",
            }

        if workspace_id == self.current_workspace:
            return {
                "status": "error",
                "message": "Cannot delete the currently active workspace",
            }

        del self.workspaces[workspace_id]
        self._save_workspaces()
        self.logger.info(f"Deleted workspace: {workspace_id}")

        return {
            "status": "success",
            "message": f"Workspace deleted: {workspace_id}",
        }


# Global singleton
_workspace_service: Optional[VibeWorkspaceService] = None


def get_workspace_service() -> VibeWorkspaceService:
    """Get or create the global workspace service."""
    global _workspace_service
    if _workspace_service is None:
        _workspace_service = VibeWorkspaceService()
    return _workspace_service
