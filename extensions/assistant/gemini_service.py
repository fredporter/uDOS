"""
Gemini Service - AI Assistant Extension
Google Gemini API integration for uDOS

Features:
- Conversational AI (ask questions, get answers)
- Code analysis and debugging
- Command explanations
- Script generation
- Knowledge bank integration
- Offline fallback support
- Usage tracking and cost monitoring

Version: 1.0.0 (migrated from extensions/core/ok_assistant)
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# Suppress warnings from google-api-core
import warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='google.api_core')

# Suppress AttributeError from google-api-core on Python 3.9
import io
_stderr_backup = sys.stderr
sys.stderr = io.StringIO()
try:
    import google.generativeai as genai
finally:
    sys.stderr = _stderr_backup


class GeminiService:
    """Gemini AI service for uDOS assistant extension"""

    def __init__(self, api_key: Optional[str] = None, config_manager=None):
        """
        Initialize Gemini service with optional API key.

        Args:
            api_key: Gemini API key (optional, will try config_manager or env)
            config_manager: ConfigManager instance for loading settings

        Raises:
            ValueError: If no API key found (graceful - extension becomes inactive)
        """
        self.config_manager = config_manager
        self.api_key = None
        self.username = None
        self.installation_id = None
        self.model = None
        self.chat = None
        self.conversation_history = []
        self.is_available = False

        # Usage tracking
        self.total_requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.session_start = datetime.now()

        # Try to initialize
        try:
            self._load_config(api_key)
            self._initialize_client()
            self.is_available = True
        except Exception as e:
            # Graceful degradation - extension inactive but no error
            self.is_available = False
            self.error_message = str(e)

    def _load_config(self, api_key: Optional[str] = None) -> None:
        """
        Load configuration from ConfigManager or environment.

        Args:
            api_key: Optional API key to use instead of config

        Raises:
            ValueError: If no API key found
        """
        # Try provided API key first
        if api_key:
            self.api_key = api_key
        # Try config manager
        elif self.config_manager:
            self.api_key = self.config_manager.get_env('GEMINI_API_KEY')
            self.username = self.config_manager.get('USERNAME', 'user')
            self.installation_id = self.config_manager.get('INSTALLATION_ID', 'default')
        # Fallback to environment
        else:
            self.api_key = os.getenv('GEMINI_API_KEY')
            self.username = os.getenv('USERNAME', 'user')
            self.installation_id = os.getenv('INSTALLATION_ID', 'default')

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. "
                "Add to .env: GEMINI_API_KEY=your_key_here\n"
                "Get key from: https://makersuite.google.com/app/apikey"
            )

    def _initialize_client(self) -> None:
        """
        Initialize Gemini API client.

        Raises:
            RuntimeError: If client initialization fails
        """
        try:
            genai.configure(api_key=self.api_key)

            # Use Gemini 2.5 Flash for fast, cost-effective responses
            self.model = genai.GenerativeModel('gemini-2.5-flash')

            # Start chat session
            self.chat = self.model.start_chat(history=[])

        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini client: {e}")

    def ask(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Send a prompt to Gemini and get response.

        Args:
            prompt: User's question or command
            context: Optional context dict with:
                - workspace: Current workspace name
                - files: List of relevant files
                - local_knowledge: Knowledge bank search results
                - panel: Panel content if analyzing a panel
                - user_role: User role (wizard/user)

        Returns:
            Gemini's response text

        Raises:
            RuntimeError: If service is not available
        """
        if not self.is_available:
            raise RuntimeError(
                f"Gemini service not available: {self.error_message}\n"
                "Check GEMINI_API_KEY in .env"
            )

        try:
            # Build full prompt with context
            full_prompt = self._build_prompt(prompt, context)

            # Send to Gemini
            start_time = time.time()
            response = self.chat.send_message(full_prompt)
            duration_ms = (time.time() - start_time) * 1000

            # Extract token usage (if available)
            tokens = self._extract_token_usage(response)
            if tokens:
                self.total_input_tokens += tokens.get('input_tokens', 0)
                self.total_output_tokens += tokens.get('output_tokens', 0)
                self.total_cost += self._calculate_cost(tokens)

            self.total_requests += 1

            # Store in history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'prompt': prompt,
                'context': context,
                'response': response.text,
                'tokens': tokens,
                'duration_ms': duration_ms
            })

            return response.text

        except Exception as e:
            # Return error message but don't crash
            return f"❌ Gemini Error: {str(e)}"

    def _build_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Build full prompt with uDOS system context.

        Args:
            prompt: User's question
            context: Optional context dictionary

        Returns:
            Full prompt with system context
        """
        username = self.username or 'user'
        installation_id = self.installation_id or 'default'
        workspace = context.get('workspace', 'memory') if context else 'memory'

        system_context = f"""You are uDOS AI Assistant, helping user '{username}' (installation: {installation_id}).

uDOS is an offline-first operating system for survival knowledge, mapping, and text-based computing:
- Minimal design, offline functionality, human-centric interfaces
- Text-first: Terminal-based, ASCII graphics, teletext rendering
- Knowledge bank: 166+ survival guides (water, fire, shelter, food, navigation, medical)
- Grid system: 480×270 TILE codes (AA-RL columns, 0-269 rows), 5 layers (100-500)
- 4-tier memory: Private → Shared → Community → Public
- Workflow automation with .upy scripts
- Extension system (assistant, play, web)

Current workspace: {workspace}

