"""
Workspace Command Handler

Routes WORKSPACE/TAG/LOCATION command families to SpatialFilesystemHandler.
"""

from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.commands.spatial_filesystem_handler import (
    SpatialFilesystemHandler,
    dispatch_spatial_command,
)
from core.services.spatial_filesystem import UserRole


class WorkspaceHandler(BaseCommandHandler):
    """Command adapter for spatial filesystem command families."""

    def __init__(self):
        super().__init__()
        self._handler = SpatialFilesystemHandler(fs=None)

    def _get_user_role(self) -> UserRole:
        try:
            from core.services.user_service import get_user_manager, is_ghost_mode

            if is_ghost_mode():
                return UserRole.GUEST

            user = get_user_manager().current()
            if user and user.role:
                return UserRole(user.role.value)
        except Exception:
            pass

        admin_mode = self.get_state("dev_mode", False) or self.get_state("admin_mode", False)
        return UserRole.ADMIN if admin_mode else UserRole.USER

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        self._handler.fs.user_role = self._get_user_role()
        output = dispatch_spatial_command(self._handler, [command] + params)
        status = "error" if output.startswith("❌") else "success"
        return {
            "status": status,
            "message": output.splitlines()[0] if output else "Workspace command complete",
            "output": output,
        }

