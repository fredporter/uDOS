"""
Binder Configuration Management

Handles metadata loading/saving for binder folders.

**Metadata File Format (.binder-config):**
```json
{
  "name": "My Research Binder",
  "version": "1.0.0",
  "created_at": "2026-01-17T10:30:00Z",
  "author": "Fred",
  "description": "Research notes and data analysis",
  "tags": ["research", "data", "analysis"]
}
```

**Usage:**
```python
from core.binder import load_binder_config, BinderConfig

config = load_binder_config(Path("/path/to/MyBinder"))
print(config.name, config.version, config.created_at)
```
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import json
from enum import Enum


class BinderMetadata(Enum):
    """Standard metadata keys for binder configuration."""

    NAME = "name"
    VERSION = "version"
    CREATED_AT = "created_at"
    AUTHOR = "author"
    DESCRIPTION = "description"
    TAGS = "tags"


@dataclass
class BinderConfig:
    """Binder configuration metadata.

    **Attributes:**
        name: Binder display name (e.g., "My Research")
        version: Semantic version (e.g., "1.0.0")
        created_at: Creation timestamp (ISO format)
        author: Optional author name
        description: Optional description
        tags: Optional list of tags for organization
        path: Path to binder folder (set during load, not serialized)
    """

    name: str
    version: str
    created_at: datetime
    author: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    path: Optional[Path] = field(default=None, repr=False)

    def __post_init__(self):
        """Normalize created_at to datetime if string provided."""
        if isinstance(self.created_at, str):
            try:
                self.created_at = datetime.fromisoformat(
                    self.created_at.replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                self.created_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert to serializable dictionary (excludes path).

        **Returns:**
            Dictionary with string ISO datetime
        """
        data = asdict(self)
        data.pop("path", None)  # Don't serialize path
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict, path: Optional[Path] = None) -> "BinderConfig":
        """Create from dictionary.

        **Args:**
            data: Configuration dictionary
            path: Optional binder path

        **Returns:**
            BinderConfig instance
        """
        # Ensure required fields
        data.setdefault("author", None)
        data.setdefault("description", None)
        data.setdefault("tags", [])

        instance = cls(
            name=data["name"],
            version=data["version"],
            created_at=data["created_at"],
            author=data.get("author"),
            description=data.get("description"),
            tags=data.get("tags", []),
        )
        instance.path = path
        return instance

    def default_db_path(self) -> Path:
        """Get standard database path for this binder.

        **Returns:**
            Path to uDOS-table.db
        """
        if not self.path:
            raise ValueError("Binder path not set")
        return self.path / "uDOS-table.db"


def load_binder_config(binder_path: Path) -> BinderConfig:
    """Load configuration from .binder-config file.

    If file doesn't exist, creates default config from folder name.

    **Args:**
        binder_path: Path to binder folder

    **Returns:**
        BinderConfig instance

    **Raises:**
        ValueError: If binder_path doesn't exist
    """
    binder_path = Path(binder_path)
    if not binder_path.exists():
        raise ValueError(f"Binder path does not exist: {binder_path}")

    config_file = binder_path / ".binder-config"

    if config_file.exists():
        # Load from file
        try:
            with open(config_file, "r") as f:
                data = json.load(f)
            return BinderConfig.from_dict(data, path=binder_path)
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid binder config file: {e}")
    else:
        # Create default from folder name
        folder_name = binder_path.name
        return BinderConfig(
            name=folder_name,
            version="1.0.0",
            created_at=datetime.now(),
            author=None,
            description=f"Binder: {folder_name}",
            tags=[],
            path=binder_path,
        )


def save_binder_config(
    config: BinderConfig, binder_path: Optional[Path] = None
) -> Path:
    """Save configuration to .binder-config file.

    **Args:**
        config: BinderConfig to save
        binder_path: Optional path override (uses config.path if not provided)

    **Returns:**
        Path to saved config file

    **Raises:**
        ValueError: If path not available
    """
    path = binder_path or config.path
    if not path:
        raise ValueError("Binder path must be provided or set in config")

    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    config_file = path / ".binder-config"
    with open(config_file, "w") as f:
        json.dump(config.to_dict(), f, indent=2)

    return config_file
