"""
Prompt Parser Service
=====================

Classifies free-text instructions into seeded types and emits Task objects plus
metadata that other workflows (todo, schedule, Hotkey) can consume.
"""

import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.services.logging_api import get_logger, get_repo_root
from core.services.todo_service import Task, TodoManager, get_service

logger = get_logger("prompt-parser")


@dataclass
class InstructionType:
    id: str
    label: str
    description: str
    primary_signals: List[str]
    secondary_signals: List[str]
    output_target: str
    reminder: Dict[str, Any]
    story_guidance: str
    reference_links: List[str]


class PromptParserService:
    def __init__(self, seed_path: Optional[Path] = None):
        self.repo_root = get_repo_root()
        self.seed_path = seed_path or (
            self.repo_root
            / "core"
            / "framework"
            / "seed"
            / "bank"
            / "templates"
            / "prompt_parser_seed.json"
        )
        self.instruction_types: Dict[str, InstructionType] = {}
        self.default_type: Optional[InstructionType] = None
        self.todo_manager = get_service()
        self._load_seed()

    def _load_seed(self) -> None:
        if not self.seed_path.exists():
            logger.warning("[PromptParser] Seed missing: %s", self.seed_path)
            return
        try:
            data = json.loads(self.seed_path.read_text(encoding="utf-8"))
            parser_data = data.get("PROMPT_PARSER", {})
            default_id = parser_data.get("DEFAULT_TYPE")
            for entry in parser_data.get("INSTRUCTION_TYPES", []):
                inst = InstructionType(
                    id=entry.get("id"),
                    label=entry.get("label", ""),
                    description=entry.get("description", ""),
                    primary_signals=[
                        signal.lower() for signal in entry.get("primary_signals", [])
                    ],
                    secondary_signals=[
                        signal.lower() for signal in entry.get("secondary_signals", [])
                    ],
                    output_target=entry.get("output_target", ""),
                    reminder=entry.get("reminder", {}),
                    story_guidance=entry.get("story_guidance", ""),
                    reference_links=entry.get("reference_links", []),
                )
                self.instruction_types[inst.id] = inst
            if default_id and default_id in self.instruction_types:
                self.default_type = self.instruction_types[default_id]
            elif self.instruction_types:
                self.default_type = next(iter(self.instruction_types.values()))
        except Exception as exc:
            logger.warning("[PromptParser] Failed to read seed: %s", exc)

    def classify(self, text: str) -> InstructionType:
        normalized = text.lower()
        best_score = 0
        best_type = self.default_type
        for inst in self.instruction_types.values():
            score = sum(normalized.count(signal) * 10 for signal in inst.primary_signals)
            score += sum(normalized.count(signal) * 2 for signal in inst.secondary_signals)
            if score > best_score:
                best_score = score
                best_type = inst
        return best_type or InstructionType(
            id="unknown",
            label="Unknown",
            description="Default fallback instruction type",
            primary_signals=[],
            secondary_signals=[],
            output_target="",
            reminder={},
            story_guidance="",
            reference_links=[],
        )

    def parse(self, text: str) -> Dict[str, Any]:
        instruction = self.classify(text)
        tasks = self._extract_tasks(text, instruction)
        result = {
            "instruction_id": instruction.id,
            "instruction_label": instruction.label,
            "instruction_description": instruction.description,
            "tasks": tasks,
            "reminder": instruction.reminder,
            "story_guidance": instruction.story_guidance,
            "reference_links": instruction.reference_links,
        }
        return result

    def _extract_tasks(self, text: str, instruction: InstructionType) -> List[Task]:
        separators = r"[\n•\-\–\—;]+"
        fragments = [
            frag.strip()
            for frag in re.split(separators, text)
            if frag and len(frag.strip()) > 5
        ]
        now = datetime.utcnow()
        tasks: List[Task] = []
        for idx, frag in enumerate(fragments):
            due = now + timedelta(hours=4 + idx * 2)
            task_id = f"prompt-{uuid.uuid4().hex[:8]}"
            task = Task(
                task_id=task_id,
                title=frag.strip(),
                due_date=due,
                duration_hours=1.0,
                description=f"Seeded from PROMPT ({instruction.id})",
                tags=[instruction.id],
            )
            tasks.append(task)
        return tasks


_PROMPT_PARSER: Optional[PromptParserService] = None


def get_prompt_parser_service() -> PromptParserService:
    global _PROMPT_PARSER
    if _PROMPT_PARSER is None:
        _PROMPT_PARSER = PromptParserService()
    return _PROMPT_PARSER
