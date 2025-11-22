# uDOS v1.0.0 - Parser

import json
import re

class Parser:
    def __init__(self, commands_file='knowledge/system/commands.json', theme='dungeon'):
        commands_list = self.load_json(commands_file)['COMMANDS']
        self.commands = {cmd['NAME']: cmd for cmd in commands_list}

        # Load theme lexicon
        theme_file = f'knowledge/system/themes/{theme.lower()}.json'
        theme_data = self.load_json(theme_file)
        self.lexicon = theme_data.get('TERMINOLOGY', {})
        self.reverse_lexicon = {v: k.replace('CMD_', '') for k, v in self.lexicon.items() if k.startswith('CMD_')}

    def load_json(self, file_path):
        with open(file_path, 'r') as f:
            return json.load(f)

    def translate_themed_command(self, user_input):
        command_word = user_input.split(' ')[0].upper()
        if command_word in self.reverse_lexicon:
            standard_command = self.reverse_lexicon[command_word]
            # Use regex to replace only the first word, case-insensitively
            return re.sub(f'^{re.escape(command_word)}', standard_command, user_input, flags=re.IGNORECASE)
        return user_input

    def parse(self, user_input):
        original_input = user_input.strip()

        best_match_cmd = None
        for cmd_name in self.commands.keys():
            # Check if the input starts with the command name, ensuring a word boundary
            if original_input.upper().startswith(cmd_name) and (len(original_input) == len(cmd_name) or original_input[len(cmd_name)].isspace()):
                if best_match_cmd is None or len(cmd_name) > len(best_match_cmd):
                    best_match_cmd = cmd_name

        if best_match_cmd is None:
            # Fallback for themed/alias commands if no primary command matched
            command_word = original_input.split(' ')[0].upper()
            if command_word in self.reverse_lexicon:
                standard_cmd = self.reverse_lexicon[command_word]
                if standard_cmd in self.commands:
                    best_match_cmd = standard_cmd
                    original_input = re.sub(f'^{re.escape(command_word)}', standard_cmd, original_input, flags=re.IGNORECASE)

        if best_match_cmd:
            command_data = self.commands[best_match_cmd]

            arg_string = original_input[len(best_match_cmd):].strip()

            # Extract parameters: quoted strings (without quotes) or non-space words
            # Use two capturing groups to handle both cases
            matches = re.findall(r'"([^"]*)"|(\S+)', arg_string)
            # Flatten tuples: take first group (quoted) or second group (unquoted)
            raw_params = [g1 or g2 for g1, g2 in matches]

            # Filter out keywords but keep actual parameter values
            params = [p for p in raw_params if p and p.upper() not in ['TO', 'FROM']]

            ucode_template = command_data['UCODE_TEMPLATE']
            default_params = command_data.get('DEFAULT_PARAMS', {})

            ucode = ucode_template
            for i, param in enumerate(params, 1):
                placeholder = f"${i}"
                ucode = ucode.replace(placeholder, param)

            for placeholder, value in default_params.items():
                if placeholder in ucode and value is not None:
                    ucode = ucode.replace(placeholder, value)

            ucode = re.sub(r'\*\$[0-9]+', '', ucode)

            return ucode

        return f"[SYSTEM|ERROR*Invalid command: {original_input}]"

    def get_command_names(self):
        """
        Returns a list of all command names.
        """
        return list(self.commands.keys()) + list(self.reverse_lexicon.keys())

# Example Usage (for testing)
if __name__ == '__main__':
    parser = Parser()

    # Test cases
    print(parser.parse('CLEAR'))
    print(parser.parse('HELP'))
    print(parser.parse('TREE'))
    print(parser.parse('SHOW "README.MD"'))
    print(parser.parse('ASK "What is uDOS?"'))
    print(parser.parse('EXTENSIONS LIST'))
    print(parser.parse('FONT LIST'))


# Alias for backward compatibility with tests
CommandParser = Parser
