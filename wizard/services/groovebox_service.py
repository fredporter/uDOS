"""
Groovebox service for storing and loading pattern data.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pathlib import Path

from library.groovebox import GrooveboxStore
from wizard.services.logging_manager import get_logger

logger = get_logger("groovebox-service")


class GrooveboxService:
    """Persist Groovebox patterns in memory/groovebox."""

    def __init__(self, memory_root: Optional[Path] = None):
        self.store = GrooveboxStore(memory_root=memory_root)

    def list_patterns(self) -> List[Dict[str, Any]]:
        return self.store.list_patterns()

    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_pattern(pattern_id)

    def save_pattern(
        self,
        pattern: Dict[str, Any],
        pattern_id: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.store.save_pattern(pattern, pattern_id=pattern_id, source=source)


def get_groovebox_service() -> GrooveboxService:
    return GrooveboxService()
