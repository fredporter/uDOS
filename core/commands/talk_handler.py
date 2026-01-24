"""
Talk Handler

Handle conversations with NPCs using the dialogue engine.
"""

from typing import Dict, List, Any
from .base import BaseCommandHandler
from .npc_handler import NPCHandler
from .dialogue_engine import DialogueEngine
from core.tui.output import OutputToolkit


class TalkHandler(BaseCommandHandler):
    """Handle TALK command for NPC conversations"""

    def __init__(self, npc_handler: NPCHandler, dialogue_engine: DialogueEngine):
        """Initialize talk handler"""
        super().__init__()
        self.npc_handler = npc_handler
        self.dialogue_engine = dialogue_engine
        self.active_conversations: Dict[str, Dict[str, Any]] = (
            {}
        )  # player_id -> conversation_state

    def handle(
        self, command: str, params: List[str], grid: Any, parser: Any
    ) -> Dict[str, Any]:
        """Route TALK commands"""
        if command == "TALK":
            return self._handle_talk(params)
        elif command == "REPLY":
            return self._handle_reply(params)
        else:
            return {"status": "error", "message": f"Unknown command: {command}"}

    def _handle_talk(self, params: List[str]) -> Dict[str, Any]:
        """Initiate conversation with NPC"""
        if not params:
            return {
                "status": "error",
                "message": "Usage: TALK <npc_name>",
                "suggestion": "Example: TALK Kenji",
            }

        npc_name = " ".join(params)
        player_id = "player1"  # TODO: Get from game state

        # Find NPC by name
        npc = self._find_npc_by_name(npc_name)
        if not npc:
            return {
                "status": "error",
                "message": f"NPC not found: {npc_name}",
                "suggestion": "Use NPC <location> to see NPCs nearby",
            }

        # Get dialogue tree
        tree_id = npc.get("dialogue_tree", "merchant_generic")
        context = self._build_context(npc, player_id)

        # Start conversation
        result = self.dialogue_engine.start_conversation(tree_id, context)

        if result["status"] == "success":
            # Store conversation state
            self.active_conversations[player_id] = {
                "npc_id": npc["id"],
                "npc_name": npc["name"],
                "tree_id": tree_id,
                "current_node": result["node_id"],
            }

            options = result.get("options", [])
            if options:
                option_rows = [[str(i + 1), opt.get("text", "")] for i, opt in enumerate(options)]
                options_block = OutputToolkit.table(["#", "option"], option_rows)
            else:
                options_block = "No options available."

            output = "\n".join(
                [
                    OutputToolkit.banner(f"TALK {npc['name'].upper()}"),
                    result["text"],
                    "",
                    "Options:",
                    options_block,
                ]
            )

            return {
                "status": "success",
                "npc": npc["name"],
                "text": result["text"],
                "options": result["options"],
                "output": output,
                "conversation_active": True,
            }

        return result

    def _handle_reply(self, params: List[str]) -> Dict[str, Any]:
        """Reply to NPC dialogue option"""
        if not params:
            return {
                "status": "error",
                "message": "Usage: REPLY <option_number>",
                "suggestion": "Example: REPLY 1",
            }

        player_id = "player1"  # TODO: Get from game state

        # Check if conversation is active
        if player_id not in self.active_conversations:
            return {
                "status": "error",
                "message": "No active conversation",
                "suggestion": "Use TALK <npc_name> to start a conversation",
            }

        try:
            option_num = int(params[0]) - 1  # Convert to 0-indexed
        except ValueError:
            return {
                "status": "error",
                "message": "Invalid option number",
                "suggestion": "Use a number like: REPLY 1",
            }

        conv_state = self.active_conversations[player_id]
        tree_id = conv_state["tree_id"]
        npc_id = conv_state["npc_id"]

        # Get current dialogue node
        tree = self.dialogue_engine.get_tree(tree_id)
        if not tree:
            return {"status": "error", "message": "Dialogue tree not found"}

        current_node = tree.get_node(conv_state["current_node"])
        if not current_node:
            return {"status": "error", "message": "Current dialogue node not found"}

        # Validate option
        if option_num < 0 or option_num >= len(current_node.options):
            return {
                "status": "error",
                "message": f"Invalid option: {option_num + 1}",
                "suggestion": f"Choose 1-{len(current_node.options)}",
            }

        selected_option = current_node.options[option_num]
        next_node_id = selected_option.get("next")

        if not next_node_id:
            # End conversation
            del self.active_conversations[player_id]
            return {
                "status": "success",
                "message": "Conversation ended",
                "output": OutputToolkit.banner("CONVERSATION ENDED"),
                "conversation_active": False,
            }

        # Continue conversation
        npc = self.npc_handler.get_npc_by_id(npc_id)
        context = self._build_context(npc, player_id)

        result = self.dialogue_engine.continue_conversation(
            tree_id, next_node_id, context
        )

        if result["status"] == "success":
            conv_state["current_node"] = next_node_id

            # Check if conversation is complete
            if result.get("complete", False):
                del self.active_conversations[player_id]

            options = result.get("options", [])
            if options:
                option_rows = [[str(i + 1), opt.get("text", "")] for i, opt in enumerate(options)]
                options_block = OutputToolkit.table(["#", "option"], option_rows)
            else:
                options_block = "No options available."

            output = "\n".join(
                [
                    OutputToolkit.banner(f"TALK {conv_state['npc_name'].upper()}"),
                    result["text"],
                    "",
                    "Options:",
                    options_block,
                ]
            )

            return {
                "status": "success",
                "npc": conv_state["npc_name"],
                "text": result["text"],
                "options": result.get("options", []),
                "output": output,
                "conversation_active": not result.get("complete", False),
                "action": selected_option.get(
                    "action"
                ),  # For quest acceptance, combat, etc.
            }

        return result

    def _find_npc_by_name(self, npc_name: str) -> Dict[str, Any]:
        """Find NPC by name (case-insensitive)"""
        npc_name_lower = npc_name.lower()
        for npc in self.npc_handler.npcs.values():
            if npc["name"].lower() == npc_name_lower:
                return npc
        return None

    def _build_context(self, npc: Dict[str, Any], player_id: str) -> Dict[str, Any]:
        """Build context for dialogue conditions"""
        return {
            "npc": npc,
            "player_id": player_id,
            "player_level": 1,  # TODO: Get from game state
            "player_gold": 100,  # TODO: Get from game state
            "player_inventory": [],  # TODO: Get from game state
        }

    def end_conversation(self, player_id: str):
        """End active conversation for player"""
        if player_id in self.active_conversations:
            del self.active_conversations[player_id]
