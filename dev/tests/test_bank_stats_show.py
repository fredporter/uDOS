"""
Test BANK STATS and BANK SHOW commands (v1.0.29)

Tests to verify BANK command fixes.

Author: uDOS Development Team
Version: 1.0.29
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestBankStatsCommand(unittest.TestCase):
    """Test BANK STATS command"""

    def test_bank_stats_handler_exists(self):
        """Test _handle_stats method exists in BankCommandHandler"""
        try:
            from core.commands.bank_handler import BankCommandHandler
            handler = BankCommandHandler()
            self.assertTrue(hasattr(handler, '_handle_stats'))
        except ImportError:
            self.skipTest("BankCommandHandler not available")

    def test_bank_stats_uses_correct_property(self):
        """Test BANK STATS uses bank_manager not knowledge_manager"""
        try:
            from core.commands.bank_handler import BankCommandHandler
            import inspect

            handler = BankCommandHandler()

            # Check the _handle_stats method source
            source = inspect.getsource(handler._handle_stats)

            # Should use bank_manager
            self.assertIn('bank_manager', source, "BANK STATS should use bank_manager")

            # Should NOT use knowledge_manager
            self.assertNotIn('knowledge_manager', source, "BANK STATS should not use knowledge_manager")

        except ImportError:
            self.skipTest("BankCommandHandler not available")

    def test_bank_stats_command_documented(self):
        """Test BANK STATS is documented in commands.json"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])

        # Look for BANK STATS
        stats_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'BANK STATS'), None)
        self.assertIsNotNone(stats_cmd, "BANK STATS command should be documented")


class TestBankShowCommand(unittest.TestCase):
    """Test BANK SHOW command"""

    def test_bank_show_handler_exists(self):
        """Test _handle_show method exists in BankCommandHandler"""
        try:
            from core.commands.bank_handler import BankCommandHandler
            handler = BankCommandHandler()
            self.assertTrue(hasattr(handler, '_handle_show'))
        except ImportError:
            self.skipTest("BankCommandHandler not available")

    def test_bank_show_command_documented(self):
        """Test BANK SHOW is documented in commands.json"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])

        # Look for BANK SHOW
        show_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'BANK SHOW'), None)
        self.assertIsNotNone(show_cmd, "BANK SHOW command should be documented")

    def test_bank_show_has_examples(self):
        """Test BANK SHOW has proper examples"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        show_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'BANK SHOW'), None)

        if show_cmd:
            examples = show_cmd.get('EXAMPLES', [])
            self.assertGreater(len(examples), 0, "BANK SHOW should have examples")


class TestBankCommandRouting(unittest.TestCase):
    """Test BANK command routing"""

    def test_bank_handler_routes_stats(self):
        """Test BANK handler routes STATS command"""
        try:
            from core.commands.bank_handler import BankCommandHandler
            import inspect

            handler = BankCommandHandler()

            # Check the handle method routes STATS
            source = inspect.getsource(handler.handle)

            self.assertIn('STATS', source)
            self.assertIn('_handle_stats', source)

        except ImportError:
            self.skipTest("BankCommandHandler not available")

    def test_bank_handler_routes_show(self):
        """Test BANK handler routes SHOW command"""
        try:
            from core.commands.bank_handler import BankCommandHandler
            import inspect

            handler = BankCommandHandler()

            # Check the handle method routes SHOW
            source = inspect.getsource(handler.handle)

            self.assertIn('SHOW', source)
            self.assertIn('_handle_show', source)

        except ImportError:
            self.skipTest("BankCommandHandler not available")


if __name__ == '__main__':
    unittest.main()
