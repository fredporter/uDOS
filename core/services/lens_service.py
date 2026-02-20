"""Lens registry and rendering service."""

from typing import Dict, List, Optional, Type

from core.services.logging_manager import get_logger
from core.lenses.base import BaseLens, GameState, LensOutput
from core.lenses.simple_ascii_lens import SimpleAsciiLens
from core.lenses.nethack_lens import NethackLens
from core.lenses.elite_lens import EliteLens
from core.lenses.rpgbbs_lens import RPGBBSLens
from core.lenses.crawler3d_lens import Crawler3DLens

logger = get_logger("lens-service")


class LensService:
    """Manage lens registry and rendering."""

    LENS_ALIASES = {
        "ascii": "ascii",
        "simple": "ascii",
        "nethack": "nethack",
        "hethack": "nethack",
        "elite": "elite",
        "rpgbbs": "rpgbbs",
        "crawler3d": "crawler3d",
    }

    def __init__(self) -> None:
        self._registry: Dict[str, Type[BaseLens]] = {
            "ascii": SimpleAsciiLens,
            "nethack": NethackLens,
            "elite": EliteLens,
            "rpgbbs": RPGBBSLens,
            "crawler3d": Crawler3DLens,
        }

    def list_lenses(self) -> List[Dict[str, str]]:
        rows = []
        for key, lens_cls in sorted(self._registry.items()):
            instance = lens_cls()
            meta = instance.get_metadata()
            rows.append(
                {
                    "id": key,
                    "name": meta.get("name", key),
                    "description": meta.get("description", ""),
                    "supported_variants": meta.get("supported_variants", ""),
                }
            )
        return rows

    def _canonical_name(self, name: Optional[str]) -> str:
        if not name:
            return "ascii"
        raw = str(name).strip().lower()
        return self.LENS_ALIASES.get(raw, raw)

    def get_lens(self, name: Optional[str] = None, variant: Optional[str] = None) -> BaseLens:
        canonical = self._canonical_name(name or variant)
        lens_cls = self._registry.get(canonical, SimpleAsciiLens)
        return lens_cls()

    def render(self, state: GameState) -> LensOutput:
        lens = self.get_lens(variant=state.variant)
        try:
            return lens.render(state)
        except Exception as exc:
            logger.warning("Lens render failed: %s", exc)
            fallback = SimpleAsciiLens(width=state.viewport_width, height=state.viewport_height)
            return fallback.render(state)


_lens_service: Optional[LensService] = None


def get_lens_service() -> LensService:
    """Return singleton lens service."""
    global _lens_service
    if _lens_service is None:
        _lens_service = LensService()
    return _lens_service
