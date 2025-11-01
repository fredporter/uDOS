#!/usr/bin/env python3
"""
🎨 CSS Framework Showcase Launcher
Starts all CSS framework demo servers for uDOS
"""

import subprocess
import time
import signal
import sys
import os
from threading import Thread

# Server configurations
SERVERS = [
    {
        "name": "Classic.css (Mac OS 8.1)",
        "port": 8885,
        "directory": "classic-demo",
        "icon": "🖥️"
    },
    {
        "name": "NES.css (8-bit Nintendo)",
        "port": 8884,
        "directory": "nes-demo",
        "icon": "🎮"
    },
    {
        "name": "System.css (Mac System 6)",
        "port": 8883,
        "directory": "system-demo",
        "icon": "💾"
    },
    {
        "name": "After Dark CSS (Screensavers)",
        "port": 8882,
        "directory": "afterdark-demo",
        "icon": "✨"
    }
]

class FrameworkLauncher:
    def __init__(self):
        self.processes = []
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def start_server(self, server_config):
        """Start a single HTTP server"""
        try:
            demo_path = os.path.join(self.base_dir, server_config["directory"])
            if not os.path.exists(demo_path):
                print(f"❌ Directory not found: {demo_path}")
                return None

            cmd = [
                "python3", "-m", "http.server",
                str(server_config["port"]),
                "--directory", demo_path
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.base_dir
            )

            print(f"{server_config['icon']} {server_config['name']}")
            print(f"   📡 Server: http://localhost:{server_config['port']}")
            print(f"   📁 Directory: {server_config['directory']}")
            print()

            return process

        except Exception as e:
            print(f"❌ Failed to start {server_config['name']}: {e}")
            return None

    def start_all(self):
        """Start all CSS framework demo servers"""
        print("🎨 CSS Framework Showcase Launcher")
        print("=" * 50)
        print()

        for server_config in SERVERS:
            process = self.start_server(server_config)
            if process:
                self.processes.append(process)
                time.sleep(0.5)  # Brief delay between starts

        if self.processes:
            print("🚀 All servers started successfully!")
            print()
            print("🌐 Framework URLs:")
            for server_config in SERVERS:
                print(f"   {server_config['icon']} {server_config['name']}: http://localhost:{server_config['port']}")
            print()
            print("💡 Tips:")
            print("   • Press Ctrl+C to stop all servers")
            print("   • Each framework showcases different retro computing styles")
            print("   • Visit the URLs above to explore each framework")
            print()
            print("⏰ Servers running... (Press Ctrl+C to stop)")

        else:
            print("❌ No servers started successfully!")
            sys.exit(1)

    def stop_all(self):
        """Stop all running servers"""
        print("\n🛑 Stopping CSS framework servers...")

        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"⚠️  Error stopping process: {e}")

        print("✅ All servers stopped.")
        sys.exit(0)

    def run(self):
        """Main run loop"""
        # Setup signal handler for graceful shutdown
        def signal_handler(sig, frame):
            self.stop_all()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start all servers
        self.start_all()

        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_all()

def main():
    """Main entry point"""
    launcher = FrameworkLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
