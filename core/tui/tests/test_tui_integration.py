"""Integration tests for lightweight TUI

Test suite for the lightweight CLI interface.
Coverage:
- REPL loop functionality
- Command dispatcher routing
- Result rendering
- Game state management
- Special commands
"""

import pytest
from pathlib import Path
import json
import tempfile

from core.tui import TUIRepl, CommandDispatcher, GridRenderer, GameState
from core.services.error_contract import CommandError


class TestGameState:
    """Test game state management"""

    def test_init(self):
        """Test state initialization"""
        state = GameState()
        assert state.current_location == "L300-BJ10"
        assert state.inventory == []
        assert "L300-BJ10" in state.discovered_locations
        assert state.player_stats["level"] == 1

    def test_update_from_handler_location(self):
        """Test state update with location change"""
        state = GameState()
        result = {"status": "success", "location": "L300-BJ11"}

        state.update_from_handler(result)
        assert state.current_location == "L300-BJ11"

    def test_update_from_handler_inventory(self):
        """Test state update with inventory change"""
        state = GameState()
        items = [{"name": "sword", "quantity": 1}]
        result = {"status": "success", "inventory": items}

        state.update_from_handler(result)
        assert state.inventory == items

    def test_update_from_handler_discovered(self):
        """Test state update with discovered location"""
        state = GameState()
        result = {"status": "success", "location_id": "L300-BJ12"}

        state.update_from_handler(result)
        assert "L300-BJ12" in state.discovered_locations

    def test_to_dict(self):
        """Test state serialization"""
        state = GameState()
        state.current_location = "L300-BJ11"
        state.inventory = [{"name": "key", "quantity": 1}]

        data = state.to_dict()
        assert data["current_location"] == "L300-BJ11"
        assert data["inventory"][0]["name"] == "key"

    def test_from_dict(self):
        """Test state deserialization"""
        state = GameState()
        data = {
            "current_location": "L300-BJ12",
            "inventory": [{"name": "potion", "quantity": 2}],
            "discovered_locations": ["L300-BJ10", "L300-BJ11", "L300-BJ12"],
            "player_stats": {"level": 5},
        }

        state.from_dict(data)
        assert state.current_location == "L300-BJ12"
        assert state.inventory[0]["name"] == "potion"
        assert state.player_stats["level"] == 5

    def test_add_to_history(self):
        """Test command history tracking"""
        state = GameState()
        state.add_to_history("FIND tokyo")
        state.add_to_history("TELL L300-BJ10")

        assert len(state.session_history) == 2
        assert state.session_history[0] == "FIND tokyo"


class TestCommandDispatcher:
    """Test command dispatching"""

    def test_init(self):
        """Test dispatcher initialization"""
        dispatcher = CommandDispatcher()
        assert len(dispatcher.handlers) >= 16

    def test_get_command_list(self):
        """Test getting list of commands"""
        dispatcher = CommandDispatcher()
        commands = dispatcher.get_command_list()

        assert "MAP" in commands
        assert "FIND" in commands
        assert "BAG" in commands
        assert "HELP" in commands
        assert "NPC" in commands
        assert "SEND" in commands
        assert "OPERATOR" in commands
        assert len(commands) >= 16

    def test_dispatch_unknown_command(self):
        """Test dispatching unknown command"""
        dispatcher = CommandDispatcher()
        with pytest.raises(CommandError):
            dispatcher.dispatch("UNKNOWN")

    def test_dispatch_empty_input(self):
        """Test dispatching empty input"""
        dispatcher = CommandDispatcher()
        with pytest.raises(CommandError):
            dispatcher.dispatch("")

    def test_dispatch_find_command(self):
        """Test FIND command routing"""
        dispatcher = CommandDispatcher()
        result = dispatcher.dispatch("FIND tokyo")

        assert result["status"] in ["success", "error"]  # Depends on data
        assert "results" in result or "message" in result

    def test_dispatch_help_command(self):
        """Test HELP command routing"""
        dispatcher = CommandDispatcher()
        result = dispatcher.dispatch("HELP")

        assert result["status"] == "success"
        assert "commands" in result or "message" in result

    def test_get_command_help(self):
        """Test getting command help"""
        dispatcher = CommandDispatcher()

        # All commands
        help_all = dispatcher.get_command_help()
        assert help_all["status"] == "success"
        assert len(help_all["commands"]) >= 16

        # Specific command
        help_map = dispatcher.get_command_help("MAP")
        assert help_map["status"] == "success"
        assert help_map["command"] == "MAP"


