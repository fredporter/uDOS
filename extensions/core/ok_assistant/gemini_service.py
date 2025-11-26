"""
uDOS Gemini CLI Integration
Provides AI-powered assistance via Google's Gemini API
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

# Suppress Python 3.9 compatibility warnings from google-api-core
import warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='google.api_core')

# Suppress AttributeError from google-api-core on Python 3.9
# (packages_distributions was added in Python 3.10)
import io
_stderr_backup = sys.stderr
sys.stderr = io.StringIO()
try:
    import google.generativeai as genai
finally:
    sys.stderr = _stderr_backup

from datetime import datetime

class GeminiCLI:
    """Gemini AI integration for uDOS CLI"""

    def __init__(self, env_path: Optional[Path] = None):
        """Initialize Gemini CLI with API key from ConfigManager (v1.5.0)"""
        self.env_path = env_path or Path(__file__).parent.parent.parent / '.env'
        self.api_key = None
        self.username = None
        self.installation_id = None
        self.model = None
        self.chat = None
        self.conversation_history = []

        # Load configuration
        self._load_env()
        self._initialize_client()

    def _load_env(self) -> None:
        """Load environment variables from ConfigManager (v1.5.0) with fallback"""
        try:
            # Try ConfigManager first (v1.5.0)
            from core.uDOS_main import get_config
            config = get_config()

            self.api_key = config.get('GEMINI_API_KEY')
            self.username = config.get('USERNAME', 'user')
            self.installation_id = config.get('INSTALLATION_ID', 'default')

            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found in configuration")

        except Exception as e:
            # Fallback to direct .env reading
            if not self.env_path.exists():
                raise FileNotFoundError(
                    f".env file not found at {self.env_path}\n"
                    f"Please create it with: GEMINI_API_KEY=your_key_here"
                )

            env_vars = {}
            with open(self.env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            # Remove quotes if present
                            value = value.strip().strip('"\'')
                            env_vars[key.strip()] = value

            self.api_key = env_vars.get('GEMINI_API_KEY')
            self.username = env_vars.get('USERNAME', 'user')
            self.installation_id = env_vars.get('INSTALLATION_ID', 'default')

            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found in .env file")

    def _initialize_client(self) -> None:
        """Initialize Gemini API client"""
        try:
            genai.configure(api_key=self.api_key)

            # Use latest Gemini Flash model for fast responses
            self.model = genai.GenerativeModel('gemini-2.5-flash')

            # Start chat session
            self.chat = self.model.start_chat(history=[])

        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini client: {e}")

    def ask(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Send a prompt to Gemini and get response

        Args:
            prompt: User's question or command
            context: Optional context (current workspace, files, etc.)

        Returns:
            Gemini's response text
        """
        try:
            # Build full prompt with context
            full_prompt = self._build_prompt(prompt, context)

            # Send to Gemini
            response = self.chat.send_message(full_prompt)

            # Store in history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'prompt': prompt,
                'context': context,
                'response': response.text
            })

            return response.text

        except Exception as e:
            return f"❌ Gemini Error: {str(e)}"

    def _build_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build full prompt with system context"""
        system_context = f"""You are uDOS AI Assistant, helping user '{self.username}' (installation: {self.installation_id}).

uDOS is a retro-futuristic command-line operating system with:
- Teletext-style 16×16 grid display
- Polaroid 8-color palette (Red, Green, Yellow, Blue, Purple, Cyan, White, Black)
- Flat design (no curves, shadows, or gradients)
- Web dashboard and terminal integration
- File management system with workspaces (sandbox, memory, data, knowledge)
- Markdown support with .UDO and .UDT files
- Extension system (typo, micro, monaspace fonts)

Current workspace: {context.get('workspace', 'sandbox') if context else 'sandbox'}
Current files: {context.get('files', []) if context else []}

