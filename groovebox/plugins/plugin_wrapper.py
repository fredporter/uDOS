"""
Plugin Wrapper - External Instrument Bridge
===========================================

Provides a unified interface for loading external instruments:
- FluidSynth (SoundFont .sf2 playback)
- LMMS projects (via CLI rendering)
- VCV Rack patches (via CLI rendering)

Part of uDOS Groovebox Extension v1.0.0.36+

Design Philosophy:
- Offline-first: All rendering is local
- No realtime dependencies: Render to WAV files
- Graceful fallback: Use built-in instruments if plugins unavailable
"""

import subprocess
import shutil
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from enum import Enum
import tempfile

from core.services.logging_service import get_logger

logger = get_logger("groovebox-plugins")


class PluginType(Enum):
    """Supported plugin types."""

    FLUIDSYNTH = "fluidsynth"  # SoundFont playback
    LMMS = "lmms"  # LMMS CLI rendering
    VCV_RACK = "vcvrack"  # VCV Rack CLI rendering


@dataclass
class PluginInfo:
    """Information about an installed plugin."""

    plugin_type: PluginType
    name: str
    version: str
    path: Path
    available: bool = False
    error: Optional[str] = None


@dataclass
class SoundFont:
    """A SoundFont file (.sf2)."""

    path: Path
    name: str
    bank: int = 0
    preset: int = 0

    def exists(self) -> bool:
        return self.path.exists()


@dataclass
class RenderJob:
    """A rendering job for external plugins."""

    plugin_type: PluginType
    midi_file: Optional[Path] = None
    project_file: Optional[Path] = None
    soundfont: Optional[SoundFont] = None
    output_path: Optional[Path] = None
    sample_rate: int = 44100
    duration: float = 0.0
    options: Dict[str, Any] = field(default_factory=dict)


