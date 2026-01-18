#!/usr/bin/env python3
"""
Sonic Screwdriver Flash Pack Manager - Firmware provisioning for Layer 650

Manages firmware flash packs, version tracking, signature verification,
and OTA update orchestration for MeshCore devices.

Flash Pack Structure:
- firmware.bin - Compiled firmware binary
- manifest.json - Metadata (version, target devices, checksums)
- signature.sig - Cryptographic signature
- README.md - Release notes and changelog

Version: v1.2.14
Author: Fred Porter
Date: December 7, 2025
"""

import json
import hashlib
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum


class FlashPackStatus(Enum):
    """Flash pack validation status."""
    VALID = "✓"           # Valid, ready to flash
    INVALID = "✗"         # Invalid signature or checksum
    OUTDATED = "⚠"        # Older version available
    UNKNOWN = "?"         # Not yet validated


class FlashStage(Enum):
    """Firmware flash stages."""
    IDLE = "idle"
    VERIFYING = "verifying"
    ERASING = "erasing"
    WRITING = "writing"
    VALIDATING = "validating"
    HEALTH_CHECK = "health_check"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class FlashPackManifest:
    """Firmware flash pack manifest."""
    version: str                    # Firmware version (e.g., "2.4.1")
    build_date: str                 # ISO timestamp
    target_devices: List[str]       # Compatible device types
    min_hardware_rev: str           # Minimum hardware revision
    binary_size: int                # Binary size in bytes
    checksum_sha256: str            # SHA256 checksum
    signature: str                  # Cryptographic signature
    release_notes: str              # Changelog/notes
    features: List[str]             # New features
    bugfixes: List[str]             # Bug fixes
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FlashPackManifest':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class FlashProgress:
    """Real-time flash progress tracking."""
    device_id: str
    stage: FlashStage
    percentage: int          # 0-100
    bytes_written: int
    total_bytes: int
    elapsed_seconds: float
    error_message: Optional[str] = None
    
    @property
    def estimated_remaining(self) -> float:
        """Estimate remaining time in seconds."""
        if self.percentage == 0 or self.elapsed_seconds == 0:
            return 0.0
        
        total_time = self.elapsed_seconds / (self.percentage / 100)
        return max(0, total_time - self.elapsed_seconds)


