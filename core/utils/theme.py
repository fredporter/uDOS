# uDOS v1.0.0 - Color Theme and Styling
import json
import os

class Colors:
    """ANSI color codes for terminal output."""

    # Basic colors
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'

    # Bright foreground colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


class uDOSTheme:
    """Semantic color scheme for uDOS CLI."""

    # Command elements
    COMMAND = Colors.BRIGHT_CYAN
    PARAMETER = Colors.BRIGHT_WHITE
    FLAG = Colors.BRIGHT_YELLOW

    # Status indicators
    SUCCESS = Colors.BRIGHT_GREEN
    ERROR = Colors.BRIGHT_RED
    WARNING = Colors.BRIGHT_YELLOW
    INFO = Colors.BRIGHT_BLUE

    # File system
    FILE = Colors.WHITE
    DIRECTORY = Colors.BRIGHT_YELLOW
    EXECUTABLE = Colors.BRIGHT_GREEN

    # UI elements
    PROMPT = Colors.BRIGHT_MAGENTA
    HINT = Colors.GRAY
    HIGHLIGHT = Colors.BRIGHT_CYAN

    # Panels and grids
    PANEL = Colors.CYAN
    GRID_BORDER = Colors.GRAY

    # Special
    ACCENT = Colors.BRIGHT_MAGENTA
    MUTED = Colors.DIM + Colors.GRAY

    @staticmethod
    def colorize(text, color):
        """
        Wrap text in color codes.

        Args:
            text: Text to colorize
            color: Color code from Colors class

        Returns:
            Colored text string
        """
        return f"{color}{text}{Colors.RESET}"

    @staticmethod
    def success(text):
        """Format success message."""
        return uDOSTheme.colorize(f"✓ {text}", uDOSTheme.SUCCESS)

    @staticmethod
    def error(text):
        """Format error message."""
        return uDOSTheme.colorize(f"✗ {text}", uDOSTheme.ERROR)

    @staticmethod
    def warning(text):
        """Format warning message."""
        return uDOSTheme.colorize(f"⚠ {text}", uDOSTheme.WARNING)

    @staticmethod
    def info(text):
        """Format info message."""
        return uDOSTheme.colorize(f"ℹ {text}", uDOSTheme.INFO)

    @staticmethod
    def command(text):
        """Format command name."""
        return uDOSTheme.colorize(text, uDOSTheme.COMMAND)

    @staticmethod
    def file(text, is_dir=False):
        """Format file/directory name."""
        color = uDOSTheme.DIRECTORY if is_dir else uDOSTheme.FILE
        icon = "📁" if is_dir else "📄"
        return f"{icon} {uDOSTheme.colorize(text, color)}"

    @staticmethod
    def hint(text):
        """Format hint/suggestion."""
        return uDOSTheme.colorize(text, uDOSTheme.HINT)

    @staticmethod
    def bold(text):
        """Make text bold."""
        return f"{Colors.BOLD}{text}{Colors.RESET}"


# Prompt_toolkit style dictionary
PT_STYLE = {
    'prompt': 'ansibrightmagenta bold',
    'command': 'ansibrightcyan',
    'parameter': 'ansiwhite',
    'completion-menu': 'bg:#1e1e1e #ffffff',
    'completion-menu.completion.current': 'bg:#00aaff #000000',
    'completion-menu.completion': 'bg:#1e1e1e #888888',
    'completion-menu.meta.completion.current': 'bg:#00aaff #000000',
    'completion-menu.meta.completion': 'bg:#1e1e1e #888888',
    'scrollbar.background': 'bg:#888888',
    'scrollbar.button': 'bg:#00aaff',
}


# =============================================================================
# Theme Management Functions
# =============================================================================