class PluginManager:
    """
    Manager for external music plugins.

    Detects installed plugins and provides rendering capabilities.
    """

    def __init__(self):
        self._plugins: Dict[PluginType, PluginInfo] = {}
        self._soundfonts: List[SoundFont] = []

        # Detect available plugins
        self._detect_plugins()

        logger.info("[LOCAL] PluginManager initialized")

    def _detect_plugins(self):
        """Detect installed plugins."""
        # FluidSynth
        self._detect_fluidsynth()

        # LMMS
        self._detect_lmms()

        # VCV Rack
        self._detect_vcvrack()

    def _detect_fluidsynth(self):
        """Detect FluidSynth installation."""
        fluidsynth_path = shutil.which("fluidsynth")

        if fluidsynth_path:
            try:
                result = subprocess.run(
                    ["fluidsynth", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                # Parse version from output
                version = "unknown"
                for line in result.stdout.split("\n"):
                    if "FluidSynth" in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            version = parts[-1]
                        break

                self._plugins[PluginType.FLUIDSYNTH] = PluginInfo(
                    plugin_type=PluginType.FLUIDSYNTH,
                    name="FluidSynth",
                    version=version,
                    path=Path(fluidsynth_path),
                    available=True,
                )
                logger.info(f"[LOCAL] FluidSynth detected: v{version}")

            except Exception as e:
                self._plugins[PluginType.FLUIDSYNTH] = PluginInfo(
                    plugin_type=PluginType.FLUIDSYNTH,
                    name="FluidSynth",
                    version="",
                    path=Path(fluidsynth_path),
                    available=False,
                    error=str(e),
                )
        else:
            self._plugins[PluginType.FLUIDSYNTH] = PluginInfo(
                plugin_type=PluginType.FLUIDSYNTH,
                name="FluidSynth",
                version="",
                path=Path(""),
                available=False,
                error="Not installed",
            )

    def _detect_lmms(self):
        """Detect LMMS installation."""
        # Try common LMMS CLI names
        lmms_names = ["lmms", "lmms-cli"]
        lmms_path = None

        for name in lmms_names:
            path = shutil.which(name)
            if path:
                lmms_path = path
                break

        if lmms_path:
            try:
                result = subprocess.run(
                    [lmms_path, "--version"], capture_output=True, text=True, timeout=10
                )
                version = result.stdout.strip() if result.stdout else "unknown"

                self._plugins[PluginType.LMMS] = PluginInfo(
                    plugin_type=PluginType.LMMS,
                    name="LMMS",
                    version=version,
                    path=Path(lmms_path),
                    available=True,
                )
                logger.info(f"[LOCAL] LMMS detected: {version}")

            except Exception as e:
                self._plugins[PluginType.LMMS] = PluginInfo(
                    plugin_type=PluginType.LMMS,
                    name="LMMS",
                    version="",
                    path=Path(lmms_path),
                    available=False,
                    error=str(e),
                )
        else:
            self._plugins[PluginType.LMMS] = PluginInfo(
                plugin_type=PluginType.LMMS,
                name="LMMS",
                version="",
                path=Path(""),
                available=False,
                error="Not installed",
            )

    def _detect_vcvrack(self):
        """Detect VCV Rack installation."""
        # VCV Rack CLI (Rack headless)
        vcv_names = ["Rack", "rack", "vcvrack"]
        vcv_path = None

        # Also check common installation paths
        common_paths = [
            "/Applications/Rack.app/Contents/MacOS/Rack",
            "/Applications/VCV Rack 2.app/Contents/MacOS/Rack",
            Path.home() / ".local" / "share" / "Rack2" / "Rack",
        ]

        for name in vcv_names:
            path = shutil.which(name)
            if path:
                vcv_path = path
                break

        if not vcv_path:
            for path in common_paths:
                if Path(path).exists():
                    vcv_path = str(path)
                    break

        if vcv_path:
            self._plugins[PluginType.VCV_RACK] = PluginInfo(
                plugin_type=PluginType.VCV_RACK,
                name="VCV Rack",
                version="2.x",
                path=Path(vcv_path),
                available=True,
            )
            logger.info(f"[LOCAL] VCV Rack detected: {vcv_path}")
        else:
            self._plugins[PluginType.VCV_RACK] = PluginInfo(
                plugin_type=PluginType.VCV_RACK,
                name="VCV Rack",
                version="",
                path=Path(""),
                available=False,
                error="Not installed",
            )

    # === Public API ===

    def is_available(self, plugin_type: PluginType) -> bool:
        """Check if a plugin is available."""
        info = self._plugins.get(plugin_type)
        return info is not None and info.available

    def get_info(self, plugin_type: PluginType) -> Optional[PluginInfo]:
        """Get plugin information."""
        return self._plugins.get(plugin_type)

    def list_plugins(self) -> List[PluginInfo]:
        """List all plugins (available and unavailable)."""
        return list(self._plugins.values())

    def list_available(self) -> List[PluginInfo]:
        """List only available plugins."""
        return [p for p in self._plugins.values() if p.available]

    # === SoundFont Management ===

    def register_soundfont(self, path: Path, name: str = "") -> Optional[SoundFont]:
        """Register a SoundFont file."""
        path = Path(path)
        if not path.exists():
            logger.warning(f"[LOCAL] SoundFont not found: {path}")
            return None

        sf = SoundFont(path=path, name=name or path.stem)
        self._soundfonts.append(sf)
        logger.info(f"[LOCAL] Registered SoundFont: {sf.name}")
        return sf

    def list_soundfonts(self) -> List[SoundFont]:
        """List registered SoundFonts."""
        return self._soundfonts

    def find_soundfont(self, name: str) -> Optional[SoundFont]:
        """Find SoundFont by name."""
        for sf in self._soundfonts:
            if sf.name.lower() == name.lower():
                return sf
        return None

    # === Rendering ===

    def render_fluidsynth(
        self,
        midi_path: Path,
        soundfont: SoundFont,
        output_path: Path,
        sample_rate: int = 44100,
    ) -> Tuple[bool, str]:
        """
        Render MIDI file using FluidSynth.

        Args:
            midi_path: Path to MIDI file
            soundfont: SoundFont to use
            output_path: Output WAV path
            sample_rate: Sample rate

        Returns:
            (success, message)
        """
        if not self.is_available(PluginType.FLUIDSYNTH):
            return False, "FluidSynth not available"

        if not soundfont.exists():
            return False, f"SoundFont not found: {soundfont.path}"

        if not midi_path.exists():
            return False, f"MIDI file not found: {midi_path}"

        try:
            info = self._plugins[PluginType.FLUIDSYNTH]

            # FluidSynth command
            cmd = [
                str(info.path),
                "-ni",  # No interactive mode
                "-F",
                str(output_path),  # Output file
                "-r",
                str(sample_rate),  # Sample rate
                "-g",
                "0.5",  # Gain
                str(soundfont.path),
                str(midi_path),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0 and output_path.exists():
                logger.info(f"[LOCAL] FluidSynth rendered: {output_path}")
                return True, f"Rendered to {output_path}"
            else:
                error = result.stderr or "Unknown error"
                return False, f"FluidSynth error: {error}"

        except subprocess.TimeoutExpired:
            return False, "FluidSynth timeout"
        except Exception as e:
            return False, f"FluidSynth error: {e}"

    def render_lmms(
        self, project_path: Path, output_path: Path, format: str = "wav"
    ) -> Tuple[bool, str]:
        """
        Render LMMS project to audio.

        Args:
            project_path: Path to .mmpz or .mmp project
            output_path: Output file path
            format: Output format (wav, ogg, mp3)

        Returns:
            (success, message)
        """
        if not self.is_available(PluginType.LMMS):
            return False, "LMMS not available"

        if not project_path.exists():
            return False, f"Project not found: {project_path}"

        try:
            info = self._plugins[PluginType.LMMS]

            cmd = [
                str(info.path),
                "-r",
                str(project_path),  # Render project
                "-o",
                str(output_path),  # Output file
                "-f",
                format,  # Format
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout for complex projects
            )

            if result.returncode == 0 and output_path.exists():
                logger.info(f"[LOCAL] LMMS rendered: {output_path}")
                return True, f"Rendered to {output_path}"
            else:
                error = result.stderr or "Unknown error"
                return False, f"LMMS error: {error}"

        except subprocess.TimeoutExpired:
            return False, "LMMS render timeout"
        except Exception as e:
            return False, f"LMMS error: {e}"

    def render_vcvrack(
        self,
        patch_path: Path,
        output_path: Path,
        duration: float = 10.0,
        sample_rate: int = 44100,
    ) -> Tuple[bool, str]:
        """
        Render VCV Rack patch to audio.

        Note: Requires Rack headless mode with AUDIO-FILE module

        Args:
            patch_path: Path to .vcv patch
            output_path: Output WAV path
            duration: Render duration in seconds
            sample_rate: Sample rate

        Returns:
            (success, message)
        """
        if not self.is_available(PluginType.VCV_RACK):
            return False, "VCV Rack not available"

        if not patch_path.exists():
            return False, f"Patch not found: {patch_path}"

        # VCV Rack headless rendering is complex and requires
        # specific patch setup. Return guidance instead.
        return False, (
            "VCV Rack headless rendering requires patch configuration. "
            "Add an AUDIO-FILE module to your patch with the output path."
        )


# === Convenience Functions ===

_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get or create plugin manager singleton."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


def render_midi_with_soundfont(
    midi_path: Path, soundfont_path: Path, output_path: Path
) -> Tuple[bool, str]:
    """
    Convenience function to render MIDI with SoundFont.

    Args:
        midi_path: MIDI file
        soundfont_path: .sf2 file
        output_path: Output WAV

    Returns:
        (success, message)
    """
    manager = get_plugin_manager()

    sf = SoundFont(path=soundfont_path, name=soundfont_path.stem)
    return manager.render_fluidsynth(midi_path, sf, output_path)


def check_plugin_status() -> Dict[str, Dict[str, Any]]:
    """Get status of all plugins."""
    manager = get_plugin_manager()

    status = {}
    for info in manager.list_plugins():
        status[info.plugin_type.value] = {
            "name": info.name,
            "version": info.version,
            "available": info.available,
            "path": str(info.path) if info.path else "",
            "error": info.error,
        }

    return status


if __name__ == "__main__":
    # Demo
    print("Plugin Manager Status")
    print("=" * 40)

    status = check_plugin_status()
    for plugin, info in status.items():
        icon = "✅" if info["available"] else "❌"
        print(f"{icon} {info['name']}: {info['version'] or info['error']}")
