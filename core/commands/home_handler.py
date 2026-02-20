"""HOME command handler - Home Assistant integration."""

from __future__ import annotations

from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger
from core.services.error_contract import CommandError

logger = get_logger("command-home")

_HA_BASE = "http://localhost:8123"


class HomeHandler(BaseCommandHandler):
    """Handler for HOME command - Home Assistant control.

    Commands:
      HOME                          — show status / help
      HOME STATUS                   — connection + HA version
      HOME LIGHTS                   — list all light entities
      HOME LIGHTS ON <entity_id>    — turn a light on
      HOME LIGHTS OFF <entity_id>   — turn a light off
      HOME DEVICES                  — list all devices/entities
      HOME CALL <domain> <service> [entity_id]  — raw HA service call
    """

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._help()

        action = params[0].lower()

        if action in {"help", "?"}:
            return self._help()
        if action == "status":
            return self._status()
        if action == "lights":
            return self._lights(params[1:])
        if action == "devices":
            return self._devices()
        if action == "call":
            return self._service_call(params[1:])

        raise CommandError(
            code="ERR_COMMAND_NOT_FOUND",
            message=f"Unknown HOME action '{params[0]}'. Try HOME HELP.",
            recovery_hint="Use HOME STATUS, LIGHTS, DEVICES, or CALL",
            level="INFO",
        )

    # ------------------------------------------------------------------
    def _get_token(self) -> str:
        """Retrieve long-lived access token from state or env."""
        import os
        return self._state.get("ha_token") or os.environ.get("HA_TOKEN", "")

    def _ha_get(self, path: str) -> Dict:
        try:
            import httpx
            token = self._get_token()
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"} if token else {}
            resp = httpx.get(f"{_HA_BASE}{path}", headers=headers, timeout=10)
            if resp.status_code == 401:
                raise CommandError(
                    code="ERR_AUTH_REQUIRED",
                    message="Home Assistant: unauthorised. Set HA_TOKEN env var.",
                    recovery_hint="Set HA_TOKEN environment variable",
                    level="ERROR",
                )
            resp.raise_for_status()
            return {"status": "success", "data": resp.json()}
        except Exception as e:
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message=f"Home Assistant unreachable: {e}",
                recovery_hint="Check Home Assistant is running on localhost:8123",
                level="ERROR",
                cause=e,
            )

    def _ha_post(self, path: str, payload: Dict) -> Dict:
        try:
            import httpx
            token = self._get_token()
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"} if token else {}
            resp = httpx.post(f"{_HA_BASE}{path}", json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            return {"status": "success", "data": resp.json() if resp.content else {}}
        except Exception as e:
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message=f"Home Assistant error: {e}",
                recovery_hint="Check Home Assistant service and API",
                level="ERROR",
                cause=e,
            )

    def _status(self) -> Dict:
        result = self._ha_get("/api/")
        if result["status"] != "success":
            return result
        data = result["data"]
        return {
            "status": "success",
            "message": f"Home Assistant {data.get('version', '?')} — connected",
            "version": data.get("version"),
            "location_name": data.get("location_name"),
        }

    def _lights(self, params: List[str]) -> Dict:
        if not params:
            result = self._ha_get("/api/states")
            if result["status"] != "success":
                return result
            lights = [e for e in result["data"] if e["entity_id"].startswith("light.")]
            lines = [f"  {e['entity_id']}: {e['state']}" for e in lights]
            return {"status": "success", "output": "Lights:\n" + ("\n".join(lines) or "  (none found)"), "count": len(lights)}

        action = params[0].lower()
        entity = params[1] if len(params) > 1 else None
        if action in {"on", "off"} and entity:
            return self._ha_post(f"/api/services/light/turn_{action}", {"entity_id": entity})
        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message="Usage: HOME LIGHTS [ON|OFF <entity_id>]",
            recovery_hint="Provide action (ON/OFF) and entity ID",
            level="INFO",
        )

    def _devices(self) -> Dict:
        result = self._ha_get("/api/states")
        if result["status"] != "success":
            return result
        entities = result["data"]
        by_domain: Dict[str, int] = {}
        for e in entities:
            domain = e["entity_id"].split(".")[0]
            by_domain[domain] = by_domain.get(domain, 0) + 1
        summary = ", ".join(f"{d}:{n}" for d, n in sorted(by_domain.items()))
        return {"status": "success", "total": len(entities), "by_domain": by_domain, "output": f"Entities ({len(entities)}): {summary}"}

    def _service_call(self, params: List[str]) -> Dict:
        if len(params) < 2:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Usage: HOME CALL <domain> <service> [entity_id]",
                recovery_hint="Provide domain and service parameters",
                level="INFO",
            )
        domain, service = params[0], params[1]
        payload = {"entity_id": params[2]} if len(params) > 2 else {}
        return self._ha_post(f"/api/services/{domain}/{service}", payload)

    def _help(self) -> Dict:
        return {
            "status": "success",
            "output": (
                "HOME - Home Assistant integration\n"
                "  HOME STATUS                        Check connection\n"
                "  HOME LIGHTS                        List lights\n"
                "  HOME LIGHTS ON|OFF <entity_id>     Toggle a light\n"
                "  HOME DEVICES                       List all entities by domain\n"
                "  HOME CALL <domain> <service> [id]  Raw HA service call\n"
            ),
        }
