"""Deterministic operator-mode planner for ucode-first runtime."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from core.services.external_repo_service import sonic_repo_available
from core.services.logging_api import get_repo_root
from core.services.release_profile_service import get_release_profile_service


@dataclass(frozen=True)
class OperatorIntent:
    label: str
    confidence: float
    reason: str


@dataclass(frozen=True)
class OperatorAction:
    action_type: str
    command: str
    safe: bool = True
    description: str = ""


@dataclass(frozen=True)
class OperatorTask:
    task_id: str
    title: str
    queue: str
    status: str


@dataclass(frozen=True)
class OperatorCapability:
    name: str
    available: bool
    detail: str


@dataclass(frozen=True)
class OperatorSessionState:
    mode: str
    topology: str
    enabled_profiles: list[str]
    queued_tasks: int


@dataclass(frozen=True)
class OperatorPlan:
    summary: str
    intent: OperatorIntent
    actions: list[OperatorAction] = field(default_factory=list)
    tasks: list[OperatorTask] = field(default_factory=list)
    capabilities: list[OperatorCapability] = field(default_factory=list)
    needs_confirmation: bool = False


class OperatorModeService:
    """Rule-based operator planning with no model/runtime dependency."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or get_repo_root()
        self.profile_service = get_release_profile_service()

    def session_state(self) -> OperatorSessionState:
        state = self.profile_service._load_state()
        topology = self.profile_service.topology_summary()["mode"]
        return OperatorSessionState(
            mode="operator",
            topology=topology,
            enabled_profiles=list(state["enabled"]),
            queued_tasks=len(self._queued_tasks()),
        )

    def status_payload(self) -> dict[str, Any]:
        session = self.session_state()
        capabilities = [
            OperatorCapability("profiles", True, "Release profile registry ready"),
            OperatorCapability("packages", True, "Package groups available"),
            OperatorCapability(
                "wizard-pairing",
                (self.repo_root / "wizard" / "server.py").exists(),
                "Wizard service path present" if (self.repo_root / "wizard" / "server.py").exists() else "Wizard service not present",
            ),
            OperatorCapability(
                "sonic",
                sonic_repo_available(self.repo_root),
                "Sonic external repo present" if sonic_repo_available(self.repo_root) else "Sonic external repo missing",
            ),
        ]
        return {
            "session": asdict(session),
            "capabilities": [asdict(item) for item in capabilities],
            "tasks": [asdict(task) for task in self._queued_tasks()],
        }

    def plan(self, prompt: str) -> OperatorPlan:
        text = (prompt or "").strip().lower()
        if not text:
            intent = OperatorIntent("assist", 0.30, "No prompt provided")
            return OperatorPlan(
                summary="Operator mode is ready. Ask for profiles, packages, Wizard pairing, repair, update, music, gameplay, or Sonic workflows.",
                intent=intent,
                capabilities=self._default_capabilities(),
            )

        if "profile" in text or "install" in text:
            return self._profile_plan(text)
        if "wizard" in text or "pair" in text:
            return self._wizard_plan(text)
        if "repair" in text or "heal" in text or "fix" in text:
            return self._repair_plan(text)
        if "sonic" in text or "usb" in text or "flash" in text:
            return self._sonic_plan(text)
        if "music" in text or "song" in text or "groove" in text or "transcrib" in text:
            return self._creator_plan(text)
        if "game" in text or "learn" in text or "mission" in text or "play" in text:
            return self._gaming_plan(text)
        return OperatorPlan(
            summary="Operator mode mapped the request to guided ucode actions.",
            intent=OperatorIntent("assist", 0.62, "Generic operator assistance"),
            actions=[
                OperatorAction("command", "UCODE PROFILE LIST", description="Inspect supported release profiles."),
                OperatorAction("command", "STATUS", description="Check runtime status."),
                OperatorAction("command", "HEALTH", description="Review service health before changes."),
            ],
            capabilities=self._default_capabilities(),
        )

    def _profile_plan(self, text: str) -> OperatorPlan:
        matched = [
            profile["profile_id"]
            for profile in self.profile_service.list_profiles()
            if profile["profile_id"] in text
        ]
        actions = [OperatorAction("command", "UCODE PROFILE LIST", description="Show certified profile inventory.")]
        for profile_id in matched:
            actions.append(
                OperatorAction(
                    "command",
                    f"UCODE PROFILE INSTALL {profile_id}",
                    description=f"Install and enable the {profile_id} profile.",
                )
            )
            actions.append(
                OperatorAction(
                    "command",
                    f"UCODE PROFILE VERIFY {profile_id}",
                    description=f"Verify blockers and dependencies for {profile_id}.",
                )
            )
        if not matched:
            actions.append(
                OperatorAction(
                    "command",
                    "UCODE PROFILE SHOW core",
                    description="Start from the mandatory core profile.",
                )
            )
        return OperatorPlan(
            summary="Release profile plan prepared.",
            intent=OperatorIntent("profiles", 0.88, "Prompt mentions profile/install workflow"),
            actions=actions,
            capabilities=self._default_capabilities(),
        )

    def _wizard_plan(self, _text: str) -> OperatorPlan:
        topology = self.profile_service.topology_summary()
        return OperatorPlan(
            summary=topology["summary"],
            intent=OperatorIntent("wizard", 0.83, "Prompt mentions Wizard or pairing"),
            actions=[
                OperatorAction("command", "WIZARD STATUS", description="Check Wizard runtime availability."),
                OperatorAction("command", "UCODE PROFILE VERIFY home", description="Verify the home profile."),
            ],
            capabilities=self._default_capabilities(),
        )

    def _repair_plan(self, _text: str) -> OperatorPlan:
        return OperatorPlan(
            summary="Prepared a guided repair sequence anchored in ucode/system health.",
            intent=OperatorIntent("repair", 0.86, "Prompt mentions repair/fix/heal"),
            actions=[
                OperatorAction("command", "HEALTH", description="Collect current health signals."),
                OperatorAction("command", "REPAIR STATUS", description="Inspect global repair options."),
                OperatorAction("command", "UCODE REPAIR STATUS", description="Review profile-aware repair contracts."),
            ],
            tasks=self._queued_tasks(),
            capabilities=self._default_capabilities(),
            needs_confirmation=True,
        )

    def _sonic_plan(self, _text: str) -> OperatorPlan:
        return OperatorPlan(
            summary="Prepared Sonic screwdriver workflow for planning or repair.",
            intent=OperatorIntent("sonic", 0.90, "Prompt mentions Sonic/USB/flash workflow"),
            actions=[
                OperatorAction("command", "SONIC STATUS", description="Check Sonic dataset and database status."),
                OperatorAction("command", "SONIC PLAN --dry-run", description="Draft a manifest before any device changes."),
                OperatorAction("command", "UCODE PROFILE VERIFY core", description="Confirm base operator/runtime readiness."),
            ],
            capabilities=self._default_capabilities(),
            needs_confirmation=True,
        )

    def _creator_plan(self, _text: str) -> OperatorPlan:
        return OperatorPlan(
            summary="Prepared creator-profile workflow for Groovebox and Songscribe lanes.",
            intent=OperatorIntent("creator", 0.84, "Prompt mentions music/transcription/creator workflows"),
            actions=[
                OperatorAction("command", "UCODE PROFILE INSTALL creator", description="Enable creator profile scaffolding."),
                OperatorAction("command", "MUSIC STATUS", description="Check Groovebox and Songscribe availability."),
                OperatorAction("command", "UCODE EXTENSION VERIFY groovebox", description="Verify creator extension readiness."),
            ],
            capabilities=self._default_capabilities(),
        )

    def _gaming_plan(self, _text: str) -> OperatorPlan:
        return OperatorPlan(
            summary="Prepared integrated gameplay/education workflow.",
            intent=OperatorIntent("gaming", 0.80, "Prompt mentions gameplay or missions"),
            actions=[
                OperatorAction("command", "UCODE PROFILE INSTALL gaming", description="Enable gaming profile."),
                OperatorAction("command", "PLAY STATUS", description="Inspect gameplay progression state."),
                OperatorAction("command", "PLAY LENS STATUS", description="Review educational gameplay lens readiness."),
            ],
            capabilities=self._default_capabilities(),
        )

    def _default_capabilities(self) -> list[OperatorCapability]:
        topology = self.profile_service.topology_summary()
        return [
            OperatorCapability("profiles", True, "Certified profile registry loaded"),
            OperatorCapability("topology", True, topology["summary"]),
            OperatorCapability("wizard", (self.repo_root / "wizard" / "server.py").exists(), "Wizard runtime detected" if (self.repo_root / "wizard" / "server.py").exists() else "Wizard runtime missing"),
            OperatorCapability("sonic", sonic_repo_available(self.repo_root), "Sonic runtime detected" if sonic_repo_available(self.repo_root) else "Sonic runtime missing"),
        ]

    def _queued_tasks(self) -> list[OperatorTask]:
        return [
            OperatorTask("release-core", "Rebaseline core entrypoint", "operator", "ready"),
            OperatorTask("release-home", "Verify Wizard pairing topology", "operator", "ready"),
        ]


_service: OperatorModeService | None = None


def get_operator_mode_service() -> OperatorModeService:
    global _service
    if _service is None:
        _service = OperatorModeService()
    return _service
