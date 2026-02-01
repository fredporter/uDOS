"""
Sound Library Manager - uDOS Groovebox

Manages sound packs, samples, and instrument presets for the Groovebox extension.
Supports local storage, pack installation, and sample catalog browsing.

Part of uDOS v1.0.3.0+ - Groovebox Extension

Features:
- Sound pack manifest format
- Pack installation from local/mesh sources
- Sample catalog browser
- Preset management
- User sound upload

Directory Structure:
  memory/sounds/
  ├── packs/                    # Installed sound packs
  │   ├── 808-classic/
  │   │   ├── manifest.json
  │   │   └── samples/
  │   │       ├── kick.wav
  │   │       ├── snare.wav
  │   │       └── ...
  │   └── lofi-drums/
  │       └── ...
  ├── user/                     # User-created/imported sounds
  │   └── samples/
  └── presets/                  # Pattern presets
      └── *.json

Manifest Format:
{
    "name": "808 Classic",
    "version": "1.0.0",
    "author": "uDOS",
    "description": "Classic TR-808 drum machine sounds",
    "license": "CC0",
    "instruments": {
        "kick": "samples/kick.wav",
        "snare": "samples/snare.wav",
        ...
    },
    "tags": ["drums", "808", "classic"]
}

Version: v1.0.0.0
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from core.services.logging_service import get_logger
from core.config import Config

logger = get_logger("groovebox-library")


class SoundType(Enum):
    """Sound categorization."""

    DRUM = "drum"
    BASS = "bass"
    SYNTH = "synth"
    PERCUSSION = "percussion"
    FX = "fx"
    VOCAL = "vocal"
    OTHER = "other"


@dataclass
class SoundSample:
    """Individual sound sample metadata."""

    name: str
    path: Path
    sound_type: SoundType = SoundType.OTHER
    duration_ms: int = 0
    sample_rate: int = 44100
    channels: int = 1
    tags: List[str] = field(default_factory=list)
    pack_id: Optional[str] = None

    def exists(self) -> bool:
        """Check if sample file exists."""
        return self.path.exists()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "path": str(self.path),
            "type": self.sound_type.value,
            "duration_ms": self.duration_ms,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "tags": self.tags,
            "pack_id": self.pack_id,
        }


@dataclass
class SoundPackManifest:
    """Sound pack manifest structure."""

    id: str
    name: str
    version: str
    author: str
    description: str
    license: str
    instruments: Dict[str, str]  # instrument_name -> relative_path
    tags: List[str] = field(default_factory=list)
    created: str = ""
    updated: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize manifest."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "license": self.license,
            "instruments": self.instruments,
            "tags": self.tags,
            "created": self.created or datetime.now().isoformat(),
            "updated": self.updated or datetime.now().isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SoundPackManifest":
        """Deserialize manifest."""
        return cls(
            id=data.get("id", "unknown"),
            name=data.get("name", "Unknown Pack"),
            version=data.get("version", "1.0.0"),
            author=data.get("author", "Unknown"),
            description=data.get("description", ""),
            license=data.get("license", "Unknown"),
            instruments=data.get("instruments", {}),
            tags=data.get("tags", []),
            created=data.get("created", ""),
            updated=data.get("updated", ""),
        )


@dataclass
class SoundPack:
    """Installed sound pack."""

    manifest: SoundPackManifest
    path: Path
    samples: Dict[str, SoundSample] = field(default_factory=dict)
    is_valid: bool = True

    def get_sample(self, instrument: str) -> Optional[SoundSample]:
        """Get sample for instrument."""
        return self.samples.get(instrument)

    def list_instruments(self) -> List[str]:
        """List available instruments."""
        return list(self.manifest.instruments.keys())


class SoundLibrary:
    """
    Central sound library manager.

    Handles:
    - Pack installation and management
    - Sample catalog
    - User sounds
    - Preset storage
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize sound library.

        Args:
            base_path: Root path for sound storage (default: memory/sounds)
        """
        self.base_path = base_path or Path(Config.MEMORY_DIR) / "sounds"
        self.packs_path = self.base_path / "packs"
        self.user_path = self.base_path / "user" / "samples"
        self.presets_path = self.base_path / "presets"

        # Ensure directories exist
        self._ensure_directories()

        # Loaded packs cache
        self._packs: Dict[str, SoundPack] = {}
        self._loaded = False

        logger.info(f"[LOCAL] SoundLibrary initialized: {self.base_path}")

    def _ensure_directories(self):
        """Create required directories."""
        for path in [self.packs_path, self.user_path, self.presets_path]:
            path.mkdir(parents=True, exist_ok=True)

    def load(self) -> int:
        """
        Load all installed packs.

        Returns:
            Number of packs loaded
        """
        self._packs.clear()

        for pack_dir in self.packs_path.iterdir():
            if pack_dir.is_dir():
                manifest_path = pack_dir / "manifest.json"
                if manifest_path.exists():
                    pack = self._load_pack(pack_dir)
                    if pack:
                        self._packs[pack.manifest.id] = pack

        self._loaded = True
        logger.info(f"[LOCAL] Loaded {len(self._packs)} sound packs")
        return len(self._packs)

    def _load_pack(self, pack_dir: Path) -> Optional[SoundPack]:
        """Load a single pack from directory."""
        manifest_path = pack_dir / "manifest.json"

        try:
            data = json.loads(manifest_path.read_text())
            manifest = SoundPackManifest.from_dict(data)

            pack = SoundPack(manifest=manifest, path=pack_dir)

            # Load samples
            for inst_name, rel_path in manifest.instruments.items():
                sample_path = pack_dir / rel_path
                if sample_path.exists():
                    pack.samples[inst_name] = SoundSample(
                        name=inst_name,
                        path=sample_path,
                        sound_type=SoundType.DRUM,
                        pack_id=manifest.id,
                    )
                else:
                    logger.warning(f"[LOCAL] Missing sample: {sample_path}")
                    pack.is_valid = False

            return pack

        except Exception as e:
            logger.error(f"[LOCAL] Failed to load pack {pack_dir}: {e}")
            return None

    def list_packs(self) -> List[Dict[str, Any]]:
        """
        List all installed packs.

        Returns:
            List of pack info dictionaries
        """
        if not self._loaded:
            self.load()

        return [
            {
                "id": pack.manifest.id,
                "name": pack.manifest.name,
                "version": pack.manifest.version,
                "author": pack.manifest.author,
                "instruments": len(pack.manifest.instruments),
                "valid": pack.is_valid,
            }
            for pack in self._packs.values()
        ]

    def get_pack(self, pack_id: str) -> Optional[SoundPack]:
        """Get pack by ID."""
        if not self._loaded:
            self.load()
        return self._packs.get(pack_id)

    def install_pack(self, source_path: Path) -> Tuple[bool, str]:
        """
        Install a sound pack from a directory.

        Args:
            source_path: Path to pack directory with manifest.json

        Returns:
            (success, message)
        """
        manifest_path = source_path / "manifest.json"

        if not manifest_path.exists():
            return False, "No manifest.json found"

        try:
            data = json.loads(manifest_path.read_text())
            manifest = SoundPackManifest.from_dict(data)

            # Check if already installed
            dest_path = self.packs_path / manifest.id
            if dest_path.exists():
                return False, f"Pack '{manifest.id}' already installed"

            # Copy pack
            shutil.copytree(source_path, dest_path)

            # Reload
            self._loaded = False
            self.load()

            logger.info(f"[LOCAL] Installed pack: {manifest.name}")
            return True, f"Installed: {manifest.name} v{manifest.version}"

        except Exception as e:
            logger.error(f"[LOCAL] Install failed: {e}")
            return False, f"Install failed: {e}"

    def uninstall_pack(self, pack_id: str) -> Tuple[bool, str]:
        """
        Remove an installed pack.

        Args:
            pack_id: Pack identifier

        Returns:
            (success, message)
        """
        pack_path = self.packs_path / pack_id

        if not pack_path.exists():
            return False, f"Pack '{pack_id}' not found"

        try:
            shutil.rmtree(pack_path)
            if pack_id in self._packs:
                del self._packs[pack_id]

            logger.info(f"[LOCAL] Uninstalled pack: {pack_id}")
            return True, f"Uninstalled: {pack_id}"

        except Exception as e:
            logger.error(f"[LOCAL] Uninstall failed: {e}")
            return False, f"Uninstall failed: {e}"

    def search_samples(
        self,
        query: Optional[str] = None,
        sound_type: Optional[SoundType] = None,
        pack_id: Optional[str] = None,
    ) -> List[SoundSample]:
        """
        Search for samples.

        Args:
            query: Search query (matches name, tags)
            sound_type: Filter by type
            pack_id: Filter by pack

        Returns:
            List of matching samples
        """
        if not self._loaded:
            self.load()

        results = []

        for pack in self._packs.values():
            if pack_id and pack.manifest.id != pack_id:
                continue

            for sample in pack.samples.values():
                # Type filter
                if sound_type and sample.sound_type != sound_type:
                    continue

                # Query filter
                if query:
                    query_lower = query.lower()
                    name_match = query_lower in sample.name.lower()
                    tag_match = any(query_lower in t.lower() for t in sample.tags)
                    if not (name_match or tag_match):
                        continue

                results.append(sample)

        return results

    def get_sample_path(self, pack_id: str, instrument: str) -> Optional[Path]:
        """
        Get absolute path to a sample.

        Args:
            pack_id: Pack identifier
            instrument: Instrument name

        Returns:
            Path to sample file or None
        """
        pack = self.get_pack(pack_id)
        if not pack:
            return None

        sample = pack.get_sample(instrument)
        if not sample:
            return None

        return sample.path if sample.exists() else None

    def create_pack_manifest(
        self,
        pack_id: str,
        name: str,
        author: str,
        description: str = "",
        license: str = "CC0",
    ) -> SoundPackManifest:
        """
        Create a new pack manifest (for creating new packs).

        Args:
            pack_id: Unique identifier
            name: Display name
            author: Creator name
            description: Pack description
            license: License type

        Returns:
            New manifest object
        """
        return SoundPackManifest(
            id=pack_id,
            name=name,
            version="1.0.0",
            author=author,
            description=description,
            license=license,
            instruments={},
            tags=[],
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
        )

    def save_pack_manifest(self, manifest: SoundPackManifest, pack_path: Path) -> bool:
        """
        Save manifest to pack directory.

        Args:
            manifest: Manifest object
            pack_path: Pack directory path

        Returns:
            Success status
        """
        try:
            pack_path.mkdir(parents=True, exist_ok=True)
            samples_path = pack_path / "samples"
            samples_path.mkdir(exist_ok=True)

            manifest.updated = datetime.now().isoformat()
            manifest_path = pack_path / "manifest.json"
            manifest_path.write_text(json.dumps(manifest.to_dict(), indent=2))

            logger.info(f"[LOCAL] Saved manifest: {manifest_path}")
            return True

        except Exception as e:
            logger.error(f"[LOCAL] Save manifest failed: {e}")
            return False

    # === User Samples ===

    def import_user_sample(
        self,
        source_path: Path,
        name: Optional[str] = None,
        sound_type: SoundType = SoundType.OTHER,
    ) -> Tuple[bool, str]:
        """
        Import a sample to user library.

        Args:
            source_path: Source file path
            name: Optional name (defaults to filename)
            sound_type: Sound category

        Returns:
            (success, message)
        """
        if not source_path.exists():
            return False, f"File not found: {source_path}"

        # Supported formats
        if source_path.suffix.lower() not in [".wav", ".mp3", ".ogg", ".flac"]:
            return False, "Unsupported format (use WAV, MP3, OGG, FLAC)"

        try:
            dest_name = name or source_path.stem
            dest_path = self.user_path / f"{dest_name}{source_path.suffix}"

            shutil.copy2(source_path, dest_path)

            logger.info(f"[LOCAL] Imported user sample: {dest_path}")
            return True, f"Imported: {dest_name}"

        except Exception as e:
            logger.error(f"[LOCAL] Import failed: {e}")
            return False, f"Import failed: {e}"

    def list_user_samples(self) -> List[Dict[str, Any]]:
        """List user-imported samples."""
        samples = []

        for f in self.user_path.iterdir():
            if f.is_file() and f.suffix.lower() in [".wav", ".mp3", ".ogg", ".flac"]:
                samples.append(
                    {
                        "name": f.stem,
                        "path": str(f),
                        "format": f.suffix[1:].upper(),
                        "size_kb": f.stat().st_size // 1024,
                    }
                )

        return samples

    # === Presets ===

    def save_preset(self, name: str, pattern_data: Dict[str, Any]) -> bool:
        """
        Save a pattern preset.

        Args:
            name: Preset name
            pattern_data: Pattern dictionary

        Returns:
            Success status
        """
        try:
            preset_path = self.presets_path / f"{name}.json"
            preset_path.write_text(json.dumps(pattern_data, indent=2))
            logger.info(f"[LOCAL] Saved preset: {name}")
            return True
        except Exception as e:
            logger.error(f"[LOCAL] Save preset failed: {e}")
            return False

    def load_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a pattern preset."""
        preset_path = self.presets_path / f"{name}.json"

        if not preset_path.exists():
            return None

        try:
            return json.loads(preset_path.read_text())
        except Exception as e:
            logger.error(f"[LOCAL] Load preset failed: {e}")
            return None

    def list_presets(self) -> List[str]:
        """List available presets."""
        return [f.stem for f in self.presets_path.glob("*.json")]


