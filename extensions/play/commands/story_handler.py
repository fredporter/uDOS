"""
STORY Command Handler - Adventure Management System
Integrates with SPRITE and OBJECT variables for interactive .upy adventures.

Version: v1.1.9 Round 3 - Refactored with command registry
"""

import json
import random
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import variable manager and command registry
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from core.utils.variables import VariableManager
from core.utils.command_registry import command


class AdventureEngine:
    """Execute .upy adventure scripts with SPRITE/OBJECT integration."""

    def __init__(self, vm: VariableManager):
        """
        Initialize adventure engine.

        Args:
            vm: VariableManager instance for variable access
        """
        self.vm = vm
        self.current_adventure = None
        self.choice_pending = None
        self.labels = {}  # Label positions for GOTO/BRANCH

    def load_adventure(self, adventure_path: str) -> bool:
        """
        Load an adventure script.

        Args:
            adventure_path: Path to .upy adventure file

        Returns:
            True if loaded successfully
        """
        path = Path(adventure_path)
        if not path.exists():
            print(f"❌ Adventure not found: {adventure_path}")
            return False

        try:
            with open(path, 'r') as f:
                self.current_adventure = {
                    'path': str(path),
                    'name': path.stem,
                    'lines': f.readlines(),
                    'line_num': 0
                }

            # Pre-parse labels
            self._parse_labels()

            # Set story variables
            self.vm.set_variable('STORY-CURRENT', path.stem, 'session')
            self.vm.set_variable('STORY-CHAPTER', 1, 'session')

            print(f"✅ Loaded adventure: {path.stem}")
            return True

        except Exception as e:
            print(f"❌ Error loading adventure: {e}")
            return False

    def _parse_labels(self):
        """Pre-parse all LABEL definitions."""
        self.labels = {}
        if not self.current_adventure:
            return

        for i, line in enumerate(self.current_adventure['lines']):
            line = line.strip()
            if line.startswith('LABEL [') and line.endswith(']'):
                label_name = line[7:-1]  # Extract label name
                self.labels[label_name] = i

    def execute(self) -> bool:
        """
        Execute the current adventure line by line.

        Returns:
            True if adventure completed successfully
        """
        if not self.current_adventure:
            print("❌ No adventure loaded")
            return False

        lines = self.current_adventure['lines']
        line_num = self.current_adventure['line_num']

        while line_num < len(lines):
            line = lines[line_num].strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                line_num += 1
                continue

            # Execute command
            should_continue, new_line_num = self._execute_line(line, line_num)

            if new_line_num is not None:
                line_num = new_line_num
            else:
                line_num += 1

            # Update current position
            self.current_adventure['line_num'] = line_num

            if not should_continue:
                break

        return True

    def _execute_line(self, line: str, current_line: int) -> tuple[bool, Optional[int]]:
        """
        Execute a single adventure command.

        Returns:
            Tuple of (should_continue, new_line_number)
        """
        # SET command
        if line.startswith('SET ['):
            return self._cmd_set(line), None

        # PRINT command
        elif line.startswith('PRINT ['):
            return self._cmd_print(line), None

        # CHOICE command
        elif line.startswith('CHOICE ['):
            return self._cmd_choice(line, current_line), None

        # OPTION command (part of CHOICE)
        elif line.startswith('OPTION ['):
            return True, None  # Handled by CHOICE

        # LABEL command
        elif line.startswith('LABEL ['):
            return True, None  # Just a marker, skip

        # BRANCH command
        elif line.startswith('BRANCH [') or line.startswith('→ BRANCH-'):
            return True, self._cmd_branch(line)

        # ROLL command (dice roll)
        elif line.startswith('ROLL ['):
            return self._cmd_roll(line), None

        # IF command
        elif line.startswith('IF ['):
            return self._cmd_if(line, current_line), None

        # ENDIF command
        elif line.startswith('ENDIF'):
            return True, None

        # XP command (award experience)
        elif line.startswith('XP ['):
            return self._cmd_xp(line), None

        # HP command (modify health)
        elif line.startswith('HP ['):
            return self._cmd_hp(line), None

        # ITEM command (add to inventory)
        elif line.startswith('ITEM ['):
            return self._cmd_item(line), None

        # FLAG command (set story flag)
        elif line.startswith('FLAG ['):
            return self._cmd_flag(line), None

        # END command
        elif line.startswith('END'):
            return False, None

        else:
            # Unknown command, just print it
            print(line)
            return True, None

    def _cmd_set(self, line: str) -> bool:
        """Execute SET [$VAR = value]."""
        # Parse: SET [$VAR = value]
        content = line[5:-1]  # Remove 'SET [' and ']'

        if '=' in content:
            var_part, value_part = content.split('=', 1)
            var_name = var_part.strip().lstrip('$')
            value_str = value_part.strip().strip('"')

            # Try to parse as number
            try:
                if '.' in value_str:
                    value = float(value_str)
                else:
                    value = int(value_str)
            except ValueError:
                value = value_str

            self.vm.set_variable(var_name, value, 'session')

        return True

    def _cmd_print(self, line: str) -> bool:
        """Execute PRINT [text with $VARS]."""
        content = line[7:-1]  # Remove 'PRINT [' and ']'
        resolved = self.vm.resolve(content)
        print(resolved)
        return True

    def _cmd_choice(self, line: str, current_line: int) -> bool:
        """Execute CHOICE [question] with following OPTIONs."""
        question = line[8:-1]  # Remove 'CHOICE [' and ']'
        print(f"\n{self.vm.resolve(question)}")

        # Find all OPTION lines following this CHOICE
        options = []
        lines = self.current_adventure['lines']
        i = current_line + 1

        while i < len(lines):
            opt_line = lines[i].strip()
            if opt_line.startswith('OPTION ['):
                # Parse: OPTION [text] → BRANCH-label
                parts = opt_line[8:-1].split('→')
                if len(parts) == 2:
                    option_text = parts[0].strip()
                    branch_target = parts[1].strip().replace('BRANCH-', '')
                    options.append((option_text, branch_target))
            elif opt_line and not opt_line.startswith('#'):
                # End of options
                break
            i += 1

        # Display options
        for idx, (text, _) in enumerate(options, 1):
            print(f"  {idx}. {text}")

        # Get user choice
        while True:
            try:
                choice = input("\nYour choice: ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    _, branch_target = options[choice_num - 1]

                    # Store choice in STORY-CHOICES
                    choices = self.vm.get_variable('STORY-CHOICES') or {}
                    choices[question] = options[choice_num - 1][0]
                    self.vm.set_variable('STORY-CHOICES', choices, 'session')

                    # Jump to branch
                    if branch_target in self.labels:
                        self.current_adventure['line_num'] = self.labels[branch_target]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(options)}")
            except (ValueError, EOFError):
                print("Invalid input")

        return True

    def _cmd_branch(self, line: str) -> int:
        """Execute BRANCH [label] - jump to label."""
        if '→ BRANCH-' in line:
            # From OPTION line
            label = line.split('→ BRANCH-')[1].strip()
        else:
            # Direct BRANCH command
            label = line[8:-1]  # Remove 'BRANCH [' and ']'

        if label in self.labels:
            return self.labels[label]
        else:
            print(f"⚠️  Label not found: {label}")
            return None

    def _cmd_roll(self, line: str) -> bool:
        """Execute ROLL [dice] → $VAR (e.g., ROLL [1d20] → $RESULT)."""
        content = line[6:]  # Remove 'ROLL ['

        # Remove trailing bracket if present
        if content.endswith(']'):
            content = content[:-1]

        parts = content.split('→')
        dice_str = parts[0].strip().rstrip(']')  # Remove any remaining bracket
        var_name = parts[1].strip().lstrip('$') if len(parts) > 1 else 'ROLL-RESULT'

        # Parse dice notation (e.g., "1d20", "2d6")
        if 'd' in dice_str:
            num_dice, die_size = dice_str.split('d')
            num_dice = int(num_dice)
            die_size = int(die_size)

            result = sum(random.randint(1, die_size) for _ in range(num_dice))
            self.vm.set_variable(var_name, result, 'local')

            print(f"🎲 Rolled {dice_str}: {result}")

        return True

    def _cmd_if(self, line: str, current_line: int) -> bool:
        """Execute IF [$VAR comparison value] block."""
        condition = line[4:-1]  # Remove 'IF [' and ']'

        # Parse condition (e.g., "$ROLL-RESULT > 15")
        for op in ['>=', '<=', '==', '!=', '>', '<']:
            if op in condition:
                left, right = condition.split(op)
                left_val = self._evaluate_value(left.strip())
                right_val = self._evaluate_value(right.strip())

                # Evaluate condition
                if op == '>':
                    condition_met = left_val > right_val
                elif op == '<':
                    condition_met = left_val < right_val
                elif op == '>=':
                    condition_met = left_val >= right_val
                elif op == '<=':
                    condition_met = left_val <= right_val
                elif op == '==':
                    condition_met = left_val == right_val
                elif op == '!=':
                    condition_met = left_val != right_val

                # If condition not met, skip to ENDIF
                if not condition_met:
                    self._skip_to_endif(current_line)

                return True

        return True

    def _skip_to_endif(self, current_line: int):
        """Skip lines until ENDIF is found."""
        lines = self.current_adventure['lines']
        i = current_line + 1
        depth = 1

        while i < len(lines) and depth > 0:
            line = lines[i].strip()
            if line.startswith('IF ['):
                depth += 1
            elif line.startswith('ENDIF'):
                depth -= 1
            i += 1

        self.current_adventure['line_num'] = i - 1

    def _evaluate_value(self, expr: str) -> Any:
        """Evaluate a value expression (variable or literal)."""
        expr = expr.strip()

        # Check if it's a variable
        if expr.startswith('$'):
            return self.vm.get_variable(expr.lstrip('$'), 0)

        # Try to parse as number
        try:
            if '.' in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            # String literal
            return expr.strip('"\'')

    def _cmd_xp(self, line: str) -> bool:
        """Execute XP [+/-amount] to modify experience."""
        amount_str = line[4:-1]  # Remove 'XP [' and ']'
        amount = int(amount_str)

        current_xp = self.vm.get_variable('SPRITE-XP', 0)
        new_xp = max(0, current_xp + amount)
        self.vm.set_variable('SPRITE-XP', new_xp, 'session')

        if amount > 0:
            print(f"✨ Gained {amount} XP! (Total: {new_xp})")
        else:
            print(f"⚠️  Lost {abs(amount)} XP (Total: {new_xp})")

        # Check for level up
        current_level = self.vm.get_variable('SPRITE-LEVEL', 1)
        xp_for_next = current_level * 100

        if new_xp >= xp_for_next:
            self.vm.set_variable('SPRITE-LEVEL', current_level + 1, 'session')
            print(f"🎉 Level up! Now level {current_level + 1}")

            # Restore HP on level up
            max_hp = self.vm.get_variable('SPRITE-HP-MAX', 100)
            self.vm.set_variable('SPRITE-HP', max_hp, 'session')
            print(f"❤️  HP fully restored!")

        return True

    def _cmd_hp(self, line: str) -> bool:
        """Execute HP [+/-amount] to modify health."""
        amount_str = line[4:-1]  # Remove 'HP [' and ']'
        amount = int(amount_str)

        current_hp = self.vm.get_variable('SPRITE-HP', 100)
        max_hp = self.vm.get_variable('SPRITE-HP-MAX', 100)
        new_hp = max(0, min(max_hp, current_hp + amount))

        self.vm.set_variable('SPRITE-HP', new_hp, 'session')

        if amount > 0:
            print(f"❤️  Restored {amount} HP (HP: {new_hp}/{max_hp})")
        else:
            print(f"💔 Lost {abs(amount)} HP (HP: {new_hp}/{max_hp})")

        if new_hp == 0:
            print("💀 You have died!")
            return False

        return True

    def _cmd_item(self, line: str) -> bool:
        """Execute ITEM [item_id] to add to inventory."""
        item_id = line[6:-1].strip()  # Remove 'ITEM [' and ']'

        inventory = self.vm.get_variable('SPRITE-INVENTORY', [])
        if not isinstance(inventory, list):
            inventory = []

        inventory.append(item_id)
        self.vm.set_variable('SPRITE-INVENTORY', inventory, 'session')

        print(f"📦 Added to inventory: {item_id}")

        return True

    def _cmd_flag(self, line: str) -> bool:
        """Execute FLAG [flag_name] to set story flag."""
        flag = line[6:-1].strip()  # Remove 'FLAG [' and ']'

        flags = self.vm.get_variable('STORY-FLAGS', [])
        if not isinstance(flags, list):
            flags = []

        if flag not in flags:
            flags.append(flag)
            self.vm.set_variable('STORY-FLAGS', flags, 'session')
            print(f"🏁 Story flag set: {flag}")

        return True


