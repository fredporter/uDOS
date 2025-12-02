"""
Scenario Play Command Handler for v1.0.18
Integrates scenario engine with uDOS command system
"""

import os
import json
from typing import Dict, List, Any, Optional

from core.services.scenario_service import ScenarioService, ScenarioType
from core.services.scenario_engine import ScenarioEngine, EventType
from extensions.play.services.game_mechanics.xp_service import XPService
from extensions.play.services.game_mechanics.inventory_service import InventoryService
from extensions.play.services.game_mechanics.survival_service import SurvivalService


class ScenarioPlayHandler:
    """
    Handles scenario playback and player interaction
    """

    def __init__(self, data_dir: str = "data"):
        """Initialize handler with all required services"""
        self.data_dir = data_dir

        # Initialize services
        self.scenario_service = ScenarioService(data_dir=data_dir)
        self.xp_service = XPService(db_path=os.path.join(data_dir, "xp.db"))
        self.inventory_service = InventoryService(data_dir=data_dir)
        self.survival_service = SurvivalService(data_dir=data_dir)

        # Initialize engine
        self.engine = ScenarioEngine(
            scenario_service=self.scenario_service,
            xp_service=self.xp_service,
            inventory_service=self.inventory_service,
            survival_service=self.survival_service
        )

        self.current_choice = None
        self.awaiting_choice = False

    def handle_command(self, command: str, args: List[str]) -> Dict[str, Any]:
        """
        Route scenario commands

        Commands:
            PLAY LIST - List available scenarios
            PLAY START <name> - Start a scenario
            PLAY CONTINUE - Continue current scenario
            PLAY CHOOSE <option> - Make choice in scenario
            PLAY STATUS - Show current scenario status
            PLAY SAVE - Save current progress
            PLAY QUIT - Exit current scenario
        """
        if not args:
            return self._show_help()

        subcommand = args[0].upper()

        if subcommand == "LIST":
            return self._list_scenarios()
        elif subcommand == "START" and len(args) > 1:
            return self._start_scenario(args[1])
        elif subcommand == "CONTINUE":
            return self._continue_scenario()
        elif subcommand == "CHOOSE" and len(args) > 1:
            return self._make_choice(args[1])
        elif subcommand == "STATUS":
            return self._show_status()
        elif subcommand == "SAVE":
            return self._save_progress()
        elif subcommand == "QUIT":
            return self._quit_scenario()
        else:
            return {"error": f"Unknown subcommand: {subcommand}"}

    def _show_help(self) -> Dict[str, Any]:
        """Show command help"""
        return {
            "type": "help",
            "message": """PLAY Commands:

PLAY LIST              - List available scenarios
PLAY START <name>      - Start a new scenario
PLAY CONTINUE          - Continue current scenario
PLAY CHOOSE <option>   - Make a choice (when prompted)
PLAY STATUS            - Show current scenario status
PLAY SAVE              - Save current progress
PLAY QUIT              - Exit current scenario

Example:
  PLAY LIST
  PLAY START the_last_day
  PLAY CHOOSE 1
  PLAY CONTINUE
"""
        }

    def _list_scenarios(self) -> Dict[str, Any]:
        """List available scenario files"""
        scenarios_dir = "memory/scenarios"

        if not os.path.exists(scenarios_dir):
            return {"error": "No scenarios directory found"}

        scenario_files = []
        for filename in os.listdir(scenarios_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(scenarios_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        metadata = data.get("metadata", {})
                        scenario_files.append({
                            "name": metadata.get("name", filename),
                            "title": metadata.get("title", "Unknown"),
                            "type": metadata.get("type", "unknown"),
                            "difficulty": metadata.get("difficulty", 0),
                            "estimated_minutes": metadata.get("estimated_minutes", 0),
                            "description": metadata.get("description", ""),
                            "tags": metadata.get("tags", [])
                        })
                except Exception as e:
                    continue

        return {
            "type": "scenario_list",
            "scenarios": scenario_files,
            "count": len(scenario_files)
        }

    def _start_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Start a scenario from JSON file"""
        # Find scenario file
        scenarios_dir = "memory/scenarios"
        scenario_path = os.path.join(scenarios_dir, f"{scenario_name}.json")

        if not os.path.exists(scenario_path):
            return {"error": f"Scenario '{scenario_name}' not found"}

        # Register scenario if needed
        script = self.engine.load_scenario_script(scenario_path)
        if "error" in script:
            return script

        metadata = script.get("metadata", {})

        # Register in database
        self.scenario_service.register_scenario(
            name=metadata.get("name", scenario_name),
            scenario_type=ScenarioType[metadata.get("type", "story").upper()],
            title=metadata.get("title", "Unknown"),
            description=metadata.get("description", ""),
            difficulty=metadata.get("difficulty", 1),
            estimated_minutes=metadata.get("estimated_minutes", 30),
            xp_reward=metadata.get("xp_reward", 100)
        )

        # Start scenario
        result = self.engine.start_scenario_from_script(scenario_path)

        if "error" in result:
            return result

        # Process first event
        return self._continue_scenario()

    def _continue_scenario(self) -> Dict[str, Any]:
        """Process next event(s) in scenario"""
        if not self.engine.current_session_id:
            return {"error": "No active scenario. Use PLAY START <name>"}

        if self.awaiting_choice:
            return {
                "type": "awaiting_choice",
                "message": "Make a choice first with PLAY CHOOSE <option>",
                "choice": self.current_choice
            }

        results = []

        # Process events until we hit a choice or end
        while self.engine.has_more_events():
            event = self.engine.get_next_event()
            if not event:
                break

            result = self.engine.process_event(event)
            results.append(result)

            # Stop at choices
            if result.get("type") == "choice":
                self.current_choice = result
                self.awaiting_choice = True
                break

            # Stop at end
            if result.get("type") == "end":
                self.engine.current_session_id = None
                break

        return {
            "type": "scenario_events",
            "events": results,
            "has_more": self.engine.has_more_events(),
            "awaiting_choice": self.awaiting_choice
        }

    def _make_choice(self, choice_input: str) -> Dict[str, Any]:
        """Make a choice in scenario"""
        if not self.awaiting_choice:
            return {"error": "No choice pending"}

        # Parse choice (1, 2, 3, etc.)
        try:
            choice_index = int(choice_input) - 1
        except ValueError:
            return {"error": "Choice must be a number"}

        if not self.current_choice or "options" not in self.current_choice:
            return {"error": "No valid choice available"}

        options = self.current_choice["options"]

        if choice_index < 0 or choice_index >= len(options):
            return {"error": f"Invalid choice. Choose 1-{len(options)}"}

        # Set variable based on choice
        chosen_option = options[choice_index]
        if "variable" in chosen_option and "value" in chosen_option:
            self.scenario_service.set_variable(
                self.engine.current_session_id,
                chosen_option["variable"],
                chosen_option["value"]
            )

        # Clear choice state
        self.awaiting_choice = False
        choice_result = {
            "type": "choice_made",
            "option": chosen_option.get("text", "Unknown"),
            "index": choice_index + 1
        }

        # Continue to next events
        continue_result = self._continue_scenario()

        # Combine results
        return {
            "type": "choice_and_continue",
            "choice_result": choice_result,
            "events": continue_result.get("events", [])
        }

    def _show_status(self) -> Dict[str, Any]:
        """Show current scenario status"""
        if not self.engine.current_session_id:
            return {"error": "No active scenario"}

        session_info = self.scenario_service.get_session_info(
            self.engine.current_session_id
        )

        if not session_info:
            return {"error": "Session not found"}

        # Get variables
        variables = self.scenario_service.get_all_variables(
            self.engine.current_session_id
        )

        # Get active quests
        quests = self.scenario_service.get_active_quests(
            self.engine.current_session_id
        )

        return {
            "type": "scenario_status",
            "session_info": session_info,
            "variables": variables,
            "active_quests": quests,
            "event_index": self.engine.event_index,
            "total_events": len(self.engine.current_events),
            "awaiting_choice": self.awaiting_choice
        }

    def _save_progress(self) -> Dict[str, Any]:
        """Save current scenario progress"""
        if not self.engine.current_session_id:
            return {"error": "No active scenario"}

        result = self.engine.save_progress()
        return result

    def _quit_scenario(self) -> Dict[str, Any]:
        """Quit current scenario"""
        if not self.engine.current_session_id:
            return {"error": "No active scenario"}

        # Save before quitting
        save_result = self.engine.save_progress()

        session_id = self.engine.current_session_id
        self.engine.current_session_id = None
        self.awaiting_choice = False
        self.current_choice = None

        return {
            "type": "scenario_quit",
            "message": "Scenario progress saved. Use PLAY CONTINUE to resume.",
            "session_id": session_id,
            "save_result": save_result
        }


def format_scenario_output(result: Dict[str, Any]) -> str:
    """Format scenario result for display"""
    output = []

    if result.get("type") == "scenario_list":
        output.append("=== Available Scenarios ===\n")
        for i, scenario in enumerate(result.get("scenarios", []), 1):
            output.append(f"{i}. {scenario['title']}")
            output.append(f"   Name: {scenario['name']}")
            output.append(f"   Type: {scenario['type']} | Difficulty: {scenario['difficulty']}")
            output.append(f"   Time: ~{scenario['estimated_minutes']} minutes")
            output.append(f"   {scenario['description']}")
            output.append("")

    elif result.get("type") == "scenario_events":
        for event in result.get("events", []):
            event_type = event.get("type")

            if event_type == "narrative":
                output.append(event.get("text", ""))
                if event.get("speaker"):
                    output.append(f"  — {event['speaker']}")
                output.append("")

            elif event_type == "choice":
                output.append(event.get("prompt", "Choose:"))
                for i, option in enumerate(event.get("options", []), 1):
                    output.append(f"  {i}. {option.get('text', 'Option')}")
                output.append("\nUse: PLAY CHOOSE <number>")
                output.append("")

            elif event_type == "xp_award":
                output.append(f"[+{event.get('amount', 0)} XP] {event.get('result', {}).get('reason', '')}")

            elif event_type == "item_give":
                qty = event.get('quantity', 1)
                item = event.get('item', 'Item')
                output.append(f"[Received: {item} x{qty}]")

            elif event_type == "stat_change":
                stat = event.get('stat', 'stat')
                change = event.get('change', 0)
                sign = '+' if change >= 0 else ''
                output.append(f"[{stat.title()}: {sign}{change}]")

            elif event_type == "time_pass":
                hours = event.get('hours', 0)
                output.append(f"[{hours} hour(s) passed...]")

            elif event_type == "end":
                output.append("\n" + "="*50)
                output.append(event.get("message", "Scenario complete!"))
                output.append("="*50)

    elif result.get("type") == "choice_and_continue":
        choice = result.get("choice_result", {})
        output.append(f"You chose: {choice.get('option', 'Unknown')}\n")

        # Format continuation events
        for event in result.get("events", []):
            # (same formatting as above)
            pass

    elif result.get("type") == "scenario_status":
        info = result.get("session_info", {})
        output.append("=== Scenario Status ===")
        output.append(f"Scenario: {info.get('title', 'Unknown')}")
        output.append(f"Progress: Event {result.get('event_index', 0)}/{result.get('total_events', 0)}")

        quests = result.get("active_quests", [])
        if quests:
            output.append(f"\nActive Quests: {len(quests)}")
            for quest in quests:
                output.append(f"  - {quest.get('title', 'Quest')}: {quest.get('progress_percent', 0)}%")

    elif "error" in result:
        output.append(f"Error: {result['error']}")

    return "\n".join(output)