Provide concise, helpful responses optimized for CLI output.
Use emoji sparingly (🔮 for AI, ✅/❌ for status, 📚 for knowledge).
Format code blocks with triple backticks.
Keep responses under 500 words unless explicitly asked for more.
Prioritize offline/local solutions before suggesting API calls.
"""

        # Add local knowledge context if available
        if context and context.get('local_knowledge'):
            kb = context['local_knowledge']
            if kb.get('results'):
                system_context += f"\n\nLocal Knowledge Bank results ({len(kb['results'])} items):\n"
                for i, result in enumerate(kb['results'][:3], 1):
                    system_context += f"{i}. {result['title']} ({result['category']})\n"
                    if result.get('snippet'):
                        system_context += f"   {result['snippet'][:150]}...\n"

        # Add panel content if analyzing
        if context and context.get('panel'):
            panel = context['panel']
            system_context += f"\n\nPanel '{panel['name']}' content:\n{panel['content']}\n"

        # Add file context
        if context and context.get('files'):
            system_context += f"\n\nRelevant files: {', '.join(context['files'])}\n"

        return f"{system_context}\n\nUser: {prompt}"

    def clear_history(self) -> None:
        """Clear conversation history and start fresh."""
        self.conversation_history = []
        if self.chat:
            self.chat = self.model.start_chat(history=[])

    def get_history(self, last_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get last N conversation entries.

        Args:
            last_n: Number of recent conversations to return

        Returns:
            List of conversation dictionaries
        """
        return self.conversation_history[-last_n:]

    def get_status(self) -> Dict[str, Any]:
        """
        Get service status and usage statistics.

        Returns:
            Dictionary with status, usage, and cost data
        """
        uptime = (datetime.now() - self.session_start).total_seconds()

        return {
            'available': self.is_available,
            'model': 'gemini-2.5-flash',
            'uptime_seconds': uptime,
            'total_requests': self.total_requests,
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_cost_usd': round(self.total_cost, 4),
            'conversation_history_size': len(self.conversation_history),
            'error': self.error_message if not self.is_available else None
        }

    def analyze_code(self, code: str, language: str = "python") -> str:
        """
        Analyze code and provide suggestions.

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Analysis with summary, issues, suggestions, security concerns
        """
        prompt = f"""Analyze this {language} code and provide:
1. Brief summary of what it does
2. Any bugs or issues found
3. Suggestions for improvement
4. Security concerns (if any)

```{language}
{code}
```"""
        return self.ask(prompt)

    def explain_command(self, command: str) -> str:
        """
        Explain a uDOS or shell command.

        Args:
            command: Command to explain

        Returns:
            Simple explanation of the command
        """
        prompt = f"Explain this command in simple terms: {command}"
        return self.ask(prompt)

    def generate_script(self, description: str) -> str:
        """
        Generate a uDOS script from natural language description.

        Args:
            description: What the script should do

        Returns:
            Generated .upy script code
        """
        prompt = f"""Generate a uDOS script (.upy) for: {description}

Use uDOS commands like:
- OUTPUT <text> - Display text
- MEMORY NEW <filename> - Create file
- MEMORY DELETE <filename> - Delete file
- CATALOG - List files
- GUIDE <topic> - Show survival guide
- GENERATE DO <query> - AI assistance

Format as a complete .upy file with proper syntax."""
        return self.ask(prompt)

    def debug_error(self, error_msg: str, context: Optional[str] = None) -> str:
        """
        Help debug an error message.

        Args:
            error_msg: Error message to debug
            context: Optional context (code, command, etc.)

        Returns:
            Debug help with explanation and solutions
        """
        prompt = f"I got this error: {error_msg}"
        if context:
            prompt += f"\n\nContext: {context}"
        prompt += "\n\nWhat's wrong and how do I fix it?"
        return self.ask(prompt)

    def _extract_token_usage(self, response) -> Optional[Dict[str, int]]:
        """
        Extract token usage from Gemini response.

        Args:
            response: Gemini API response object

        Returns:
            Dictionary with input_tokens, output_tokens, total_tokens or None
        """
        try:
            # Check if response has usage_metadata attribute
            if hasattr(response, 'usage_metadata'):
                metadata = response.usage_metadata
                return {
                    'input_tokens': getattr(metadata, 'prompt_token_count', 0),
                    'output_tokens': getattr(metadata, 'candidates_token_count', 0),
                    'total_tokens': getattr(metadata, 'total_token_count', 0)
                }
        except:
            pass
        return None

    def _calculate_cost(self, tokens: Dict[str, int]) -> float:
        """
        Calculate API cost based on token usage.

        Args:
            tokens: Dictionary with input_tokens and output_tokens

        Returns:
            Cost in USD

        Pricing (Gemini 2.5 Flash, Dec 2024):
            - Input: $0.075 per 1M tokens
            - Output: $0.30 per 1M tokens
        """
        input_cost_per_million = 0.075
        output_cost_per_million = 0.30

        input_tokens = tokens.get('input_tokens', 0)
        output_tokens = tokens.get('output_tokens', 0)

        input_cost = (input_tokens / 1_000_000) * input_cost_per_million
        output_cost = (output_tokens / 1_000_000) * output_cost_per_million

        return input_cost + output_cost


# Global instance for lazy loading
_gemini_instance: Optional[GeminiService] = None


def get_gemini_service(config_manager=None, api_key: Optional[str] = None) -> GeminiService:
    """
    Get or create global Gemini service instance (lazy loading).

    Args:
        config_manager: Optional ConfigManager instance
        api_key: Optional API key (overrides config)

    Returns:
        GeminiService instance (may not be available if no API key)
    """
    global _gemini_instance
    if _gemini_instance is None:
        _gemini_instance = GeminiService(api_key=api_key, config_manager=config_manager)
    return _gemini_instance
