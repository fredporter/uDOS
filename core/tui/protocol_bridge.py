"""JSONL backend bridge for the v1.5 Go TUI frontend."""

from __future__ import annotations

from dataclasses import dataclass
import json
import sys
from typing import Any, TextIO
from uuid import uuid4
from pathlib import Path

from core.services.command_catalog import parse_slash_command
from core.services.logging_api import get_repo_root
from core.services.operator_mode_service import get_operator_mode_service
from core.tui.dispatcher import CommandDispatcher
from core.tui.renderer import GridRenderer
from core.tui.state import GameState
from core.ulogic.contracts import IntentFrame
from core.ulogic.parser import parse_primary_input


HOME_ACTIONS = [
    {"key": "1", "label": "Status", "job": "status"},
    {"key": "2", "label": "Workflow Templates", "job": "workflow.templates"},
    {"key": "3", "label": "Workflow Runs", "job": "workflow.runs"},
    {"key": "4", "label": "Knowledge Templates", "job": "knowledge.templates"},
    {"key": "5", "label": "Research Notes", "job": "knowledge.research.list"},
    {"key": "6", "label": "Health", "job": "health.status"},
    {"key": "7", "label": "Repair Status", "job": "repair.status"},
    {"key": "8", "label": "Sonic Status", "job": "sonic.status"},
    {"key": "9", "label": "Custom Command", "job": "custom.command"},
]


HOME_COMMANDS = {
    "status": "STATUS",
    "workflow.templates": "WORKFLOW LIST TEMPLATES",
    "workflow.runs": "WORKFLOW LIST RUNS",
    "knowledge.templates": "UCODE TEMPLATE LIST",
    "knowledge.research.list": "UCODE RESEARCH LIST",
    "health.status": "HEALTH",
    "repair.status": "UCODE REPAIR STATUS",
    "sonic.status": "SONIC STATUS",
}


@dataclass
class ProtocolContext:
    dispatcher: CommandDispatcher
    game_state: GameState
    renderer: GridRenderer


