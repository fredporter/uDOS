#!/usr/bin/env python3
"""
uNETWORK WebSocket Test Client
Tests WebSocket connectivity and real-time features
"""

import socketio
import time
import json
import sys

# Configuration
SERVER_URL = "http://127.0.0.1:8080"

class WebSocketTester:
    def __init__(self):
        self.sio = socketio.Client()
        self.connected = False
        self.messages_received = 0

        # Set up event handlers
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('response', self.on_response)
        self.sio.on('system_update', self.on_system_update)

    def on_connect(self):
        print("✅ Connected to WebSocket server")
        self.connected = True

    def on_disconnect(self):
        print("❌ Disconnected from WebSocket server")
        self.connected = False

    def on_response(self, data):
        print(f"📨 Response: {data}")
        self.messages_received += 1

    def on_system_update(self, data):
        print(f"🔄 System update: {data}")
        self.messages_received += 1

    def connect(self):
        """Connect to the WebSocket server"""
        try:
            print(f"Connecting to {SERVER_URL}...")
            self.sio.connect(SERVER_URL, wait_timeout=5)
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def test_ping(self):
        """Test basic ping/pong"""
        if not self.connected:
            return False

        print("\nTesting ping...")
        self.sio.emit('ping', {'timestamp': time.time()})
        time.sleep(1)
        return True

    def test_system_status(self):
        """Request system status via WebSocket"""
        if not self.connected:
            return False

        print("\nRequesting system status...")
        self.sio.emit('get_system_status')
        time.sleep(2)
        return True

    def test_echo(self):
        """Test echo functionality"""
        if not self.connected:
            return False

        print("\nTesting echo...")
        test_message = {"test": "Hello uDOS WebSocket!", "timestamp": time.time()}
        self.sio.emit('echo', test_message)
        time.sleep(1)
        return True

    def disconnect(self):
        """Disconnect from server"""
        if self.connected:
            self.sio.disconnect()

def main():
    """Run WebSocket tests"""
    print("uDOS WebSocket Test Client")
    print("=" * 40)

    tester = WebSocketTester()

    # Connect to server
    if not tester.connect():
        print("Cannot connect to WebSocket server")
        print("Make sure the uDOS server is running: ./start-server.sh")
        return 1

    try:
        # Wait a moment for connection to stabilize
        time.sleep(1)

        # Run tests
        tests = [
            ("Ping test", tester.test_ping),
            ("Echo test", tester.test_echo),
            ("System status test", tester.test_system_status),
        ]

        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            test_func()

        # Wait for any final messages
        time.sleep(2)

        print(f"\n📊 Test Summary:")
        print(f"  Messages received: {tester.messages_received}")
        print(f"  Connection stable: {'Yes' if tester.connected else 'No'}")

    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    finally:
        tester.disconnect()
        print("\nWebSocket test completed")

    return 0

if __name__ == "__main__":
    try:
        import socketio
    except ImportError:
        print("❌ python-socketio not installed")
        print("Install with: pip install python-socketio[client]")
        sys.exit(1)

    sys.exit(main())