Provide concise, helpful responses optimized for CLI output.
Use emoji sparingly (🔮 for uDOS-specific, ✓/✗ for status).
Format code blocks with triple backticks.
Keep responses under 500 words unless explicitly asked for more.
"""

        if context:
            system_context += f"\n\nAdditional context: {json.dumps(context, indent=2)}"

        return f"{system_context}\n\nUser: {prompt}"

    def clear_history(self) -> None:
        """Clear conversation history and start fresh"""
        self.conversation_history = []
        self.chat = self.model.start_chat(history=[])

    def get_history(self, last_n: int = 10) -> List[Dict[str, Any]]:
        """Get last N conversation entries"""
        return self.conversation_history[-last_n:]

    def analyze_code(self, code: str, language: str = "python") -> str:
        """Analyze code and provide suggestions"""
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
        """Explain a uDOS or shell command"""
        prompt = f"Explain this command in simple terms: {command}"
        return self.ask(prompt)

    def generate_script(self, description: str) -> str:
        """Generate a uDOS script from natural language description"""
        prompt = f"""Generate a uDOS script (.uscript) for: {description}

Use uDOS commands like:
- NEW <filename> - Create file
- DELETE <filename> - Delete file
- OUTPUT <text> - Display text
- HELP - Show help
- WORKSPACE <name> - Switch workspace

Format as a complete .uscript file."""
        return self.ask(prompt)

    def debug_error(self, error_msg: str, context: Optional[str] = None) -> str:
        """Help debug an error message"""
        prompt = f"I got this error: {error_msg}"
        if context:
            prompt += f"\n\nContext: {context}"
        prompt += "\n\nWhat's wrong and how do I fix it?"
        return self.ask(prompt)


# Global instance for CLI use
_gemini_instance: Optional[GeminiCLI] = None

def get_gemini() -> GeminiCLI:
    """Get or create global Gemini instance"""
    global _gemini_instance
    if _gemini_instance is None:
        _gemini_instance = GeminiCLI()
    return _gemini_instance


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='uDOS Gemini AI Assistant')
    parser.add_argument('prompt', nargs='*', help='Question or command')
    parser.add_argument('--analyze', help='Analyze code from file')
    parser.add_argument('--explain', help='Explain a command')
    parser.add_argument('--generate', help='Generate script from description')
    parser.add_argument('--debug', help='Debug an error message')
    parser.add_argument('--clear', action='store_true', help='Clear conversation history')
    parser.add_argument('--history', type=int, help='Show last N conversations')

    args = parser.parse_args()

    try:
        gemini = get_gemini()

        if args.clear:
            gemini.clear_history()
            print("✓ Conversation history cleared")
            sys.exit(0)

        if args.history:
            history = gemini.get_history(args.history)
            print(f"\n📜 Last {len(history)} conversations:\n")
            for i, entry in enumerate(history, 1):
                print(f"{i}. [{entry['timestamp']}]")
                print(f"   Q: {entry['prompt'][:100]}...")
                print(f"   A: {entry['response'][:100]}...\n")
            sys.exit(0)

        if args.analyze:
            with open(args.analyze, 'r') as f:
                code = f.read()
            ext = Path(args.analyze).suffix[1:]
            response = gemini.analyze_code(code, ext or 'python')
            print(f"\n🔍 Code Analysis:\n\n{response}\n")
            sys.exit(0)

        if args.explain:
            response = gemini.explain_command(args.explain)
            print(f"\n💡 Command Explanation:\n\n{response}\n")
            sys.exit(0)

        if args.generate:
            response = gemini.generate_script(args.generate)
            print(f"\n📜 Generated Script:\n\n{response}\n")
            sys.exit(0)

        if args.debug:
            response = gemini.debug_error(args.debug)
            print(f"\n🐛 Debug Help:\n\n{response}\n")
            sys.exit(0)

        if args.prompt:
            prompt = ' '.join(args.prompt)
            response = gemini.ask(prompt)
            print(f"\n🔮 Gemini:\n\n{response}\n")
        else:
            # Interactive mode
            print("🔮 uDOS Gemini AI Assistant")
            print("Type 'exit' to quit, 'clear' to reset conversation\n")

            while True:
                try:
                    prompt = input("You: ").strip()

                    if not prompt:
                        continue

                    if prompt.lower() in ('exit', 'quit', 'q'):
                        print("\n✓ Goodbye!\n")
                        break

                    if prompt.lower() == 'clear':
                        gemini.clear_history()
                        print("✓ Conversation cleared\n")
                        continue

                    response = gemini.ask(prompt)
                    print(f"\nGemini: {response}\n")

                except KeyboardInterrupt:
                    print("\n\n✓ Goodbye!\n")
                    break
                except EOFError:
                    break

    except Exception as e:
        print(f"\n❌ Error: {e}\n", file=sys.stderr)
        sys.exit(1)
