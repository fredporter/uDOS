"""Tests transport policy validator audit persistence."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from extensions.transport.validator import PolicyValidator, ValidationError


class TransportValidatorAuditTest(unittest.TestCase):
    def test_audit_violation_writes_log_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            old = Path.cwd()
            try:
                import os
                os.chdir(cwd)
                validator = PolicyValidator()
                err = ValidationError(
                    code="ERR_POLICY_TEST",
                    message="test",
                    severity="high",
                    rule="unit-test",
                )
                validator.audit_violation(err, {"command": "PLAY"})
            finally:
                os.chdir(old)

            log_path = cwd / "memory" / "logs" / "security-audit.log"
            self.assertTrue(log_path.exists())
            self.assertIn("ERR_POLICY_TEST", log_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
