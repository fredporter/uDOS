"""
⚠️ DEPRECATED: TinyCore ISO Setup and Management

**Status:** DEPRECATED — Use Alpine Linux instead
**Date:** 2026-01-24
**Migration:** See docs/decisions/ADR-0003-alpine-linux-migration.md

This module is kept for backwards compatibility only.
uDOS has migrated to Alpine Linux. Use Alpine installer instead.

For Alpine Linux setup:
    - See: docs/howto/alpine-install.md
    - Use: APK packages instead of TCZ
    - Builder: wizard/services/plugin_factory.py (APKBuilder)

Legacy Usage (DO NOT USE):
    python -m library.tinycore.setup download tinycore
    python -m library.tinycore.setup verify TinyCore-current.iso
    python -m library.tinycore.setup list
"""

import warnings
import hashlib
import json
import urllib.request
import sys
from pathlib import Path
from typing import Optional, Dict

# Deprecation warning
warnings.warn(
    "library.tinycore.setup is deprecated. "
    "uDOS has migrated to Alpine Linux. "
    "See docs/decisions/ADR-0003-alpine-linux-migration.md",
    DeprecationWarning,
    stacklevel=2,
)

# Add project root to path (library/ is at root)
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TinyCoreSetup:
    """
    TinyCore ISO download and verification utility.

    Manages ISO images for uDOS deployment on TinyCore Linux.
    """

    def __init__(self):
        self.library_dir = Path(__file__).parent
        self.os_images_dir = self.library_dir.parent / "os-images"
        self.checksums_file = self.os_images_dir / "checksums.json"
        self.checksums = self._load_checksums()

    def _load_checksums(self) -> Dict:
        """Load checksums.json"""
        if self.checksums_file.exists():
            return json.loads(self.checksums_file.read_text())
        return {"schema_version": "1.0.0", "images": {}}

    def _save_checksums(self):
        """Save checksums.json"""
        with open(self.checksums_file, "w") as f:
            json.dump(self.checksums, f, indent=2)

    def list_images(self) -> Dict:
        """List available TinyCore images"""
        images = {}
        for name, info in self.checksums.get("images", {}).items():
            # Check if downloaded
            iso_path = self.library_dir / info.get("filename", f"{name}.iso")
            alt_path = self.os_images_dir / info.get("filename", f"{name}.iso")

            images[name] = {
                "name": info.get("name", name),
                "filename": info.get("filename"),
                "description": info.get("description", ""),
                "url": info.get("url"),
                "downloaded": iso_path.exists() or alt_path.exists(),
                "verified": info.get("sha256") is not None,
                "size_mb": info.get("size_mb"),
            }
        return images

    def download(self, image_name: str, force: bool = False) -> Optional[Path]:
        """
        Download a TinyCore ISO image.

        Args:
            image_name: Image key (tinycore, core, coreplus, etc.)
            force: Re-download even if exists

        Returns:
            Path to downloaded ISO, or None on failure
        """
        if image_name not in self.checksums.get("images", {}):
            print(f"❌ Unknown image: {image_name}")
            print(f"   Available: {', '.join(self.checksums.get('images', {}).keys())}")
            return None

        info = self.checksums["images"][image_name]
        filename = info.get("filename", f"{image_name}.iso")
        url = info.get("url")

        if not url:
            print(f"❌ No download URL for: {image_name}")
            return None

        # Destination path
        dest_path = self.library_dir / filename

        if dest_path.exists() and not force:
            print(f"✅ Already downloaded: {dest_path}")
            return dest_path

        print(f"⬇️  Downloading {image_name}...")
        print(f"   URL: {url}")
        print(f"   Destination: {dest_path}")

        try:
            # Download with progress
            def reporthook(block_num, block_size, total_size):
                downloaded = block_num * block_size
                if total_size > 0:
                    percent = min(100, downloaded * 100 / total_size)
                    mb = downloaded / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)
                    print(
                        f"\r   Progress: {percent:.1f}% ({mb:.1f}/{total_mb:.1f} MB)",
                        end="",
                    )

            urllib.request.urlretrieve(url, dest_path, reporthook)
            print()  # Newline after progress

            # Calculate and store checksum
            sha256 = self._calculate_sha256(dest_path)
            info["sha256"] = sha256
            info["size_mb"] = round(dest_path.stat().st_size / (1024 * 1024), 1)
            self._save_checksums()

            print(f"✅ Downloaded: {dest_path}")
            print(f"   SHA256: {sha256[:16]}...")
            print(f"   Size: {info['size_mb']} MB")

            return dest_path

        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None

    def verify(self, iso_path: Path) -> bool:
        """
        Verify ISO checksum.

        Args:
            iso_path: Path to ISO file

        Returns:
            True if checksum matches or is stored, False on mismatch
        """
        if not iso_path.exists():
            print(f"❌ File not found: {iso_path}")
            return False

        # Find matching image info
        filename = iso_path.name
        image_info = None
        image_name = None

        for name, info in self.checksums.get("images", {}).items():
            if info.get("filename") == filename:
                image_info = info
                image_name = name
                break

        if not image_info:
            print(f"⚠️  Unknown ISO: {filename}")
            print("   Calculating checksum anyway...")

        # Calculate checksum
        print(f"🔍 Verifying: {iso_path}")
        sha256 = self._calculate_sha256(iso_path)
        print(f"   SHA256: {sha256}")

        if image_info:
            stored_sha256 = image_info.get("sha256")

            if stored_sha256:
                if sha256 == stored_sha256:
                    print(f"✅ Checksum verified for {image_name}")
                    return True
                else:
                    print(f"❌ Checksum MISMATCH!")
                    print(f"   Expected: {stored_sha256}")
                    print(f"   Got:      {sha256}")
                    return False
            else:
                # Store new checksum
                print(f"📝 Storing checksum for {image_name}")
                image_info["sha256"] = sha256
                image_info["size_mb"] = round(
                    iso_path.stat().st_size / (1024 * 1024), 1
                )
                self._save_checksums()
                return True

        return True

    def _calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def get_iso_path(self, image_name: str) -> Optional[Path]:
        """
        Get path to an ISO image (downloads if not present).

        Args:
            image_name: Image key

        Returns:
            Path to ISO, or None if unavailable
        """
        if image_name not in self.checksums.get("images", {}):
            return None

        info = self.checksums["images"][image_name]
        filename = info.get("filename", f"{image_name}.iso")

        # Check local tinycore directory
        local_path = self.library_dir / filename
        if local_path.exists():
            return local_path

        # Check os-images directory
        os_path = self.os_images_dir / filename
        if os_path.exists():
            return os_path

        return None

    def create_bootable_usb(self, image_name: str, device: str) -> bool:
        """
        Create bootable USB from ISO (Linux/macOS only).

        Args:
            image_name: Image key
            device: Device path (e.g., /dev/sdb, /dev/disk2)

        Returns:
            True on success
        """
        import platform
        import subprocess

        if platform.system() not in ["Linux", "Darwin"]:
            print("❌ USB creation only supported on Linux/macOS")
            return False

        iso_path = self.get_iso_path(image_name)
        if not iso_path:
            print(f"❌ ISO not found: {image_name}")
            print("   Run: python setup.py download {image_name}")
            return False

        print(f"⚠️  WARNING: This will ERASE all data on {device}")
        confirm = input("   Type 'yes' to continue: ")

        if confirm.lower() != "yes":
            print("   Cancelled.")
            return False

        print(f"📀 Writing {iso_path} to {device}...")

        try:
            # Use dd
            if platform.system() == "Darwin":
                # macOS: unmount first
                subprocess.run(["diskutil", "unmountDisk", device], check=False)
                # Use raw device for speed
                raw_device = device.replace("/dev/disk", "/dev/rdisk")
                cmd = ["sudo", "dd", f"if={iso_path}", f"of={raw_device}", "bs=1m"]
            else:
                # Linux
                cmd = [
                    "sudo",
                    "dd",
                    f"if={iso_path}",
                    f"of={device}",
                    "bs=4M",
                    "status=progress",
                ]

            subprocess.run(cmd, check=True)
            subprocess.run(["sync"], check=True)

            print(f"✅ Bootable USB created: {device}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create USB: {e}")
            return False


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="TinyCore ISO Setup")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List command
    subparsers.add_parser("list", help="List available images")

    # Download command
    dl_parser = subparsers.add_parser("download", help="Download an ISO")
    dl_parser.add_argument("image", help="Image name (tinycore, core, etc.)")
    dl_parser.add_argument("--force", "-f", action="store_true", help="Re-download")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify ISO checksum")
    verify_parser.add_argument("iso", help="Path to ISO file")

    # USB command
    usb_parser = subparsers.add_parser("usb", help="Create bootable USB")
    usb_parser.add_argument("image", help="Image name")
    usb_parser.add_argument("device", help="USB device (e.g., /dev/sdb)")

    args = parser.parse_args()
    setup = TinyCoreSetup()

    if args.command == "list":
        images = setup.list_images()
        print("\n📀 TinyCore Images:\n")
        for name, info in images.items():
            status = "✅" if info["downloaded"] else "⬇️"
            verified = "🔒" if info["verified"] else ""
            print(f"  {status} {name}: {info['name']} {verified}")
            print(f"      {info['description']}")
            if info["size_mb"]:
                print(f"      Size: {info['size_mb']} MB")
            print()

    elif args.command == "download":
        setup.download(args.image, force=args.force)

    elif args.command == "verify":
        setup.verify(Path(args.iso))

    elif args.command == "usb":
        setup.create_bootable_usb(args.image, args.device)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
