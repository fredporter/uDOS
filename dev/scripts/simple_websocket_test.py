#!/usr/bin/env python3
"""
simple_websocket_test.py - Simple WebSocket Event Test

Tests WebSocket event broadcasting by:
1. Connecting a Socket.IO client
2. Registering and triggering a webhook
3. Verifying the client receives the event

Usage:
    python dev/scripts/simple_websocket_test.py
"""

import sys
import os
import json
import time
import requests
import socketio

# Configuration
SERVER_URL = "http://localhost:5001"
API_BASE_URL = f"{SERVER_URL}/api"


def test_websocket_events():
    """Test WebSocket event reception."""
    print("=" * 60)
    print("🧪 Simple WebSocket Test")
    print("=" * 60)

    # Create Socket.IO client
    print("\n1. Connecting to WebSocket...")
    sio = socketio.Client()
    events_received = []

    @sio.event
    def connect():
        print("   ✅ Connected to WebSocket")

    @sio.event
    def disconnect():
        print("   ℹ️  Disconnected from WebSocket")

    @sio.on('webhook_event')
    def on_webhook_event(data):
        print(f"\n   📨 Received WebSocket event!")
        print(f"      Event ID: {data.get('event_id')}")
        print(f"      Platform: {data.get('platform')}")
        print(f"      Status: {data.get('response_status')}")
        print(f"      Time: {data.get('execution_time_ms')}ms")
        events_received.append(data)

    try:
        # Connect
        sio.connect(SERVER_URL, transports=['websocket'])
        time.sleep(1)

        # Register webhook
        print("\n2. Registering webhook...")
        webhook_data = {
            "name": "Test Webhook",
            "platform": "github",
            "events": ["push"],
            "secret": "test_secret_123"
        }
        
        response = requests.post(f"{API_BASE_URL}/webhooks/register", json=webhook_data)
        if response.status_code != 200:
            print(f"   ❌ Failed to register webhook: {response.text}")
            return False

        result = response.json()
        webhook = result.get('webhook', result)
        webhook_id = webhook.get('id')
        print(f"   ✅ Webhook registered: {webhook_id}")

        # Test webhook
        print("\n3. Triggering test event...")
        test_event = {
            "platform": "github",
            "event_type": "push",
            "webhook_id": webhook_id
        }

        response = requests.post(f"{API_BASE_URL}/webhooks/events/test", json=test_event)
        if response.status_code != 200:
            print(f"   ❌ Failed to trigger test event: {response.text}")
            return False

        result = response.json()
        print(f"   ✅ Test event created: {result.get('event_id')}")

        # Wait for WebSocket event
        print("\n4. Waiting for WebSocket event (3 seconds)...")
        time.sleep(3)

        # Check results
        if events_received:
            print(f"\n✅ SUCCESS! Received {len(events_received)} event(s)")
            return True
        else:
            print("\n❌ FAILED: No WebSocket events received")
            print("   Check server logs for errors")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if sio.connected:
            sio.disconnect()


if __name__ == '__main__':
    success = test_websocket_events()
    print("\n" + "=" * 60)
    
    if success:
        print("✅ WebSocket integration working!")
        print("\nNext: Open analytics-demo.html to see real-time updates")
    else:
        print("❌ WebSocket test failed")
        print("\nTroubleshooting:")
        print("  1. Check server logs: extensions/api/server.log")
        print("  2. Verify Flask-SocketIO is running")
        print("  3. Make sure port 5001 is accessible")
    
    print("=" * 60)
    sys.exit(0 if success else 1)