# === Built-in Packs ===


def create_builtin_808_pack(library: SoundLibrary) -> bool:
    """
    Create the built-in 808 pack (generates from Drum808 synth).

    Args:
        library: Sound library instance

    Returns:
        Success status
    """
    pack_id = "808-builtin"
    pack_path = library.packs_path / pack_id

    if pack_path.exists():
        return True  # Already exists

    manifest = library.create_pack_manifest(
        pack_id=pack_id,
        name="808 Built-in",
        author="uDOS",
        description="Built-in TR-808 sounds generated by Groovebox engine",
        license="CC0",
    )

    # Define instruments
    manifest.instruments = {
        "kick": "samples/kick.wav",
        "snare": "samples/snare.wav",
        "hat_closed": "samples/hat_closed.wav",
        "hat_open": "samples/hat_open.wav",
        "clap": "samples/clap.wav",
        "tom_low": "samples/tom_low.wav",
        "tom_mid": "samples/tom_mid.wav",
        "tom_high": "samples/tom_high.wav",
    }
    manifest.tags = ["drums", "808", "classic", "builtin"]

    library.save_pack_manifest(manifest, pack_path)

    # Note: Actual WAV generation would use Drum808.generate()
    # For now, just create the structure
    logger.info(f"[LOCAL] Created 808-builtin pack structure")
    return True


# Singleton instance
_library: Optional[SoundLibrary] = None


def get_sound_library() -> SoundLibrary:
    """Get or create the sound library singleton."""
    global _library
    if _library is None:
        _library = SoundLibrary()
        _library.load()
    return _library


if __name__ == "__main__":
    # Test
    library = SoundLibrary(Path("./test_sounds"))

    print("Sound Library Manager Test")
    print("=" * 40)

    print(f"Base path: {library.base_path}")
    print(f"Packs: {library.list_packs()}")
    print(f"User samples: {library.list_user_samples()}")
    print(f"Presets: {library.list_presets()}")
