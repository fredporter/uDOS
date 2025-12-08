"""
.upy Adventure Script Parser
Converts .upy adventure scripts to ScenarioEngine event format

Round 2: STORY Command Extension
"""

import re
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class UPYParseError(Exception):
    """Exception raised for parsing errors in .upy files"""
    pass


class UPYAdventureParser:
    """
    Parser for .upy adventure script format

    Converts .upy scripts with CHOICE/OPTION/LABEL/ROLL/IF keywords
    into ScenarioEngine-compatible event structures.
    """

    def __init__(self):
        self.labels = {}  # label_name -> line_number
        self.events = []  # Parsed events list
        self.variables = {}  # Variable storage during parsing
        self.flags = set()  # Story flags
        self.line_number = 0
        self.current_event = None

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a .upy adventure file

        Args:
            file_path: Path to .upy file

        Returns:
            Dict with scenario structure compatible with ScenarioEngine
        """
        path = Path(file_path)
        if not path.exists():
            raise UPYParseError(f"File not found: {file_path}")

        # Read file
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Extract metadata from comments at top
        metadata = self._extract_metadata(lines)

        # First pass: Find all labels
        self._find_labels(lines)

        # Second pass: Parse commands and build events
        self._parse_commands(lines)

        # Build scenario structure
        scenario = {
            "metadata": metadata,
            "events": self.events,
            "labels": self.labels,
            "variables": self.variables,
            "flags": list(self.flags)
        }

        return scenario

    def _extract_metadata(self, lines: List[str]) -> Dict[str, Any]:
        """Extract metadata from file header comments"""
        metadata = {
            "name": "unknown",
            "description": "",
            "author": "unknown",
            "version": "1.0",
            "created": datetime.now().isoformat()
        }

        # Look for comments in first 10 lines
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            if line.startswith('#') and not line.startswith('#!/'):
                # Extract title from first comment line
                if i == 1 or (i == 2 and lines[0].startswith('#!')):
                    parts = line.lstrip('#').strip().split('-', 1)
                    if parts:
                        metadata["name"] = parts[0].strip()
                        if len(parts) > 1:
                            metadata["description"] = parts[1].strip()

        return metadata

    def _find_labels(self, lines: List[str]):
        """First pass: Find all LABEL declarations"""
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('LABEL ['):
                match = re.match(r'LABEL\s+\[([^\]]+)\]', line)
                if match:
                    label_name = match.group(1).strip()
                    self.labels[label_name] = i

    def _parse_commands(self, lines: List[str]):
        """Second pass: Parse commands and build event structure"""
        i = 0
        while i < len(lines):
            self.line_number = i + 1
            line = lines[i].strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                i += 1
                continue

            # Parse different command types
            if line.startswith('PRINT ['):
                self._parse_print(line)
            elif line.startswith('CHOICE ['):
                # Multi-line CHOICE block
                i = self._parse_choice(lines, i)
            elif line.startswith('LABEL ['):
                self._parse_label(line)
            elif line.startswith('BRANCH ['):
                self._parse_branch(line)
            elif line.startswith('ROLL ['):
                self._parse_roll(line)
            elif line.startswith('IF ['):
                # Multi-line IF block
                i = self._parse_if(lines, i)
            elif line.startswith('XP ['):
                self._parse_xp(line)
            elif line.startswith('HP ['):
                self._parse_hp(line)
            elif line.startswith('STAMINA ['):
                self._parse_stamina(line)
            elif line.startswith('THIRST ['):
                self._parse_thirst(line)
            elif line.startswith('HUNGER ['):
                self._parse_hunger(line)
            elif line.startswith('FLAG ['):
                self._parse_flag(line)
            elif line.startswith('GIVE ['):
                self._parse_give(line)
            elif line.startswith('TAKE ['):
                self._parse_take(line)
            elif line.startswith('SET ['):
                self._parse_set(line)
            elif line.startswith('ENDIF'):
                pass  # Handled in _parse_if
            else:
                # Unknown command - skip with warning
                pass

            i += 1

    def _parse_print(self, line: str):
        """Parse PRINT command - creates narrative event"""
        match = re.match(r'PRINT\s+\[([^\]]*)\]', line)
        if match:
            text = match.group(1).strip()

            # If current event is narrative, append to it
            if self.current_event and self.current_event.get("type") == "narrative":
                self.current_event["content"] += "\n" + text
            else:
                # Create new narrative event
                event = {
                    "id": f"event_{len(self.events) + 1}",
                    "type": "narrative",
                    "content": text,
                    "effects": []
                }
                self.events.append(event)
                self.current_event = event

    def _parse_choice(self, lines: List[str], start_idx: int) -> int:
        """Parse CHOICE block with OPTION lines"""
        line = lines[start_idx].strip()
        match = re.match(r'CHOICE\s+\[([^\]]+)\]', line)
        if not match:
            raise UPYParseError(f"Line {self.line_number}: Invalid CHOICE syntax")

        question = match.group(1).strip()

        # Collect OPTIONS
        options = []
        i = start_idx + 1
        while i < len(lines):
            opt_line = lines[i].strip()
            if not opt_line or opt_line.startswith('#'):
                i += 1
                continue
            if not opt_line.startswith('OPTION ['):
                break  # End of CHOICE block

            # Parse OPTION
            opt_match = re.match(r'OPTION\s+\[([^\]]+)\]\s*→\s*([A-Z0-9\-_]+)', opt_line)
            if opt_match:
                option_text = opt_match.group(1).strip()
                target_label = opt_match.group(2).strip()
                options.append({
                    "text": option_text,
                    "next_event": target_label
                })
            i += 1

        # Create choice event
        event = {
            "id": f"event_{len(self.events) + 1}",
            "type": "choice",
            "content": question,
            "choices": options,
            "effects": []
        }
        self.events.append(event)
        self.current_event = event

        return i - 1  # Return last processed line index

    def _parse_label(self, line: str):
        """Parse LABEL - creates checkpoint event"""
        match = re.match(r'LABEL\s+\[([^\]]+)\]', line)
        if match:
            label_name = match.group(1).strip()
            event = {
                "id": label_name,
                "type": "checkpoint",
                "label": label_name,
                "content": f"Checkpoint: {label_name}",
                "effects": []
            }
            self.events.append(event)
            self.current_event = event

    def _parse_branch(self, line: str):
        """Parse BRANCH - unconditional jump"""
        match = re.match(r'BRANCH\s+\[([^\]]+)\]', line)
        if match:
            target = match.group(1).strip()
            # Add branch effect to current event
            if self.current_event:
                self.current_event.setdefault("branch_target", target)

    def _parse_roll(self, line: str):
        """Parse ROLL - dice roll and store result"""
        match = re.match(r'ROLL\s+\[([^\]]+)\]\s*→\s*(\$[A-Z0-9\-_]+)', line)
        if match:
            dice_expr = match.group(1).strip()
            var_name = match.group(2).strip()

            # Execute dice roll
            result = self._roll_dice(dice_expr)
            self.variables[var_name] = result

            # Add roll effect to current event
            if self.current_event:
                self.current_event["effects"].append({
                    "type": "dice_roll",
                    "expression": dice_expr,
                    "variable": var_name,
                    "result": result
                })

    def _parse_if(self, lines: List[str], start_idx: int) -> int:
        """Parse IF block with conditional logic"""
        line = lines[start_idx].strip()
        match = re.match(r'IF\s+\[([^\]]+)\]', line)
        if not match:
            raise UPYParseError(f"Line {self.line_number}: Invalid IF syntax")

        condition = match.group(1).strip()

        # Parse condition
        condition_met = self._evaluate_condition(condition)

        # Find ENDIF
        endif_idx = start_idx + 1
        depth = 1
        while endif_idx < len(lines) and depth > 0:
            if lines[endif_idx].strip().startswith('IF ['):
                depth += 1
            elif lines[endif_idx].strip() == 'ENDIF':
                depth -= 1
            endif_idx += 1

        # If condition met, parse block contents
        if condition_met:
            i = start_idx + 1
            while i < endif_idx - 1:
                self.line_number = i + 1
                inner_line = lines[i].strip()

                if inner_line and not inner_line.startswith('#'):
                    if inner_line.startswith('PRINT ['):
                        self._parse_print(inner_line)
                    elif inner_line.startswith('XP ['):
                        self._parse_xp(inner_line)
                    elif inner_line.startswith('HP ['):
                        self._parse_hp(inner_line)
                    elif inner_line.startswith('FLAG ['):
                        self._parse_flag(inner_line)
                    elif inner_line.startswith('BRANCH ['):
                        self._parse_branch(inner_line)

                i += 1

        return endif_idx - 1

    def _parse_xp(self, line: str):
        """Parse XP award/penalty"""
        match = re.match(r'XP\s+\[([+\-]?\d+)\]', line)
        if match:
            amount = int(match.group(1))
            if self.current_event:
                self.current_event["effects"].append({
                    "type": "xp_award",
                    "value": amount
                })

    def _parse_hp(self, line: str):
        """Parse HP modification"""
        match = re.match(r'HP\s+\[([+\-]?\d+)\]', line)
        if match:
            amount = int(match.group(1))
            if self.current_event:
                self.current_event["effects"].append({
                    "type": "stat_change",
                    "target": "health",
                    "value": amount
                })

    def _parse_stamina(self, line: str):
        """Parse STAMINA modification"""
        match = re.match(r'STAMINA\s+\[([+\-]?\d+)\]', line)
        if match:
            amount = int(match.group(1))
            if self.current_event:
                self.current_event["effects"].append({
                    "type": "stat_change",
                    "target": "stamina",
                    "value": amount
                })

    def _parse_thirst(self, line: str):
        """Parse THIRST modification"""
        match = re.match(r'THIRST\s+\[([+\-]?\d+)\]', line)
        if match:
            amount = int(match.group(1))
            if self.current_event:
                self.current_event["effects"].append({
                    "type": "stat_change",
                    "target": "thirst",
                    "value": amount
                })

    def _parse_hunger(self, line: str):
        """Parse HUNGER modification"""
        match = re.match(r'HUNGER\s+\[([+\-]?\d+)\]', line)
        if match:
            amount = int(match.group(1))
            if self.current_event:
                self.current_event["effects"].append({
                    "type": "stat_change",
                    "target": "hunger",
                    "value": amount
                })

    def _parse_flag(self, line: str):
        """Parse FLAG setting"""
        match = re.match(r'FLAG\s+\[([a-z0-9_]+)\]', line)
        if match:
            flag_name = match.group(1).strip()
            self.flags.add(flag_name)
            if self.current_event:
                self.current_event["effects"].append({
                    "type": "flag_set",
                    "flag": flag_name,
                    "value": True
                })

    def _parse_give(self, line: str):
        """Parse GIVE (add item to inventory)"""
        match = re.match(r'GIVE\s+\[([a-z0-9_]+)\]', line)
        if match:
            item_name = match.group(1).strip()
            if self.current_event:
                self.current_event["effects"].append({
                    "type": "item_give",
                    "item": item_name,
                    "quantity": 1
                })

    def _parse_take(self, line: str):
        """Parse TAKE (remove item from inventory)"""
        match = re.match(r'TAKE\s+\[([a-z0-9_]+)\]', line)
        if match:
            item_name = match.group(1).strip()
            if self.current_event:
                self.current_event["effects"].append({
                    "type": "item_take",
                    "item": item_name,
                    "quantity": 1
                })

    def _parse_set(self, line: str):
        """Parse SET variable assignment"""
        match = re.match(r'SET\s+\[\s*(\$[A-Z0-9\-_]+)\s*=\s*(.+)\]', line)
        if match:
            var_name = match.group(1).strip()
            var_value = match.group(2).strip().strip('"\'')

            # Try to parse as number
            try:
                if '.' in var_value:
                    var_value = float(var_value)
                else:
                    var_value = int(var_value)
            except ValueError:
                pass  # Keep as string

            self.variables[var_name] = var_value

    def _evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate conditional expression

        Examples:
            $TRACKING >= 14
            $HP < 50
            FLAG:found_water
        """
        # Flag check
        if condition.startswith('FLAG:'):
            flag_name = condition[5:].strip()
            return flag_name in self.flags

        # Variable comparison
        match = re.match(r'(\$[A-Z0-9\-_]+)\s*([><=!]+)\s*(\d+)', condition)
        if match:
            var_name = match.group(1)
            operator = match.group(2)
            value = int(match.group(3))

            var_val = self.variables.get(var_name, 0)

            if operator == '>=':
                return var_val >= value
            elif operator == '<=':
                return var_val <= value
            elif operator == '>':
                return var_val > value
            elif operator == '<':
                return var_val < value
            elif operator == '==':
                return var_val == value
            elif operator == '!=':
                return var_val != value

        return False

    def _roll_dice(self, expression: str) -> int:
        """
        Roll dice from expression

        Formats:
            1d20 - Roll 1 twenty-sided die
            2d6 - Roll 2 six-sided dice
            1d100 - Roll 1 hundred-sided die
            2d6+3 - Roll 2d6 and add 3
        """
        # Parse XdY+Z format
        match = re.match(r'(\d+)d(\d+)(?:([+\-])(\d+))?', expression.lower())
        if not match:
            return 0

        num_dice = int(match.group(1))
        die_size = int(match.group(2))
        modifier = 0

        if match.group(3):
            modifier = int(match.group(4))
            if match.group(3) == '-':
                modifier = -modifier

        # Roll dice
        result = sum(random.randint(1, die_size) for _ in range(num_dice))
        return result + modifier


def parse_upy_adventure(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to parse a .upy adventure file

    Args:
        file_path: Path to .upy file

    Returns:
        Parsed scenario structure
    """
    parser = UPYAdventureParser()
    return parser.parse_file(file_path)
