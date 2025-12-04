#!/usr/bin/env python3
"""
demo_webhook_analytics.py - Interactive Demo of Webhook Analytics (v1.2.6)

Demonstrates the webhook analytics system with real examples.
"""

import requests
import json
from datetime import datetime

API_BASE = 'http://localhost:5001/api'


def print_header(title):
    """Print section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_json(data):
    """Pretty print JSON."""
    print(json.dumps(data, indent=2))


def demo_list_webhooks():
    """Demo: List all webhooks."""
    print_header("1. List All Webhooks")

    res = requests.get(f'{API_BASE}/webhooks')
    data = res.json()

    if data['status'] == 'success':
        webhooks = data.get('webhooks', [])
        print(f"Found {len(webhooks)} webhook(s):")
        for wh in webhooks:
            print(f"  • {wh['id']} - {wh['platform']} ({len(wh.get('events', []))} events)")
    else:
        print(f"Error: {data.get('message')}")


def demo_create_test_webhook():
    """Demo: Create a test webhook."""
    print_header("2. Create Test Webhook")

    res = requests.post(f'{API_BASE}/webhooks/register', json={
        'platform': 'github',
        'events': ['push', 'pull_request', 'issues'],
        'actions': [
            {
                'type': 'workflow',
                'workflow': 'ci-test.upy',
                'events': ['push']
            },
            {
                'type': 'command',
                'command': 'NOTIFY "New PR created"',
                'events': ['pull_request']
            }
        ]
    })

    data = res.json()

    if data['status'] == 'success':
        webhook = data['webhook']
        print(f"✓ Webhook created:")
        print(f"  ID: {webhook['id']}")
        print(f"  Platform: {webhook['platform']}")
        print(f"  URL: {webhook['url']}")
        print(f"  Events: {', '.join(webhook['events'])}")
        print(f"  Actions: {len(webhook.get('actions', []))}")
        return webhook['id']
    else:
        print(f"✗ Error: {data.get('message')}")
        return None


def demo_test_webhook(webhook_id):
    """Demo: Test a webhook."""
    print_header("3. Test Webhook (Simulated Event)")

    if not webhook_id:
        print("⚠ No webhook ID provided")
        return

    res = requests.post(f'{API_BASE}/webhooks/test/{webhook_id}', json={
        'event': 'push',
        'test_data': {
            'ref': 'refs/heads/main',
            'repository': {'name': 'uDOS'},
            'commits': [
                {'message': 'Add webhook analytics', 'author': 'dev'}
            ]
        }
    })

    data = res.json()

    if data['status'] == 'success':
        print(f"✓ Test successful:")
        print(f"  Webhook: {data['webhook_id']}")
        print(f"  Event: {data['event']}")
        print(f"  Actions found: {data['actions_found']}")
        if data.get('actions'):
            for action in data['actions']:
                print(f"    - {action.get('type')}: {action.get('workflow') or action.get('command')}")
    else:
        print(f"✗ Error: {data.get('message')}")


def demo_list_events():
    """Demo: List webhook events."""
    print_header("4. List Webhook Events")

    res = requests.get(f'{API_BASE}/webhooks/events?limit=10')
    data = res.json()

    if data['status'] == 'success':
        events = data.get('events', [])
        print(f"Found {data['count']} event(s):")

        if events:
            for event in events[:5]:  # Show first 5
                print(f"\n  Event: {event['id']}")
                print(f"  Platform: {event['platform']}")
                print(f"  Type: {event['event_type']}")
                print(f"  Status: {event['response_status']}")
                print(f"  Time: {event['execution_time_ms']:.2f}ms")
                print(f"  Created: {event['created_at']}")
        else:
            print("  (No events logged yet)")
    else:
        print(f"✗ Error: {data.get('message')}")


def demo_analytics():
    """Demo: Get webhook analytics."""
    print_header("5. Webhook Analytics (Last 7 Days)")

    res = requests.get(f'{API_BASE}/webhooks/analytics?days=7')
    data = res.json()

    if data['status'] == 'success':
        analytics = data['analytics']
        print(f"📊 Metrics:")
        print(f"  Total Events: {analytics['total_events']}")
        print(f"  Successful: {analytics['success_count']}")
        print(f"  Failed: {analytics['error_count']}")
        print(f"  Success Rate: {analytics['success_rate']:.1f}%")
        print(f"  Avg Execution Time: {analytics['avg_execution_time_ms']:.2f}ms")

        if analytics.get('by_platform'):
            print(f"\n  By Platform:")
            for platform, count in analytics['by_platform'].items():
                print(f"    {platform}: {count}")

        if analytics.get('by_event_type'):
            print(f"\n  By Event Type:")
            for event_type, count in analytics['by_event_type'].items():
                print(f"    {event_type}: {count}")

        if analytics.get('recent_errors'):
            print(f"\n  Recent Errors:")
            for error in analytics['recent_errors'][:3]:
                print(f"    • {error.get('error')} ({error.get('platform')})")
    else:
        print(f"✗ Error: {data.get('message')}")


def demo_event_details(event_id):
    """Demo: Get event details."""
    print_header(f"6. Event Details: {event_id}")

    res = requests.get(f'{API_BASE}/webhooks/events/{event_id}')
    data = res.json()

    if data['status'] == 'success':
        event = data['event']
        print(f"Event Information:")
        print(f"  ID: {event['id']}")
        print(f"  Webhook: {event['webhook_id']}")
        print(f"  Platform: {event['platform']}")
        print(f"  Event Type: {event['event_type']}")
        print(f"  Status: {event['response_status']}")
        print(f"  Execution Time: {event['execution_time_ms']:.2f}ms")
        print(f"  Created: {event['created_at']}")

        if event.get('error'):
            print(f"  Error: {event['error']}")

        print(f"\n  Payload: {json.dumps(event.get('payload', {}), indent=4)[:200]}...")
    else:
        print(f"✗ Error: {data.get('message')}")


def demo_replay_event(event_id):
    """Demo: Replay an event."""
    print_header(f"7. Replay Event: {event_id}")

    res = requests.post(f'{API_BASE}/webhooks/events/{event_id}/replay')
    data = res.json()

    if data['status'] == 'success':
        print(f"✓ Event replayed successfully:")
        print(f"  Original Event: {event_id}")
        print(f"  Actions Triggered: {data['actions_triggered']}")

        if data.get('results'):
            print(f"\n  Results:")
            for result in data['results']:
                print(f"    - {result.get('action')}: {result.get('status')}")
    else:
        print(f"✗ Error: {data.get('message')}")


def demo_cleanup(webhook_id):
    """Demo: Cleanup test webhook."""
    print_header("8. Cleanup Test Webhook")

    if not webhook_id:
        print("⚠ No webhook to delete")
        return

    res = requests.delete(f'{API_BASE}/webhooks/{webhook_id}')
    data = res.json()

    if data['status'] == 'success':
        print(f"✓ Webhook deleted: {webhook_id}")
    else:
        print(f"✗ Error: {data.get('message')}")


def main():
    """Run the interactive demo."""
    print("\n" + "="*70)
    print("  🌀 uDOS v1.2.6 - Webhook Analytics Demo")
    print("="*70)
    print("\nThis demo showcases the webhook analytics system.")
    print("Server: http://localhost:5001")
    print()

    # Check server
    try:
        res = requests.get(f'{API_BASE}/health', timeout=2)
        if res.status_code != 200:
            print("❌ Server not responding. Start with:")
            print("   python extensions/api/server.py")
            return
    except:
        print("❌ Cannot connect to server. Start with:")
        print("   python extensions/api/server.py")
        return

    webhook_id = None
    event_id = None

    try:
        # Demo flow
        demo_list_webhooks()
        webhook_id = demo_create_test_webhook()
        demo_test_webhook(webhook_id)
        demo_list_events()
        demo_analytics()

        # Get first event for detail demo
        res = requests.get(f'{API_BASE}/webhooks/events?limit=1')
        data = res.json()
        if data.get('events'):
            event_id = data['events'][0]['id']
            demo_event_details(event_id)
            demo_replay_event(event_id)

        # Cleanup
        demo_cleanup(webhook_id)

        print_header("Demo Complete!")
        print("✨ Webhook analytics system is fully operational!")
        print("\nKey Features Demonstrated:")
        print("  ✓ Webhook management (create, list, test, delete)")
        print("  ✓ Event logging and history")
        print("  ✓ Analytics and metrics")
        print("  ✓ Event details and replay")
        print()

    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        if webhook_id:
            demo_cleanup(webhook_id)


if __name__ == '__main__':
    main()
