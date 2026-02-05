"""
Anchor Registry Implementation (Python)

Manages coordinate frame definitions, validation, and transforms.
Mirrors TypeScript implementation for cross-platform consistency.

@module wizard/services/anchor_registry.py
"""

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from wizard.services.spatial_parser import parse_place_ref, is_valid_cell, parse_locid


class LayerBand(str, Enum):
    """Layer band semantics (v1.3)"""

    TERRESTRIAL = "terrestrial"  # L300-L305: Earth surface/underground
    REGIONAL = "regional"  # L306-L399: Local regions, overlays
    CITIES = "cities"  # L400-L499: City/metro overlays
    NATIONS = "nations"  # L500-L599: Nation/continent scales
    PLANETARY = "planetary"  # L600-L699: Planets, moons, bodies
    ORBITAL = "orbital"  # L700-L799: Solar system, orbits
    STELLAR = "stellar"  # L800-L899: Stars, exoplanets, catalogues


# Layer band configuration
LAYER_BANDS: Dict[LayerBand, Dict[str, Any]] = {
    LayerBand.TERRESTRIAL: {
        "band": "terrestrial",
        "min_layer": 300,
        "max_layer": 305,
        "description": "Human-scale surface precision (Earth SUR/UDN/SUB)",
    },
    LayerBand.REGIONAL: {
        "band": "regional",
        "min_layer": 306,
        "max_layer": 399,
        "description": "Local regions and overlays",
    },
    LayerBand.CITIES: {
        "band": "cities",
        "min_layer": 400,
        "max_layer": 499,
        "description": "City and metro area overlays",
    },
    LayerBand.NATIONS: {
        "band": "nations",
        "min_layer": 500,
        "max_layer": 599,
        "description": "Nation and continent scale",
    },
    LayerBand.PLANETARY: {
        "band": "planetary",
        "min_layer": 600,
        "max_layer": 699,
        "description": "Planets, moons, celestial bodies",
    },
    LayerBand.ORBITAL: {
        "band": "orbital",
        "min_layer": 700,
        "max_layer": 799,
        "description": "Solar system and orbital mechanics",
    },
    LayerBand.STELLAR: {
        "band": "stellar",
        "min_layer": 800,
        "max_layer": 899,
        "description": "Stars, exoplanets, and galactic catalogues",
    },
}

# Global layer constraints
LAYER_CONSTRAINTS = {
    "MIN_LAYER": 300,
    "MAX_LAYER": 899,
    "MAX_DEPTH": 99,  # SUB depth D0..D99
}


@dataclass
class AnchorMeta:
    """Anchor metadata"""

    anchor_id: str
    title: str
    kind: Optional[str] = None
    status: str = "active"  # active|deprecated
    version: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: __import__("time").time())
    updated_at: float = field(default_factory=lambda: __import__("time").time())