class UdosProtocolBridge:
    """Protocol bridge exposing routed uDOS command execution as JSONL events."""

    def __init__(self, context: ProtocolContext | None = None) -> None:
        self.context = context or ProtocolContext(
            dispatcher=CommandDispatcher(),
            game_state=GameState(),
            renderer=GridRenderer(),
        )

    def handle_message(self, message: dict[str, Any]) -> list[dict[str, Any]]:
        msg_type = str(message.get("type") or "").strip()
        msg_id = str(message.get("id") or uuid4().hex)

        if msg_type == "hello":
            return [
                {
                    "v": 1,
                    "type": "result",
                    "id": msg_id,
                    "value": {
                        "status": "ready",
                        "canvas_width": 78,
                        "render_modes": ["ascii", "blocks"],
                        "actions": HOME_ACTIONS,
                        "backend": "python-jsonl",
                    },
                },
                {
                    "v": 1,
                    "type": "event",
                    "id": msg_id,
                    "stream": "main",
                    "event": {
                        "kind": "teletext",
                        "title": "uDOS",
                        "mode": "ascii",
                        "rows": [
                            " _   _ ____   ___  ____  ",
                            "| | | |  _ \\ / _ \\/ ___| ",
                            "| |_| | | | | | | \\___ \\ ",
                            "|  _  | |_| | |_| |___) |",
                            "|_| |_|____/ \\___/|____/ ",
                        ],
                    },
                },
            ]

        if msg_type != "run":
            return [
                {
                    "v": 1,
                    "type": "done",
                    "id": msg_id,
                    "ok": False,
                    "exit_code": 2,
                    "error": f"Unsupported message type: {msg_type}",
                }
            ]

        job_id = f"job-{uuid4().hex[:8]}"
        command_text = self._resolve_run_command(message)
        if not command_text:
            return [
                {
                    "v": 1,
                    "type": "done",
                    "id": msg_id,
                    "ok": False,
                    "exit_code": 2,
                    "error": "Run request did not contain a command",
                }
            ]

        result = self._route_input(command_text)
        packets: list[dict[str, Any]] = [
            {
                "v": 1,
                "type": "result",
                "id": msg_id,
                "value": {
                    "job_id": job_id,
                    "command": command_text,
                },
            }
        ]
        packets.append(
            self._progress_packet(job_id, command_text, current=0, total=1, status="running")
        )
        packets.extend(self._result_to_event_packets(job_id, result))
        packets.append(
            self._progress_packet(job_id, command_text, current=1, total=1, status="done")
        )
        packets.append(
            {
                "v": 1,
                "type": "done",
                "id": job_id,
                "ok": result.get("status") not in {"error"},
                "exit_code": 0 if result.get("status") not in {"error"} else 1,
                "result": {
                    "status": result.get("status"),
                    "message": result.get("message", ""),
                },
            }
        )
        return packets

    @staticmethod
    def _progress_packet(
        job_id: str,
        command_text: str,
        *,
        current: int,
        total: int,
        status: str,
    ) -> dict[str, Any]:
        return {
            "v": 1,
            "type": "event",
            "id": job_id,
            "stream": "progress",
            "event": {
                "kind": "progress",
                "pid": "run-main",
                "label": command_text,
                "current": current,
                "total": total,
                "status": status,
                "style": "accent" if status != "done" else "ok",
            },
        }

    def _resolve_run_command(self, message: dict[str, Any]) -> str:
        job = str(message.get("job") or "").strip()
        args = message.get("args") or {}
        if isinstance(args, dict):
            command = str(args.get("command") or "").strip()
            if command:
                return command
        if job in HOME_COMMANDS:
            return HOME_COMMANDS[job]
        if job == "ucode.command":
            return str((args or {}).get("command") or "").strip()
        return job

    def _dispatch_command(
        self,
        command_text: str,
        frame: IntentFrame | None = None,
        route: str | None = None,
    ) -> dict[str, Any]:
        result = self.context.dispatcher.dispatch(
            command_text,
            parser=None,
            game_state=self.context.game_state,
        )
        if frame and route:
            routed = dict(result)
            routed["routing"] = {
                "route": route,
                "input_class": frame.input_class,
                "intent": frame.intent,
                "confidence": frame.confidence,
                "source": frame.source,
                "command_text": command_text,
            }
            return routed
        return result

    def _route_input(self, user_input: str) -> dict[str, Any]:
        raw = user_input.strip()
        if not raw:
            return {"status": "error", "message": "Empty input"}

        if raw.startswith("?"):
            return self._route_to_operator(raw[1:].strip())

        lowered = raw.lower()
        if lowered == "operator" or lowered.startswith("operator "):
            prompt = raw.split(None, 1)[1] if " " in raw else ""
            return self._route_to_operator(prompt)

        if raw.startswith("/"):
            slash = parse_slash_command(raw)
            if slash:
                return self._dispatch_command(slash)
            return {"status": "error", "message": f"Unknown slash command: {raw}"}

        frame = parse_primary_input(raw)
        if frame:
            return self._route_frame(frame)

        return self._route_to_operator(raw)

    def _route_frame(self, frame: IntentFrame) -> dict[str, Any]:
        route = frame.routing_outcome().route
        if route == "dispatch.command":
            command_text = str(frame.slots.get("command_text") or "").strip()
            if not command_text:
                return {"status": "error", "message": "Command frame missing command text"}
            return self._dispatch_command(command_text, frame, route)
        if route == "dispatch.workflow":
            return self._route_workflow_frame(frame)
        if route == "dispatch.knowledge":
            return self._route_knowledge_frame(frame)
        return self._route_guidance_frame(frame)

    def _route_workflow_frame(self, frame: IntentFrame) -> dict[str, Any]:
        slots = frame.slots
        intent = frame.intent
        workflow_id = str(slots.get("workflow_id", "")).strip()
        template_id = str(slots.get("template_id", "")).strip()

        if intent == "workflow.list":
            return self._dispatch_command("WORKFLOW LIST TEMPLATES", frame, "dispatch.workflow")
        if intent == "workflow.status" and workflow_id:
            return self._dispatch_command(f"WORKFLOW STATUS {workflow_id}", frame, "dispatch.workflow")
        if intent == "workflow.run" and workflow_id:
            return self._dispatch_command(f"WORKFLOW RUN {workflow_id}", frame, "dispatch.workflow")
        if intent == "workflow.approve" and workflow_id:
            return self._dispatch_command(f"WORKFLOW APPROVE {workflow_id}", frame, "dispatch.workflow")
        if intent == "workflow.escalate" and workflow_id:
            return self._dispatch_command(f"WORKFLOW ESCALATE {workflow_id}", frame, "dispatch.workflow")
        if intent == "workflow.new" and template_id and workflow_id:
            return self._dispatch_command(
                f"WORKFLOW NEW {template_id} {workflow_id}",
                frame,
                "dispatch.workflow",
            )
        guided = self._route_to_operator(
            f"Create a workflow runbook plan for {template_id or workflow_id or frame.intent}"
        )
        guided["routing"] = {
            "route": "dispatch.guidance",
            "input_class": frame.input_class,
            "intent": frame.intent,
            "confidence": frame.confidence,
            "source": frame.source,
            "command_text": None,
        }
        return guided

    def _route_knowledge_frame(self, frame: IntentFrame) -> dict[str, Any]:
        slots = frame.slots
        intent = frame.intent
        if intent == "knowledge.browse":
            knowledge_path = str(slots.get("knowledge_path", "")).strip()
            family, template_name = self._parse_template_reference(knowledge_path)
            if family and template_name:
                return self._dispatch_command(
                    f"UCODE TEMPLATE READ {family} {template_name}",
                    frame,
                    "dispatch.knowledge",
                )
            if family:
                return self._dispatch_command(
                    f"UCODE TEMPLATE LIST {family}",
                    frame,
                    "dispatch.knowledge",
                )
            return self._dispatch_command("UCODE TEMPLATE LIST", frame, "dispatch.knowledge")

        if intent == "knowledge.duplicate":
            source_path = str(slots.get("source_path", "")).strip()
            target_path = str(slots.get("target_path", "")).strip()
            family, template_name = self._parse_template_reference(source_path)
            target_name = Path(target_path).name if target_path else ""
            if family and template_name and target_name:
                return self._dispatch_command(
                    f"UCODE TEMPLATE DUPLICATE {family} {template_name} {target_name}",
                    frame,
                    "dispatch.knowledge",
                )

        text = str(slots.get("text", "")).strip()
        if intent == "knowledge.capture":
            return self._dispatch_command(
                f"UCODE ENRICH prompt shell://input {text}",
                frame,
                "dispatch.knowledge",
            )
        if intent == "knowledge.research":
            return self._dispatch_command(
                f"UCODE RESEARCH prompt shell://input {text}",
                frame,
                "dispatch.knowledge",
            )
        if intent == "knowledge.generate":
            return self._dispatch_command(
                f"UCODE GENERATE prompt shell://input {text}",
                frame,
                "dispatch.knowledge",
            )

        guided = self._route_to_operator(text or frame.intent)
        guided["routing"] = {
            "route": "dispatch.guidance",
            "input_class": frame.input_class,
            "intent": frame.intent,
            "confidence": frame.confidence,
            "source": frame.source,
            "command_text": None,
        }
        return guided

    def _route_guidance_frame(self, frame: IntentFrame) -> dict[str, Any]:
        guided = self._route_to_operator(str(frame.slots.get("text") or frame.intent))
        guided["routing"] = {
            "route": "dispatch.guidance",
            "input_class": frame.input_class,
            "intent": frame.intent,
            "confidence": frame.confidence,
            "source": frame.source,
            "command_text": None,
        }
        return guided

    def _route_to_operator(self, prompt: str) -> dict[str, Any]:
        plan = get_operator_mode_service().plan(prompt)
        lines = [
            f"Operator intent: {plan.intent.label} ({plan.intent.confidence:.2f})",
            plan.summary,
        ]
        for action in plan.actions:
            lines.append(f"- {action.command}: {action.description}")
        return {
            "status": "success",
            "message": "Local operator guidance ready",
            "output": "\n".join(lines),
            "operator_plan": {
                "summary": plan.summary,
                "intent": {
                    "label": plan.intent.label,
                    "confidence": plan.intent.confidence,
                    "reason": plan.intent.reason,
                },
                "actions": [
                    {
                        "type": item.action_type,
                        "command": item.command,
                        "safe": item.safe,
                        "description": item.description,
                    }
                    for item in plan.actions
                ],
            },
        }

    @staticmethod
    def _parse_template_reference(raw_ref: str) -> tuple[str | None, str | None]:
        aliases = {
            "workflow": "workflows",
            "workflows": "workflows",
            "mission": "missions",
            "missions": "missions",
            "capture": "captures",
            "captures": "captures",
            "submission": "submissions",
            "submissions": "submissions",
        }
        normalized = raw_ref.strip().strip("/")
        if not normalized:
            return None, None
        parts = [part for part in normalized.split("/") if part]
        if len(parts) >= 2:
            return aliases.get(parts[0].lower()), parts[-1]
        token = parts[0]
        family = aliases.get(token.lower())
        if family:
            return family, None
        lower = token.lower()
        if "workflow" in lower:
            return "workflows", token
        if "mission" in lower:
            return "missions", token
        if "capture" in lower:
            return "captures", token
        if "submission" in lower or "device" in lower:
            return "submissions", token
        return None, token

    def _result_to_event_packets(self, job_id: str, result: dict[str, Any]) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for event in self._result_to_events(result):
            events.append(
                {
                    "v": 1,
                    "type": "event",
                    "id": job_id,
                    "stream": event.get("stream", "main"),
                    "event": event,
                }
            )
        return events

    def _result_to_events(self, result: dict[str, Any]) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        routing = result.get("routing") or {}
        if routing:
            events.append(
                {
                    "kind": "block",
                    "title": "UCODE ROUTE",
                    "style": "info",
                    "lines": [
                        f"class: {routing.get('input_class', 'unknown')}",
                        f"intent: {routing.get('intent', 'unknown')}",
                        f"route: {routing.get('route', 'dispatch.unknown')}",
                        f"confidence: {float(routing.get('confidence') or 0.0):.2f}",
                        f"source: {routing.get('source', 'unknown')}",
                    ]
                    + ([f"command: {routing['command_text']}"] if routing.get("command_text") else []),
                }
            )

        workflow = result.get("workflow")
        if isinstance(workflow, dict) and "state" in workflow:
            state = workflow.get("state") or {}
            phases = state.get("phases") or []
            current_index = int(state.get("current_phase_index", 0) or 0)
            current = phases[current_index] if current_index < len(phases) else {}
            events.append(
                {
                    "kind": "block",
                    "title": "WORKFLOW STATE",
                    "style": "accent",
                    "lines": [
                        f"workflow: {result.get('workflow_id') or workflow.get('workflow_id') or 'n/a'}",
                        f"status: {state.get('status', result.get('state', 'unknown'))}",
                        f"current phase: {current.get('name', 'n/a')}",
                        f"next window: {state.get('next_run_at', 'n/a')}",
                        f"tokens: {state.get('total_tokens', 0)}",
                        f"budget usd: {float(state.get('total_cost_usd', 0.0)):.2f}",
                    ],
                }
            )
        elif result.get("workflow_id") or result.get("state"):
            events.append(
                {
                    "kind": "block",
                    "title": "WORKFLOW STATE",
                    "style": "accent",
                    "lines": [
                        f"workflow: {result.get('workflow_id', 'n/a')}",
                        f"status: {result.get('state', 'unknown')}",
                    ],
                }
            )

        operator_plan = result.get("operator_plan")
        if isinstance(operator_plan, dict):
            lines = [f"summary: {operator_plan.get('summary', '')}"]
            intent = operator_plan.get("intent") or {}
            if intent:
                lines.append(
                    f"intent: {intent.get('label', 'unknown')} ({float(intent.get('confidence', 0.0)):.2f})"
                )
                if intent.get("reason"):
                    lines.append(f"reason: {intent['reason']}")
            actions = operator_plan.get("actions") or []
            if actions:
                lines.append("")
                lines.append("actions:")
                lines.extend(
                    f"- {item.get('command', 'n/a')} :: {item.get('description', '')}"
                    for item in actions
                )
            events.append(
                {
                    "kind": "block",
                    "title": "OPERATOR PLAN",
                    "style": "warn",
                    "lines": lines,
                }
            )

        knowledge_lines: list[str] = []
        if result.get("saved_path"):
            knowledge_lines.append(f"saved: {result['saved_path']}")
        if result.get("artifact_path"):
            knowledge_lines.append(f"artifact: {result['artifact_path']}")
        if isinstance(result.get("imported"), dict):
            imported = result["imported"]
            knowledge_lines.extend(
                [
                    f"note: {imported.get('note_id', 'n/a')}",
                    f"target: {imported.get('target_path', 'n/a')}",
                    f"processed: {imported.get('processed_snapshot', 'n/a')}",
                ]
            )
        if isinstance(result.get("duplicate"), dict):
            duplicate = result["duplicate"]
            knowledge_lines.extend(
                [
                    f"template copy: {duplicate.get('target_template', 'n/a')}",
                    f"duplicate path: {duplicate.get('target_path', 'n/a')}",
                ]
            )
        if knowledge_lines:
            events.append(
                {
                    "kind": "block",
                    "title": "KNOWLEDGE ARTIFACTS",
                    "style": "ok",
                    "lines": knowledge_lines,
                }
            )

        format_helper = result.get("format_helper")
        if isinstance(format_helper, dict):
            lines = [
                f"profile: {format_helper.get('profile_label', format_helper.get('profile', 'JSON'))}",
                f"valid: {'yes' if format_helper.get('valid', False) else 'no'}",
                f"changed: {'yes' if format_helper.get('changed', False) else 'no'}",
            ]
            if result.get("source_path"):
                lines.append(f"target: {result['source_path']}")
            if result.get("written") is not None:
                lines.append(f"written: {'yes' if result.get('written') else 'no'}")
            errors = format_helper.get("errors") or []
            if errors:
                lines.append("errors:")
                lines.extend(f"- {error}" for error in errors)
            events.append(
                {
                    "kind": "block",
                    "title": "FORMAT HELPER",
                    "style": "accent" if format_helper.get("valid") else "warn",
                    "lines": lines,
                }
            )

        output_text = str(result.get("output") or "").strip()
        if output_text:
            events.append(
                {
                    "kind": "block",
                    "title": "OUTPUT",
                    "style": "default",
                    "lines": output_text.splitlines(),
                }
            )
        elif not events:
            rendered = self.context.renderer.render(result).strip()
            events.append(
                {
                    "kind": "block",
                    "title": "OUTPUT",
                    "style": "default",
                    "lines": rendered.splitlines() if rendered else ["No output"],
                }
            )
        return events


def run_stdio(stdin: TextIO, stdout: TextIO) -> int:
    bridge = UdosProtocolBridge()
    for line in stdin:
        raw = line.strip()
        if not raw:
            continue
        try:
            message = json.loads(raw)
        except json.JSONDecodeError as exc:
            stdout.write(
                json.dumps(
                    {
                        "v": 1,
                        "type": "done",
                        "id": "invalid-json",
                        "ok": False,
                        "exit_code": 2,
                        "error": f"Invalid JSON: {exc}",
                    }
                )
                + "\n"
            )
            stdout.flush()
            continue
        for payload in bridge.handle_message(message):
            stdout.write(json.dumps(payload) + "\n")
            stdout.flush()
    return 0


def main() -> int:
    return run_stdio(sys.stdin, sys.stdout)


if __name__ == "__main__":
    raise SystemExit(main())