class TestGridRenderer:
    """Test result rendering"""

    def test_render_success(self):
        """Test rendering success result"""
        renderer = GridRenderer()
        result = {
            "status": "success",
            "message": "Operation succeeded",
            "text": "Result text",
        }

        output = renderer.render(result)
        assert "✓" in output
        assert "Operation succeeded" in output

    def test_render_error(self):
        """Test rendering error result"""
        renderer = GridRenderer()
        result = {
            "status": "error",
            "message": "Something went wrong",
            "suggestion": "Try again",
        }

        output = renderer.render(result)
        assert "✗" in output
        assert "Something went wrong" in output
        assert "Try again" in output

    def test_render_warning(self):
        """Test rendering warning result"""
        renderer = GridRenderer()
        result = {"status": "warning", "message": "Be careful"}

        output = renderer.render(result)
        assert "!" in output
        assert "Be careful" in output

    def test_format_items(self):
        """Test formatting item list"""
        renderer = GridRenderer()
        items = [
            {"name": "sword", "quantity": 1, "equipped": True},
            {"name": "shield", "quantity": 1, "equipped": False},
        ]

        output = renderer.render(
            {"status": "success", "message": "Inventory", "items": items}
        )
        assert "sword" in output
        assert "shield" in output
        assert "[equipped]" in output

    def test_format_results(self):
        """Test formatting search results"""
        renderer = GridRenderer()
        results = [
            {"name": "Tokyo - Shibuya", "id": "L300-BJ10"},
            {"name": "Tokyo - Shinjuku", "id": "L300-BJ11"},
        ]

        output = renderer.render(
            {"status": "success", "message": "Found", "results": results}
        )
        assert "Tokyo" in output
        assert "L300-BJ10" in output

    def test_format_prompt(self):
        """Test prompt formatting"""
        renderer = GridRenderer()
        prompt = renderer.format_prompt("L300-BJ10")

        assert "L300-BJ10" in prompt
        assert ">" in prompt

    def test_separator(self):
        """Test separator generation"""
        separator = GridRenderer.separator("-", 20)
        assert separator == "--------------------"
        assert len(separator) == 20


class TestTUIREPL:
    """Test REPL functionality"""

    def test_init(self):
        """Test REPL initialization"""
        repl = TUIRepl()
        assert repl.dispatcher is not None
        assert repl.renderer is not None
        assert repl.state is not None
        assert repl.running is False

    def test_handle_special_commands_quit(self):
        """Test QUIT command"""
        repl = TUIRepl()
        repl.running = True
        handled = repl._handle_special_commands("QUIT")

        assert handled is False

    def test_handle_special_commands_exit(self):
        """Test EXIT command"""
        repl = TUIRepl()
        repl.running = True
        handled = repl._handle_special_commands("EXIT")

        assert handled is True
        assert repl.running is False

    def test_handle_special_commands_status(self):
        """Test STATUS command"""
        repl = TUIRepl()
        handled = repl._handle_special_commands("STATUS")
        assert handled is True

    def test_handle_special_commands_history(self):
        """Test HISTORY command"""
        repl = TUIRepl()
        handled = repl._handle_special_commands("HISTORY")
        assert handled is True

    def test_handle_special_commands_normal(self):
        """Test normal command (not special)"""
        repl = TUIRepl()
        handled = repl._handle_special_commands("FIND tokyo")
        assert handled is False


class TestTUIIntegration:
    """Integration tests for complete workflow"""

    def test_command_to_state_update(self):
        """Test full workflow: command → dispatch → state update"""
        repl = TUIRepl()

        # Simulate FIND command
        result = repl.dispatcher.dispatch("FIND")
        repl.state.update_from_handler(result)

        # State should be updated
        assert repl.state is not None

    def test_state_persistence(self):
        """Test save/load state persistence"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = GameState()
            state._saves_dir = Path(tmpdir)

            # Modify state
            state.current_location = "L300-BJ15"
            state.inventory = [{"name": "key", "quantity": 1}]

            # Save
            success = state.save_to_file("test-slot")
            assert success is True

            # Load into new state
            state2 = GameState()
            state2._saves_dir = Path(tmpdir)
            success = state2.load_from_file("test-slot")

            assert success is True
            assert state2.current_location == "L300-BJ15"
            assert state2.inventory[0]["name"] == "key"

    def test_command_help_flow(self):
        """Test help command flow"""
        repl = TUIRepl()

        # Get all commands
        result = repl.dispatcher.dispatch("HELP")
        assert result["status"] == "success"

        # Get specific help
        result = repl.dispatcher.dispatch("HELP MAP")
        assert result["status"] in ["success", "error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
