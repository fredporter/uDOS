"""
Smart Command Predictor (v1.2.13)

Provides intelligent command completion with:
- Syntax-aware suggestions from commands.json
- Real-time COMMAND token highlighting
- Arrow key selection interface
- Learning from command history
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
import re


@dataclass
class Prediction:
    """A single command prediction"""
    text: str
    confidence: float  # 0.0 - 1.0
    source: str  # "history", "schema", "fuzzy"
    description: Optional[str] = None
    syntax: Optional[str] = None
    category: Optional[str] = None


@dataclass
class Token:
    """Highlighted token in command"""
    text: str
    type: str  # "command", "arg", "path", "flag", "value"
    start: int
    end: int
    color: str = "white"


class CommandPredictor:
    """
    Smart command prediction engine.
    
    Features:
    - Loads command schemas from core/data/commands.json
    - Tracks command frequency from history
    - Provides ranked predictions with confidence scores
    - Real-time syntax highlighting
    - Fuzzy matching for typo tolerance
    """
    
    def __init__(self, commands_file: str = None):
        from core.utils.paths import PATHS
        if commands_file is None:
            commands_file = str(PATHS.CORE_DATA / "commands.json")
        
        self.commands_file = Path(commands_file)
        self.commands: Dict[str, Dict] = {}
        self.command_list: List[str] = []
        self.frequency_map: Dict[str, int] = {}
        self.recent_commands: List[str] = []
        
        self._load_commands()
    
    def _load_commands(self):
        """Load command schemas"""
        if self.commands_file.exists():
            try:
                with open(self.commands_file) as f:
                    data = json.load(f)
                    self.commands = data.get('commands', {})
                    self.command_list = sorted(self.commands.keys())
            except Exception as e:
                print(f"Warning: Could not load commands.json: {e}")
    
    def predict(self, partial: str, max_results: int = 10) -> List[Prediction]:
        """
        Generate predictions for partial command input.
        
        Args:
            partial: Current text being typed
            max_results: Maximum predictions to return
            
        Returns:
            List of predictions ranked by confidence
        """
        if not partial:
            # Show most frequent/recent commands
            return self._get_recent_predictions(max_results)
        
        predictions = []
        partial_lower = partial.lower()
        words = partial.split()
        
        # Extract command part (first word)
        cmd_partial = words[0] if words else ""
        
        # 1. Exact prefix matches from schema (highest confidence)
        for cmd in self.command_list:
            if cmd.lower().startswith(cmd_partial.lower()):
                confidence = 0.9
                # Boost if in history
                if cmd in self.frequency_map:
                    confidence += min(0.1, self.frequency_map[cmd] / 100)
                
                schema = self.commands.get(cmd, {})
                predictions.append(Prediction(
                    text=cmd,
                    confidence=min(1.0, confidence),
                    source="schema",
                    description=schema.get('description', ''),
                    syntax=schema.get('syntax', ''),
                    category=schema.get('category', 'general')
                ))
        
        # 2. History matches (medium confidence)
        for recent in self.recent_commands[-50:]:
            recent_cmd = recent.split()[0] if recent.split() else recent
            if recent_cmd.lower().startswith(cmd_partial.lower()):
                # Don't duplicate schema matches
                if not any(p.text == recent_cmd and p.source == "schema" for p in predictions):
                    predictions.append(Prediction(
                        text=recent_cmd,
                        confidence=0.7,
                        source="history",
                        description=f"Recent: {recent}"
                    ))
        
        # 3. Fuzzy matches (lower confidence)
        if len(cmd_partial) >= 3:
            for cmd in self.command_list:
                if cmd not in [p.text for p in predictions]:
                    similarity = self._fuzzy_score(cmd_partial.lower(), cmd.lower())
                    if similarity > 0.6:
                        schema = self.commands.get(cmd, {})
                        predictions.append(Prediction(
                            text=cmd,
                            confidence=similarity * 0.6,
                            source="fuzzy",
                            description=schema.get('description', ''),
                            syntax=schema.get('syntax', '')
                        ))
        
        # 4. If typing full command + args, suggest completions
        if len(words) > 1:
            cmd = words[0].upper()
            if cmd in self.commands:
                arg_predictions = self._predict_arguments(cmd, words[1:])
                predictions.extend(arg_predictions)
        
        # Sort by confidence and return top N
        predictions.sort(key=lambda p: p.confidence, reverse=True)
        return predictions[:max_results]
    
    def _get_recent_predictions(self, max_results: int) -> List[Prediction]:
        """Get predictions based on recent commands"""
        predictions = []
        
        # Show top 5 most frequent
        sorted_freq = sorted(self.frequency_map.items(), key=lambda x: x[1], reverse=True)
        for cmd, count in sorted_freq[:5]:
            schema = self.commands.get(cmd, {})
            predictions.append(Prediction(
                text=cmd,
                confidence=0.8,
                source="history",
                description=f"Used {count} times - {schema.get('description', '')}",
                syntax=schema.get('syntax', '')
            ))
        
        # Add recent unique commands
        seen = {p.text for p in predictions}
        for recent in reversed(self.recent_commands[-20:]):
            cmd = recent.split()[0] if recent.split() else recent
            if cmd not in seen:
                predictions.append(Prediction(
                    text=cmd,
                    confidence=0.6,
                    source="history",
                    description=f"Recent: {recent}"
                ))
                seen.add(cmd)
                if len(predictions) >= max_results:
                    break
        
        return predictions[:max_results]
    
    def _predict_arguments(self, command: str, current_args: List[str]) -> List[Prediction]:
        """Predict next argument based on command schema"""
        predictions = []
        schema = self.commands.get(command, {})
        
        # Get expected arguments from schema
        args_schema = schema.get('args', [])
        if not args_schema:
            return predictions
        
        # Determine which argument position we're at
        arg_index = len(current_args) - 1
        if arg_index < 0 or arg_index >= len(args_schema):
            return predictions
        
        arg_def = args_schema[arg_index]
        arg_type = arg_def.get('type', 'string')
        
        # Suggest based on type
        if arg_type == 'file':
            # Could integrate with file browser here
            predictions.append(Prediction(
                text="<file>",
                confidence=0.5,
                source="schema",
                description="Press Tab for file browser"
            ))
        elif arg_type == 'path':
            predictions.append(Prediction(
                text="<path>",
                confidence=0.5,
                source="schema",
                description=arg_def.get('description', 'Path argument')
            ))
        elif 'options' in arg_def:
            # Suggest from predefined options
            for option in arg_def['options']:
                predictions.append(Prediction(
                    text=option,
                    confidence=0.7,
                    source="schema",
                    description=f"Valid option for {arg_def.get('name', 'arg')}"
                ))
        
        return predictions
    
    def _fuzzy_score(self, text: str, target: str) -> float:
        """Calculate fuzzy match score (0.0 - 1.0)"""
        # Simple Levenshtein-like scoring
        if text == target:
            return 1.0
        
        # Check for substring match
        if text in target:
            return 0.8
        
        # Count matching characters in order
        matches = 0
        target_idx = 0
        for char in text:
            if target_idx < len(target) and char == target[target_idx]:
                matches += 1
                target_idx += 1
        
        return matches / max(len(text), len(target))
    
    def tokenize(self, command: str) -> List[Token]:
        """
        Parse command into highlighted tokens.
        
        Returns list of tokens with type and color info for display.
        """
        tokens = []
        words = command.split()
        
        if not words:
            return tokens
        
        position = 0
        
        # First word is the command
        cmd = words[0]
        cmd_upper = cmd.upper()
        
        # Check if it's a valid command
        is_valid_cmd = cmd_upper in self.commands
        tokens.append(Token(
            text=cmd,
            type="command",
            start=position,
            end=position + len(cmd),
            color="green" if is_valid_cmd else "yellow"
        ))
        position += len(cmd) + 1
        
        # Parse remaining arguments
        for i, word in enumerate(words[1:], 1):
            # Detect token type
            if word.startswith('-'):
                # Flag
                tokens.append(Token(
                    text=word,
                    type="flag",
                    start=position,
                    end=position + len(word),
                    color="cyan"
                ))
            elif '/' in word or '\\' in word or word.endswith('.upy') or word.endswith('.md') or word.endswith('.json'):
                # Path
                tokens.append(Token(
                    text=word,
                    type="path",
                    start=position,
                    end=position + len(word),
                    color="magenta"
                ))
            elif word.isdigit():
                # Number
                tokens.append(Token(
                    text=word,
                    type="value",
                    start=position,
                    end=position + len(word),
                    color="blue"
                ))
            else:
                # Generic argument
                tokens.append(Token(
                    text=word,
                    type="arg",
                    start=position,
                    end=position + len(word),
                    color="white"
                ))
            
            position += len(word) + 1
        
        return tokens
    
    def add_to_history(self, command: str):
        """Record command execution for learning"""
        if not command:
            return
        
        # Extract base command
        cmd = command.split()[0] if command.split() else command
        cmd_upper = cmd.upper()
        
        # Update frequency
        if cmd_upper in self.commands:
            self.frequency_map[cmd_upper] = self.frequency_map.get(cmd_upper, 0) + 1
        
        # Add to recent
        self.recent_commands.append(command)
        if len(self.recent_commands) > 100:
            self.recent_commands = self.recent_commands[-100:]
    
    def get_command_help(self, command: str) -> Optional[Dict]:
        """Get full schema info for a command"""
        cmd_upper = command.upper()
        return self.commands.get(cmd_upper)
    
    def format_prediction(self, prediction: Prediction, width: int = 60) -> str:
        """
        Format prediction for display.
        
        Returns colored/formatted string for terminal output.
        """
        # Truncate description if needed
        desc = prediction.description or ""
        if len(desc) > width - len(prediction.text) - 10:
            desc = desc[:width - len(prediction.text) - 13] + "..."
        
        confidence_bar = "█" * int(prediction.confidence * 5)
        
        return f"{prediction.text:<15} {confidence_bar:<5} {desc}"
    
    def save_state(self, path: Path):
        """Save learning state"""
        state_data = {
            "frequency_map": self.frequency_map,
            "recent_commands": self.recent_commands[-100:]
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(state_data, f, indent=2)
    
    def load_state(self, path: Path):
        """Load learning state"""
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            self.frequency_map = data.get('frequency_map', {})
            self.recent_commands = data.get('recent_commands', [])