class StoryHandler:
    """Handler for STORY command - adventure management."""

    def __init__(self):
        self.vm = VariableManager()
        self.engine = AdventureEngine(self.vm)
        self.adventures_dir = Path("sandbox/ucode/adventures")

    def handle(self, args: List[str]) -> bool:
        """
        Handle STORY command.

        Commands:
            STORY                   - Show status
            STORY LIST              - List available adventures
            STORY RUN <name>        - Run an adventure
            STORY STATUS            - Show current adventure status
            STORY CREATE <name>     - Create new adventure from template
        """
        if not args:
            return self._show_status()

        subcommand = args[0].upper()

        if subcommand == 'LIST':
            return self._list_adventures()
        elif subcommand == 'RUN' and len(args) > 1:
            return self._run_adventure(args[1])
        elif subcommand == 'STATUS':
            return self._show_status()
        elif subcommand == 'CREATE' and len(args) > 1:
            return self._create_adventure(args[1])
        else:
            return self._show_help()

    def _show_status(self) -> bool:
        """Show current story/character status."""
        print("\n📖 Adventure Status")
        print("=" * 50)

        # Story info
        current_story = self.vm.get_variable('STORY-CURRENT', '')
        chapter = self.vm.get_variable('STORY-CHAPTER', 1)

        if current_story:
            print(f"Story: {current_story} (Chapter {chapter})")
        else:
            print("No active adventure")

        # Character info
        sprite_name = self.vm.get_variable('SPRITE-NAME', 'Survivor')
        sprite_level = self.vm.get_variable('SPRITE-LEVEL', 1)
        sprite_hp = self.vm.get_variable('SPRITE-HP', 100)
        sprite_hp_max = self.vm.get_variable('SPRITE-HP-MAX', 100)
        sprite_xp = self.vm.get_variable('SPRITE-XP', 0)
        sprite_gold = self.vm.get_variable('SPRITE-GOLD', 0)

        print(f"\n👤 Character: {sprite_name}")
        print(f"   Level: {sprite_level} | XP: {sprite_xp}")
        print(f"   HP: {sprite_hp}/{sprite_hp_max}")
        print(f"   Gold: {sprite_gold}")

        # Inventory
        inventory = self.vm.get_variable('SPRITE-INVENTORY', [])
        if inventory:
            print(f"\n📦 Inventory ({len(inventory)} items):")
            for item in inventory[:10]:  # Show first 10
                print(f"   • {item}")
            if len(inventory) > 10:
                print(f"   ... and {len(inventory) - 10} more")

        # Story progress
        flags = self.vm.get_variable('STORY-FLAGS', [])
        if flags:
            print(f"\n🏁 Progress ({len(flags)} events):")
            for flag in flags[:5]:
                print(f"   ✓ {flag}")
            if len(flags) > 5:
                print(f"   ... and {len(flags) - 5} more")

        print()
        return True

    def _list_adventures(self) -> bool:
        """List available adventure files."""
        if not self.adventures_dir.exists():
            print("📁 No adventures directory found")
            print(f"   Create: {self.adventures_dir}")
            return False

        adventures = list(self.adventures_dir.glob("*.upy"))

        if not adventures:
            print("📁 No adventures found")
            print(f"   Use: STORY CREATE <name> to create one")
            return True

        print("\n📚 Available Adventures")
        print("=" * 50)

        for adv in adventures:
            print(f"  • {adv.stem}")

        print(f"\n💡 Run with: STORY RUN <name>\n")
        return True

    def _run_adventure(self, name: str) -> bool:
        """Run an adventure script."""
        # Find adventure file
        adventure_path = self.adventures_dir / f"{name}.upy"

        if not adventure_path.exists():
            print(f"❌ Adventure not found: {name}")
            print(f"   Use: STORY LIST to see available adventures")
            return False

        # Load and execute
        if self.engine.load_adventure(str(adventure_path)):
            print(f"\n🎮 Starting adventure: {name}")
            print("=" * 50)
            return self.engine.execute()

        return False

    def _create_adventure(self, name: str) -> bool:
        """Create a new adventure from template."""
        self.adventures_dir.mkdir(parents=True, exist_ok=True)

        adventure_path = self.adventures_dir / f"{name}.upy"

        if adventure_path.exists():
            print(f"❌ Adventure already exists: {name}")
            return False

        # Load template
        template_path = Path("core/data/templates/adventure.template.upy")

        if template_path.exists():
            with open(template_path, 'r') as f:
                template = f.read()
        else:
            # Default template
            template = '''#!/usr/bin/env python3
# uPY Adventure: {name}

# Initialize character
SET [$SPRITE-NAME = "Hero"]
SET [$SPRITE-HP = 100]
SET [$SPRITE-LEVEL = 1]

PRINT [Welcome to {name}!]
PRINT [You are $SPRITE-NAME, a brave adventurer.]

# First choice
CHOICE [What do you want to do?]
  OPTION [Explore the forest] → BRANCH-FOREST
  OPTION [Visit the town] → BRANCH-TOWN

LABEL [BRANCH-FOREST]
PRINT [You venture into the dark forest...]
ROLL [1d20] → $EXPLORATION
IF [$EXPLORATION > 15]
  PRINT [You found a treasure chest!]
  ITEM [treasure_chest]
  XP [+50]
ENDIF
PRINT [Adventure continues...]
END

LABEL [BRANCH-TOWN]
PRINT [You walk to the nearby town...]
PRINT [The townspeople greet you warmly.]
XP [+25]
END
'''

        # Write adventure file
        with open(adventure_path, 'w') as f:
            f.write(template.replace('{name}', name))

        print(f"✅ Created adventure: {name}")
        print(f"   Edit: {adventure_path}")
        print(f"   Run: STORY RUN {name}")

        return True

    def _show_help(self) -> bool:
        """Show STORY command help."""
        print("""
📖 STORY Command - Adventure Management

Usage:
  STORY                   Show current status
  STORY LIST              List available adventures
  STORY RUN <name>        Run an adventure
  STORY STATUS            Show detailed status
  STORY CREATE <name>     Create new adventure

Examples:
  STORY LIST
  STORY RUN water_quest
  STORY CREATE my_adventure

Adventure Syntax (.upy files):
  SET [$VAR = value]              Set variable
  PRINT [text with $VARS]         Display text
  CHOICE [question]               Present choices
    OPTION [text] → BRANCH-label  Choice option
  LABEL [name]                    Define label
  BRANCH [label]                  Jump to label
  ROLL [1d20] → $VAR              Roll dice
  IF [$VAR > value]               Conditional
  XP [+/-amount]                  Modify experience
  HP [+/-amount]                  Modify health
  ITEM [item_id]                  Add to inventory
  FLAG [flag_name]                Set story flag
  END                             End adventure
""")
        return True


# Command registration for uDOS v1.1.9+
@command(
    "STORY",
    aliases=["ADVENTURE", "QUEST"],
    category="play",
    description="Manage and run interactive text adventures",
    usage="STORY [LIST|RUN <name>|CREATE <name>|STATUS]",
    examples=[
        "STORY LIST",
        "STORY RUN water_quest",
        "STORY CREATE my_adventure",
        "STORY STATUS"
    ],
    min_args=0,
    max_args=2,
    extension="play",
    version="1.1.9"
)
def story_command_handler(args: List[str]) -> bool:
    """
    STORY command handler using new registry system.

    Args:
        args: Command arguments

    Returns:
        True if successful
    """
    handler = StoryHandler()
    return handler.handle(args)


# Backward compatibility - old registration format
def register_command():
    """Register STORY command with uDOS (legacy format)."""
    handler = StoryHandler()
    return handler.handle
