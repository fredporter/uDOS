#!/usr/bin/env python3
"""
test_websocket_analytics.py - Test WebSocket real-time analytics (v1.2.7)

Tests the WebSocket integration for real-time webhook analytics:
- Server emits events when webhooks received
- Clients receive events via Socket.IO
- Dashboard updates in real-time

Usage:
    python dev/scripts/test_websocket_analytics.py

Requirements:
    - API server running on http://localhost:5001
    - Valid webhook configured in webhooks.json
    - python-socketio for client testing
"""

import sys
import os
import json
import time
import hmac
import hashlib
import requests
import socketio

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Configuration
API_BASE_URL = "http://localhost:5001/api"
SERVER_URL = "http://localhost:5001"
WEBHOOKS_CONFIG = os.path.join(project_root, "core/data/webhooks.json")


def load_test_webhook():
    """Load first webhook from config for testing."""
    try:
        with open(WEBHOOKS_CONFIG, 'r') as f:
            config = json.load(f)
            webhooks = config.get('webhooks', [])
            if not webhooks:
                print("❌ No webhooks configured in webhooks.json")
                return None
            return webhooks[0]
    except FileNotFoundError:
        print(f"❌ Webhooks config not found: {WEBHOOKS_CONFIG}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in {WEBHOOKS_CONFIG}")
        return None


def generate_signature(payload: dict, secret: str) -> str:
    """Generate HMAC signature for webhook payload."""
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    signature = hmac.new(
        secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


def send_test_webhook(webhook: dict) -> dict:
    """Send a test webhook event."""
    payload = {
        "action": "opened",
        "number": 42,
        "pull_request": {
            "id": 12345,
            "title": "WebSocket Test PR",
            "state": "open"
        },
        "repository": {
            "name": "udos-test",
            "full_name": "test/udos-test"
        },
        "sender": {
            "login": "testuser"
        }
    }

    # Generate signature
    signature = generate_signature(payload, webhook['secret'])

    # Send webhook to /api/webhooks/receive/<platform>
    platform = webhook['platform']
    url = f"{API_BASE_URL}/webhooks/receive/{platform}"
    headers = {
        'Content-Type': 'application/json',
        'X-Hub-Signature-256': signature,
        'X-GitHub-Event': 'pull_request',
        'X-Webhook-ID': webhook['id']  # Include webhook ID in header
    }

    print(f"\n📤 Sending webhook to {url}")
    response = requests.post(url, json=payload, headers=headers)

    return response.json()


def test_websocket_connection():
    """Test WebSocket connection and event reception."""
    print("\n🔌 Testing WebSocket Connection...")

    # Create Socket.IO client
    sio = socketio.Client()
    events_received = []

    @sio.event
    def connect():
        print("✅ WebSocket connected")

    @sio.event
    def disconnect():
        print("❌ WebSocket disconnected")

    @sio.on('webhook_event')
    def on_webhook_event(data):
        print(f"\n📨 Received webhook event:")
        print(json.dumps(data, indent=2))
        events_received.append(data)

    # Connect to server
    try:
        print(f"Connecting to {SERVER_URL}...")
        sio.connect(SERVER_URL, transports=['websocket'])

        # Load test webhook
        webhook = load_test_webhook()
        if not webhook:
            print("❌ Cannot test without webhook configuration")
            sio.disconnect()
            return False

        print(f"\n📋 Using webhook: {webhook['id']} ({webhook['platform']})")

        # Wait a moment for connection to establish
        time.sleep(1)

        # Send test webhook
        result = send_test_webhook(webhook)
        print(f"\n✅ Webhook response:")
        print(json.dumps(result, indent=2))

        # Wait for WebSocket event
        print("\n⏳ Waiting for WebSocket event (5 seconds)...")
        time.sleep(5)

        # Check results
        if events_received:
            print(f"\n✅ SUCCESS: Received {len(events_received)} WebSocket event(s)")
            for i, event in enumerate(events_received, 1):
                print(f"\nEvent {i}:")
                print(f"  - Event ID: {event.get('event_id')}")
                print(f"  - Platform: {event.get('platform')}")
                print(f"  - Event Type: {event.get('event_type')}")
                print(f"  - Status: {event.get('response_status')}")
                print(f"  - Execution Time: {event.get('execution_time_ms', 0):.2f}ms")
            return True
        else:
            print("\n❌ FAILED: No WebSocket events received")
            print("Make sure the API server is running with Flask-SocketIO enabled")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    finally:
        if sio.connected:
            sio.disconnect()


def test_multiple_clients():
    """Test WebSocket broadcasting to multiple clients."""
    print("\n🔗 Testing Multiple Clients...")

    clients = []
    events_received = {0: [], 1: [], 2: []}

    # Create 3 Socket.IO clients
    for i in range(3):
        client = socketio.Client()

        @client.event
        def connect():
            print(f"✅ Client {i} connected")

        @client.on('webhook_event')
        def on_event(data, client_id=i):
            events_received[client_id].append(data)
            print(f"📨 Client {client_id} received event: {data.get('event_id')}")

        clients.append(client)

    try:
        # Connect all clients
        for i, client in enumerate(clients):
            print(f"Connecting client {i}...")
            client.connect(SERVER_URL, transports=['websocket'])
            time.sleep(0.5)

        # Load test webhook
        webhook = load_test_webhook()
        if not webhook:
            return False

        # Send test webhook
        print(f"\n📤 Sending webhook...")
        result = send_test_webhook(webhook)

        # Wait for events
        print("\n⏳ Waiting for events (5 seconds)...")
        time.sleep(5)

        # Check results
        all_received = all(len(events) > 0 for events in events_received.values())

        if all_received:
            print(f"\n✅ SUCCESS: All {len(clients)} clients received events")
            for client_id, events in events_received.items():
                print(f"  - Client {client_id}: {len(events)} event(s)")
            return True
        else:
            print("\n❌ FAILED: Not all clients received events")
            for client_id, events in events_received.items():
                status = "✅" if events else "❌"
                print(f"  {status} Client {client_id}: {len(events)} event(s)")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    finally:
        # Disconnect all clients
        for client in clients:
            if client.connected:
                client.disconnect()


def check_server_health():
    """Check if API server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print(f"   Make sure server is running on {SERVER_URL}")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False


def main():
    """Run all WebSocket tests."""
    print("=" * 60)
    print("🧪 WebSocket Analytics Test Suite (v1.2.7)")
    print("=" * 60)

    # Check server
    if not check_server_health():
        print("\n❌ Cannot proceed without API server")
        print("Start the server with: python extensions/api/server.py")
        sys.exit(1)

    # Run tests
    results = {
        "WebSocket Connection": test_websocket_connection(),
        "Multiple Clients": test_multiple_clients()
    }

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())
    print("\n" + "=" * 60)

    if all_passed:
        print("✅ All tests passed!")
        print("\nWebSocket integration is working correctly.")
        print("Open analytics-demo.html in a browser to see real-time updates.")
    else:
        print("❌ Some tests failed")
        print("\nTroubleshooting:")
        print("1. Make sure API server is running with Flask-SocketIO")
        print("2. Check server logs for errors")
        print("3. Verify webhooks.json has valid configuration")
        print("4. Install python-socketio: pip install python-socketio[client]")

    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
