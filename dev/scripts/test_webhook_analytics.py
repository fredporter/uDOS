#!/usr/bin/env python3
"""
test_webhook_analytics.py - Test Webhook Analytics System (v1.2.6)

Tests event logging, analytics endpoints, and event replay functionality.
"""

import requests
import json
import time
import hmac
import hashlib
from typing import Dict, Any

API_BASE = 'http://localhost:5001/api'
TEST_SECRET = 'test_secret_key_12345'


class AnalyticsTestSuite:
    """Test suite for webhook analytics system."""

    def __init__(self):
        self.webhook_id = None
        self.event_ids = []
        self.passed = 0
        self.failed = 0

    def run_all_tests(self):
        """Run all analytics tests."""
        print("=" * 70)
        print("🧪 uDOS v1.2.6 - Webhook Analytics Test Suite")
        print("=" * 70)
        print()

        try:
            # Setup
            self.test_1_setup_webhook()

            # Event logging tests
            self.test_2_event_logging()
            self.test_3_multiple_events()

            # Analytics endpoints
            self.test_4_list_events()
            self.test_5_get_event_details()
            self.test_6_get_analytics()

            # Event replay
            self.test_7_replay_event()

            # Event deletion
            self.test_8_delete_event()

            # Cleanup
            self.test_9_cleanup()

        except Exception as e:
            print(f"❌ Test suite error: {e}")
            self.failed += 1

        # Summary
        print()
        print("=" * 70)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        print("=" * 70)

    def test_1_setup_webhook(self):
        """Test 1: Create test webhook."""
        print("Test 1: Setup test webhook...")

        try:
            res = requests.post(f'{API_BASE}/webhooks/register', json={
                'platform': 'github',
                'events': ['push', 'pull_request'],
                'actions': [
                    {
                        'type': 'workflow',
                        'workflow': 'test_workflow.upy',
                        'events': ['push']
                    }
                ]
            })

            data = res.json()
            assert data['status'] == 'success', "Failed to create webhook"

            self.webhook_id = data['webhook']['id']
            print(f"  ✓ Webhook created: {self.webhook_id}")

            # Update webhook with test secret
            import json as json_module
            webhook_file = 'memory/system/webhooks.json'
            with open(webhook_file, 'r') as f:
                webhooks = json_module.load(f)

            for webhook in webhooks:
                if webhook['id'] == self.webhook_id:
                    webhook['secret'] = TEST_SECRET

            with open(webhook_file, 'w') as f:
                json_module.dump(webhooks, f, indent=2)

            print(f"  ✓ Webhook secret configured")
            self.passed += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.failed += 1
            raise

    def test_2_event_logging(self):
        """Test 2: Verify events are logged."""
        print("\nTest 2: Event logging...")

        try:
            # Send webhook event
            payload = {
                'action': 'opened',
                'repository': {'name': 'test-repo'},
                'sender': {'login': 'testuser'}
            }

            payload_bytes = json.dumps(payload).encode()
            signature = 'sha256=' + hmac.new(
                TEST_SECRET.encode(),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()

            res = requests.post(
                f'{API_BASE}/webhooks/receive/github',
                json=payload,
                headers={'X-Hub-Signature-256': signature}
            )

            data = res.json()
            assert data['status'] == 'success', "Webhook receive failed"
            assert 'event_id' in data, "No event_id in response"

            event_id = data['event_id']
            self.event_ids.append(event_id)

            print(f"  ✓ Event logged: {event_id}")
            print(f"  ✓ Response includes event_id")

            self.passed += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.failed += 1

    def test_3_multiple_events(self):
        """Test 3: Log multiple events."""
        print("\nTest 3: Multiple events logging...")

        try:
            platforms = ['github', 'slack', 'notion']

            for platform in platforms:
                payload = {'test': 'data', 'platform': platform}
                payload_bytes = json.dumps(payload).encode()

                signature_header = {
                    'github': 'X-Hub-Signature-256',
                    'slack': 'X-Slack-Signature',
                    'notion': 'X-Notion-Signature'
                }[platform]

                signature = 'sha256=' + hmac.new(
                    TEST_SECRET.encode(),
                    payload_bytes,
                    hashlib.sha256
                ).hexdigest()

                res = requests.post(
                    f'{API_BASE}/webhooks/receive/{platform}',
                    json=payload,
                    headers={signature_header: signature}
                )

                if res.status_code == 200:
                    data = res.json()
                    if 'event_id' in data:
                        self.event_ids.append(data['event_id'])
                        print(f"  ✓ {platform} event logged")

            print(f"  ✓ Total events logged: {len(self.event_ids)}")
            self.passed += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.failed += 1

    def test_4_list_events(self):
        """Test 4: List events endpoint."""
        print("\nTest 4: List events...")

        try:
            res = requests.get(f'{API_BASE}/webhooks/events?limit=10')
            data = res.json()

            assert data['status'] == 'success', "List events failed"
            assert 'events' in data, "No events in response"
            assert len(data['events']) > 0, "No events returned"

            print(f"  ✓ Events retrieved: {data['count']}")
            print(f"  ✓ Limit: {data['limit']}, Offset: {data['offset']}")

            # Test filtering by platform
            res = requests.get(f'{API_BASE}/webhooks/events?platform=github')
            data = res.json()

            if data['status'] == 'success':
                print(f"  ✓ Platform filter works: {data['count']} github events")

            self.passed += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.failed += 1

    def test_5_get_event_details(self):
        """Test 5: Get event details."""
        print("\nTest 5: Get event details...")

        try:
            if not self.event_ids:
                print("  ⚠ No event IDs to test")
                return

            event_id = self.event_ids[0]
            res = requests.get(f'{API_BASE}/webhooks/events/{event_id}')
            data = res.json()

            assert data['status'] == 'success', "Get event failed"
            assert 'event' in data, "No event in response"

            event = data['event']
            assert event['id'] == event_id, "Event ID mismatch"
            assert 'platform' in event, "No platform in event"
            assert 'event_type' in event, "No event_type in event"
            assert 'execution_time_ms' in event, "No execution time in event"

            print(f"  ✓ Event details retrieved: {event_id}")
            print(f"  ✓ Platform: {event['platform']}")
            print(f"  ✓ Event type: {event['event_type']}")
            print(f"  ✓ Execution time: {event['execution_time_ms']:.2f}ms")

            self.passed += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.failed += 1

    def test_6_get_analytics(self):
        """Test 6: Get analytics."""
        print("\nTest 6: Get analytics...")

        try:
            res = requests.get(f'{API_BASE}/webhooks/analytics?days=7')
            data = res.json()

            assert data['status'] == 'success', "Get analytics failed"
            assert 'analytics' in data, "No analytics in response"

            analytics = data['analytics']
            assert 'total_events' in analytics, "No total_events"
            assert 'success_rate' in analytics, "No success_rate"
            assert 'avg_execution_time' in analytics, "No avg_execution_time"
            assert 'platforms' in analytics, "No platforms"

            print(f"  ✓ Analytics retrieved:")
            print(f"    Total events: {analytics['total_events']}")
            print(f"    Success rate: {analytics['success_rate']:.1f}%")
            print(f"    Avg execution time: {analytics['avg_execution_time']:.2f}ms")
            print(f"    Platforms: {', '.join(analytics['platforms'].keys())}")

            self.passed += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.failed += 1

    def test_7_replay_event(self):
        """Test 7: Replay event."""
        print("\nTest 7: Replay event...")

        try:
            if not self.event_ids:
                print("  ⚠ No event IDs to test")
                return

            event_id = self.event_ids[0]
            res = requests.post(f'{API_BASE}/webhooks/events/{event_id}/replay')
            data = res.json()

            assert data['status'] == 'success', "Replay failed"
            assert 'original_event' in data, "No original_event in response"
            assert 'actions_triggered' in data, "No actions_triggered"

            print(f"  ✓ Event replayed: {event_id}")
            print(f"  ✓ Actions triggered: {data['actions_triggered']}")

            self.passed += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.failed += 1

    def test_8_delete_event(self):
        """Test 8: Delete event."""
        print("\nTest 8: Delete event...")

        try:
            if len(self.event_ids) < 2:
                print("  ⚠ Not enough events to test deletion")
                return

            # Delete last event
            event_id = self.event_ids[-1]
            res = requests.delete(f'{API_BASE}/webhooks/events/{event_id}')
            data = res.json()

            assert data['status'] == 'success', "Delete failed"

            # Verify deletion
            res = requests.get(f'{API_BASE}/webhooks/events/{event_id}')
            data = res.json()

            assert res.status_code == 404, "Event still exists after deletion"

            print(f"  ✓ Event deleted: {event_id}")
            print(f"  ✓ Deletion verified")

            self.event_ids.remove(event_id)
            self.passed += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.failed += 1

    def test_9_cleanup(self):
        """Test 9: Cleanup test data."""
        print("\nTest 9: Cleanup...")

        try:
            # Delete test webhook
            if self.webhook_id:
                res = requests.delete(f'{API_BASE}/webhooks/{self.webhook_id}')
                data = res.json()

                if data['status'] == 'success':
                    print(f"  ✓ Test webhook deleted: {self.webhook_id}")
                else:
                    print(f"  ⚠ Failed to delete webhook: {data.get('message')}")

            # Clean up remaining events
            for event_id in self.event_ids:
                try:
                    requests.delete(f'{API_BASE}/webhooks/events/{event_id}')
                except:
                    pass

            print(f"  ✓ Cleanup complete")
            self.passed += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.failed += 1


def main():
    """Run the analytics test suite."""
    print("\nStarting webhook analytics tests...")
    print("Make sure the API server is running on port 5001\n")

    # Wait for server
    time.sleep(1)

    # Check server is running
    try:
        res = requests.get(f'{API_BASE}/health', timeout=2)
        if res.status_code != 200:
            print("❌ Server not responding. Start with: python extensions/api/server.py")
            return
    except:
        print("❌ Cannot connect to server. Start with: python extensions/api/server.py")
        return

    # Run tests
    suite = AnalyticsTestSuite()
    suite.run_all_tests()


if __name__ == '__main__':
    main()
