"""
Test Suite for Feature 1.1.2.2: Command-Based Security Hardening
v1.1.2 Phase 1: Advanced Security & Roles

Tests command-based security model with explicit API/web access controls.
No implicit API/web calls - all must go through centralized security layer
with explicit command prefixes (API/OK/ASSIST, WEB/FETCH/CRAWL, OFFLINE/PROMPT).

Test Categories:
1. Security Layer Architecture (5 tests)
2. API Access Control (6 tests)
3. Web Access Control (6 tests)
4. Offline Prompt Management (5 tests)
5. Implicit Call Detection (5 tests)
6. Command Authorization (6 tests)
7. Security Rule Enforcement (5 tests)
8. Audit Trail (5 tests)
9. Rate Limiting (4 tests)
10. Security Policies (5 tests)
11. Violation Handling (4 tests)
12. Integration Scenarios (3 tests)

Total: 59 tests
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime, timedelta
from enum import Enum


class SecurityAction(Enum):
    """Security-controlled action types."""
    API_OK = "api/ok"
    API_ASSIST = "api/assist"
    WEB_FETCH = "web/fetch"
    WEB_CRAWL = "web/crawl"
    OFFLINE_PROMPT = "offline/prompt"


class SecurityViolation(Enum):
    """Security violation types."""
    IMPLICIT_API_CALL = "implicit_api_call"
    IMPLICIT_WEB_CALL = "implicit_web_call"
    UNAUTHORIZED_ACTION = "unauthorized_action"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_COMMAND = "invalid_command"


class CommandSecurityManager:
    """Centralized security layer for command execution."""
    
    def __init__(self):
        self.security_log = []
        self.violations = []
        self.rate_limits = {
            SecurityAction.API_OK: {"limit": 100, "window": 3600, "calls": []},
            SecurityAction.API_ASSIST: {"limit": 50, "window": 3600, "calls": []},
            SecurityAction.WEB_FETCH: {"limit": 200, "window": 3600, "calls": []},
            SecurityAction.WEB_CRAWL: {"limit": 10, "window": 3600, "calls": []}
        }
        self.security_policies = {}
        self.authorized_commands = {
            SecurityAction.API_OK: ["ok", "help", "query", "translate"],
            SecurityAction.API_ASSIST: ["assist", "code", "debug", "explain"],
            SecurityAction.WEB_FETCH: ["fetch", "download", "read"],
            SecurityAction.WEB_CRAWL: ["crawl", "spider", "index"],
            SecurityAction.OFFLINE_PROMPT: ["test", "validate", "develop"]
        }
        self.blocked_patterns = [
            "eval(",
            "exec(",
            "__import__",
            "compile("
        ]
        
    def authorize_action(self, action, command, context=None):
        """Authorize security-controlled action."""
        if not isinstance(action, SecurityAction):
            raise ValueError(f"Invalid security action: {action}")
        
        # Check if command is authorized for this action
        if command not in self.authorized_commands.get(action, []):
            self._log_violation(
                SecurityViolation.UNAUTHORIZED_ACTION,
                {"action": action.value, "command": command}
            )
            return False
        
        # Check rate limits
        if not self._check_rate_limit(action):
            self._log_violation(
                SecurityViolation.RATE_LIMIT_EXCEEDED,
                {"action": action.value, "command": command}
            )
            return False
        
        # Check security policies
        if not self._check_policies(action, command, context):
            return False
        
        # Log authorized action
        self._log_security_event("action_authorized", {
            "action": action.value,
            "command": command,
            "context": context
        })
        
        # Record for rate limiting
        self._record_action(action)
        
        return True
    
    def execute_api_call(self, operation, prompt, context=None):
        """Execute API call with explicit authorization."""
        # Determine action type
        if operation == "ok":
            action = SecurityAction.API_OK
        elif operation == "assist":
            action = SecurityAction.API_ASSIST
        else:
            raise ValueError(f"Invalid API operation: {operation}")
        
        # Authorize
        if not self.authorize_action(action, operation, context):
            raise PermissionError(f"API call not authorized: {operation}")
        
        # Execute (mock)
        result = {
            "action": action.value,
            "operation": operation,
            "prompt": prompt,
            "response": f"API response for: {prompt[:50]}...",
            "timestamp": datetime.now().isoformat()
        }
        
        self._log_security_event("api_call_executed", {
            "operation": operation,
            "prompt_length": len(prompt)
        })
        
        return result
    
    def execute_web_call(self, operation, url, context=None):
        """Execute web call with explicit authorization."""
        # Determine action type
        if operation == "fetch":
            action = SecurityAction.WEB_FETCH
        elif operation == "crawl":
            action = SecurityAction.WEB_CRAWL
        else:
            raise ValueError(f"Invalid web operation: {operation}")
        
        # Authorize
        if not self.authorize_action(action, operation, context):
            raise PermissionError(f"Web call not authorized: {operation}")
        
        # Execute (mock)
        result = {
            "action": action.value,
            "operation": operation,
            "url": url,
            "content": f"Content from {url}",
            "timestamp": datetime.now().isoformat()
        }
        
        self._log_security_event("web_call_executed", {
            "operation": operation,
            "url": url
        })
        
        return result
    
    def manage_offline_prompt(self, operation, prompt_data):
        """Manage offline prompt with authorization."""
        action = SecurityAction.OFFLINE_PROMPT
        
        # Authorize
        if not self.authorize_action(action, operation, prompt_data):
            raise PermissionError(f"Offline prompt operation not authorized: {operation}")
        
        # Execute (mock)
        result = {
            "action": action.value,
            "operation": operation,
            "prompt_id": prompt_data.get("id", "new"),
            "timestamp": datetime.now().isoformat()
        }
        
        self._log_security_event("offline_prompt_managed", {
            "operation": operation,
            "prompt_id": result["prompt_id"]
        })
        
        return result
    
    def detect_implicit_call(self, code_or_command):
        """Detect implicit API/web calls in code."""
        violations = []
        
        # Check for API call patterns
        api_patterns = ["openai.", "anthropic.", "google.ai", "requests.post"]
        for pattern in api_patterns:
            if pattern in code_or_command:
                violations.append({
                    "type": SecurityViolation.IMPLICIT_API_CALL,
                    "pattern": pattern,
                    "location": code_or_command.find(pattern)
                })
        
        # Check for web call patterns
        web_patterns = ["urllib.request", "requests.get", "http.client", "selenium"]
        for pattern in web_patterns:
            if pattern in code_or_command:
                violations.append({
                    "type": SecurityViolation.IMPLICIT_WEB_CALL,
                    "pattern": pattern,
                    "location": code_or_command.find(pattern)
                })
        
        # Log violations
        for violation in violations:
            self._log_violation(violation["type"], violation)
        
        return violations
    
    def validate_command(self, command):
        """Validate command for security issues."""
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if pattern in command:
                self._log_violation(
                    SecurityViolation.INVALID_COMMAND,
                    {"pattern": pattern, "command": command}
                )
                return False
        
        return True
    
    def set_security_policy(self, action, policy):
        """Set security policy for action."""
        if not isinstance(action, SecurityAction):
            raise ValueError(f"Invalid action: {action}")
        
        self.security_policies[action] = policy
        
        self._log_security_event("policy_set", {
            "action": action.value,
            "policy": policy
        })
    
    def get_security_policy(self, action):
        """Get security policy for action."""
        return self.security_policies.get(action, {})
    
    def _check_rate_limit(self, action):
        """Check if action is within rate limit."""
        if action not in self.rate_limits:
            return True
        
        config = self.rate_limits[action]
        now = datetime.now()
        window_start = now - timedelta(seconds=config["window"])
        
        # Clean old calls
        config["calls"] = [
            call for call in config["calls"]
            if call > window_start
        ]
        
        # Check limit
        return len(config["calls"]) < config["limit"]
    
    def _record_action(self, action):
        """Record action for rate limiting."""
        if action in self.rate_limits:
            self.rate_limits[action]["calls"].append(datetime.now())
    
    def _check_policies(self, action, command, context):
        """Check security policies."""
        policy = self.security_policies.get(action, {})
        
        # Check required context
        if policy.get("require_context") and not context:
            self._log_violation(
                SecurityViolation.UNAUTHORIZED_ACTION,
                {"action": action.value, "reason": "missing_context"}
            )
            return False
        
        # Check allowed domains (for web operations)
        if "allowed_domains" in policy and context:
            url = context.get("url", "")
            domain = url.split("//")[1].split("/")[0] if "//" in url else url
            if domain not in policy["allowed_domains"]:
                self._log_violation(
                    SecurityViolation.UNAUTHORIZED_ACTION,
                    {"action": action.value, "reason": "domain_not_allowed", "domain": domain}
                )
                return False
        
        return True
    
    def _log_security_event(self, event_type, data):
        """Log security event."""
        entry = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.security_log.append(entry)
    
    def _log_violation(self, violation_type, data):
        """Log security violation."""
        entry = {
            "type": violation_type.value if isinstance(violation_type, SecurityViolation) else violation_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.violations.append(entry)
        self._log_security_event("violation", entry)
    
    def get_security_log(self, filter_type=None):
        """Get security log with optional filtering."""
        if filter_type:
            return [
                entry for entry in self.security_log
                if entry["type"] == filter_type
            ]
        return self.security_log.copy()
    
    def get_violations(self, filter_type=None):
        """Get violations with optional filtering."""
        if filter_type:
            violation_value = filter_type.value if isinstance(filter_type, SecurityViolation) else filter_type
            return [
                entry for entry in self.violations
                if entry["type"] == violation_value
            ]
        return self.violations.copy()
    
    def get_rate_limit_status(self, action):
        """Get rate limit status for action."""
        if action not in self.rate_limits:
            return {"limited": False}
        
        config = self.rate_limits[action]
        now = datetime.now()
        window_start = now - timedelta(seconds=config["window"])
        
        # Count calls in current window
        recent_calls = [
            call for call in config["calls"]
            if call > window_start
        ]
        
        return {
            "limited": True,
            "limit": config["limit"],
            "window_seconds": config["window"],
            "current_count": len(recent_calls),
            "remaining": max(0, config["limit"] - len(recent_calls)),
            "reset_at": (window_start + timedelta(seconds=config["window"])).isoformat()
        }
    
    def reset_rate_limits(self):
        """Reset all rate limits (for testing/admin)."""
        for action in self.rate_limits:
            self.rate_limits[action]["calls"] = []
        
        self._log_security_event("rate_limits_reset", {})


class TestSecurityLayerArchitecture(unittest.TestCase):
    """Test security layer architecture."""
    
    def setUp(self):
        self.security = CommandSecurityManager()
    
    def test_security_action_types(self):
        """Test security action enumeration."""
        self.assertEqual(SecurityAction.API_OK.value, "api/ok")
        self.assertEqual(SecurityAction.WEB_FETCH.value, "web/fetch")
        self.assertEqual(SecurityAction.OFFLINE_PROMPT.value, "offline/prompt")
    
    def test_centralized_authorization(self):
        """Test all actions go through central authorization."""
        result = self.security.authorize_action(
            SecurityAction.API_OK,
            "help",
            {"user": "test"}
        )
        self.assertTrue(result)
        
        # Check it was logged
        log = self.security.get_security_log("action_authorized")
        self.assertEqual(len(log), 1)
    
    def test_authorized_commands_registry(self):
        """Test authorized commands registry."""
        api_commands = self.security.authorized_commands[SecurityAction.API_OK]
        self.assertIn("help", api_commands)
        self.assertIn("query", api_commands)
    
    def test_security_log_structure(self):
        """Test security log entry structure."""
        self.security.authorize_action(SecurityAction.API_OK, "help")
        log = self.security.get_security_log()
        
        entry = log[0]
        self.assertIn("type", entry)
        self.assertIn("timestamp", entry)
        self.assertIn("data", entry)
    
    def test_violation_tracking(self):
        """Test violation tracking."""
        self.security.detect_implicit_call("openai.ChatCompletion.create()")
        violations = self.security.get_violations()
        
        self.assertGreater(len(violations), 0)
        self.assertEqual(violations[0]["type"], SecurityViolation.IMPLICIT_API_CALL.value)


class TestAPIAccessControl(unittest.TestCase):
    """Test API access control."""
    
    def setUp(self):
        self.security = CommandSecurityManager()
    
    def test_explicit_api_ok_call(self):
        """Test explicit API/OK call."""
        result = self.security.execute_api_call("ok", "What is 2+2?")
        self.assertEqual(result["operation"], "ok")
        self.assertIn("response", result)
    
    def test_explicit_api_assist_call(self):
        """Test explicit API/ASSIST call."""
        result = self.security.execute_api_call("assist", "Help me debug this code")
        self.assertEqual(result["operation"], "assist")
        self.assertEqual(result["action"], "api/assist")
    
    def test_unauthorized_api_command(self):
        """Test unauthorized API command rejected."""
        # Remove 'ok' from authorized commands temporarily
        original = self.security.authorized_commands[SecurityAction.API_OK].copy()
        self.security.authorized_commands[SecurityAction.API_OK] = []
        
        with self.assertRaises(PermissionError):
            self.security.execute_api_call("ok", "test prompt")
        
        # Restore
        self.security.authorized_commands[SecurityAction.API_OK] = original
    
    def test_api_call_logging(self):
        """Test API calls are logged."""
        self.security.execute_api_call("ok", "test prompt")
        log = self.security.get_security_log("api_call_executed")
        
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["data"]["operation"], "ok")
    
    def test_api_operation_validation(self):
        """Test invalid API operation rejected."""
        with self.assertRaises(ValueError):
            self.security.execute_api_call("invalid", "test")
    
    def test_api_authorization_required(self):
        """Test API calls require authorization."""
        # Remove authorization for 'help'
        self.security.authorized_commands[SecurityAction.API_OK] = []
        
        with self.assertRaises(PermissionError):
            self.security.execute_api_call("ok", "help me")


class TestWebAccessControl(unittest.TestCase):
    """Test web access control."""
    
    def setUp(self):
        self.security = CommandSecurityManager()
    
    def test_explicit_web_fetch(self):
        """Test explicit WEB/FETCH call."""
        result = self.security.execute_web_call("fetch", "https://example.com")
        self.assertEqual(result["operation"], "fetch")
        self.assertIn("content", result)
    
    def test_explicit_web_crawl(self):
        """Test explicit WEB/CRAWL call."""
        result = self.security.execute_web_call("crawl", "https://example.com")
        self.assertEqual(result["operation"], "crawl")
        self.assertEqual(result["action"], "web/crawl")
    
    def test_unauthorized_web_command(self):
        """Test unauthorized web command rejected."""
        # Remove 'fetch' from authorized commands temporarily
        original = self.security.authorized_commands[SecurityAction.WEB_FETCH].copy()
        self.security.authorized_commands[SecurityAction.WEB_FETCH] = []
        
        with self.assertRaises(PermissionError):
            self.security.execute_web_call("fetch", "https://example.com")
        
        # Restore
        self.security.authorized_commands[SecurityAction.WEB_FETCH] = original
    
    def test_web_call_logging(self):
        """Test web calls are logged."""
        self.security.execute_web_call("fetch", "https://example.com")
        log = self.security.get_security_log("web_call_executed")
        
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["data"]["operation"], "fetch")
    
    def test_web_operation_validation(self):
        """Test invalid web operation rejected."""
        with self.assertRaises(ValueError):
            self.security.execute_web_call("invalid", "https://example.com")
    
    def test_web_domain_policy(self):
        """Test web domain policy enforcement."""
        # Set domain policy
        self.security.set_security_policy(SecurityAction.WEB_FETCH, {
            "allowed_domains": ["example.com", "test.com"]
        })
        
        # Should fail for unlisted domain
        with self.assertRaises(PermissionError):
            self.security.execute_web_call("fetch", "https://forbidden.com", {"url": "https://forbidden.com"})


class TestOfflinePromptManagement(unittest.TestCase):
    """Test offline prompt management."""
    
    def setUp(self):
        self.security = CommandSecurityManager()
    
    def test_offline_prompt_test(self):
        """Test OFFLINE/PROMPT/TEST operation."""
        result = self.security.manage_offline_prompt("test", {"id": "prompt_1", "content": "test"})
        self.assertEqual(result["operation"], "test")
        self.assertEqual(result["action"], "offline/prompt")
    
    def test_offline_prompt_validate(self):
        """Test OFFLINE/PROMPT/VALIDATE operation."""
        result = self.security.manage_offline_prompt("validate", {"id": "prompt_2"})
        self.assertEqual(result["operation"], "validate")
    
    def test_offline_prompt_develop(self):
        """Test OFFLINE/PROMPT/DEVELOP operation."""
        result = self.security.manage_offline_prompt("develop", {"id": "new"})
        self.assertIn("prompt_id", result)
    
    def test_offline_prompt_logging(self):
        """Test offline prompt operations are logged."""
        self.security.manage_offline_prompt("test", {"id": "test"})
        log = self.security.get_security_log("offline_prompt_managed")
        
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["data"]["operation"], "test")
    
    def test_unauthorized_offline_operation(self):
        """Test unauthorized offline operation rejected."""
        with self.assertRaises(PermissionError):
            self.security.manage_offline_prompt("unauthorized", {})


class TestImplicitCallDetection(unittest.TestCase):
    """Test detection of implicit API/web calls."""
    
    def setUp(self):
        self.security = CommandSecurityManager()
    
    def test_detect_implicit_openai_call(self):
        """Test detection of implicit OpenAI call."""
        code = "import openai\nopenai.ChatCompletion.create()"
        violations = self.security.detect_implicit_call(code)
        
        self.assertGreater(len(violations), 0)
        self.assertEqual(violations[0]["type"], SecurityViolation.IMPLICIT_API_CALL)
    
    def test_detect_implicit_requests_call(self):
        """Test detection of implicit requests call."""
        code = "import requests\nrequests.get('http://api.com')"
        violations = self.security.detect_implicit_call(code)
        
        self.assertGreater(len(violations), 0)
        self.assertEqual(violations[0]["type"], SecurityViolation.IMPLICIT_WEB_CALL)
    
    def test_detect_multiple_violations(self):
        """Test detection of multiple violations."""
        code = "import openai\nimport requests\nopenai.call()\nrequests.get()"
        violations = self.security.detect_implicit_call(code)
        
        self.assertEqual(len(violations), 2)
    
    def test_clean_code_no_violations(self):
        """Test clean code has no violations."""
        code = "def add(a, b):\n    return a + b"
        violations = self.security.detect_implicit_call(code)
        
        self.assertEqual(len(violations), 0)
    
    def test_violations_logged(self):
        """Test violations are logged."""
        self.security.detect_implicit_call("openai.call()")
        violations = self.security.get_violations(SecurityViolation.IMPLICIT_API_CALL)
        
        self.assertGreater(len(violations), 0)


class TestCommandAuthorization(unittest.TestCase):
    """Test command authorization."""
    
    def setUp(self):
        self.security = CommandSecurityManager()
    
    def test_authorize_valid_command(self):
        """Test authorizing valid command."""
        result = self.security.authorize_action(SecurityAction.API_OK, "help")
        self.assertTrue(result)
    
    def test_reject_invalid_command(self):
        """Test rejecting invalid command."""
        result = self.security.authorize_action(SecurityAction.API_OK, "invalid")
        self.assertFalse(result)
    
    def test_command_validation(self):
        """Test command validation."""
        self.assertTrue(self.security.validate_command("safe_command()"))
        self.assertFalse(self.security.validate_command("eval('malicious')"))
    
    def test_blocked_patterns(self):
        """Test blocked code patterns."""
        patterns = ["eval(", "exec(", "__import__", "compile("]
        for pattern in patterns:
            self.assertFalse(self.security.validate_command(pattern + "code"))
    
    def test_authorization_logging(self):
        """Test authorization attempts are logged."""
        self.security.authorize_action(SecurityAction.API_OK, "help")
        log = self.security.get_security_log("action_authorized")
        
        self.assertGreater(len(log), 0)
    
    def test_invalid_action_type(self):
        """Test invalid action type rejected."""
        with self.assertRaises(ValueError):
            self.security.authorize_action("invalid", "command")


class TestSecurityRuleEnforcement(unittest.TestCase):
    """Test security rule enforcement."""
    
    def setUp(self):
        self.security = CommandSecurityManager()
    
    def test_set_security_policy(self):
        """Test setting security policy."""
        policy = {"require_context": True}
        self.security.set_security_policy(SecurityAction.API_OK, policy)
        
        retrieved = self.security.get_security_policy(SecurityAction.API_OK)
        self.assertEqual(retrieved, policy)
    
    def test_enforce_context_requirement(self):
        """Test enforcing context requirement."""
        self.security.set_security_policy(SecurityAction.API_OK, {"require_context": True})
        
        # Should fail without context
        result = self.security.authorize_action(SecurityAction.API_OK, "help")
        self.assertFalse(result)
        
        # Should succeed with context
        result = self.security.authorize_action(SecurityAction.API_OK, "help", {"user": "test"})
        self.assertTrue(result)
    
    def test_enforce_domain_whitelist(self):
        """Test enforcing domain whitelist."""
        self.security.set_security_policy(SecurityAction.WEB_FETCH, {
            "allowed_domains": ["example.com"]
        })
        
        # Should fail for non-whitelisted domain
        result = self.security.authorize_action(
            SecurityAction.WEB_FETCH,
            "fetch",
            {"url": "https://forbidden.com"}
        )
        self.assertFalse(result)
    
    def test_policy_logging(self):
        """Test policy changes are logged."""
        self.security.set_security_policy(SecurityAction.API_OK, {})
        log = self.security.get_security_log("policy_set")
        
        self.assertEqual(len(log), 1)
    
    def test_invalid_policy_action(self):
        """Test invalid policy action rejected."""
        with self.assertRaises(ValueError):
            self.security.set_security_policy("invalid", {})


class TestAuditTrail(unittest.TestCase):
    """Test comprehensive audit trail."""
    
    def setUp(self):
        self.security = CommandSecurityManager()
    
    def test_all_actions_logged(self):
        """Test all actions are logged."""
        self.security.execute_api_call("ok", "test")
        self.security.execute_web_call("fetch", "https://example.com")
        
        log = self.security.get_security_log()
        self.assertGreaterEqual(len(log), 4)  # 2 authorizations + 2 executions
    
    def test_log_filtering(self):
        """Test filtering audit log by type."""
        self.security.execute_api_call("ok", "test1")
        self.security.execute_api_call("ok", "test2")
        
        api_log = self.security.get_security_log("api_call_executed")
        self.assertEqual(len(api_log), 2)
    
    def test_violation_filtering(self):
        """Test filtering violations by type."""
        self.security.detect_implicit_call("openai.call()")
        self.security.detect_implicit_call("requests.get()")
        
        api_violations = self.security.get_violations(SecurityViolation.IMPLICIT_API_CALL)
        web_violations = self.security.get_violations(SecurityViolation.IMPLICIT_WEB_CALL)
        
        self.assertGreater(len(api_violations), 0)
        self.assertGreater(len(web_violations), 0)
    
    def test_timestamp_recording(self):
        """Test timestamps are recorded."""
        self.security.execute_api_call("ok", "test")
        log = self.security.get_security_log()
        
        for entry in log:
            self.assertIn("timestamp", entry)
            datetime.fromisoformat(entry["timestamp"])
    
    def test_audit_immutability(self):
        """Test audit log returns copies."""
        log1 = self.security.get_security_log()
        log1.append({"fake": "entry"})
        log2 = self.security.get_security_log()
        
        self.assertNotEqual(len(log1), len(log2))


class TestRateLimiting(unittest.TestCase):
    """Test rate limiting."""
    
    def setUp(self):
        self.security = CommandSecurityManager()
    
    def test_rate_limit_enforcement(self):
        """Test rate limits are enforced."""
        # Set low limit for testing
        self.security.rate_limits[SecurityAction.API_OK]["limit"] = 2
        
        # Should succeed twice
        self.assertTrue(self.security.authorize_action(SecurityAction.API_OK, "help"))
        self.assertTrue(self.security.authorize_action(SecurityAction.API_OK, "help"))
        
        # Should fail on third
        self.assertFalse(self.security.authorize_action(SecurityAction.API_OK, "help"))
    
    def test_rate_limit_status(self):
        """Test getting rate limit status."""
        status = self.security.get_rate_limit_status(SecurityAction.API_OK)
        
        self.assertTrue(status["limited"])
        self.assertEqual(status["limit"], 100)
        self.assertIn("remaining", status)
    
    def test_rate_limit_reset(self):
        """Test rate limit reset."""
        self.security.authorize_action(SecurityAction.API_OK, "help")
        self.security.reset_rate_limits()
        
        status = self.security.get_rate_limit_status(SecurityAction.API_OK)
        self.assertEqual(status["current_count"], 0)
    
    def test_rate_limit_violation_logged(self):
        """Test rate limit violations are logged."""
        self.security.rate_limits[SecurityAction.API_OK]["limit"] = 1
        self.security.authorize_action(SecurityAction.API_OK, "help")
        self.security.authorize_action(SecurityAction.API_OK, "help")
        
        violations = self.security.get_violations(SecurityViolation.RATE_LIMIT_EXCEEDED)
        self.assertGreater(len(violations), 0)


class TestSecurityPolicies(unittest.TestCase):
    """Test security policy system."""
    
    def setUp(self):
        self.security = CommandSecurityManager()
    
    def test_default_no_policy(self):
        """Test default is no policy restrictions."""
        result = self.security.authorize_action(SecurityAction.API_OK, "help")
        self.assertTrue(result)
    
    def test_policy_context_requirement(self):
        """Test policy requiring context."""
        self.security.set_security_policy(SecurityAction.API_OK, {"require_context": True})
        
        # Without context
        self.assertFalse(self.security.authorize_action(SecurityAction.API_OK, "help"))
        
        # With context
        self.assertTrue(self.security.authorize_action(SecurityAction.API_OK, "help", {"data": "test"}))
    
    def test_policy_domain_restriction(self):
        """Test policy domain restrictions."""
        self.security.set_security_policy(SecurityAction.WEB_FETCH, {
            "allowed_domains": ["safe.com", "trusted.org"]
        })
        
        # Allowed domain
        result = self.security.authorize_action(
            SecurityAction.WEB_FETCH,
            "fetch",
            {"url": "https://safe.com/page"}
        )
        self.assertTrue(result)
    
    def test_multiple_policies(self):
        """Test multiple policies can coexist."""
        self.security.set_security_policy(SecurityAction.API_OK, {"require_context": True})
        self.security.set_security_policy(SecurityAction.WEB_FETCH, {"allowed_domains": ["example.com"]})
        
        api_policy = self.security.get_security_policy(SecurityAction.API_OK)
        web_policy = self.security.get_security_policy(SecurityAction.WEB_FETCH)
        
        self.assertTrue(api_policy["require_context"])
        self.assertIn("example.com", web_policy["allowed_domains"])
    
    def test_policy_override(self):
        """Test policy can be overridden."""
        self.security.set_security_policy(SecurityAction.API_OK, {"rule": "old"})
        self.security.set_security_policy(SecurityAction.API_OK, {"rule": "new"})
        
        policy = self.security.get_security_policy(SecurityAction.API_OK)
        self.assertEqual(policy["rule"], "new")


class TestViolationHandling(unittest.TestCase):
    """Test security violation handling."""
    
    def setUp(self):
        self.security = CommandSecurityManager()
    
    def test_unauthorized_action_violation(self):
        """Test unauthorized action creates violation."""
        self.security.authorize_action(SecurityAction.API_OK, "unauthorized")
        violations = self.security.get_violations(SecurityViolation.UNAUTHORIZED_ACTION)
        
        self.assertGreater(len(violations), 0)
    
    def test_rate_limit_violation(self):
        """Test rate limit creates violation."""
        self.security.rate_limits[SecurityAction.API_OK]["limit"] = 1
        self.security.authorize_action(SecurityAction.API_OK, "help")
        self.security.authorize_action(SecurityAction.API_OK, "help")
        
        violations = self.security.get_violations(SecurityViolation.RATE_LIMIT_EXCEEDED)
        self.assertGreater(len(violations), 0)
    
    def test_invalid_command_violation(self):
        """Test invalid command creates violation."""
        self.security.validate_command("eval('bad')")
        violations = self.security.get_violations(SecurityViolation.INVALID_COMMAND)
        
        self.assertGreater(len(violations), 0)
    
    def test_violation_data_capture(self):
        """Test violations capture relevant data."""
        self.security.detect_implicit_call("openai.call()")
        violations = self.security.get_violations()
        
        self.assertIn("pattern", violations[0]["data"])
        self.assertIn("location", violations[0]["data"])


class TestIntegrationScenarios(unittest.TestCase):
    """Test end-to-end security scenarios."""
    
    def setUp(self):
        self.security = CommandSecurityManager()
    
    def test_secure_api_workflow(self):
        """Test secure API usage workflow."""
        # 1. Authorize
        authorized = self.security.authorize_action(SecurityAction.API_OK, "help")
        self.assertTrue(authorized)
        
        # 2. Execute
        result = self.security.execute_api_call("ok", "What is Python?")
        self.assertIn("response", result)
        
        # 3. Verify logging
        log = self.security.get_security_log()
        self.assertGreater(len(log), 0)
    
    def test_security_violation_workflow(self):
        """Test security violation detection workflow."""
        # 1. Detect implicit call
        code = "import openai\nopenai.call()"
        violations = self.security.detect_implicit_call(code)
        
        # 2. Verify violation logged
        self.assertGreater(len(violations), 0)
        
        # 3. Check audit trail
        log = self.security.get_security_log("violation")
        self.assertGreater(len(log), 0)
    
    def test_policy_enforcement_workflow(self):
        """Test policy enforcement workflow."""
        # 1. Set policy
        self.security.set_security_policy(SecurityAction.WEB_FETCH, {
            "allowed_domains": ["example.com"]
        })
        
        # 2. Attempt authorized access
        result = self.security.execute_web_call("fetch", "https://example.com", {"url": "https://example.com"})
        self.assertIn("content", result)
        
        # 3. Attempt unauthorized access
        with self.assertRaises(PermissionError):
            self.security.execute_web_call("fetch", "https://forbidden.com", {"url": "https://forbidden.com"})
        
        # 4. Verify violation
        violations = self.security.get_violations(SecurityViolation.UNAUTHORIZED_ACTION)
        self.assertGreater(len(violations), 0)


if __name__ == "__main__":
    unittest.main()
