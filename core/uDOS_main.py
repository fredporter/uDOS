# uDOS v1.5.0 - Main Application

# Suppress dependency warnings gracefully
import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL 1.1.1+')
warnings.filterwarnings('ignore', category=FutureWarning, module='google.api_core')

from .output.splash import print_splash_screen
from .uDOS_parser import Parser
from .uDOS_commands import CommandHandler
from .uDOS_grid import Grid
from .uDOS_logger import Logger
from .utils.completer import AdvancedCompleter
from .utils.setup import SystemSetup
from .services.history_manager import ActionHistory
from .services.history import CommandHistory
from .uDOS_startup import SystemHealth, check_system_health, repair_system
from .services.connection_manager import ConnectionMonitor
from .utils.viewport import ViewportDetector
from .services.user_manager import UserManager
from .input.smart_prompt import SmartPrompt
from .input.prompt_decorator import get_prompt_decorator
# Old tree utility removed - now using TreeHandler
from .utils.fast_startup import fast_initialize  # v1.0.31 Fast Startup
from .services.standardized_input import StandardizedInput
from .config_manager import get_config_manager  # v1.5.0 Unified Configuration
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import sys
import os
import time

# Global configuration manager (v1.5.0+)
_config_manager = None


def get_config():
    """
    Get global ConfigManager instance.

    Returns:
        ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = get_config_manager()
    return _config_manager

def run_script(script_path, parser, grid, command_handler, logger, command_history=None):
    """
    Executes a uDOS script file non-interactively.
    """
    try:
        with open(script_path, 'r') as f:
            for line in f:
                clean_line = line.strip()
                if not clean_line or clean_line.startswith('#'):
                    continue

                # Store command in command history if available
                if command_history:
                    command_history.append_string(clean_line)

                logger.log(f"uDOS> {clean_line}")

                # Check if line is already in uCODE format
                if clean_line.startswith('[') and clean_line.endswith(']'):
                    ucode = clean_line  # Already uCODE, use as-is
                else:
                    ucode = parser.parse(clean_line)  # Parse plain text to uCODE

                if ucode.startswith("[SYSTEM|ERROR"):
                    result = ucode
                else:
                    result = command_handler.handle_command(ucode, grid, parser)

                logger.log(result)
                print(result)
    except FileNotFoundError:
        error_msg = f"Error: Script file not found at '{script_path}'"
        logger.log(error_msg)
        print(error_msg)
    except Exception as e:
        error_msg = f"An error occurred while running the script: {e}"
        logger.log(error_msg)
        print(error_msg)

def initialize_system(is_script_mode=False, run_health_check=False, use_fast_startup=True):
    """
    Initialize all system components.

    Args:
        is_script_mode: True if running a script (non-interactive)
        run_health_check: True to run full health check (slower)
        use_fast_startup: True to use optimized FastStartup (v1.0.31)
    """

    # v1.0.31: Use FastStartup for optimized initialization
    if use_fast_startup:
        try:
            components = fast_initialize(
                verbose=not is_script_mode,
                run_health_check=run_health_check,
                is_script_mode=is_script_mode
            )

            # Tree generation removed from startup - use TREE command instead
            components['tree_generated'] = False

            return components

        except Exception as e:
            # Fall back to legacy initialization on error
            print(f"⚠️  FastStartup failed ({e}), using standard init...")
            use_fast_startup = False

    # Standard initialization (fallback)
    components = {}

    try:
        # 1. Initialize configuration (v1.5.0+)
        if not is_script_mode:
            print("⚙️  Loading configuration...", end=" ", flush=True)
        config = get_config()
        components['config'] = config
        if not is_script_mode:
            username = config.get('username', 'user')
            print(f"✓ {username}")

        # 2. Detect viewport
        if not is_script_mode:
            print("🔍 Detecting viewport...", end=" ", flush=True)
        viewport = ViewportDetector()
        viewport.detect_terminal_size()
        viewport.classify_device()
        components['viewport'] = viewport
        if not is_script_mode:
            print(f"✓ {viewport.device_type} ({viewport.width}×{viewport.height})")
            # Show full-screen viewport measurement (with error handling)
            try:
                from core.uDOS_splash import print_viewport_measurement
                print_viewport_measurement(viewport, delay=1.0)
            except (BrokenPipeError, IOError):
                # Skip viewport display if output is piped or redirected
                pass

        # 3. Check connection
        if not is_script_mode:
            print("🌐 Checking connectivity...", end=" ", flush=True)
        connection = ConnectionMonitor()
        connection.check_internet_connection()
        components['connection'] = connection
        mode = connection.get_mode()
        if not is_script_mode:
            print(f"✓ {mode}")

        # 4. User profile
        user_manager = UserManager()
        components['user_manager'] = user_manager

        viewport_data = viewport.get_status_summary()

        if user_manager.needs_user_setup():
            user_manager.run_user_setup(interactive=not is_script_mode, viewport_data=viewport_data)
        else:
            user_manager.load_user_profile()
            session_id = f"session_{int(time.time())}"
            user_manager.update_session_data(session_id, viewport_data)

        # 5. System health check
        if not is_script_mode and run_health_check:
            print("🏥 System health...", end=" ", flush=True)

        from core.uDOS_startup import quick_health_check, check_system_health, repair_system

        is_healthy, message = quick_health_check()
        health = None  # Initialize health variable

        if not is_script_mode and run_health_check:
            # Show brief status
            if is_healthy and "warning" not in message.lower():
                print("✓ Healthy")
            elif is_healthy:
                print(f"⚠️  Warnings")
            else:
                print(f"❌ Issues")

            # If there are issues, offer to repair
            if not is_healthy:
                print()
                print(f"  {message}")
                print()

                # Only prompt if we have an interactive terminal
                import sys
                if sys.stdin.isatty():
                    try:
                        input_service = StandardizedInput()
                        response = input_service.select_option(
                            title="Attempt auto-repair?",
                            options=["Yes", "No", "OK"],
                            default_index=0
                        )
                        if response in ['Yes', 'OK']:
                            print()
                            health = check_system_health(verbose=False, return_dict=False)
                            health = repair_system(health, verbose=True)
                            print()
                            if health.is_healthy():
                                print("  ✅ System repaired successfully!")
                            else:
                                print("  ⚠️  Some issues remain - run 'REPAIR --report' for details")
                    except (EOFError, KeyboardInterrupt):
                        print("\n  ⚠️  Skipping auto-repair")
                        print("  💡 Run 'REPAIR' command later to fix issues")
                else:
                    print("  ⚠️  Non-interactive mode - skipping auto-repair")
                    print("  💡 Run 'REPAIR' command to fix issues")
                print()
        elif not is_script_mode and not run_health_check:
            # Fast mode: skip health check silently
            pass

        # Store health check results (if available)
        if health:
            components['health'] = health

        # 5. Project setup
        setup = SystemSetup()
        if setup.needs_setup():
            story_data = setup.create_default_story() if is_script_mode else setup.run_setup()
        else:
            story_data = setup.load_story()

        setup.increment_session()
        components['setup'] = setup
        components['story_data'] = story_data

        # Tree generation removed from startup - use TREE command instead
        components['tree_generated'] = False

        return components

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n💥 Critical initialization error: {e}")
        return None

def main():
    """Main function with full system initialization."""
    try:
        # Check for flags
        is_script_mode = len(sys.argv) > 1 and not sys.argv[1].startswith('--')
        run_health_check = '--check' in sys.argv
        fast_mode = not run_health_check  # Skip health by default unless --check is passed

        components = initialize_system(is_script_mode, run_health_check)
        if not components:
            return 1

        viewport = components['viewport']
        connection = components['connection']
        user_manager = components['user_manager']
        story_data = components['story_data']

        print_splash_screen()

        # Initialize core components (only once!)
        parser = Parser()
        grid = Grid()
        logger = Logger()
        history = ActionHistory(logger=logger)

        # Initialize command history system with persistent storage
        command_history = CommandHistory()

        # Get session and move stats
        move_stats = logger.get_move_stats()

        # Display startup information
        if not is_script_mode:
            print(f"\n{user_manager.get_user_greeting()}")
            print(f"🌐 Mode: {connection.get_mode()}")
            print(f"📐 Viewport: {viewport.width}×{viewport.height} ({viewport.device_type})")

            project_name = story_data.get('STORY', {}).get('PROJECT_NAME', 'Unknown Quest')
            print(f"📖 Project: {project_name}")
            print(f"🔢 Session: #{move_stats['session_number']} | 🎯 Moves: {move_stats['total_moves']}")

            # Check lifespan status
            lifespan_status = user_manager.check_lifespan_status(move_stats['total_moves'])
            if lifespan_status['status'] != 'OK':
                print(f"⏳ {lifespan_status['message']}")

            # v1.0.30: Show welcome and offer demo
            try:
                from core.utils.startup_welcome import startup_sequence
                # Check if this is a first run or fresh session
                import os
                demo_shown_file = os.path.join(os.path.dirname(__file__), '..', 'memory', '.demo_shown_v1_0_30')
                show_demo = not os.path.exists(demo_shown_file)

                startup_sequence(viewport_width=viewport.width, auto_skip_demo=not show_demo)

                # Mark demo as shown
                if show_demo:
                    try:
                        os.makedirs(os.path.dirname(demo_shown_file), exist_ok=True)
                        with open(demo_shown_file, 'w') as f:
                            f.write('Demo shown on first run of v1.0.30')
                    except:
                        pass  # Non-critical
            except Exception as e:
                # Don't fail startup if welcome fails
                pass

            # v1.0.32: Planet selection on first run
            try:
                from core.services.planet_manager import PlanetManager
                pm = PlanetManager()

                # Check if this is first time using planet system
                current_planet = pm.get_current()
                if not current_planet:
                    # Offer planet setup
                    print()
                    print("="*viewport.width)
                    print("🪐 PLANET SYSTEM INITIALIZATION")
                    print("="*viewport.width)
                    print()
                    print("uDOS v1.0.32 introduces the Planet System - your workspaces")
                    print("are now visualized as planets in solar systems!")
                    print()
                    print("The default planet 'Earth' has been created for you.")
                    print("You can create additional planets anytime with: CONFIG PLANET NEW")
                    print()

                    # Set Earth as default
                    earth = pm.list_planets()[0] if pm.list_planets() else None
                    if earth:
                        print(f"✅ Active Planet: {earth.icon} {earth.name} ({earth.solar_system})")
                        print()
                        print("💡 Tip: Use LOCATE CITY to set your Earth location for")
                        print("   location-aware survival knowledge and world maps!")
                        print()
            except Exception as e:
                # Don't fail startup if planet setup fails
                pass

            print()  # Blank line

        command_handler = CommandHandler(
            history=history,
            connection=connection,
            viewport=viewport,
            user_manager=user_manager,
            command_history=command_history,
            logger=logger
        )

        if is_script_mode:
            script_path = sys.argv[1]
            run_script(script_path, parser, grid, command_handler, logger, command_history)
            logger.close()
            return 0

        project_name = story_data.get('STORY', {}).get('PROJECT_NAME', 'uDOS') if story_data else 'uDOS'

        # Initialize smart prompt with autocomplete
        smart_prompt = SmartPrompt(command_history=command_history, theme='dungeon')

        # Initialize prompt decorator for themed prompts
        prompt_decorator = get_prompt_decorator(theme='dungeon')

        # OPTIONAL: Web GUI Extension - API Server
        # Only loads if explicitly enabled in user settings
        # CLI functionality is complete without this
        api_server_started = False
        try:
            user_data = user_manager.get_user_data()
            if user_data.get('settings', {}).get('api_server_enabled', False):
                # Try to load API server extension (not in core)
                from extensions.api.manager import APIServerManager

                print("🌐 Starting Web GUI API server...", end=" ", flush=True)
                api_manager = APIServerManager(port=5001, auto_restart=True)
                if api_manager.start_server():
                    api_server_started = True
                    print("✓ http://localhost:5001")
                else:
                    print("❌ Failed (continuing in CLI mode)")
        except ImportError:
            # Extension not installed - CLI works fine without it
            pass
        except Exception as e:
            # Extension failed to load - not critical for CLI
            pass

        print()  # Blank line before prompt

        last_command = None

        while True:
            try:
                if command_handler.reboot_requested:
                    print("\n🔄 Restarting uDOS...\n")
                    logger.close()
                    os.execv(sys.executable, ['python'] + sys.argv)

                # Generate smart prompt string with flash effect
                # Note: Flash disabled by default to preserve terminal scrollback
                # Set flash=True below if you want the animated prompt
                is_assist = user_manager.is_assist_mode()

                # Check DEV MODE status (v1.5.0)
                dev_mode_active = False
                try:
                    from core.services.dev_mode_manager import get_dev_mode_manager
                    dev_mode_mgr = get_dev_mode_manager()
                    dev_mode_active = dev_mode_mgr.is_active
                except Exception:
                    pass  # DEV MODE not available, continue normally

                prompt_string = prompt_decorator.get_prompt(
                    is_assist_mode=is_assist,
                    panel_name=grid.selected_panel,
                    flash=False,  # Changed from True - preserves scrollback
                    dev_mode=dev_mode_active  # v1.5.0: Show 🔧 DEV indicator
                )

                # Show context hints if available
                hint = prompt_decorator.get_context_hint(
                    last_command=last_command,
                    panel_content_length=len(grid.get_panel(grid.selected_panel) or "")
                )
                if hint:
                    print(hint)

                # Use new SmartPrompt with autocomplete (v1.0.19)
                user_input = smart_prompt.ask(prompt_text=prompt_string)

                # Skip empty input (happens with piped input at EOF)
                if not user_input or not user_input.strip():
                    continue

                logger.log("INPUT", user_input)

                if user_input.lower() == 'exit':
                    break

                # Store for smart hints
                last_command = user_input

                ucode = parser.parse(user_input)

                # Check DEV MODE permissions for dangerous commands (v1.5.0)
                try:
                    from core.services.dev_mode_manager import get_dev_mode_manager
                    dev_mode_mgr = get_dev_mode_manager()

                    # Extract command from ucode
                    parts = ucode.strip('[]').split('|')
                    if len(parts) >= 2:
                        command_parts = parts[1].split('*')
                        command = command_parts[0].upper()

                        # Check permission
                        allowed, message = dev_mode_mgr.check_permission(command)
                        if not allowed:
                            print(message)
                            continue  # Skip execution
                        elif message:
                            # Show warning but allow execution
                            print(message)
                except Exception:
                    pass  # DEV MODE not available, continue normally

                result = command_handler.handle_command(ucode, grid, parser)

                # Track command usage
                try:
                    # Parse the ucode to extract command and params
                    parts = ucode.strip('[]').split('|')
                    if len(parts) >= 2:
                        command_parts = parts[1].split('*')
                        command = command_parts[0].upper()
                        params = command_parts[1:] if len(command_parts) > 1 else []

                        # Track the command (success if we got a result)
                        command_handler.system_handler.usage_tracker.track_command(
                            command=command,
                            params=params,
                            success=(result is not None and "ERROR" not in result.upper()[:50])
                        )
                except:
                    pass  # Silently ignore tracking errors

                if result:
                    logger.log("OUTPUT", result)
                    print(result)

                    # Show command chain hint
                    chain_hint = smart_prompt.format_command_chain_hint(user_input)
                    if chain_hint:
                        print(chain_hint)

                if user_manager.is_assist_mode() and not command_handler.reboot_requested:
                    suggestion = command_handler.offline_engine.generate_response(
                        "What should I do next?",
                        context=result
                    )
                    if suggestion and not suggestion.startswith("I don't"):
                        print(f"\n💡 {suggestion}\n")

            except KeyboardInterrupt:
                logger.log("EVENT", "KeyboardInterrupt")
                print(f"\n{command_handler.get_message('INFO_EXIT')}")
                break
            except EOFError:
                logger.log("EVENT", "EOFError")
                print(f"\n{command_handler.get_message('INFO_EXIT')}")
                break
            except BrokenPipeError:
                # Handle pipe errors gracefully (e.g., when piping to head/tail)
                logger.log("EVENT", "BrokenPipeError (handled)")
                # Silence the error - this is normal when output is piped
                sys.stderr.close()
                break
            except IOError as e:
                # Handle other I/O errors gracefully
                if e.errno == 32:  # EPIPE
                    logger.log("EVENT", "EPIPE (handled)")
                    sys.stderr.close()
                    break
                else:
                    logger.log("ERROR", f"IOError: {e}")
                    print(command_handler.get_message("ERROR_GENERIC", error=str(e)))
            except Exception as e:
                # Check if this is a normal termination condition
                error_str = str(e).lower()
                if any(term in error_str for term in ['eof', 'closed', 'input', 'terminal']):
                    # Likely end of piped input or terminal closed - exit gracefully
                    logger.log("EVENT", f"Terminal condition: {e}")
                    break

                # Otherwise log and display error
                logger.log("ERROR", str(e))
                print(command_handler.get_message("ERROR_CRASH", error=str(e)))

                # Self-healing attempt for recoverable errors
                if "connection" in error_str or "timeout" in error_str:
                    print("🔧 Attempting self-heal...")
                    try:
                        connection = ConnectionMonitor()
                        command_handler.connection = connection
                        print("✅ Connection reset successful")
                    except:
                        print("⚠️  Self-heal failed - continuing anyway")

        logger.close()

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        return 0
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n💥 Critical error during startup: {e}")
        print("💡 Try running: REPAIR (to diagnose system issues)")
        print("💡 Or run: SETUP (to reconfigure user profile)")
        return 1

    return 0


# Signal handler for graceful shutdown
def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    import signal

    def signal_handler(signum, frame):
        """Handle shutdown signals gracefully"""
        print("\n\n👋 Shutting down gracefully...")
        sys.exit(0)

    # Handle common signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Handle SIGPIPE (broken pipe) by ignoring it
    if hasattr(signal, 'SIGPIPE'):
        signal.signal(signal.SIGPIPE, signal.SIG_IGN)


if __name__ == "__main__":
    setup_signal_handlers()
    sys.exit(main())