def load_themes():
    """
    Load all available themes from THEMES.UDO.

    Returns:
        dict: Themes data or None if file doesn't exist
    """
    themes_path = os.path.join('data', 'THEMES.UDO')
    try:
        with open(themes_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to LEXICON.UDO for backwards compatibility
        lexicon_path = os.path.join('data', 'LEXICON.UDO')
        try:
            with open(lexicon_path, 'r', encoding='utf-8') as f:
                lexicon = json.load(f)
                # Convert old format to new
                return {
                    'VERSION': '1.0.0',
                    'DEFAULT_THEME': 'DUNGEON',
                    'THEMES': {
                        'DUNGEON': {
                            'NAME': 'Dungeon Crawler',
                            'TERMINOLOGY': lexicon.get('TERMINOLOGY', {})
                        }
                    }
                }
        except Exception:
            return None
    except Exception as e:
        print(f"Error loading themes: {e}")
        return None


def get_theme(theme_name='DUNGEON'):
    """
    Get a specific theme by name.

    Args:
        theme_name: Name of theme (DUNGEON, GALAXY, or FOUNDATION)

    Returns:
        dict: Theme data or None
    """
    themes_data = load_themes()
    if not themes_data:
        return None

    theme_name = theme_name.upper()
    return themes_data.get('THEMES', {}).get(theme_name)


def list_available_themes():
    """
    Get list of all available themes.

    Returns:
        list: List of theme names
    """
    themes_data = load_themes()
    if not themes_data:
        return ['DUNGEON']
    return list(themes_data.get('THEMES', {}).keys())


def get_theme_info(theme_name):
    """
    Get human-readable info about a theme.

    Args:
        theme_name: Name of theme

    Returns:
        dict: Theme metadata (NAME, STYLE, ICON, etc.)
    """
    theme = get_theme(theme_name)
    if not theme:
        return None

    return {
        'name': theme.get('NAME', theme_name),
        'style': theme.get('STYLE', ''),
        'icon': theme.get('ICON', '⚔️'),
        'description': theme.get('DESCRIPTION', ''),
        'verbose_level': theme.get('VERBOSE_LEVEL', 'MEDIUM')
    }


def display_theme_list():
    """
    Display all available themes in a formatted list.

    Returns:
        str: Formatted theme list
    """
    themes_data = load_themes()
    if not themes_data:
        return "No themes available."

    output = []
    output.append(f"\n{uDOSTheme.bold('🎭 Available Themes:')}\n")

    themes = themes_data.get('THEMES', {})
    for i, (theme_key, theme_data) in enumerate(themes.items(), 1):
        icon = theme_data.get('ICON', '⚔️')
        name = theme_data.get('NAME', theme_key)
        style = theme_data.get('STYLE', '')
        verbose = theme_data.get('VERBOSE_LEVEL', 'MEDIUM')

        output.append(f"  {i}. {icon} {uDOSTheme.colorize(name, uDOSTheme.ACCENT)} ({theme_key})")
        output.append(f"     {uDOSTheme.hint(style)}")
        output.append(f"     Verbosity: {verbose}\n")

    return "\n".join(output)


def get_themed_text(theme_name, key, **format_vars):
    """
    Get themed text for a specific message key.

    Args:
        theme_name: Active theme name
        key: Message key (e.g., 'ACTION_SUCCESS', 'ERROR_NOT_FOUND')
        **format_vars: Variables to format into the message

    Returns:
        str: Themed message with variables replaced
    """
    theme = get_theme(theme_name)
    if not theme:
        return f"[{key}]"

    terminology = theme.get('TERMINOLOGY', {})
    message = terminology.get(key, f"[{key}]")

    # Format with provided variables
    try:
        return message.format(**format_vars)
    except KeyError:
        return message


# Test function
if __name__ == "__main__":
    print("🎨 Testing Theme System\n")

    # List themes
    print(display_theme_list())

    # Test each theme
    for theme_name in list_available_themes():
        print(f"\n{'='*60}")
        print(f"Testing theme: {theme_name}")
        print(f"{'='*60}")

        info = get_theme_info(theme_name)
        if info:
            print(f"Name: {info['name']}")
            print(f"Style: {info['style']}")
            print(f"Icon: {info['icon']}\n")

        # Test some messages
        print("Sample messages:")
        print(f"  Success: {get_themed_text(theme_name, 'ACTION_SUCCESS')}")
        print(f"  Error: {get_themed_text(theme_name, 'ERROR_NOT_FOUND')}")
        print(f"  Exit: {get_themed_text(theme_name, 'INFO_EXIT')}")

