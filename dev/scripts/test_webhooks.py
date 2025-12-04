#!/usr/bin/env python3
"""
Webhook Integration Test Suite for uDOS v1.2.5

Tests all webhook endpoints, signature validation, and event processing.
"""

import json
import hmac
import hashlib
import requests
from datetime import datetime
from typing import Dict, List


class WebhookTester:
    """Test webhook integration."""

    def __init__(self, api_url: str = "http://localhost:5000"):
        self.api_url = api_url
        self.webhooks = []
        self.test_results = []

    def run_all_tests(self):
        """Run complete test suite."""
        print("\n" + "="*70)
        print("🧪 uDOS v1.2.5 - Webhook Integration Test Suite")
        print("="*70 + "\n")

        tests = [
            ("Server Health", self.test_server_health),
            ("GitHub Registration", self.test_github_registration),
            ("Slack Registration", self.test_slack_registration),
            ("List Webhooks", self.test_list_webhooks),
            ("GitHub Event", self.test_github_event),
            ("Slack Event", self.test_slack_event),
            ("Test Endpoint", self.test_webhook_test),
            ("Delete Webhook", self.test_delete_webhook),
        ]

        passed = 0
        failed = 0

        for name, test_func in tests:
            try:
                print(f"⏳ Running: {name}...")
                test_func()
                print(f"✅ PASS: {name}\n")
                passed += 1
                self.test_results.append({"test": name, "status": "PASS"})
            except AssertionError as e:
                print(f"❌ FAIL: {name}")
                print(f"   Error: {e}\n")
                failed += 1
                self.test_results.append({"test": name, "status": "FAIL", "error": str(e)})
            except Exception as e:
                print(f"⚠️  ERROR: {name}")
                print(f"   Exception: {e}\n")
                failed += 1
                self.test_results.append({"test": name, "status": "ERROR", "error": str(e)})

        print("="*70)
        print(f"📊 Test Results: {passed} passed, {failed} failed")
        print("="*70 + "\n")

        return passed, failed

    def test_server_health(self):
        """Test server is running."""
        response = requests.get(f"{self.api_url}/api/health")
        assert response.status_code == 200, "Server not responding"
        data = response.json()
        assert data['status'] == 'healthy', "Server not healthy"
        print(f"   Server version: {data.get('version')}")

    def test_github_registration(self):
        """Test GitHub webhook registration."""
        payload = {
            "platform": "github",
            "events": ["push", "pull_request"],
            "actions": [
                {
                    "event": "push",
                    "workflow": "knowledge-quality-scan",
                    "args": {}
                }
            ]
        }

        response = requests.post(
            f"{self.api_url}/api/webhooks/register",
            json=payload
        )

        assert response.status_code == 200, f"Registration failed: {response.status_code}"
        data = response.json()
        assert data['status'] == 'success', "Registration not successful"
        assert 'webhook' in data, "No webhook in response"

        webhook = data['webhook']
        self.webhooks.append(webhook)

        print(f"   Webhook ID: {webhook['id']}")
        print(f"   Secret: {webhook['secret'][:16]}...")

    def test_slack_registration(self):
        """Test Slack webhook registration."""
        payload = {
            "platform": "slack",
            "events": ["message", "slash_command"],
            "actions": []
        }

        response = requests.post(
            f"{self.api_url}/api/webhooks/register",
            json=payload
        )

        assert response.status_code == 200, "Slack registration failed"
        data = response.json()
        assert data['status'] == 'success', "Slack registration not successful"

        webhook = data['webhook']
        self.webhooks.append(webhook)

        print(f"   Slack Webhook ID: {webhook['id']}")

    def test_list_webhooks(self):
        """Test listing webhooks."""
        response = requests.get(f"{self.api_url}/api/webhooks/list")

        assert response.status_code == 200, "List webhooks failed"
        data = response.json()
        assert data['status'] == 'success', "List not successful"
        assert data['count'] >= 2, f"Expected at least 2 webhooks, got {data['count']}"

        print(f"   Total webhooks: {data['count']}")

        # Test platform filter
        response = requests.get(f"{self.api_url}/api/webhooks/list?platform=github")
        data = response.json()
        github_count = data['count']
        print(f"   GitHub webhooks: {github_count}")

    def test_github_event(self):
        """Test GitHub webhook event processing."""
        if not self.webhooks:
            raise AssertionError("No webhooks registered")

        # Find GitHub webhook
        github_wh = next((wh for wh in self.webhooks if wh['platform'] == 'github'), None)
        if not github_wh:
            raise AssertionError("No GitHub webhook found")

        # Create test payload
        payload = {
            "ref": "refs/heads/main",
            "repository": {"full_name": "test/repo"},
            "commits": [
                {
                    "id": "abc123",
                    "message": "Update knowledge guides",
                    "modified": ["knowledge/water/boiling.md"]
                }
            ]
        }

        payload_bytes = json.dumps(payload).encode()
        signature = self.create_github_signature(payload_bytes, github_wh['secret'])

        headers = {
            'Content-Type': 'application/json',
            'X-GitHub-Event': 'push',
            'X-Hub-Signature-256': signature
        }

        response = requests.post(
            f"{self.api_url}/api/webhooks/receive/github",
            data=payload_bytes,
            headers=headers
        )

        assert response.status_code == 200, f"GitHub event failed: {response.status_code}"
        data = response.json()
        assert data['status'] == 'success', f"GitHub event not processed: {data}"

        print(f"   Event processed: {data.get('event')}")
        print(f"   Actions triggered: {data.get('actions_triggered', 0)}")

    def test_slack_event(self):
        """Test Slack webhook event processing."""
        # Find Slack webhook
        slack_wh = next((wh for wh in self.webhooks if wh['platform'] == 'slack'), None)
        if not slack_wh:
            raise AssertionError("No Slack webhook found")

        # Slack URL verification
        payload = {
            "type": "url_verification",
            "challenge": "test_challenge_12345"
        }

        payload_str = json.dumps(payload)
        timestamp = str(int(datetime.now().timestamp()))
        signature = self.create_slack_signature(payload_str, timestamp, slack_wh['secret'])

        headers = {
            'Content-Type': 'application/json',
            'X-Slack-Signature': signature,
            'X-Slack-Request-Timestamp': timestamp
        }

        response = requests.post(
            f"{self.api_url}/api/webhooks/receive/slack",
            json=payload,
            headers=headers
        )

        assert response.status_code == 200, f"Slack verification failed: {response.status_code}"
        data = response.json()
        assert data.get('challenge') == 'test_challenge_12345', "Challenge not returned"

        print(f"   Slack verification: OK")

    def test_webhook_test(self):
        """Test webhook test endpoint."""
        if not self.webhooks:
            raise AssertionError("No webhooks to test")

        webhook = self.webhooks[0]

        response = requests.post(
            f"{self.api_url}/api/webhooks/test/{webhook['id']}",
            json={
                "event": "push",
                "test_data": {"test": True}
            }
        )

        assert response.status_code == 200, f"Webhook test failed: {response.status_code}"
        data = response.json()
        assert data['status'] == 'success', "Test not successful"

        print(f"   Test webhook: {webhook['id']}")
        print(f"   Actions found: {data.get('actions_found', 0)}")

    def test_delete_webhook(self):
        """Test webhook deletion."""
        if len(self.webhooks) < 2:
            raise AssertionError("Not enough webhooks to test deletion")

        # Delete second webhook (keep first for other tests)
        webhook = self.webhooks[1]

        response = requests.delete(
            f"{self.api_url}/api/webhooks/delete/{webhook['id']}"
        )

        assert response.status_code == 200, f"Deletion failed: {response.status_code}"
        data = response.json()
        assert data['status'] == 'success', "Deletion not successful"

        print(f"   Deleted webhook: {webhook['id']}")

        # Verify deletion
        response = requests.get(f"{self.api_url}/api/webhooks/list")
        data = response.json()
        remaining = [wh['id'] for wh in data['webhooks']]
        assert webhook['id'] not in remaining, "Webhook still exists after deletion"

    def create_github_signature(self, payload: bytes, secret: str) -> str:
        """Create GitHub webhook signature."""
        signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

    def create_slack_signature(self, body: str, timestamp: str, secret: str) -> str:
        """Create Slack webhook signature."""
        basestring = f"v0:{timestamp}:{body}"
        signature = hmac.new(
            secret.encode(),
            basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"v0={signature}"

    def cleanup(self):
        """Clean up test webhooks."""
        print("\n🧹 Cleaning up test webhooks...")
        for webhook in self.webhooks:
            try:
                requests.delete(f"{self.api_url}/api/webhooks/delete/{webhook['id']}")
                print(f"   ✓ Deleted {webhook['id']}")
            except Exception as e:
                print(f"   ⚠️  Failed to delete {webhook['id']}: {e}")


def main():
    """Run webhook integration tests."""
    tester = WebhookTester()

    try:
        passed, failed = tester.run_all_tests()

        # Optionally cleanup
        cleanup = input("\n🗑️  Clean up test webhooks? (y/N): ")
        if cleanup.lower() == 'y':
            tester.cleanup()

        print("\n" + "="*70)
        print("✅ Testing Complete!" if failed == 0 else f"⚠️  {failed} test(s) failed")
        print("="*70 + "\n")

        return 0 if failed == 0 else 1

    except Exception as e:
        print(f"\n❌ Test suite error: {e}\n")
        return 1


if __name__ == "__main__":
    exit(main())
