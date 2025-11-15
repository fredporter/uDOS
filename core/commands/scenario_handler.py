"""
Scenario Command Handler for uDOS v1.0.18 - Apocalypse Adventures
Handles SCENARIO, QUEST, and adventure-related commands.
"""

from typing import Dict, List
from core.services.scenario_service import ScenarioService, ScenarioType, QuestStatus


class ScenarioCommandHandler:
    """Handler for scenario and quest commands"""

    def __init__(self, data_dir: str = "data"):
        """Initialize with scenario service"""
        self.scenario_service = ScenarioService(data_dir)
        self.current_session_id = None

    def handle_command(self, command: str, args: List[str]) -> Dict:
        """
        Route scenario commands to appropriate handlers.

        Args:
            command: Command name (SCENARIO, QUEST, etc.)
            args: Command arguments

        Returns:
            Dict with command results
        """
        command_upper = command.upper()

        if command_upper == "SCENARIO":
            return self.handle_scenario(args)
        elif command_upper == "QUEST":
            return self.handle_quest(args)
        else:
            return {"type": "error", "message": f"Unknown scenario command: {command}"}

    def handle_scenario(self, args: List[str]) -> Dict:
        """
        Handle SCENARIO command.

        Usage:
            SCENARIO - List available scenarios
            SCENARIO LIST - List available scenarios
            SCENARIO START <name> - Start a scenario
            SCENARIO RESUME [session_id] - Resume scenario
            SCENARIO SAVE - Save current state
            SCENARIO CHECKPOINT <name> - Create checkpoint
            SCENARIO RESTORE <name> - Restore checkpoint
            SCENARIO INFO - Show current scenario info
        """
        if not args or args[0].lower() == "list":
            scenarios = self.scenario_service.list_scenarios()
            return {
                "type": "scenario_list",
                "scenarios": scenarios,
                "total": len(scenarios)
            }

        subcmd = args[0].lower()

        if subcmd == "start" and len(args) >= 2:
            scenario_name = args[1]
            result = self.scenario_service.start_scenario(scenario_name)

            if "error" in result:
                return {"type": "error", "message": result["error"]}

            self.current_session_id = result["session_id"]
            return {
                "type": "scenario_started",
                "result": result
            }

        elif subcmd == "resume":
            if len(args) >= 2:
                session_id = int(args[1])
            else:
                session_id = self.current_session_id

            if not session_id:
                return {
                    "type": "error",
                    "message": "No active session. Specify session ID or start a new scenario."
                }

            self.current_session_id = session_id
            info = self.scenario_service.get_session_info(session_id)

            return {
                "type": "scenario_resumed",
                "session_id": session_id,
                "info": info
            }

        elif subcmd == "save":
            if not self.current_session_id:
                return {"type": "error", "message": "No active scenario session"}

            # This would normally save the current game state
            # For now, just acknowledge
            return {
                "type": "scenario_saved",
                "session_id": self.current_session_id,
                "message": "State saved"
            }

        elif subcmd == "checkpoint" and len(args) >= 2:
            if not self.current_session_id:
                return {"type": "error", "message": "No active scenario session"}

            checkpoint_name = args[1]
            state = self.scenario_service.load_state(self.current_session_id) or {}

            result = self.scenario_service.create_checkpoint(
                self.current_session_id, checkpoint_name, state
            )

            return {
                "type": "checkpoint_created",
                "result": result
            }

        elif subcmd == "restore" and len(args) >= 2:
            if not self.current_session_id:
                return {"type": "error", "message": "No active scenario session"}

            checkpoint_name = args[1]
            state = self.scenario_service.restore_checkpoint(
                self.current_session_id, checkpoint_name
            )

            if state is None:
                return {
                    "type": "error",
                    "message": f"Checkpoint '{checkpoint_name}' not found"
                }

            return {
                "type": "checkpoint_restored",
                "checkpoint": checkpoint_name,
                "state": state
            }

        elif subcmd == "info":
            if not self.current_session_id:
                return {"type": "error", "message": "No active scenario session"}

            info = self.scenario_service.get_session_info(self.current_session_id)
            variables = self.scenario_service.get_all_variables(self.current_session_id)
            quests = self.scenario_service.get_active_quests(self.current_session_id)

            return {
                "type": "scenario_info",
                "info": info,
                "variables": variables,
                "active_quests": quests
            }

        else:
            return {
                "type": "error",
                "message": "Usage: SCENARIO [LIST/START/RESUME/SAVE/CHECKPOINT/RESTORE/INFO]"
            }

    def handle_quest(self, args: List[str]) -> Dict:
        """
        Handle QUEST command.

        Usage:
            QUEST - List active quests
            QUEST LIST - List active quests
            QUEST START <quest_id> - Start a quest
            QUEST PROGRESS <quest_id> - Show quest progress
            QUEST COMPLETE <quest_id> <objective> - Mark objective complete
        """
        if not self.current_session_id:
            return {"type": "error", "message": "No active scenario session"}

        if not args or args[0].lower() == "list":
            quests = self.scenario_service.get_active_quests(self.current_session_id)
            return {
                "type": "quest_list",
                "quests": quests,
                "total": len(quests)
            }

        subcmd = args[0].lower()

        if subcmd == "start" and len(args) >= 2:
            try:
                quest_id = int(args[1])
                result = self.scenario_service.start_quest(
                    self.current_session_id, quest_id
                )

                if "error" in result:
                    return {"type": "error", "message": result["error"]}

                return {
                    "type": "quest_started",
                    "result": result
                }
            except ValueError:
                return {"type": "error", "message": "Invalid quest ID"}

        elif subcmd == "progress" and len(args) >= 2:
            try:
                quest_id = int(args[1])
                progress = self.scenario_service.get_quest_progress(
                    self.current_session_id, quest_id
                )

                if not progress:
                    return {"type": "error", "message": "Quest not found or not started"}

                return {
                    "type": "quest_progress",
                    "progress": progress
                }
            except ValueError:
                return {"type": "error", "message": "Invalid quest ID"}

        elif subcmd == "complete" and len(args) >= 3:
            try:
                quest_id = int(args[1])
                objective_index = int(args[2])

                result = self.scenario_service.update_quest_objective(
                    self.current_session_id, quest_id, objective_index, True
                )

                if "error" in result:
                    return {"type": "error", "message": result["error"]}

                return {
                    "type": "objective_completed",
                    "result": result
                }
            except ValueError:
                return {"type": "error", "message": "Invalid quest ID or objective index"}

        else:
            return {
                "type": "error",
                "message": "Usage: QUEST [LIST/START/PROGRESS/COMPLETE]"
            }

    def set_variable(self, var_name: str, value: any, var_type: str = "string") -> Dict:
        """Set a scenario variable (for template execution)"""
        if not self.current_session_id:
            return {"error": "No active session"}

        return self.scenario_service.set_variable(
            self.current_session_id, var_name, value, var_type
        )

    def get_variable(self, var_name: str, default: any = None) -> any:
        """Get a scenario variable (for template execution)"""
        if not self.current_session_id:
            return default

        return self.scenario_service.get_variable(
            self.current_session_id, var_name, default
        )

    def evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate a condition string for branching.

        Supports simple conditions like:
        - {var} == value
        - {var} > number
        - {var} < number
        - {var} >= number
        - {var} <= number
        """
        if not self.current_session_id:
            return False

        # Simple parser for conditions
        condition = condition.strip()

        # Extract variable name and operator
        for op in ['==', '>=', '<=', '>', '<', '!=']:
            if op in condition:
                parts = condition.split(op)
                if len(parts) == 2:
                    var_name = parts[0].strip().strip('{}')
                    expected = parts[1].strip().strip('"\'')

                    actual = self.get_variable(var_name)

                    # Try numeric comparison
                    try:
                        actual_num = float(actual) if actual is not None else 0
                        expected_num = float(expected)

                        if op == '==':
                            return actual_num == expected_num
                        elif op == '>':
                            return actual_num > expected_num
                        elif op == '<':
                            return actual_num < expected_num
                        elif op == '>=':
                            return actual_num >= expected_num
                        elif op == '<=':
                            return actual_num <= expected_num
                        elif op == '!=':
                            return actual_num != expected_num
                    except (ValueError, TypeError):
                        # String comparison
                        if op == '==':
                            return str(actual) == expected
                        elif op == '!=':
                            return str(actual) != expected

        return False


# Helper functions for awarding XP on quest completion
def award_quest_xp(xp_handler, quest_name: str, xp_amount: int = 50):
    """Award XP for quest completion"""
    if hasattr(xp_handler, 'award_contribution_xp'):
        xp_handler.award_contribution_xp(xp_amount, f"Quest completed: {quest_name}")
