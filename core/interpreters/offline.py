# uDOS v1.0.31 - Offline Logic Engine

import json
import os
import re
from urllib.request import urlopen
from urllib.error import URLError

class OfflineEngine:
    """
    Local AI-style assistance using pattern matching and templates.
    Works without internet connection.
    """

    def __init__(self, knowledge_file='core/data/faq.json'):
        self.knowledge_file = knowledge_file
        self.knowledge = self.load_knowledge()
        self.is_online = self.check_connection()
        self.command_history = []  # Track recent commands for context

    def load_knowledge(self):
        """Load offline knowledge base from unified FAQ"""
        try:
            with open(self.knowledge_file, 'r') as f:
                return json.load(f)
        except:
            # Fallback minimal knowledge if file doesn't exist
            return {
                "FAQ": {},
                "QUICK_TIPS": {},
                "OFFLINE_ASSISTANCE": {
                    "PROMPTS": {},
                    "RESPONSES": {
                        "OFFLINE_MODE": "Working offline. AI features unavailable.",
                        "NO_MATCH": "Not sure what you mean. Try 'HELP'."
                    }
                }
            }

    def check_connection(self):
        """Check if internet connection is available."""
        try:
            urlopen('https://www.google.com', timeout=2)
            return True
        except (URLError, Exception):
            return False

    def analyze_intent(self, user_input):
        """
        Analyze user input to determine intent using pattern matching.
        Supports both simple string matching and regex patterns.
        Returns: (intent_type, confidence, matched_data)
        """
        user_input_lower = user_input.lower()

        prompts = self.knowledge.get('OFFLINE_ASSISTANCE', {}).get('PROMPTS', {})

        for intent_name, intent_data in prompts.items():
            patterns = intent_data.get('PATTERN', [])
            regex_patterns = intent_data.get('REGEX', [])

            # Check simple patterns
            for pattern in patterns:
                if pattern.lower() in user_input_lower:
                    return intent_name, 0.8, intent_data

            # Check regex patterns
            for regex_pattern in regex_patterns:
                try:
                    if re.search(regex_pattern, user_input_lower, re.IGNORECASE):
                        return intent_name, 0.9, intent_data  # Higher confidence for regex
                except re.error:
                    # Invalid regex, skip
                    continue

        return None, 0.0, None

    def search_faq(self, user_input):
        """Search FAQ for relevant answers based on keywords."""
        user_input_lower = user_input.lower()
        faq_data = self.faq.get('FAQ', {})
        matches = []

        for faq_id, faq_entry in faq_data.items():
            keywords = faq_entry.get('keywords', [])
            # Check if any keyword matches
            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    matches.append((faq_id, faq_entry, len(keyword)))  # Track keyword length for relevance
                    break

        # Sort by keyword length (longer = more specific = more relevant)
        matches.sort(key=lambda x: x[2], reverse=True)

        return [m[:2] for m in matches]  # Return (faq_id, faq_entry) tuples

    def generate_response(self, user_input, context=None):
        """
        Generate a helpful response based on user input.
        Falls back to offline logic when internet unavailable.
        """
        # First check FAQ for direct answers
        faq_matches = self.search_faq(user_input)
        if faq_matches:
            faq_id, faq_entry = faq_matches[0]  # Use best match
            response = f"💡 {faq_entry.get('answer', '')}\n\n"
            if faq_entry.get('commands'):
                response += f"Related commands: {', '.join(faq_entry['commands'])}"
            return response

        # Fall back to pattern matching
        intent, confidence, intent_data = self.analyze_intent(user_input)

        if not intent:
            return self.prompts.get('RESPONSES', {}).get('NO_MATCH',
                "Not sure what you mean. Try 'HELP'.")

        # Generate response based on intent
        if intent == 'HELP_REQUEST':
            return self._handle_help_request(user_input, intent_data)
        elif intent == 'FILE_SUGGESTION':
            return self._handle_file_suggestion(user_input, intent_data)
        elif intent == 'SUMMARIZE_REQUEST':
            return self._handle_summarize(user_input, intent_data, context)
        elif intent == 'COMMAND_SUGGESTION':
            return self._handle_command_suggestion(user_input, intent_data)
        elif intent == 'ERROR_HELP':
            return self._handle_error_help(user_input, intent_data)
        elif intent == 'OFFLINE_ANALYSIS':
            return self._handle_analysis(user_input, intent_data, context)

        return intent_data.get('FALLBACK', "I can help with that. Try being more specific.")

    def _handle_help_request(self, user_input, intent_data):
        """Handle help-related questions."""
        # Extract topic from user input
        topic = user_input.replace('help', '').replace('how do i', '').replace('what is', '').strip()

        response = intent_data.get('RESPONSE_TEMPLATE', '{info}')
        info = f"Available commands: CATALOG, LOAD, SAVE, ASK, GRID, HELP, REPAIR, UNDO, REDO"

        return response.format(topic=topic or 'commands', info=info)

    def _handle_file_suggestion(self, user_input, intent_data):
        """Handle file finding requests."""
        query = user_input.replace('find', '').replace('locate', '').replace('where is', '').strip()
        return intent_data.get('RESPONSE_TEMPLATE', '').format(query=query or 'files')

    def _handle_summarize(self, user_input, intent_data, context):
        """Handle summarization requests (offline)."""
        if self.is_online:
            return "For AI summarization, use: ASK \"Summarize this\" FROM \"<panel>\""

        # Offline summary - basic stats
        if context and hasattr(context, 'panels'):
            # Try to find content to summarize
            return intent_data.get('RESPONSE_TEMPLATE', '').format(file='<filename>')

        return "Offline mode: Load content with LOAD, then I can provide basic stats."

    def _handle_command_suggestion(self, user_input, intent_data):
        """Suggest commands based on user intent."""
        keywords = intent_data.get('KEYWORDS', {})

        for phrase, command in keywords.items():
            if phrase in user_input.lower():
                return f"Try this command:\n  {command}"

        return "What would you like to do? Try: CATALOG, LOAD, SAVE, ASK, or HELP"

    def _handle_error_help(self, user_input, intent_data):
        """Help with error messages."""
        common_fixes = intent_data.get('COMMON_FIXES', {})

        # Check for common error keywords
        for error_type, fix in common_fixes.items():
            if error_type in user_input.lower():
                return f"💡 {fix}"

        return "Try: REPAIR to fix common issues, or HELP <command> for specific commands."

    def _handle_analysis(self, user_input, intent_data, context):
        """Perform offline analysis on content."""
        methods = intent_data.get('METHODS', {})

        if not context:
            return "Load content first with: LOAD \"<file>\" TO \"<panel>\""

        # Return available analysis methods
        return "Offline analysis available:\n" + "\n".join([f"  • {desc}" for desc in methods.values()])

    def analyze_content(self, content):
        """Perform basic content analysis (offline)."""
        if not content:
            return "No content to analyze."

        lines = content.split('\n')
        words = content.split()

        analysis = {
            'lines': len(lines),
            'words': len(words),
            'characters': len(content),
            'non_empty_lines': len([l for l in lines if l.strip()])
        }

        # Try to detect structure
        if content.strip().startswith('{'):
            analysis['type'] = 'JSON/UDO structure detected'
            try:
                json.loads(content)
                analysis['valid_json'] = True
            except:
                analysis['valid_json'] = False

        return analysis

    def format_analysis(self, analysis):
        """Format analysis results for display."""
        if isinstance(analysis, str):
            return analysis

        result = "📊 Content Analysis (Offline):\n"
        result += f"  Lines: {analysis.get('lines', 0)}\n"
        result += f"  Words: {analysis.get('words', 0)}\n"
        result += f"  Characters: {analysis.get('characters', 0)}\n"

        if 'type' in analysis:
            result += f"  Type: {analysis['type']}\n"
        if 'valid_json' in analysis:
            status = "✅ Valid" if analysis['valid_json'] else "❌ Invalid"
            result += f"  JSON: {status}\n"

        return result

    def track_command(self, command):
        """Track command for context and chaining suggestions."""
        self.command_history.append(command.upper())
        # Keep only last 10 commands
        if len(self.command_history) > 10:
            self.command_history.pop(0)

    def suggest_next_command(self):
        """Suggest next command based on recent history."""
        if not self.command_history:
            return None

        last_command = self.command_history[-1]

        # Common command chains
        chains = {
            'LOAD': ['SHOW', 'EDIT', 'ASK'],
            'CATALOG': ['LOAD', 'EDIT'],
            'SAVE': ['SHOW', 'EDIT'],
            'GRID PANEL CREATE': ['LOAD', 'SHOW'],
            'ASK': ['SHOW', 'SAVE'],
            'EDIT': ['SHOW', 'SAVE']
        }

        for cmd_prefix, suggestions in chains.items():
            if last_command.startswith(cmd_prefix):
                # Don't suggest if already done
                for suggestion in suggestions:
                    if not any(h.startswith(suggestion) for h in self.command_history[-3:]):
                        return suggestion

        return None