class AnchorRegistry:
    """In-memory registry of anchors and coordinate systems"""

    def __init__(self):
        self.anchors: Dict[str, AnchorMeta] = {}
        self.transforms: Dict[str, Any] = {}

    def register_anchor(
        self,
        anchor_id: str,
        title: str,
        kind: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """Register an anchor with metadata"""
        meta = AnchorMeta(
            anchor_id=anchor_id,
            title=title,
            kind=kind,
            config=config or {},
            **kwargs,
        )
        self.anchors[anchor_id] = meta

    def register_transform(self, anchor_id: str, transform: Any) -> None:
        """Register a coordinate transform for an anchor"""
        self.transforms[anchor_id] = transform

    def get_anchor(self, anchor_id: str) -> Optional[AnchorMeta]:
        """Get anchor metadata by ID"""
        return self.anchors.get(anchor_id)

    def list_anchors(self) -> List[AnchorMeta]:
        """List all registered anchors"""
        return list(self.anchors.values())

    def get_transform(self, anchor_id: str) -> Optional[Any]:
        """Get coordinate transform for an anchor (if registered)"""
        return self.transforms.get(anchor_id)

    def has_anchor(self, anchor_id: str) -> bool:
        """Check if anchor exists"""
        return anchor_id in self.anchors

    def validate_anchor(self, anchor_id: str) -> bool:
        """Validate anchor existence"""
        return self.has_anchor(anchor_id)

    def count(self) -> int:
        """Count registered anchors"""
        return len(self.anchors)

    def clear(self) -> None:
        """Clear all anchors and transforms"""
        self.anchors.clear()
        self.transforms.clear()

    def to_json(self) -> str:
        """Export registry to JSON"""
        data = {
            "version": "1.3.0",
            "anchors": [
                {
                    "anchorId": meta.anchor_id,
                    "title": meta.title,
                    "kind": meta.kind,
                    "status": meta.status,
                    "description": meta.description,
                    "config": meta.config or {},
                }
                for meta in self.anchors.values()
            ],
        }
        return json.dumps(data, indent=2)

    def save_to_file(self, path: Path) -> None:
        """Save registry to JSON file"""
        path.write_text(self.to_json())

    @classmethod
    def from_json_data(cls, data: Dict[str, Any]) -> "AnchorRegistry":
        """Load registry from JSON data"""
        registry = cls()

        if not isinstance(data.get("anchors"), list):
            raise ValueError("Invalid anchor metadata: anchors array not found")

        for item in data["anchors"]:
            anchor_id = item.get("anchorId")
            title = item.get("title")

            if not anchor_id or not title:
                raise ValueError(
                    f"Invalid anchor entry: missing anchorId or title in {item}"
                )

            registry.register_anchor(
                anchor_id=anchor_id,
                title=title,
                kind=item.get("kind"),
                config=item.get("config"),
                status=item.get("status", "active"),
                description=item.get("description"),
                version=item.get("version"),
            )

        return registry

    @classmethod
    def from_json_file(cls, path: Path) -> "AnchorRegistry":
        """Load registry from JSON file"""
        data = json.loads(path.read_text())
        return cls.from_json_data(data)


# Global singleton registry
_global_registry: Optional[AnchorRegistry] = None


def get_global_registry() -> AnchorRegistry:
    """Get the global registry (lazy init)"""
    global _global_registry
    if _global_registry is None:
        _global_registry = AnchorRegistry()
    return _global_registry


def set_global_registry(registry: AnchorRegistry) -> None:
    """Set the global registry (for testing or custom initialization)"""
    global _global_registry
    _global_registry = registry


# === Validation Functions ===


def is_valid_layer(layer: int) -> bool:
    """Check if layer is within valid range"""
    return isinstance(layer, int) and LAYER_CONSTRAINTS["MIN_LAYER"] <= layer <= LAYER_CONSTRAINTS["MAX_LAYER"]


def is_valid_depth(depth: int) -> bool:
    """Check if depth is valid (for SUB layers)"""
    return isinstance(depth, int) and 0 <= depth <= LAYER_CONSTRAINTS["MAX_DEPTH"]


def get_layer_band(layer: int) -> Optional[LayerBand]:
    """Determine which band a layer belongs to"""
    if not is_valid_layer(layer):
        return None

    for band, config in LAYER_BANDS.items():
        if config["min_layer"] <= layer <= config["max_layer"]:
            return band

    return None


def get_layer_band_config(layer: int) -> Optional[Dict[str, Any]]:
    """Get band config for a layer"""
    band = get_layer_band(layer)
    return LAYER_BANDS.get(band) if band else None


def list_layer_bands() -> List[Dict[str, Any]]:
    """List all layer bands"""
    return list(LAYER_BANDS.values())


def validate_place_ref(
    place_ref: str,
    anchor_validator: Optional[Callable[[str], bool]] = None,
) -> Dict[str, Any]:
    """
    Check if a place reference is semantically valid.

    Checks:
    - Anchor exists (if validator provided)
    - Space is valid (SUR|UDN|SUB)
    - LocId parses correctly
    - Layer is in valid range
    - Depth is valid for SUB anchors

    Returns: {"valid": bool, "error": str|None}
    """
    parts = place_ref.split(":")

    # Basic structure check
    if len(parts) < 3:
        return {
            "valid": False,
            "error": "PlaceRef must have at least 3 colon-separated parts",
        }

    # Parse anchor ID (may be composite like BODY:MOON)
    anchor_id = parts[0]
    space_idx = 1

    if anchor_id in {"BODY", "GAME", "CATALOG"}:
        if len(parts) < 4:
            return {
                "valid": False,
                "error": f"Composite anchor {anchor_id} requires subtype",
            }
        anchor_id = f"{parts[0]}:{parts[1]}"
        space_idx = 2

    # Validate anchor (if validator provided)
    if anchor_validator and not anchor_validator(anchor_id):
        return {"valid": False, "error": f"Unknown anchor: {anchor_id}"}

    # Validate space
    space = parts[space_idx]
    if space not in {"SUR", "UDN", "SUB"}:
        return {
            "valid": False,
            "error": f"Invalid space: {space} (must be SUR, UDN, or SUB)",
        }

    # Validate LocId
    locid_str = parts[space_idx + 1]
    locid = parse_locid(locid_str)
    if not locid:
        return {"valid": False, "error": f"Invalid LocId: {locid_str}"}

    # Parse layer from locid
    try:
        layer = int(locid_str[1:4])
    except (ValueError, IndexError):
        return {"valid": False, "error": f"Invalid layer in LocId: {locid_str}"}

    # Validate layer
    if not is_valid_layer(layer):
        return {
            "valid": False,
            "error": f"Layer {layer} out of range ({LAYER_CONSTRAINTS['MIN_LAYER']}-{LAYER_CONSTRAINTS['MAX_LAYER']})",
        }

    # Parse and validate optional tags
    for tag in parts[space_idx + 2 :]:
        if tag.startswith("D"):
            depth_str = tag[1:]
            if not depth_str.isdigit():
                return {"valid": False, "error": f"Invalid depth tag: {tag}"}
            depth = int(depth_str)
            if not is_valid_depth(depth):
                return {
                    "valid": False,
                    "error": f"Depth {depth} out of range (0-{LAYER_CONSTRAINTS['MAX_DEPTH']})",
                }
        elif tag.startswith("I"):
            # Instance ID: any non-empty string after I
            if len(tag) < 2:
                return {"valid": False, "error": "Instance tag I requires a value"}
        else:
            return {"valid": False, "error": f"Unknown tag: {tag}"}

    return {"valid": True}


def canonicalize_place(
    anchor_id: str,
    space: str,
    locid_str: str,
    depth: Optional[int] = None,
    instance: Optional[str] = None,
) -> Optional[str]:
    """
    Format a place reference with validation.

    Ensures proper canonicalization:
    - Normalized layer encoding
    - Consistent tag ordering (D before I)
    """
    # Validate LocId
    if not parse_locid(locid_str):
        return None

    # Validate layer
    try:
        layer = int(locid_str[1:4])
    except (ValueError, IndexError):
        return None

    if not is_valid_layer(layer):
        return None

    # Validate space
    if space not in {"SUR", "UDN", "SUB"}:
        return None

    # Build canonical form
    parts = [anchor_id, space, locid_str]

    if depth is not None:
        if not is_valid_depth(depth):
            return None
        parts.append(f"D{depth}")

    if instance:
        parts.append(f"I{instance}")

    return ":".join(parts)


def describe_place_ref(place_ref: str) -> str:
    """Return a human-readable description of a place"""
    validation = validate_place_ref(place_ref)
    if not validation["valid"]:
        return f"[Invalid: {validation.get('error')}]"

    parts = place_ref.split(":")
    anchor_id = parts[0]
    space_idx = 1

    if anchor_id in {"BODY", "GAME", "CATALOG"}:
        anchor_id = f"{parts[0]}:{parts[1]}"
        space_idx = 2

    space = parts[space_idx]
    locid_str = parts[space_idx + 1]

    try:
        layer = int(locid_str[1:4])
    except (ValueError, IndexError):
        return f"[Invalid layer in {locid_str}]"

    band_config = get_layer_band_config(layer)
    band_desc = f" [{band_config['description']}]" if band_config else ""

    return f"{anchor_id}/{space}/{locid_str}{band_desc}"
