"""
ANCHOR command handler - Gameplay anchor registry access.

Usage:
  ANCHOR                       -> list anchors
  ANCHOR LIST                  -> list anchors
  ANCHOR SHOW <id>             -> show anchor details
  ANCHOR REGISTER <id> <title> -> register/update anchor
  ANCHOR INSTANCE CREATE <id>  -> create anchor instance
  ANCHOR INSTANCE DESTROY <id> -> destroy anchor instance
  ANCHOR BIND <locid> <anchor> <coord_kind> <coord_json>
  ANCHOR EVENT <anchor> <instance> <type> [locid] [data_json]
"""

import json
from typing import Dict, List, Optional

from .base import BaseCommandHandler
from .handler_logging_mixin import HandlerLoggingMixin
from core.services.anchor_registry_service import AnchorRegistryService, AnchorRecord
from core.services.anchor_store import AnchorStore, AnchorInstanceRecord
from core.services.anchor_validation import is_valid_anchor_id, is_valid_locid
from core.tui.output import OutputToolkit
from core.services.error_contract import CommandError


class AnchorHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Handle ANCHOR commands."""

    def __init__(self):
        super().__init__()
        self.registry = AnchorRegistryService()
        self.store = AnchorStore()

    def handle(self, command: str, params: List[str], grid, parser) -> Dict:
        with self.trace_command(command, params) as trace:
            action = (params[0].upper() if params else "LIST")
            if action in {"LIST"}:
                anchors = self.registry.list_anchors()
                lines = [f"{a.anchor_id} — {a.title}" for a in anchors]
                output = "\n".join(
                    [
                        OutputToolkit.banner("ANCHORS"),
                        "\n".join(lines) if lines else "No anchors registered.",
                    ]
                )
                trace.set_status("success")
                return {
                    "status": "success",
                    "message": f"{len(anchors)} anchors",
                    "output": output,
                    "anchors": [a.__dict__ for a in anchors],
                }

            if action in {"SHOW", "GET"}:
                if len(params) < 2:
                    trace.set_status("error")
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="ANCHOR SHOW requires an anchor id",
                        recovery_hint="Use ANCHOR LIST to see available anchors",
                        level="INFO",
                    )
                anchor_id = params[1]
                anchor = self.registry.get_anchor(anchor_id)
                if not anchor:
                    trace.set_status("error")
                    raise CommandError(
                        code="ERR_ANCHOR_NOT_FOUND",
                        message=f"Anchor not found: {anchor_id}",
                        recovery_hint="Use ANCHOR LIST to see available anchors",
                        level="INFO",
                    )
                output = "\n".join(
                    [
                        OutputToolkit.banner(f"ANCHOR {anchor.anchor_id}"),
                        f"Title: {anchor.title}",
                        f"Version: {anchor.version or '-'}",
                        f"Description: {anchor.description or '-'}",
                        f"Capabilities: {anchor.capabilities or {}}",
                    ]
                )
                trace.set_status("success")
                return {
                    "status": "success",
                    "message": f"Anchor {anchor.anchor_id}",
                    "output": output,
                    "anchor": anchor.__dict__,
                }

            if action == "REGISTER":
                if len(params) < 3:
                    trace.set_status("error")
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="ANCHOR REGISTER requires <id> <title>",
                        recovery_hint="Usage: ANCHOR REGISTER <id> <title>",
                        level="INFO",
                    )
                anchor_id = params[1]
                title = " ".join(params[2:])
                if not is_valid_anchor_id(anchor_id):
                    trace.set_status("error")
                    raise CommandError(
                        code="ERR_VALIDATION_INVALID_ID",
                        message=f"Invalid anchor id: {anchor_id}",
                        recovery_hint="Use alphanumeric IDs with dashes/underscores",
                        level="INFO",
                    )
                record = AnchorRecord(
                    anchor_id=anchor_id,
                    title=title,
                    description=None,
                    version=None,
                    capabilities={},
                    created_at=self.store.utc_now(),
                    updated_at=self.store.utc_now(),
                )
                self.registry.register_anchor(record)
                trace.set_status("success")
                return {
                    "status": "success",
                    "message": f"Anchor registered: {anchor_id}",
                    "output": OutputToolkit.success(f"Registered anchor {anchor_id}"),
                }

            if action == "INSTANCE":
                if len(params) < 3:
                    trace.set_status("error")
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="ANCHOR INSTANCE requires CREATE|DESTROY",
                        recovery_hint="Usage: ANCHOR INSTANCE CREATE <id>",
                        level="INFO",
                    )
                sub = params[1].upper()
                if sub == "CREATE":
                    anchor_id = params[2]
                    if not is_valid_anchor_id(anchor_id):
                        trace.set_status("error")
                        raise CommandError(
                            code="ERR_VALIDATION_INVALID_ID",
                            message=f"Invalid anchor id: {anchor_id}",
                            recovery_hint="Use alphanumeric IDs with dashes/underscores",
                            level="INFO",
                        )
                    instance = self.store.create_instance(anchor_id)
                    trace.set_status("success")
                    return {
                        "status": "success",
                        "message": f"Instance created for {anchor_id}",
                        "output": OutputToolkit.success(f"Instance {instance.instance_id} created"),
                        "instance": instance.__dict__,
                    }
                if sub == "DESTROY":
                    instance_id = params[2]
                    self.store.destroy_instance(instance_id)
                    trace.set_status("success")
                    return {
                        "status": "success",
                        "message": f"Instance destroyed: {instance_id}",
                        "output": OutputToolkit.success(f"Instance {instance_id} destroyed"),
                    }
                trace.set_status("error")
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message=f"Unknown ANCHOR INSTANCE action: {sub}",
                    recovery_hint="Use ANCHOR INSTANCE CREATE or ANCHOR INSTANCE DESTROY",
                    level="INFO",
                )

            if action == "BIND":
                if len(params) < 5:
                    trace.set_status("error")
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="ANCHOR BIND requires <locid> <anchor> <coord_kind> <coord_json>",
                        recovery_hint="Usage: ANCHOR BIND <locid> <anchor> <coord_kind> <coord_json>",
                        level="INFO",
                    )
                locid = params[1]
                anchor_id = params[2]
                coord_kind = params[3]
                coord_json_raw = " ".join(params[4:])
                if not is_valid_locid(locid):
                    trace.set_status("error")
                    raise CommandError(
                        code="ERR_VALIDATION_INVALID_ID",
                        message=f"Invalid LocId: {locid}",
                        recovery_hint="Use a valid LocId (e.g., L300-BJ10)",
                        level="INFO",
                    )
                if not is_valid_anchor_id(anchor_id):
                    trace.set_status("error")
                    raise CommandError(
                        code="ERR_VALIDATION_INVALID_ID",
                        message=f"Invalid anchor id: {anchor_id}",
                        recovery_hint="Use alphanumeric IDs with dashes/underscores",
                        level="INFO",
                    )
                try:
                    coord_payload = json.loads(coord_json_raw)
                except json.JSONDecodeError:
                    coord_payload = {"raw": coord_json_raw}
                binding_id = self.store.add_binding(
                    locid=locid,
                    anchor_id=anchor_id,
                    coord_kind=coord_kind,
                    coord_payload=coord_payload,
                )
                trace.set_status("success")
                return {
                    "status": "success",
                    "message": "Binding created",
                    "output": OutputToolkit.success(f"Binding {binding_id} created"),
                    "binding_id": binding_id,
                }

            if action == "EVENT":
                if len(params) < 4:
                    trace.set_status("error")
                    raise CommandError(
                        code="ERR_COMMAND_INVALID_ARG",
                        message="ANCHOR EVENT requires <anchor> <instance> <type> [locid] [data_json]",
                        recovery_hint="Usage: ANCHOR EVENT <anchor> <instance> <type> [locid] [data_json]",
                        level="INFO",
                    )
                anchor_id = params[1]
                instance_id = params[2]
                event_type = params[3]
                locid: Optional[str] = None
                data_payload: Optional[dict] = None
                if len(params) >= 5:
                    locid = params[4]
                    if not is_valid_locid(locid):
                        locid = None
                if len(params) >= 6:
                    raw = " ".join(params[5:])
                    try:
                        data_payload = json.loads(raw)
                    except json.JSONDecodeError:
                        data_payload = {"raw": raw}
                event_id = self.store.add_event(
                    anchor_id=anchor_id,
                    instance_id=instance_id,
                    event_type=event_type,
                    locid=locid,
                    data_payload=data_payload,
                )
                trace.set_status("success")
                return {
                    "status": "success",
                    "message": "Event recorded",
                    "output": OutputToolkit.success(f"Event {event_id} recorded"),
                    "event_id": event_id,
                }

            trace.set_status("error")
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message=f"Unknown ANCHOR action: {action}",
                recovery_hint="Use ANCHOR LIST or ANCHOR SHOW <id>",
                level="INFO",
            )
