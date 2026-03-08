"""JSONL backend bridge for the v1.5 Go TUI frontend."""

from __future__ import annotations

from dataclasses import dataclass
import json
import subprocess
import sys
from typing import Any, TextIO
from uuid import uuid4
from pathlib import Path

from core.services.command_catalog import (
    CANONICAL_UCODE_COMMANDS,
    parse_slash_command,
    normalize_command_tokens,
)
from core.services.logging_api import get_repo_root
from core.services.operator_mode_service import get_operator_mode_service
from core.tui.dispatcher import CommandDispatcher
from core.tui.renderer import GridRenderer
from core.tui.state import GameState
from core.ulogic.contracts import IntentFrame
from core.ulogic.parser import parse_primary_input


HOME_ACTIONS = [
    {
        "key": "1",
        "label": "Mission Templates",
        "desc": "List available mission templates",
        "job": "ucode.command",
        "command": "UCODE TEMPLATE LIST missions",
    },
    {
        "key": "2",
        "label": "Binder Library",
        "desc": "List available binder roots",
        "job": "ucode.command",
        "command": "PLACE LIST @binders",
    },
    {
        "key": "3",
        "label": "Read Knowledge Guide",
        "desc": "Open uCODE docs and guide references",
        "job": "ucode.command",
        "command": "UCODE DOCS --query ucode json @binder guide",
    },
    {
        "key": "4",
        "label": "Workflow Scheduler",
        "desc": "Show local workflow queue and scheduler state",
        "job": "ucode.command",
        "command": "UCODE OPERATOR QUEUE",
    },
    {
        "key": "5",
        "label": "Grid Layer Editor",
        "desc": "Run grid workflow panel using local JSON input",
        "job": "ucode.command",
        "command": "GRID WORKFLOW --input memory/system/grid-workflow-sample.json",
    },
    {
        "key": "6",
        "label": "Core Health Check",
        "desc": "Run offline core health checks",
        "job": "ucode.command",
        "command": "HEALTH",
    },
    {
        "key": "7",
        "label": "Setup Profile",
        "desc": "Show local setup profile and readiness",
        "job": "ucode.command",
        "command": "SETUP --profile",
    },
    {
        "key": "8",
        "label": "Device Config Status",
        "desc": "Show local configuration and device status",
        "job": "ucode.command",
        "command": "CONFIG SHOW",
    },
    {
        "key": "9",
        "label": "Select Role and Theme",
        "desc": "Inspect available local themes",
        "job": "ucode.command",
        "command": "MODE THEME LIST",
    },
    {
        "key": "0",
        "label": "Destroy Repair Restore",
        "desc": "Show repair/restore readiness and status",
        "job": "ucode.command",
        "command": "UCODE REPAIR STATUS",
    },
    {
        "key": "h",
        "label": "uHOME Console",
        "desc": "Inspect home profile and setup status",
        "job": "ucode.command",
        "command": "UCODE PROFILE SHOW home",
    },
    {
        "key": "t",
        "label": "Toybox Menu",
        "desc": "Open toybox/play subsystem status",
        "job": "ucode.command",
        "command": "PLAY STATUS",
    },
    {
        "key": "s",
        "label": "Runtime Status",
        "desc": "Show current runtime mode and status",
        "job": "ucode.command",
        "command": "STATUS",
    },
    {
        "key": "c",
        "label": "Wizard Status",
        "desc": "Check Wizard server readiness",
        "job": "ucode.command",
        "command": "WIZARD STATUS",
    },
    {
        "key": "w",
        "label": "Wizard Start",
        "desc": "Start wizard services for local control plane",
        "job": "ucode.command",
        "command": "WIZARD START",
    },
    {
        "key": "x",
        "label": "Wizard GUI",
        "desc": "Open Wizard GUI route for active toybox profile",
        "job": "ucode.command",
        "command": "PLAY GUI OPEN crawler3d",
    },
    {
        "key": "y",
        "label": "Thin GUI (Direct)",
        "desc": "Open Thin GUI route directly",
        "job": "ucode.command",
        "command": "THINGUI OPEN crawler3d",
    },
    {
        "key": "d",
        "label": "Dev Mode Status",
        "desc": "Inspect dev mode and wizard connectivity",
        "job": "ucode.command",
        "command": "DEV STATUS",
    },
    {
        "key": "g",
        "label": "GPT4All Prompt (?)",
        "desc": "Open local GPT4All-style prompt mode",
        "job": "ucode.command",
        "command": "?",
    },
    {
        "key": "k",
        "label": "uCODE HELP",
        "desc": "Show all core ucode commands",
        "job": "ucode.command",
        "command": "HELP",
    },
    {
        "key": "r",
        "label": "TS Runtime Verify",
        "desc": "Verify TypeScript runtime readiness",
        "job": "ucode.command",
        "command": "VERIFY",
    },
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

        if raw.startswith("/"):
            forced = raw[1:].strip()
            if not forced:
                return {"status": "error", "message": "Slash route missing command text"}
            return self._route_forced_command(forced, raw)

        if raw.startswith("?"):
            return self._route_to_operator(raw[1:].strip())

        lowered = raw.lower()
        if lowered == "operator" or lowered.startswith("operator "):
            prompt = raw.split(None, 1)[1] if " " in raw else ""
            return self._route_to_operator(prompt)

        if self._looks_like_direct_ucode_command(raw):
            return self._dispatch_command(raw)

        frame = parse_primary_input(raw)
        if frame:
            return self._route_frame(frame)

        return self._route_to_operator(raw)

    @staticmethod
    def _looks_like_direct_ucode_command(raw: str) -> bool:
        command_name, _params = normalize_command_tokens(raw)
        if not command_name:
            return False
        return command_name in CANONICAL_UCODE_COMMANDS

    def _route_forced_command(self, forced: str, original_input: str) -> dict[str, Any]:
        slash = parse_slash_command(original_input)
        if slash:
            result = self._dispatch_command(slash)
            if result.get("status") != "error":
                return result

        direct = self._dispatch_command(forced)
        if direct.get("status") != "error":
            return direct

        bash_result = self._run_fallback_bash(forced)
        if bash_result.get("status") != "error":
            return bash_result

        guided = self._route_to_operator(forced)
        guided["message"] = (
            "Slash route failed as ucode and bash; returned operator guidance fallback"
        )
        return guided

    def _run_fallback_bash(self, command_text: str) -> dict[str, Any]:
        try:
            proc = subprocess.run(
                ["/bin/bash", "-lc", command_text],
                cwd=str(get_repo_root()),
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        except Exception as exc:
            return {
                "status": "error",
                "message": f"bash fallback failed to start: {exc}",
            }

        stdout = (proc.stdout or "").strip()
        stderr = (proc.stderr or "").strip()
        if proc.returncode != 0:
            return {
                "status": "error",
                "message": f"bash fallback failed (exit {proc.returncode})",
                "output": "\n".join(line for line in [stdout, stderr] if line).strip(),
            }

        output = stdout or stderr or "(no output)"
        return {
            "status": "success",
            "message": "slash command executed via bash fallback",
            "output": output,
            "bash": {
                "command": command_text,
                "exit_code": proc.returncode,
            },
        }

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
        status_value = str(result.get("status") or "unknown")
        message_value = str(result.get("message") or "").strip()
        events.append(
            {
                "kind": "log",
                "level": "warn" if status_value == "error" else "info",
                "message": message_value or f"command finished with status={status_value}",
                "fields": {"status": status_value},
            }
        )
        events.append({"kind": "rule"})

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
                    "kind": "columns",
                    "title": "WORKFLOW OVERVIEW",
                    "cols": [
                        {
                            "title": "Identity",
                            "style": "accent",
                            "lines": [
                                f"workflow: {result.get('workflow_id') or workflow.get('workflow_id') or 'n/a'}",
                                f"status: {state.get('status', result.get('state', 'unknown'))}",
                            ],
                        },
                        {
                            "title": "Execution",
                            "style": "default",
                            "lines": [
                                f"current phase: {current.get('name', 'n/a')}",
                                f"next window: {state.get('next_run_at', 'n/a')}",
                                f"tokens: {state.get('total_tokens', 0)}",
                                f"budget usd: {float(state.get('total_cost_usd', 0.0)):.2f}",
                            ],
                        },
                    ],
                }
            )
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
        else:
            summary_lines = self._structured_result_lines(result)
            if summary_lines:
                events.append(
                    {
                        "kind": "block",
                        "title": "RESULT SUMMARY",
                        "style": "default",
                        "lines": summary_lines,
                    }
                )
        if not events:
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

    @staticmethod
    def _structured_result_lines(result: dict[str, Any]) -> list[str]:
        lines: list[str] = []
        message = str(result.get("message") or "").strip()
        if message:
            lines.append(f"message: {message}")

        preferred_keys = [
            "mode",
            "checks_passed",
            "checks_total",
            "sonic_root",
            "db_path",
            "route",
            "profile_id",
            "target",
        ]
        for key in preferred_keys:
            if key not in result:
                continue
            value = result.get(key)
            if value in (None, "", [], {}):
                continue
            lines.append(f"{key}: {value}")

        for key, value in result.items():
            if key in {
                "status",
                "message",
                "output",
                "routing",
                "operator_plan",
                "workflow",
                "format_helper",
                "saved_path",
                "artifact_path",
                "imported",
                "duplicate",
            }:
                continue
            if key in preferred_keys:
                continue
            if isinstance(value, (str, int, float, bool)):
                lines.append(f"{key}: {value}")
            elif isinstance(value, dict):
                lines.append(f"{key}: {', '.join(sorted(str(item) for item in value.keys())[:6])}")
            elif isinstance(value, list) and value:
                lines.append(f"{key}: {len(value)} item(s)")
            if len(lines) >= 8:
                break
        return lines[:8]


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