class FlashPackManager:
    """
    Manage firmware flash packs for Sonic Screwdriver provisioning.
    
    Handles flash pack storage, validation, version tracking, and
    distribution to devices.
    """
    
    def __init__(self, flash_packs_dir: Optional[Path] = None):
        """
        Initialize flash pack manager.
        
        Args:
            flash_packs_dir: Directory for flash pack storage
        """
        if flash_packs_dir is None:
            flash_packs_dir = Path(__file__).parent / "data" / "flash_packs"
        
        self.flash_packs_dir = Path(flash_packs_dir)
        self.flash_packs_dir.mkdir(parents=True, exist_ok=True)
        
        self.packs: Dict[str, FlashPackManifest] = {}
        self.active_flashes: Dict[str, FlashProgress] = {}
        
        self._load_flash_packs()
    
    def _load_flash_packs(self) -> None:
        """Load all flash packs from storage."""
        for pack_dir in self.flash_packs_dir.iterdir():
            if not pack_dir.is_dir():
                continue
            
            manifest_file = pack_dir / "manifest.json"
            if not manifest_file.exists():
                continue
            
            try:
                with open(manifest_file, 'r') as f:
                    manifest_data = json.load(f)
                    manifest = FlashPackManifest.from_dict(manifest_data)
                    self.packs[manifest.version] = manifest
            except Exception as e:
                print(f"Warning: Failed to load flash pack {pack_dir.name}: {e}")
    
    def create_flash_pack(
        self,
        version: str,
        binary_path: Path,
        target_devices: List[str],
        release_notes: str = "",
        features: Optional[List[str]] = None,
        bugfixes: Optional[List[str]] = None
    ) -> FlashPackManifest:
        """
        Create new flash pack from firmware binary.
        
        Args:
            version: Firmware version
            binary_path: Path to firmware binary
            target_devices: Compatible device types
            release_notes: Changelog/notes
            features: New features list
            bugfixes: Bug fixes list
            
        Returns:
            Created FlashPackManifest
        """
        if not binary_path.exists():
            raise FileNotFoundError(f"Firmware binary not found: {binary_path}")
        
        # Calculate checksum
        with open(binary_path, 'rb') as f:
            binary_data = f.read()
            checksum = hashlib.sha256(binary_data).hexdigest()
        
        # Create manifest
        manifest = FlashPackManifest(
            version=version,
            build_date=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            target_devices=target_devices,
            min_hardware_rev="1.0",
            binary_size=len(binary_data),
            checksum_sha256=checksum,
            signature=self._generate_signature(checksum),
            release_notes=release_notes,
            features=features or [],
            bugfixes=bugfixes or []
        )
        
        # Create flash pack directory
        pack_dir = self.flash_packs_dir / f"v{version}"
        pack_dir.mkdir(exist_ok=True)
        
        # Copy binary
        binary_dest = pack_dir / "firmware.bin"
        with open(binary_dest, 'wb') as f:
            f.write(binary_data)
        
        # Write manifest
        manifest_file = pack_dir / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest.to_dict(), f, indent=2)
        
        # Write README
        readme_file = pack_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(self._generate_readme(manifest))
        
        # Store in registry
        self.packs[version] = manifest
        
        return manifest
    
    def _generate_signature(self, checksum: str) -> str:
        """Generate cryptographic signature (simplified for demo)."""
        # In production, use proper crypto signing (e.g., RSA, Ed25519)
        signature_data = f"SIGNED:{checksum}:UDOS-SCREWDRIVER"
        return hashlib.sha256(signature_data.encode()).hexdigest()
    
    def _generate_readme(self, manifest: FlashPackManifest) -> str:
        """Generate README for flash pack."""
        lines = [
            f"# Firmware v{manifest.version}",
            "",
            f"**Build Date:** {manifest.build_date}",
            f"**Binary Size:** {manifest.binary_size:,} bytes",
            f"**Checksum:** {manifest.checksum_sha256[:16]}...",
            "",
            "## Target Devices",
            "",
        ]
        
        for device_type in manifest.target_devices:
            lines.append(f"- {device_type}")
        
        lines.append("")
        
        if manifest.features:
            lines.append("## New Features")
            lines.append("")
            for feature in manifest.features:
                lines.append(f"- {feature}")
            lines.append("")
        
        if manifest.bugfixes:
            lines.append("## Bug Fixes")
            lines.append("")
            for bugfix in manifest.bugfixes:
                lines.append(f"- {bugfix}")
            lines.append("")
        
        if manifest.release_notes:
            lines.append("## Release Notes")
            lines.append("")
            lines.append(manifest.release_notes)
        
        return '\n'.join(lines)
    
    def validate_flash_pack(self, version: str) -> FlashPackStatus:
        """
        Validate flash pack integrity.
        
        Args:
            version: Flash pack version
            
        Returns:
            Validation status
        """
        if version not in self.packs:
            return FlashPackStatus.UNKNOWN
        
        manifest = self.packs[version]
        pack_dir = self.flash_packs_dir / f"v{version}"
        binary_file = pack_dir / "firmware.bin"
        
        if not binary_file.exists():
            return FlashPackStatus.INVALID
        
        # Verify checksum
        with open(binary_file, 'rb') as f:
            binary_data = f.read()
            checksum = hashlib.sha256(binary_data).hexdigest()
        
        if checksum != manifest.checksum_sha256:
            return FlashPackStatus.INVALID
        
        # Verify signature
        expected_sig = self._generate_signature(checksum)
        if expected_sig != manifest.signature:
            return FlashPackStatus.INVALID
        
        return FlashPackStatus.VALID
    
    def get_flash_pack(self, version: str) -> Optional[FlashPackManifest]:
        """Get flash pack manifest by version."""
        return self.packs.get(version)
    
    def list_flash_packs(self) -> List[FlashPackManifest]:
        """List all available flash packs."""
        return list(self.packs.values())
    
    def get_latest_version(self, device_type: Optional[str] = None) -> Optional[str]:
        """
        Get latest firmware version.
        
        Args:
            device_type: Filter by device type
            
        Returns:
            Latest version string
        """
        compatible_packs = []
        
        for version, manifest in self.packs.items():
            if device_type is None or device_type in manifest.target_devices:
                compatible_packs.append((version, manifest))
        
        if not compatible_packs:
            return None
        
        # Sort by version (simplified - use semver in production)
        compatible_packs.sort(key=lambda x: x[0], reverse=True)
        return compatible_packs[0][0]
    
    def compare_versions(self, current: str, target: str) -> int:
        """
        Compare version strings.
        
        Args:
            current: Current version
            target: Target version
            
        Returns:
            -1 if current < target, 0 if equal, 1 if current > target
        """
        # Simplified comparison (use semver in production)
        if current == target:
            return 0
        elif current < target:
            return -1
        else:
            return 1
    
    def start_flash(
        self,
        device_id: str,
        version: str
    ) -> Optional[FlashProgress]:
        """
        Initiate firmware flash operation.
        
        Args:
            device_id: Target device ID
            version: Flash pack version
            
        Returns:
            FlashProgress tracker
        """
        if version not in self.packs:
            return None
        
        manifest = self.packs[version]
        
        progress = FlashProgress(
            device_id=device_id,
            stage=FlashStage.VERIFYING,
            percentage=0,
            bytes_written=0,
            total_bytes=manifest.binary_size,
            elapsed_seconds=0.0
        )
        
        self.active_flashes[device_id] = progress
        return progress
    
    def update_flash_progress(
        self,
        device_id: str,
        stage: FlashStage,
        percentage: int,
        bytes_written: Optional[int] = None
    ) -> bool:
        """
        Update flash progress.
        
        Args:
            device_id: Device being flashed
            stage: Current flash stage
            percentage: Completion percentage
            bytes_written: Bytes written so far
            
        Returns:
            True if updated successfully
        """
        if device_id not in self.active_flashes:
            return False
        
        progress = self.active_flashes[device_id]
        progress.stage = stage
        progress.percentage = percentage
        
        if bytes_written is not None:
            progress.bytes_written = bytes_written
        
        return True
    
    def get_flash_progress(self, device_id: str) -> Optional[FlashProgress]:
        """Get current flash progress for device."""
        return self.active_flashes.get(device_id)
    
    def complete_flash(self, device_id: str, success: bool = True) -> bool:
        """
        Mark flash operation as complete.
        
        Args:
            device_id: Device ID
            success: Whether flash succeeded
            
        Returns:
            True if marked complete
        """
        if device_id not in self.active_flashes:
            return False
        
        progress = self.active_flashes[device_id]
        progress.stage = FlashStage.COMPLETE if success else FlashStage.FAILED
        progress.percentage = 100 if success else progress.percentage
        
        # Remove from active flashes after brief delay
        # In production, move to history
        return True


