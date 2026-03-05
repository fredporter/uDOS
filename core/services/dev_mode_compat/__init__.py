"""Canonical Dev Mode compatibility service namespace.

This package provides stable imports for the Dev Mode contributor-tool service
family.
"""

from core.services.dev_mode_compat.binder_service import (
    DevModeToolBinderService,
    VibeBinderService,
    get_binder_service,
)
from core.services.dev_mode_compat.device_service import (
    DevModeToolDeviceService,
    VibeDeviceService,
    get_device_service,
)
from core.services.dev_mode_compat.network_service import (
    DevModeToolNetworkService,
    VibeNetworkService,
    get_network_service,
)
from core.services.dev_mode_compat.script_service import (
    DevModeToolScriptService,
    VibeScriptService,
    get_script_service,
)
from core.services.dev_mode_compat.sync_service import (
    DevModeToolSyncService,
    VibeSyncService,
    get_sync_service,
)
from core.services.dev_mode_compat.user_service import (
    DevModeToolUserService,
    VibeUserService,
    get_user_service,
)
from core.services.dev_mode_compat.vault_service import (
    DevModeToolVaultService,
    VibeVaultService,
    get_vault_service,
)
from core.services.dev_mode_compat.automation_service import (
    AutomationTask,
    DevModeToolAutomationService,
    VibeWizardService,
    get_wizard_service,
)
from core.services.dev_mode_compat.workspace_service import (
    DevModeToolWorkspaceService,
    VibeWorkspaceService,
    get_workspace_service,
)

__all__ = [
    "AutomationTask",
    "DevModeToolAutomationService",
    "DevModeToolBinderService",
    "DevModeToolDeviceService",
    "DevModeToolNetworkService",
    "DevModeToolScriptService",
    "DevModeToolSyncService",
    "DevModeToolUserService",
    "DevModeToolVaultService",
    "DevModeToolWorkspaceService",
    "VibeBinderService",
    "VibeDeviceService",
    "VibeNetworkService",
    "VibeScriptService",
    "VibeSyncService",
    "VibeUserService",
    "VibeVaultService",
    "VibeWizardService",
    "VibeWorkspaceService",
    "get_binder_service",
    "get_device_service",
    "get_network_service",
    "get_script_service",
    "get_sync_service",
    "get_user_service",
    "get_vault_service",
    "get_wizard_service",
    "get_workspace_service",
]
