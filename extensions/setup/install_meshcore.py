#!/usr/bin/env python3
"""
MeshCore Extension Installer for uDOS

Integrates MeshCore mesh networking library with uDOS for off-grid communication.
Supports LoRa-based multi-hop packet routing for survival/emergency scenarios.

Usage:
    python extensions/setup/install_meshcore.py [--check|--install|--uninstall]
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# Add core to path for uDOS utilities
UDOS_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(UDOS_ROOT))

# Basic logger if core modules unavailable
class SimpleLogger:
    def info(self, msg): print(f"ℹ️  {msg}")
    def warning(self, msg): print(f"⚠️  {msg}")
    def error(self, msg): print(f"❌ {msg}")

try:
    from core.config import Config
    from core.utils.logger import get_logger as core_get_logger
    logger = core_get_logger(__name__)
except ImportError:
    Config = None
    logger = SimpleLogger()

# Paths
MESHCORE_CLONE_PATH = UDOS_ROOT / "extensions" / "cloned" / "meshcore"
MESHCORE_EXTENSION_PATH = UDOS_ROOT / "extensions" / "play" / "meshcore"
MESHCORE_DATA_PATH = UDOS_ROOT / "memory" / "meshcore"

# Extension metadata
EXTENSION_INFO = {
    "id": "meshcore",
    "name": "MeshCore Mesh Networking",
    "version": "0.1.0",
    "description": "Off-grid LoRa mesh networking for survival communication",
    "author": "MeshCore Team (integration by uDOS)",
    "repo": "https://github.com/meshcore-dev/MeshCore",
    "dependencies": ["platformio"],
    "features": [
        "Multi-hop packet routing",
        "LoRa radio support (Heltec, RAK Wireless)",
        "Decentralized mesh network",
        "Companion radio for external apps",
        "Simple repeater mode",
        "Secure chat over mesh"
    ],
    "use_cases": [
        "Off-grid communication",
        "Emergency response",
        "Disaster recovery",
        "Remote sensor networks",
        "Tactical/security applications"
    ]
}


class MeshCoreInstaller:
    """Installer for MeshCore extension."""
    
    def __init__(self):
        self.config = Config() if Config else None
        self.meshcore_exists = MESHCORE_CLONE_PATH.exists()
        
    def check_status(self) -> Dict[str, any]:
        """Check installation status of MeshCore.
        
        Returns:
            Dictionary with status information
        """
        status = {
            "cloned": MESHCORE_CLONE_PATH.exists(),
            "installed": MESHCORE_EXTENSION_PATH.exists(),
            "data_dir": MESHCORE_DATA_PATH.exists(),
            "platformio": self._check_platformio(),
            "examples": [],
            "firmware": []
        }
        
        if status["cloned"]:
            # Check for examples
            examples_dir = MESHCORE_CLONE_PATH / "examples"
            if examples_dir.exists():
                status["examples"] = [d.name for d in examples_dir.iterdir() if d.is_dir()]
            
            # Check for prebuilt firmware
            bin_dir = MESHCORE_CLONE_PATH / "bin"
            if bin_dir.exists():
                status["firmware"] = [f.name for f in bin_dir.glob("*.bin")]
        
        return status
    
    def _check_platformio(self) -> bool:
        """Check if PlatformIO is installed."""
        try:
            result = subprocess.run(
                ["platformio", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def install(self) -> bool:
        """Install MeshCore extension.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.meshcore_exists:
            logger.error("MeshCore not cloned. Clone first with: git clone https://github.com/meshcore-dev/MeshCore extensions/cloned/meshcore")
            return False
        
        logger.info("Installing MeshCore extension...")
        
        # Create extension directory structure
        try:
            MESHCORE_EXTENSION_PATH.mkdir(parents=True, exist_ok=True)
            MESHCORE_DATA_PATH.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (MESHCORE_DATA_PATH / "devices").mkdir(exist_ok=True)
            (MESHCORE_DATA_PATH / "firmware").mkdir(exist_ok=True)
            (MESHCORE_DATA_PATH / "logs").mkdir(exist_ok=True)
            (MESHCORE_DATA_PATH / "config").mkdir(exist_ok=True)
            
            logger.info(f"✅ Created extension directories")
            
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            return False
        
        # Create extension manifest
        try:
            manifest_path = MESHCORE_EXTENSION_PATH / "extension.json"
            with open(manifest_path, "w") as f:
                json.dump(EXTENSION_INFO, f, indent=2)
            logger.info(f"✅ Created extension manifest")
            
        except Exception as e:
            logger.error(f"Failed to create manifest: {e}")
            return False
        
        # Create Python wrapper for MeshCore integration
        try:
            self._create_python_wrapper()
            logger.info(f"✅ Created Python wrapper")
            
        except Exception as e:
            logger.error(f"Failed to create Python wrapper: {e}")
            return False
        
        # Copy example firmware (if available)
        try:
            bin_dir = MESHCORE_CLONE_PATH / "bin"
            if bin_dir.exists():
                for firmware in bin_dir.glob("*.bin"):
                    dest = MESHCORE_DATA_PATH / "firmware" / firmware.name
                    shutil.copy2(firmware, dest)
                logger.info(f"✅ Copied example firmware")
            
        except Exception as e:
            logger.warning(f"Could not copy firmware: {e}")
        
        # Create default config
        try:
            self._create_default_config()
            logger.info(f"✅ Created default configuration")
            
        except Exception as e:
            logger.error(f"Failed to create config: {e}")
            return False
        
        logger.info("✅ MeshCore extension installed successfully!")
        logger.info(f"   Extension: {MESHCORE_EXTENSION_PATH}")
        logger.info(f"   Data: {MESHCORE_DATA_PATH}")
        
        return True
    
    def _create_python_wrapper(self):
        """Create Python wrapper for MeshCore serial communication."""
        wrapper_path = MESHCORE_EXTENSION_PATH / "meshcore_wrapper.py"
        
        wrapper_code = '''"""
MeshCore Serial Wrapper for uDOS

Provides Python interface to MeshCore devices via serial connection.
"""

import serial
import json
from typing import Optional, Dict, List
from pathlib import Path

class MeshCoreDevice:
    """Interface to MeshCore device over serial."""
    
    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.connection: Optional[serial.Serial] = None
    
    def connect(self) -> bool:
        """Connect to MeshCore device."""
        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from device."""
        if self.connection and self.connection.is_open:
            self.connection.close()
    
    def send_message(self, message: str, recipient: str = "broadcast") -> bool:
        """Send message over mesh network."""
        if not self.connection or not self.connection.is_open:
            return False
        
        try:
            command = f"SEND {recipient} {message}\\n"
            self.connection.write(command.encode())
            return True
        except Exception as e:
            print(f"Send failed: {e}")
            return False
    
    def read_messages(self) -> List[Dict]:
        """Read incoming messages."""
        messages = []
        
        if not self.connection or not self.connection.is_open:
            return messages
        
        try:
            while self.connection.in_waiting:
                line = self.connection.readline().decode().strip()
                if line:
                    messages.append({"raw": line, "timestamp": None})
        except Exception as e:
            print(f"Read failed: {e}")
        
        return messages
    
    def get_node_info(self) -> Optional[Dict]:
        """Get information about this node."""
        # Implementation depends on MeshCore serial protocol
        pass
    
    def get_network_status(self) -> Optional[Dict]:
        """Get mesh network status."""
        # Implementation depends on MeshCore serial protocol
        pass
'''
        
        with open(wrapper_path, "w") as f:
            f.write(wrapper_code)
    
    def _create_default_config(self):
        """Create default MeshCore configuration."""
        config_path = MESHCORE_DATA_PATH / "config" / "meshcore.json"
        
        default_config = {
            "device": {
                "port": "/dev/ttyUSB0",
                "baudrate": 115200,
                "model": "heltec-v3"
            },
            "network": {
                "name": "uDOS-Mesh",
                "max_hops": 3,
                "auto_repeat": True
            },
            "features": {
                "companion_radio": False,
                "simple_repeater": True,
                "secure_chat": False
            },
            "integration": {
                "tile_sync": True,
                "location_broadcast": False,
                "emergency_beacon": True
            }
        }
        
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)
    
    def uninstall(self) -> bool:
        """Uninstall MeshCore extension.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Uninstalling MeshCore extension...")
        
        try:
            # Remove extension directory
            if MESHCORE_EXTENSION_PATH.exists():
                shutil.rmtree(MESHCORE_EXTENSION_PATH)
                logger.info("✅ Removed extension directory")
            
            # Ask before removing data
            print(f"\n⚠️  Data directory: {MESHCORE_DATA_PATH}")
            response = input("Remove data directory? (y/N): ").strip().lower()
            
            if response == "y":
                if MESHCORE_DATA_PATH.exists():
                    shutil.rmtree(MESHCORE_DATA_PATH)
                    logger.info("✅ Removed data directory")
            else:
                logger.info("ℹ️  Data directory preserved")
            
            logger.info("✅ MeshCore extension uninstalled")
            return True
            
        except Exception as e:
            logger.error(f"Uninstall failed: {e}")
            return False
    
    def print_status(self):
        """Print installation status."""
        status = self.check_status()
        
        print("\n" + "="*60)
        print("MeshCore Extension Status")
        print("="*60)
        
        print(f"\n📦 Repository:")
        print(f"   Cloned: {'✅' if status['cloned'] else '❌'} {MESHCORE_CLONE_PATH}")
        
        print(f"\n🔧 Installation:")
        print(f"   Extension: {'✅' if status['installed'] else '❌'} {MESHCORE_EXTENSION_PATH}")
        print(f"   Data Dir: {'✅' if status['data_dir'] else '❌'} {MESHCORE_DATA_PATH}")
        
        print(f"\n🛠️  Dependencies:")
        print(f"   PlatformIO: {'✅' if status['platformio'] else '❌'}")
        
        if status['examples']:
            print(f"\n📝 Available Examples ({len(status['examples'])}):")
            for example in status['examples']:
                print(f"   - {example}")
        
        if status['firmware']:
            print(f"\n💾 Prebuilt Firmware ({len(status['firmware'])}):")
            for fw in status['firmware']:
                print(f"   - {fw}")
        
        print(f"\n📚 Features:")
        for feature in EXTENSION_INFO['features']:
            print(f"   • {feature}")
        
        print(f"\n🎯 Use Cases:")
        for use_case in EXTENSION_INFO['use_cases']:
            print(f"   • {use_case}")
        
        print("\n" + "="*60 + "\n")


def main():
    """Main installer entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MeshCore Extension Installer for uDOS"
    )
    parser.add_argument(
        "action",
        nargs="?",
        default="check",
        choices=["check", "install", "uninstall"],
        help="Action to perform (default: check)"
    )
    
    args = parser.parse_args()
    installer = MeshCoreInstaller()
    
    if args.action == "check":
        installer.print_status()
    
    elif args.action == "install":
        installer.print_status()
        print("\n🔧 Starting installation...\n")
        success = installer.install()
        sys.exit(0 if success else 1)
    
    elif args.action == "uninstall":
        installer.print_status()
        print("\n⚠️  Starting uninstallation...\n")
        response = input("Confirm uninstall? (y/N): ").strip().lower()
        if response == "y":
            success = installer.uninstall()
            sys.exit(0 if success else 1)
        else:
            print("Cancelled.")
            sys.exit(0)


if __name__ == "__main__":
    main()
