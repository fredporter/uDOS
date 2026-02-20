"""LIBRARY command handler - library manager sync and status."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger
from core.services.error_contract import CommandError

logger = get_logger("command-library")


class LibraryHandler(BaseCommandHandler):
    """Handler for LIBRARY command - manage integrations and containers.

    Commands:
      LIBRARY                   — show status summary
      LIBRARY STATUS            — list integrations with cloned/running state
      LIBRARY SYNC              — rescan library directory and refresh manifest
      LIBRARY LIST              — alias for STATUS
      LIBRARY INFO <name>       — show detail for one integration
      LIBRARY HELP              — show usage
    """

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._status()

        action = params[0].lower()

        if action in {"help", "?"}:
            return self._help()

        if action in {"status", "list"}:
            return self._status()

        if action == "sync":
            return self._sync()

        if action == "info":
            if len(params) < 2:
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="Usage: LIBRARY INFO <name>",
                    recovery_hint="Provide an integration name",
                    level="INFO",
                )
            return self._info(params[1])

        raise CommandError(
            code="ERR_COMMAND_NOT_FOUND",
            message=f"Unknown LIBRARY action '{params[0]}'. Use LIBRARY HELP.",
            recovery_hint="Use LIBRARY STATUS, SYNC, or INFO",
            level="INFO",
        )

    # ------------------------------------------------------------------

    def _repo_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    def _get_manager(self):
        from core.services.error_contract import CommandError
        from core.services.provider_registry import get_provider, ProviderType, ProviderNotAvailableError
        try:
            return get_provider(ProviderType.LIBRARY_MANAGER)
        except ProviderNotAvailableError:
            raise CommandError(
                code="ERR_PROVIDER_OFFLINE",
                message="Wizard library manager not available",
                recovery_hint="Start Wizard services and retry: WIZARD START",
                level="ERROR",
            )

    def _status(self) -> Dict:
        try:
            manager = self._get_manager()
            status = manager.get_library_status()
        except CommandError:
            raise
        except Exception as exc:
            logger.warning(f"[LIBRARY] status error: {exc}")
            raise CommandError(
                code="ERR_RUNTIME_DEPENDENCY_MISSING",
                message=f"Library status unavailable: {exc}",
                recovery_hint="Check Wizard services and retry",
                level="ERROR",
                cause=exc,
            )

        integrations = status.integrations if status.integrations else []
        rows = []
        for intg in integrations:
            cloned = getattr(intg, "installed", False) or getattr(intg, "cloned", False)
            enabled = getattr(intg, "enabled", False)
            state = "enabled" if enabled else ("cloned" if cloned else "not cloned")
            rows.append(f"  {intg.name:<22} [{state}]")

        total = len(integrations)
        enabled_count = sum(1 for i in integrations if getattr(i, "enabled", False))
        output = (
            f"Library: {total} integration(s), {enabled_count} enabled\n"
            + ("\n".join(rows) if rows else "  (no integrations found)")
        )
        return {
            "status": "success",
            "total": total,
            "enabled": enabled_count,
            "integrations": [i.name for i in integrations],
            "output": output,
        }

    def _sync(self) -> Dict:
        """Rescan the library directory and refresh the integration manifest."""
        try:
            manager = self._get_manager()
            # Re-read status to force a rescan (service rebuilds from disk each call)
            status = manager.get_library_status()
        except CommandError:
            raise
        except Exception as exc:
            logger.warning(f"[LIBRARY] sync error: {exc}")
            raise CommandError(
                code="ERR_RUNTIME_DEPENDENCY_MISSING",
                message=f"Library sync failed: {exc}",
                recovery_hint="Check Wizard services and retry",
                level="ERROR",
                cause=exc,
            )

        total = len(status.integrations) if status.integrations else 0
        return {
            "status": "success",
            "message": f"Library sync complete. {total} integration(s) found.",
            "total": total,
        }

    def _info(self, name: str) -> Dict:
        try:
            manager = self._get_manager()
            integration = manager.get_integration(name)
        except CommandError:
            raise
        except Exception as exc:
            raise CommandError(
                code="ERR_RUNTIME_DEPENDENCY_MISSING",
                message=f"Library info error: {exc}",
                recovery_hint="Check Wizard services and retry",
                level="ERROR",
                cause=exc,
            )

        if not integration:
            raise CommandError(
                code="ERR_COMMAND_NOT_FOUND",
                message=f"Integration '{name}' not found.",
                recovery_hint="Run LIBRARY STATUS to see available integrations",
                level="ERROR",
            )

        enabled = getattr(integration, "enabled", False)
        cloned = getattr(integration, "installed", False) or getattr(integration, "cloned", False)
        output = (
            f"Integration: {integration.name}\n"
            f"  Path:    {integration.path}\n"
            f"  Source:  {getattr(integration, 'source', 'unknown')}\n"
            f"  Cloned:  {'yes' if cloned else 'no'}\n"
            f"  Enabled: {'yes' if enabled else 'no'}\n"
        )
        return {
            "status": "success",
            "name": integration.name,
            "enabled": enabled,
            "cloned": cloned,
            "output": output,
        }

    def _help(self) -> Dict:
        return {
            "status": "success",
            "output": (
                "LIBRARY - library integration manager\n"
                "  LIBRARY STATUS            List integrations and their state\n"
                "  LIBRARY SYNC              Rescan library directory\n"
                "  LIBRARY INFO <name>       Show detail for one integration\n"
                "  LIBRARY LIST              Alias for STATUS\n"
            ),
        }