def demo_flash_pack_manager():
    """Demonstrate flash pack manager functionality."""
    
    print("=" * 80)
    print("Sonic Screwdriver Flash Pack Manager Demo - v1.2.14")
    print("=" * 80)
    print()
    
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = FlashPackManager(Path(tmpdir))
        
        # Create mock firmware binaries
        temp_binary = Path(tmpdir) / "test_firmware.bin"
        with open(temp_binary, 'wb') as f:
            f.write(b"FIRMWARE_DATA_v2.4.1" * 1000)  # Mock firmware
        
        # Demo 1: Create flash pack
        print("Demo 1: Creating Flash Pack")
        print("-" * 80)
        
        manifest = manager.create_flash_pack(
            version="2.4.1",
            binary_path=temp_binary,
            target_devices=["NODE", "GATEWAY", "SENSOR"],
            release_notes="Stability improvements and bug fixes",
            features=[
                "Improved mesh routing algorithm",
                "Lower power consumption in sleep mode",
                "Enhanced signal strength reporting"
            ],
            bugfixes=[
                "Fixed reconnection issue after power loss",
                "Corrected timestamp overflow bug"
            ]
        )
        
        print(f"  ✓ Created flash pack v{manifest.version}")
        print(f"    Size: {manifest.binary_size:,} bytes")
        print(f"    Checksum: {manifest.checksum_sha256[:16]}...")
        print(f"    Features: {len(manifest.features)}")
        print(f"    Bug Fixes: {len(manifest.bugfixes)}")
        print()
        
        # Demo 2: Validate flash pack
        print("Demo 2: Validating Flash Pack")
        print("-" * 80)
        
        status = manager.validate_flash_pack("2.4.1")
        print(f"  Validation Status: {status.value}")
        print()
        
        # Demo 3: List flash packs
        print("Demo 3: Available Flash Packs")
        print("-" * 80)
        
        packs = manager.list_flash_packs()
        for pack in packs:
            print(f"  v{pack.version} - {pack.build_date}")
            print(f"    Targets: {', '.join(pack.target_devices)}")
            print(f"    Size: {pack.binary_size:,} bytes")
        print()
        
        # Demo 4: Simulated flash operation
        print("Demo 4: Firmware Flash Simulation")
        print("-" * 80)
        
        device_id = "D1"
        progress = manager.start_flash(device_id, "2.4.1")
        
        if progress:
            print(f"  Starting flash for {device_id}...")
            
            # Simulate flash stages
            stages = [
                (FlashStage.VERIFYING, 10, "Verifying signature"),
                (FlashStage.ERASING, 30, "Erasing Bank B"),
                (FlashStage.WRITING, 70, "Writing firmware"),
                (FlashStage.VALIDATING, 90, "Validating"),
                (FlashStage.HEALTH_CHECK, 95, "Health check"),
                (FlashStage.COMPLETE, 100, "Complete")
            ]
            
            for stage, pct, desc in stages:
                manager.update_flash_progress(device_id, stage, pct)
                current_progress = manager.get_flash_progress(device_id)
                print(f"    [{pct:>3}%] {desc}... {stage.value}")
            
            manager.complete_flash(device_id, success=True)
            print(f"  ✓ Flash complete!")
        print()
        
        print("✅ Flash pack manager demo complete!")


if __name__ == "__main__":
    demo_flash_pack_manager()
