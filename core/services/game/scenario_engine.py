"""
Scenario Execution Engine for v1.0.18
Handles scenario playback, event processing, and system integration
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from core.services.game.xp_service import XPCategory
from core.services.game.inventory_service import ItemCategory
from core.services.game.survival_service import SurvivalStat, StatusEffect


class EventType(str, Enum):
    """Types of scenario events"""
    NARRATIVE = "narrative"      # Story text display
    CHOICE = "choice"            # Player decision point
    ITEM_GIVE = "item_give"      # Add item to inventory
    ITEM_TAKE = "item_take"      # Remove item from inventory
    STAT_CHANGE = "stat_change"  # Modify survival stat
    EFFECT_ADD = "effect_add"    # Add status effect
    XP_AWARD = "xp_award"        # Grant XP
    QUEST_START = "quest_start"  # Begin quest
    QUEST_UPDATE = "quest_update" # Update quest objective
    TIME_PASS = "time_pass"      # Advance time
    CONDITION = "condition"      # Conditional branching
    CHECKPOINT = "checkpoint"    # Save point
    END = "end"                  # Scenario conclusion


class ScenarioEngine:
    """
    Executes scenario scripts and integrates with game systems
    """

    def __init__(self, scenario_service, xp_service=None,
                 inventory_service=None, survival_service=None):
        """
        Initialize scenario engine

        Args:
            scenario_service: ScenarioService instance
            xp_service: Optional XPService instance
            inventory_service: Optional InventoryService instance
            survival_service: Optional SurvivalService instance
        """
        self.scenario_service = scenario_service
        self.xp_service = xp_service
        self.inventory_service = inventory_service
        self.survival_service = survival_service

        self.current_session_id = None
        self.current_events = []
        self.event_index = 0

    def load_scenario_script(self, script_path: str) -> Dict[str, Any]:
        """
        Load scenario script from JSON file

        Args:
            script_path: Path to scenario JSON file

        Returns:
            Dict with scenario script data
        """
        if not os.path.exists(script_path):
            return {"error": "Script file not found"}

        try:
            with open(script_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {str(e)}"}

    def start_scenario_from_script(self, script_path: str) -> Dict[str, Any]:
        """
        Start a scenario from a script file

        Args:
            script_path: Path to scenario JSON file

        Returns:
            Dict with start result
        """
        # Load script
        script = self.load_scenario_script(script_path)
        if "error" in script:
            return script

        # Register scenario if not already registered
        metadata = script.get("metadata", {})
        scenario_name = metadata.get("name", "unknown")

        # Start scenario session
        result = self.scenario_service.start_scenario(scenario_name)
        if "error" not in result:
            self.current_session_id = result.get("session_id")
            self.current_events = script.get("events", [])
            self.event_index = 0

            # Initialize scenario variables
            initial_vars = script.get("initial_variables", {})
            for var_name, var_value in initial_vars.items():
                self.scenario_service.set_variable(
                    self.current_session_id, var_name, var_value
                )

        return result

    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single scenario event

        Args:
            event: Event dictionary from scenario script

        Returns:
            Dict with event result and any outputs
        """
        if not self.current_session_id:
            return {"error": "No active scenario session"}

        event_type = event.get("type")
        result = {"type": event_type, "processed": False}

        if event_type == EventType.NARRATIVE:
            result = self._process_narrative(event)

        elif event_type == EventType.CHOICE:
            result = self._process_choice(event)

        elif event_type == EventType.ITEM_GIVE:
            result = self._process_item_give(event)

        elif event_type == EventType.ITEM_TAKE:
            result = self._process_item_take(event)

        elif event_type == EventType.STAT_CHANGE:
            result = self._process_stat_change(event)

        elif event_type == EventType.EFFECT_ADD:
            result = self._process_effect_add(event)

        elif event_type == EventType.XP_AWARD:
            result = self._process_xp_award(event)

        elif event_type == EventType.QUEST_START:
            result = self._process_quest_start(event)

        elif event_type == EventType.QUEST_UPDATE:
            result = self._process_quest_update(event)

        elif event_type == EventType.TIME_PASS:
            result = self._process_time_pass(event)

        elif event_type == EventType.CONDITION:
            result = self._process_condition(event)

        elif event_type == EventType.CHECKPOINT:
            result = self._process_checkpoint(event)

        elif event_type == EventType.END:
            result = self._process_end(event)

        result["processed"] = True
        return result

    def _process_narrative(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Display narrative text"""
        text = event.get("text", "")
        speaker = event.get("speaker")

        # Variable substitution
        text = self._substitute_variables(text)

        return {
            "type": "narrative",
            "text": text,
            "speaker": speaker,
            "display": True
        }

    def _process_choice(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Present player choice"""
        prompt = event.get("prompt", "What do you do?")
        options = event.get("options", [])

        return {
            "type": "choice",
            "prompt": self._substitute_variables(prompt),
            "options": options,
            "requires_input": True
        }

    def _process_item_give(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Add item to inventory"""
        if not self.inventory_service:
            return {"type": "item_give", "skipped": True}

        item_name = event.get("item")
        quantity = event.get("quantity", 1)
        category_str = event.get("category", "misc")
        category = ItemCategory[category_str.upper()]

        result = self.inventory_service.add_item(
            name=item_name,
            category=category,
            quantity=quantity,
            weight=event.get("weight", 0.0),
            volume=event.get("volume", 0.0)
        )

        return {
            "type": "item_give",
            "item": item_name,
            "quantity": quantity,
            "result": result
        }

    def _process_item_take(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Remove item from inventory"""
        if not self.inventory_service:
            return {"type": "item_take", "skipped": True}

        item_name = event.get("item")
        quantity = event.get("quantity", 1)

        # Find item by name
        inventory = self.inventory_service.get_inventory()
        item = next((i for i in inventory if i['name'] == item_name), None)

        if not item:
            return {"type": "item_take", "error": "Item not found"}

        result = self.inventory_service.remove_item(
            item_id=item['id'],
            quantity=quantity
        )

        return {
            "type": "item_take",
            "item": item_name,
            "quantity": quantity,
            "result": result
        }

    def _process_stat_change(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Modify survival stat"""
        if not self.survival_service:
            return {"type": "stat_change", "skipped": True}

        stat_str = event.get("stat")
        stat = SurvivalStat[stat_str.upper()]
        change = event.get("change", 0)

        current_dict = self.survival_service.get_stat(stat)
        current = current_dict.get('current', 0)
        new_value = max(0, min(100, current + change))

        self.survival_service.set_stat(stat, new_value)

        return {
            "type": "stat_change",
            "stat": stat_str,
            "change": change,
            "new_value": new_value
        }

    def _process_effect_add(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Add status effect"""
        if not self.survival_service:
            return {"type": "effect_add", "skipped": True}

        effect_str = event.get("effect")
        effect = StatusEffect[effect_str.upper()]
        duration_hours = event.get("duration", 1)
        duration_minutes = duration_hours * 60

        result = self.survival_service.add_status_effect(
            effect=effect,
            duration_minutes=duration_minutes
        )

        return {
            "type": "effect_add",
            "effect": effect_str,
            "result": result
        }

    def _process_xp_award(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Award XP"""
        if not self.xp_service:
            return {"type": "xp_award", "skipped": True}

        amount = event.get("amount", 0)
        category_str = event.get("category", "usage")
        category = XPCategory[category_str.upper()]
        reason = event.get("reason", "Scenario progress")

        result = self.xp_service.award_xp(
            category=category,
            amount=amount,
            reason=reason
        )

        return {
            "type": "xp_award",
            "amount": amount,
            "category": category_str,
            "result": result
        }

    def _process_quest_start(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Start a quest"""
        quest_name = event.get("quest")

        # Get session info to find scenario_id
        info = self.scenario_service.get_session_info(self.current_session_id)
        if not info:
            return {"type": "quest_start", "error": "Session not found"}

        # Quest should already be defined in scenario
        # Just start it
        result = {"type": "quest_start", "quest": quest_name}

        return result

    def _process_quest_update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Update quest objective"""
        quest_id = event.get("quest_id")
        objective_index = event.get("objective_index")
        completed = event.get("completed", True)

        result = self.scenario_service.update_quest_objective(
            self.current_session_id, quest_id, objective_index, completed
        )

        return {
            "type": "quest_update",
            "result": result
        }

    def _process_time_pass(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Advance time and apply decay"""
        hours = event.get("hours", 1)

        if self.survival_service:
            for _ in range(hours):
                self.survival_service.apply_time_decay(hours=1)

        return {
            "type": "time_pass",
            "hours": hours,
            "message": f"{hours} hour(s) passed..."
        }

    def _process_condition(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate condition and branch"""
        condition = event.get("condition")

        # Evaluate condition
        evaluated = self._evaluate_condition(condition)

        return {
            "type": "condition",
            "condition": condition,
            "result": evaluated,
            "branch": "true" if evaluated else "false"
        }

    def _process_checkpoint(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Create checkpoint"""
        name = event.get("name", f"checkpoint_{self.event_index}")

        # Get current state
        state = self.scenario_service.load_state(self.current_session_id)
        state["event_index"] = self.event_index

        result = self.scenario_service.create_checkpoint(
            self.current_session_id, name, state
        )

        return {
            "type": "checkpoint",
            "name": name,
            "result": result
        }

    def _process_end(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """End scenario"""
        outcome = event.get("outcome", "completed")
        message = event.get("message", "Scenario complete!")

        # Award final XP
        if self.xp_service and "xp" in event:
            self.xp_service.award_xp(
                category=XPCategory.USAGE,
                amount=event["xp"],
                reason=f"Completed scenario: {outcome}"
            )

        return {
            "type": "end",
            "outcome": outcome,
            "message": self._substitute_variables(message),
            "session_id": self.current_session_id
        }

    def _substitute_variables(self, text: str) -> str:
        """Replace {variable} placeholders with values"""
        if not self.current_session_id:
            return text

        variables = self.scenario_service.get_all_variables(self.current_session_id)

        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in text:
                text = text.replace(placeholder, str(var_value))

        return text

    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition string"""
        if not self.current_session_id:
            return False

        # Get variables
        variables = self.scenario_service.get_all_variables(self.current_session_id)

        # Simple evaluation (supports ==, >, <, >=, <=, !=)
        for op in ["==", ">=", "<=", "!=", ">", "<"]:
            if op in condition:
                parts = condition.split(op)
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()

                    # Get variable value
                    if left.startswith("{") and left.endswith("}"):
                        var_name = left[1:-1]
                        left_val = variables.get(var_name)
                    else:
                        left_val = left

                    # Compare
                    try:
                        if op == "==":
                            return str(left_val) == right.strip('"\'')
                        elif op == "!=":
                            return str(left_val) != right.strip('"\'')
                        else:
                            left_num = float(left_val)
                            right_num = float(right.strip('"\''))
                            if op == ">":
                                return left_num > right_num
                            elif op == "<":
                                return left_num < right_num
                            elif op == ">=":
                                return left_num >= right_num
                            elif op == "<=":
                                return left_num <= right_num
                    except (ValueError, TypeError):
                        return False

        return False

    def get_next_event(self) -> Optional[Dict[str, Any]]:
        """Get next event to process"""
        if self.event_index < len(self.current_events):
            event = self.current_events[self.event_index]
            self.event_index += 1
            return event
        return None

    def has_more_events(self) -> bool:
        """Check if more events remain"""
        return self.event_index < len(self.current_events)

    def save_progress(self) -> Dict[str, Any]:
        """Save current scenario progress"""
        if not self.current_session_id:
            return {"error": "No active session"}

        state = {
            "event_index": self.event_index,
            "timestamp": datetime.utcnow().isoformat()
        }

        return self.scenario_service.save_state(self.current_session_id, state)

    def restore_progress(self, session_id: int) -> Dict[str, Any]:
        """Restore scenario progress"""
        state = self.scenario_service.load_state(session_id)
        if state:
            self.current_session_id = session_id
            self.event_index = state.get("event_index", 0)
            return {"restored": True, "event_index": self.event_index}
        return {"error": "Could not restore progress"}
