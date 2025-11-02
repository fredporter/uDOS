# uDOS v1.0.0 - Main Application

# Suppress urllib3 OpenSSL warnings gracefully
import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL 1.1.1+')

from .uDOS_splash import print_splash_screen
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
from .uDOS_prompt import SmartPrompt
from .uDOS_tree import generate_repository_tree
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import sys
import os
import time

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
                ucode = parser.parse(clean_line)
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

def initialize_system(is_script_mode=False):
    """Initialize all system components."""
    components = {}

    try:
        # 1. Detect viewport
        if not is_script_mode:
            print("🔍 Detecting viewport...", end=" ", flush=True)
        viewport = ViewportDetector()
        viewport.detect_terminal_size()
        viewport.classify_device()
        components['viewport'] = viewport
        if not is_script_mode:
            print(f"✓ {viewport.device_type} ({viewport.width}×{viewport.height})")
            # Show full-screen viewport measurement
            from core.uDOS_splash import print_viewport_measurement
            print_viewport_measurement(viewport, delay=1.0)

        # 2. Check connection
        if not is_script_mode:
            print("🌐 Checking connectivity...", end=" ", flush=True)
        connection = ConnectionMonitor()
        connection.check_internet_connection()
        components['connection'] = connection
        mode = connection.get_mode()
        if not is_script_mode:
            print(f"✓ {mode}")

        # 3. User profile
        user_manager = UserManager()
        components['user_manager'] = user_manager

        viewport_data = viewport.get_status_summary()

        if user_manager.needs_user_setup():
            user_manager.run_user_setup(interactive=not is_script_mode, viewport_data=viewport_data)
        else:
            user_manager.load_user_profile()
            session_id = f"session_{int(time.time())}"
            user_manager.update_session_data(session_id, viewport_data)

        # 4. System health check
        if not is_script_mode:
            print("🏥 System health...", end=" ", flush=True)

        from core.uDOS_startup import quick_health_check, check_system_health, repair_system

        is_healthy, message = quick_health_check()
        health = None  # Initialize health variable

        if not is_script_mode:
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
                response = input("  Attempt auto-repair? (y/n): ").strip().lower()
                if response == 'y':
                    print()
                    health = check_system_health(verbose=False)
                    health = repair_system(health, verbose=True)
                    print()
                    if health.is_healthy():
                        print("  ✅ System repaired successfully!")
                    else:
                        print(f"  ⚠️  Some issues remain - run 'REPAIR --report' for details")
                    print()

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

        # 6. Generate repository tree structure
        if not is_script_mode:
            print("🌳 Generating repository tree...", end=" ", flush=True)
        try:
            tree_string, tree_path = generate_repository_tree()
            components['tree_generated'] = True
            if not is_script_mode:
                print(f"✓ structure.txt")
        except Exception as e:
            components['tree_generated'] = False
            if not is_script_mode:
                print(f"⚠️  ({str(e)})")

        return components

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n💥 Critical initialization error: {e}")
        return None

def main():
    """Main function with full system initialization."""
    try:
        is_script_mode = len(sys.argv) > 1

        components = initialize_system(is_script_mode)
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
            print()  # Blank line

        command_handler = CommandHandler(
            history=history,
            connection=connection,
            viewport=viewport,
            user_manager=user_manager,
            command_history=command_history
        )

        if is_script_mode:
            script_path = sys.argv[1]
            run_script(script_path, parser, grid, command_handler, logger, command_history)
            logger.close()
            return 0

        project_name = story_data.get('STORY', {}).get('PROJECT_NAME', 'uDOS') if story_data else 'uDOS'

        # Initialize smart prompt system
        smart_prompt = SmartPrompt()

        # Initialize advanced completer with command history integration
        completer = AdvancedCompleter(parser, grid, command_history)

        # Command history already initialized above        kb = KeyBindings()

        @kb.add('[')
        def _(event):
            event.current_buffer.insert_text('[')
            event.current_buffer.start_completion()

        # Add history search keybinding (Ctrl+R)
        @kb.add('c-r')
        def _(event):
            """Reverse history search with intelligent features."""
            # Get current input
            current_text = event.current_buffer.text

            # Simple search implementation - show recent matching commands
            if current_text.strip():
                suggestions = command_history.get_suggestions(current_text, limit=5)
                if suggestions:
                    # Show suggestions in a simple format
                    print(f"\n📜 History matches for '{current_text}':")
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"  {i}. {suggestion}")
                    print()

        session = PromptSession(
            completer=completer,
            history=command_history,
            key_bindings=kb,
            auto_suggest=AutoSuggestFromHistory(),
            complete_while_typing=True,
            enable_history_search=True
        )

        last_command = None

        while True:
            try:
                if command_handler.reboot_requested:
                    print("\n🔄 Restarting uDOS...\n")
                    logger.close()
                    os.execv(sys.executable, ['python'] + sys.argv)

                # Generate smart prompt with flash effect
                is_assist = user_manager.is_assist_mode()
                prompt_string = smart_prompt.get_prompt(
                    is_assist_mode=is_assist,
                    panel_name=grid.selected_panel,
                    flash=True
                )

                # Show context hints if available
                hint = smart_prompt.get_context_hint(
                    last_command=last_command,
                    panel_content_length=len(grid.get_panel(grid.selected_panel) or "")
                )
                if hint:
                    print(hint)

                user_input = session.prompt(prompt_string)
                logger.log("INPUT", user_input)

                if user_input.lower() == 'exit':
                    break

                # Store for smart hints
                last_command = user_input

                ucode = parser.parse(user_input)
                result = command_handler.handle_command(ucode, grid, parser)

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
                logger.log("ERROR", str(e))
                print(command_handler.get_message("ERROR_CRASH", error=str(e)))

                # Self-healing attempt for recoverable errors
                if "connection" in str(e).lower() or "timeout" in str(e).lower():
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
