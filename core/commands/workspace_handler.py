"""
PLACE command handler.

Routes unified PLACE command family to SpatialFilesystemHandler.
"""

from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.commands.spatial_filesystem_handler import (
    SpatialFilesystemHandler,
    dispatch_spatial_command,
)
from core.services.spatial_filesystem import UserRole


class WorkspaceHandler(BaseCommandHandler):
    """Command adapter for PLACE command family."""

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
        cmd = (command or "").upper()
        routed = [cmd] + params

        # Canonical command surface: PLACE
        if cmd == "PLACE":
            if not params:
                routed = ["WORKSPACE", "HELP"]
            else:
                sub = params[0].upper()
                rest = params[1:]
                if sub in {"LIST", "READ", "WRITE", "DELETE", "INFO", "HELP"}:
                    routed = ["WORKSPACE", sub, *rest]
                elif sub == "TAG":
                    routed = ["LOCATION", "TAG", *rest]
                elif sub == "FIND":
                    routed = ["LOCATION", "FIND", *rest]
                elif sub == "TAGS":
                    routed = ["TAG", "LIST", *rest]
                elif sub == "SEARCH":
                    routed = ["TAG", "FIND", *rest]
                else:
                    return {
                        "status": "error",
                        "message": (
                            "PLACE usage: PLACE <LIST|READ|WRITE|DELETE|INFO|HELP> ... | "
                            "PLACE TAG <@ws/file> <LocId> | PLACE FIND <LocId> | "
                            "PLACE TAGS <@workspace> | PLACE SEARCH <tag...>"
                        ),
                    }

        output = dispatch_spatial_command(self._handler, routed)
        status = "error" if output.startswith("❌") else "success"
        return {
            "status": status,
            "message": output.splitlines()[0] if output else "Workspace command complete",
            "output": output,
        }
