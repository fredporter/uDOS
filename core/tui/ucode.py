"""
uCODE - Unified Terminal TUI
=============================

The pivotal single-entry-point Terminal TUI for uDOS.

Features:
- Auto-detects available components (core, wizard, extensions)
- Graceful fallback to core-only mode if components are missing
- Integrated Wizard server control (start/stop/status)
- Extension/plugin packaging, installation, and distribution
- Core command dispatch with context-aware pages
- Dynamic capability loading based on available folders

Architecture:
  1. On startup, detect available components
  2. Build capability registry dynamically
  3. Expose only commands/pages for what's present
  4. If wizard exists, allow server control + Wizard pages
  5. If extensions exist, allow plugin management
  6. Fallback gracefully to core-only mode

Commands:
  STATUS          - System status and component detection
  HELP            - Show available commands
  WIZARD [cmd]    - Wizard server control (if available)
  PLUGIN [cmd]    - Extension/plugin management (if available)
  EXT [cmd]       - Extension management (alias for PLUGIN)
  + Core commands (routed to dispatcher)

Version: v1.0.0 (uCODE Unified)
Status: Production
Date: 2026-01-28
"""

import sys
import os
import json
import logging
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.tui.dispatcher import CommandDispatcher
from core.tui.renderer import GridRenderer
from core.tui.state import GameState
from core.input import SmartPrompt
from core.services.logging_manager import get_logger


def get_repo_root() -> Path:
    """Get uDOS repository root."""
    current = Path(__file__).parent
    while current != current.parent:
        if (current / "core" / "tui").exists() and (current / "wizard").exists():
            return current
        current = current.parent
    # Fallback: current working directory
    return Path.cwd()


class ComponentState(Enum):
    """Component availability state."""
    AVAILABLE = "available"
    MISSING = "missing"
    ERROR = "error"


@dataclass
class Component:
    """Component registration."""
    name: str
    path: Path
    state: ComponentState
    version: Optional[str] = None
    description: str = ""


class ComponentDetector:
    """Detect and validate available components."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.logger = get_logger("ucode-detector")
        self.components: Dict[str, Component] = {}

    def detect_all(self) -> Dict[str, Component]:
        """Detect all available components."""
        self.components = {
            "core": self._detect_core(),
            "wizard": self._detect_wizard(),
            "extensions": self._detect_extensions(),
            "app": self._detect_app(),
        }
        return self.components

    def _detect_core(self) -> Component:
        """Detect core component."""
        path = self.repo_root / "core"
        if path.exists() and (path / "__init__.py").exists():
            version = self._get_version(path / "version.json")
            return Component(
                name="core",
                path=path,
                state=ComponentState.AVAILABLE,
                version=version,
                description="Core TUI runtime"
            )
        return Component(
            name="core",
            path=path,
            state=ComponentState.MISSING,
            description="Core TUI runtime (missing)"
        )

    def _detect_wizard(self) -> Component:
        """Detect Wizard server component."""
        path = self.repo_root / "wizard"
        if path.exists() and (path / "server.py").exists():
            version = self._get_version(path / "version.json")
            return Component(
                name="wizard",
                path=path,
                state=ComponentState.AVAILABLE,
                version=version,
                description="Wizard server & services"
            )
        return Component(
            name="wizard",
            path=path,
            state=ComponentState.MISSING,
            description="Wizard server (not installed)"
        )

    def _detect_extensions(self) -> Component:
        """Detect extensions component."""
        path = self.repo_root / "extensions"
        # Extensions folder exists and has subdirectories like api, transport
        if path.exists() and ((path / "api").exists() or (path / "transport").exists()):
            version = self._get_version(path / "version.json")
            return Component(
                name="extensions",
                path=path,
                state=ComponentState.AVAILABLE,
                version=version,
                description="Extensible plugin system"
            )
        return Component(
            name="extensions",
            path=path,
            state=ComponentState.MISSING,
            description="Extensions system (not installed)"
        )

    def _detect_app(self) -> Component:
        """Detect app component."""
        path = self.repo_root / "app"
        if path.exists() and (path / "package.json").exists():
            version = self._get_version(path / "version.json")
            return Component(
                name="app",
                path=path,
                state=ComponentState.AVAILABLE,
                version=version,
                description="Desktop GUI application"
            )
        return Component(
            name="app",
            path=path,
            state=ComponentState.MISSING,
            description="Desktop app (not installed)"
        )

    def _get_version(self, version_file: Path) -> Optional[str]:
        """Read version from component's version.json."""
        try:
            if version_file.exists():
                with open(version_file) as f:
                    data = json.load(f)
                    return data.get("display") or data.get("version")
        except Exception as e:
            self.logger.debug(f"Failed to read version from {version_file}: {e}")
        return None

    def is_available(self, component_name: str) -> bool:
        """Check if component is available."""
        comp = self.components.get(component_name)
        return comp and comp.state == ComponentState.AVAILABLE


class uCODETUI:
    """Unified Terminal TUI for uDOS."""

    def __init__(self):
        """Initialize uCODE TUI."""
        self.repo_root = get_repo_root()
        self.logger = get_logger("ucode-tui")
        self.running = False

        # Component detection
        self.detector = ComponentDetector(self.repo_root)
        self.components = self.detector.detect_all()

        # Core components (always available)
        self.dispatcher = CommandDispatcher()
        self.renderer = GridRenderer()
        self.state = GameState()
        self.prompt = SmartPrompt()

        # Command registry
        self.commands: Dict[str, Callable] = {
            "STATUS": self._cmd_status,
            "HELP": self._cmd_help,
            "EXIT": self._cmd_exit,
            "QUIT": self._cmd_exit,
        }

        # Conditional commands
        if self.detector.is_available("wizard"):
            self.commands["WIZARD"] = self._cmd_wizard
            self.commands["WIZ"] = self._cmd_wizard

        if self.detector.is_available("extensions"):
            self.commands["PLUGIN"] = self._cmd_plugin
            self.commands["EXT"] = self._cmd_plugin
            self.commands["EXTENSION"] = self._cmd_plugin

        if self.prompt.use_fallback:
            self.logger.info(f"[SmartPrompt] Using fallback mode: {self.prompt.fallback_reason}")
        else:
            self.logger.info("[SmartPrompt] Initialized with prompt_toolkit")

    def run(self) -> None:
        """Start uCODE TUI."""
        self.running = True
        self._show_banner()
        self._show_component_status()
        
        # Check if fresh install and run setup if needed
        self._check_fresh_install()

        try:
            while self.running:
                try:
                    plain_prompt = "[uCODE] > "
                    
                    # Ensure terminal is in good state before asking for input
                    sys.stdout.flush()
                    sys.stderr.flush()
                    
                    user_input = self.prompt.ask(plain_prompt)

                    if not user_input:
                        continue

                    # Parse command
                    parts = user_input.split(None, 1)
                    cmd = parts[0].upper()
                    args = parts[1] if len(parts) > 1 else ""

                    # Check for uCODE commands
                    if cmd in self.commands:
                        self.commands[cmd](args)
                        continue

                    # Special handling for STORY commands with forms
                    if cmd == "STORY":
                        result = self.dispatcher.dispatch(user_input)
                        
                        # Check if this is a form-based story
                        if result.get("story_form"):
                            collected_data = self._handle_story_form(result["story_form"])
                            print("\n✅ Setup form completed!")
                            print(f"\nCollected {len(collected_data)} values")
                            if collected_data:
                                print("\nData saved. Next steps:")
                                print("  SETUP              - View your profile")
                                print("  CONFIG             - View variables")
                        else:
                            # Show the result for non-form stories
                            output = self.renderer.render(result)
                            print(output)
                        
                        self.state.update_from_handler(result)
                        self.logger.info(f"[COMMAND] {user_input} -> {result.get('status')}")
                        self.state.add_to_history(user_input)
                        continue

                    # Route to core dispatcher (fallback)
                    result = self.dispatcher.dispatch(user_input)
                    self.state.update_from_handler(result)
                    self.logger.info(f"[COMMAND] {user_input} -> {result.get('status')}")
                    self.state.add_to_history(user_input)

                    output = self.renderer.render(result)
                    print(output)

                except KeyboardInterrupt:
                    print()
                    continue
                except Exception as e:
                    self.logger.error(f"[ERROR] {e}", exc_info=True)
                    print(f"ERROR: {e}")

        except KeyboardInterrupt:
            print("\nInterrupt. Type EXIT to quit.")
        except EOFError:
            self.running = False
        finally:
            self._cleanup()

    def _show_banner(self) -> None:
        """Show startup banner."""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                        uCODE v1.0.1                           ║
║                 Unified Terminal TUI for uDOS                 ║
║                    Type HELP for commands                     ║
╚═══════════════════════════════════════════════════════════════╝
"""
        print(banner)

    def _ask_yes_no(self, question: str, default: bool = True) -> bool:
        """Ask a standardized yes/no question.

        Prompt format: "Question? [Y/N] (Enter=default)"
        Accepts: Y/N (single key), Enter for default

        Args:
            question: The question to ask (without punctuation)
            default: Default answer if user just presses Enter

        Returns:
            True for yes, False for no
        """
        default_key = "y" if default else "n"
        prompt_text = f"{question}? [Y/N] (Enter={default_key.upper()}) "

        response = self.prompt.ask_single_key(prompt_text, valid_keys=["y", "n"], default=default_key)
        response_lower = response.lower().strip()

        if response_lower == "y":
            return True
        if response_lower == "n":
            return False

        # Should not happen, but fall back to default
        return default
    
    def _handle_story_form(self, form_data: Dict) -> Dict:
        """Handle interactive story form - collect user responses for all sections.
        
        Args:
            form_data: Form structure with title and sections or fields
        
        Returns:
            Dictionary of collected field values from all sections
        """
        collected = {}
        
        # Show form title
        title = form_data.get("title", "Form")
        print(f"\n📋 {title}")
        print("=" * 60)
        
        # Check if this is multi-section form
        sections = form_data.get("sections", [])
        
        # DEBUG: Log what we received
        self.logger.debug(f"[STORY] Form sections: {len(sections)} sections, form_data keys: {list(form_data.keys())}")
        if sections:
            self.logger.debug(f"[STORY] Section titles: {[s.get('title') for s in sections]}")
        
        if sections:
            # Process each section
            for section_idx, section in enumerate(sections):
                section_title = section.get("title", "Section")
                section_text = section.get("text", "").strip()
                fields = section.get("fields", [])
                
                self.logger.debug(f"[STORY] Processing section {section_idx}: '{section_title}' with {len(fields)} fields")
                
                if fields:  # Only show sections that have fields
                    print(f"\n## {section_title}\n")
                    if section_text:
                        print(f"{section_text}\n")
                        print("-" * 60)
                    
                    # Collect responses for each field in section
                    for field in fields:
                        response = self._collect_field_response(field)
                        if response is not None:
                            field_name = field.get("name", "")
                            collected[field_name] = response
        else:
            # Single section form (backward compatibility)
            fields = form_data.get("fields", [])
            text = form_data.get("text", "").strip()
            
            if text:
                print(f"\n{text}\n")
                print("-" * 60)
            
            for field in fields:
                response = self._collect_field_response(field)
                if response is not None:
                    field_name = field.get("name", "")
                    collected[field_name] = response
        
        print("\n" + "=" * 60)
        return collected
    
    def _save_user_profile(self, collected_data: Dict) -> None:
        """Save collected form data to user profile.
        
        This submits to the Wizard's /api/v1/setup/story/submit endpoint,
        which properly splits the data into user and install profiles.
        
        Args:
            collected_data: Dictionary of field names and values from form
        """
        try:
            # Try to save via Wizard API endpoint (preferred method)
            try:
                import requests
                
                # Get the token
                token_path = self.repo_root / "memory" / "private" / "wizard_admin_token.txt"
                
                if token_path.exists():
                    token = token_path.read_text().strip()
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                    
                    # Submit to the story endpoint which handles splitting
                    response = requests.post(
                        "http://localhost:8765/api/v1/setup/story/submit",
                        headers=headers,
                        json={"answers": collected_data},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        self.logger.info("[SETUP] Setup data submitted to Wizard API")
                        print("\n✅ Setup data saved to Wizard keystore.")
                        return
                    elif response.status_code == 503:
                        self.logger.warning(f"[SETUP] Wizard secret store locked")
                        print(f"\n⚠️  Wizard secret store is locked. Please ensure WIZARD_KEY is set.")
                    else:
                        error_detail = response.json().get("detail", f"HTTP {response.status_code}")
                        self.logger.warning(f"[SETUP] Wizard API error: {error_detail}")
                        print(f"\n⚠️  Could not save to Wizard: {error_detail}")
                        
            except requests.exceptions.ConnectionError:
                self.logger.debug("Wizard server not running, trying direct save")
            except Exception as e:
                self.logger.debug(f"Wizard API submission failed: {e}")
            
            # Fallback: Try direct save via Wizard services (if Wizard is available but server isn't running)
            try:
                from wizard.services.setup_profiles import save_user_profile, save_install_profile
                
                # Split the collected data into user and install sections
                # User profile fields
                user_profile = {
                    "username": collected_data.get("user_username"),
                    "date_of_birth": collected_data.get("user_dob"),
                    "role": collected_data.get("user_role"),
                    "timezone": collected_data.get("user_timezone"),
                    "local_time": collected_data.get("user_local_time"),
                    "location_id": collected_data.get("user_location_id"),
                    "permissions": collected_data.get("user_permissions"),
                }
                
                # Install profile fields
                install_profile = {
                    "installation_id": collected_data.get("install_id"),
                    "os_type": collected_data.get("install_os_type"),
                    "lifespan_mode": collected_data.get("install_lifespan_mode"),
                    "moves_limit": collected_data.get("install_moves_limit"),
                    "permissions": collected_data.get("install_permissions"),
                    "capabilities": {
                        "web_proxy": bool(collected_data.get("capability_web_proxy")),
                        "gmail_relay": bool(collected_data.get("capability_gmail_relay")),
                        "ai_gateway": bool(collected_data.get("capability_ai_gateway")),
                        "github_push": bool(collected_data.get("capability_github_push")),
                        "notion": bool(collected_data.get("capability_notion")),
                        "hubspot": bool(collected_data.get("capability_hubspot")),
                        "icloud": bool(collected_data.get("capability_icloud")),
                        "plugin_repo": bool(collected_data.get("capability_plugin_repo")),
                        "plugin_auto_update": bool(collected_data.get("capability_plugin_auto_update")),
                    },
                }
                
                user_result = save_user_profile(user_profile)
                install_result = save_install_profile(install_profile)
                
                if user_result.data and install_result.data:
                    self.logger.info("[SETUP] Setup data saved via direct Wizard services")
                    print("\n✅ Setup data saved to Wizard keystore.")
                    return
                elif user_result.locked or install_result.locked:
                    error = user_result.error or install_result.error
                    self.logger.warning(f"[SETUP] Secret store locked: {error}")
                    print(f"\n⚠️  Secret store is locked: {error}")
                    print("Please ensure WIZARD_KEY is set in .env file.")
                    
            except (ImportError, Exception) as e:
                self.logger.debug(f"Wizard direct save not available: {e}")
            
            # Final fallback: Save to local profile file in memory/
            profile_dir = self.repo_root / "memory" / "user"
            profile_dir.mkdir(parents=True, exist_ok=True)
            profile_file = profile_dir / "profile.json"
            
            import json
            from datetime import datetime
            
            # Create profile structure with timestamp
            profile = {
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "data": collected_data
            }
            
            with open(profile_file, "w") as f:
                json.dump(profile, f, indent=2)
            
            self.logger.info(f"[SETUP] User profile saved to local file: {profile_file}")
            print(f"\n💾 Setup data saved locally to {profile_file}")
            print("⚠️  Note: Start Wizard server to sync this data to the keystore.")
            
        except Exception as e:
            self.logger.error(f"[SETUP] Failed to save user profile: {e}", exc_info=True)
            print(f"\n⚠️  Warning: Could not save profile: {e}")

    
    def _collect_field_response(self, field: Dict) -> Optional[str]:
        """Collect response for a single form field.
        
        Args:
            field: Field definition with name, label, type, etc.
        
        Returns:
            User's response or None
        """
        name = field.get("name", "")
        label = field.get("label", name)
        field_type = field.get("type", "text")
        required = field.get("required", False)
        placeholder = field.get("placeholder", "")
        options = field.get("options", [])
        
        # Build prompt text
        prompt_prefix = f"{label}"
        if not required:
            prompt_prefix += " (optional)"
        
        response = None
        
        if field_type == "select" and options:
            # Show options menu
            print(f"\n{prompt_prefix}:")
            for idx, option in enumerate(options, 1):
                print(f"  {idx}. {option}")
            
            # Get selection (simple integer input)
            response = self.prompt.ask("  Enter number")
            try:
                choice_idx = int(response) - 1
                if 0 <= choice_idx < len(options):
                    response = options[choice_idx]
                else:
                    response = placeholder or ""
            except (ValueError, TypeError):
                response = placeholder or ""
        
        elif field_type == "checkbox":
            # Yes/no prompt
            yn = self._ask_yes_no(prompt_prefix)
            response = "yes" if yn else "no"
        
        else:
            # Text input (text or textarea)
            print(f"\n{prompt_prefix}:")
            response = self.prompt.ask("  > ", default=placeholder or "")
        
        return response if response else None
    
    def _check_fresh_install(self) -> None:
        """Check if this is a fresh install and run setup story if needed.
        
        A fresh install is detected when:
        - No user profile exists in Wizard
        - No setup has been completed
        
        Self-healing: Automatically builds TS runtime if missing.
        """
        try:
            # Check if Wizard is available
            if not self.detector.is_available("wizard"):
                self.logger.debug("Wizard not available, skipping fresh install check")
                return
            
            # Try to load user profile from Wizard
            try:
                from wizard.services.setup_profiles import load_user_profile
                
                result = load_user_profile()
                
                # If we have user data, not a fresh install
                if result.data and not result.locked:
                    self.logger.debug("User profile exists, not a fresh install")
                    return
                
                # If locked due to no encryption key, still consider it fresh
                if result.locked and "not set" in str(result.error).lower():
                    self.logger.debug("Wizard not yet initialized, treating as fresh install")
                
            except (ImportError, Exception) as e:
                self.logger.debug(f"Could not check user profile: {e}")
                return
            
            # Fresh install detected
            print("\n" + "="*60)
            print("⚙️  FRESH INSTALLATION DETECTED")
            print("="*60)
            print("\nNo user profile found. Let's set up your uDOS installation!")
            print("\nWe'll capture:")
            print("  • Your identity (username, role, timezone, location)")
            print("  • Installation settings (OS type, lifespan mode)")
            print("  • Capability preferences (cloud services, integrations)")
            print("\nThis data will be stored securely in the Wizard keystore.")
            print("-"*60)
            
            # Check if TS runtime is built
            ts_runtime_path = self.repo_root / "core" / "grid-runtime" / "dist" / "index.js"
            if not ts_runtime_path.exists():
                print("\n🔨 Building TypeScript runtime (auto-heal)...")
                print("   This may take 30-60 seconds on first build...\n")
                
                # Verify Node.js and npm are available before attempting build
                try:
                    node_check = subprocess.run(
                        ["node", "--version"],
                        capture_output=True,
                        timeout=5,
                        text=True
                    )
                    npm_check = subprocess.run(
                        ["npm", "--version"],
                        capture_output=True,
                        timeout=5,
                        text=True
                    )
                    
                    if node_check.returncode != 0 or npm_check.returncode != 0:
                        print("   ❌ Node.js/npm not available.\n")
                        print("   The TypeScript runtime requires Node.js and npm.")
                        print("\n   Please install Node.js from: https://nodejs.org/")
                        print("   Then try again with:")
                        print("      bash /Users/fredbook/Code/uDOS/core/tools/build_ts_runtime.sh")
                        return
                    
                except Exception as e:
                    print("   ⚠️  Could not verify Node.js/npm availability.\n")
                    print(f"   Error: {e}")
                    print("\n   Try manually building:")
                    build_script = self.repo_root / "core" / "tools" / "build_ts_runtime.sh"
                    print(f"      bash {build_script}")
                    return
                
                # Self-heal: automatically build the TS runtime
                build_script = self.repo_root / "core" / "tools" / "build_ts_runtime.sh"
                if build_script.exists():
                    try:
                        import threading
                        
                        # Spinner animation
                        spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
                        spinner_idx = [0]
                        build_complete = [False]
                        
                        def show_spinner():
                            """Show animated spinner while build runs."""
                            while not build_complete[0]:
                                sys.stdout.write(f'\r   {spinner_chars[spinner_idx[0]]} Building...')
                                sys.stdout.flush()
                                spinner_idx[0] = (spinner_idx[0] + 1) % len(spinner_chars)
                                time.sleep(0.1)
                        
                        # Start spinner in background thread
                        spinner_thread = threading.Thread(target=show_spinner, daemon=True)
                        spinner_thread.start()
                        
                        # Run build with combined output for better error visibility
                        result = subprocess.run(
                            ["bash", str(build_script)],
                            cwd=str(self.repo_root),
                            capture_output=True,
                            timeout=300,  # 5 minute timeout for build
                            text=True
                        )
                        
                        build_complete[0] = True
                        spinner_thread.join(timeout=1)
                        
                        # Clear the spinner line
                        sys.stdout.write('\r' + ' ' * 50 + '\r')
                        sys.stdout.flush()
                        
                        if result.returncode == 0:
                            print("   ✅ TypeScript runtime built successfully!")
                            self.logger.info("[SETUP] TS runtime auto-built")
                            
                            # Small delay for visual clarity
                            time.sleep(0.5)
                        else:
                            print("   ❌ Build failed.\n")
                            
                            # Combine stdout and stderr for complete error picture
                            output_text = result.stdout + result.stderr
                            
                            if output_text.strip():
                                print("   Error details:")
                                # Show last 20 lines of output
                                lines = output_text.split("\n")
                                for line in lines[-20:]:
                                    if line.strip():
                                        print("   " + line)
                            else:
                                print("   (No error output captured)")
                            
                            print("\n   To fix manually, run:")
                            print(f"      bash {build_script}")
                            print("\n   Or check the build logs:")
                            log_path = self.repo_root / "core" / "grid-runtime" / "build.log"
                            print(f"      tail -100 {log_path}")
                            return
                    except subprocess.TimeoutExpired:
                        build_complete[0] = True
                        sys.stdout.write('\r' + ' ' * 50 + '\r')
                        sys.stdout.flush()
                        print("   ❌ Build timed out (>5 minutes).\n")
                        print("   The TypeScript runtime is taking too long to build.")
                        print("   Try manually:")
                        print(f"      bash {build_script}")
                        return
                    except Exception as e:
                        build_complete[0] = True
                        sys.stdout.write('\r' + ' ' * 50 + '\r')
                        sys.stdout.flush()
                        print(f"   ❌ Build error: {e}\n")
                        print("   To fix manually, run:")
                        print(f"      bash {build_script}")
                        return
                else:
                    print(f"   ❌ Build script not found: {build_script}")
                    return
            
            # TS runtime is available - run setup story automatically
            print()
            if self._ask_yes_no("Run setup story now"):
                print("\n🚀 Launching setup story...\n")
                
                # Auto-execute the STORY wizard-setup command
                result = self.dispatcher.dispatch("STORY wizard-setup")
                
                # Check if this is a form-based story
                if result.get("story_form"):
                    collected_data = self._handle_story_form(result["story_form"])
                    print("\n✅ Setup form completed!")
                    print(f"\nCollected {len(collected_data)} values")
                    
                    # Save the collected data to user profile
                    if collected_data:
                        self._save_user_profile(collected_data)
                        print("\nData saved. Next steps:")
                        print("  SETUP              - View your profile")
                        print("  CONFIG             - View variables")
                else:
                    # Show the result for non-form stories
                    output = self.renderer.render(result)
                    print(output)
                
                self.logger.info("[SETUP] Fresh install setup completed")
            else:
                print("\n⏭️  Setup skipped. You can run it anytime with:")
                print("   STORY wizard-setup")
                print()
        
        except Exception as e:
            self.logger.error(f"[SETUP] Fresh install check failed: {e}", exc_info=True)
            # Non-fatal error, continue with startup

    def _show_component_status(self) -> None:
        """Show detected components."""
        print("\n📦 Component Detection:\n")
        for comp_name, comp in self.components.items():
            status = "✅" if comp.state == ComponentState.AVAILABLE else "❌"
            version_str = f" ({comp.version})" if comp.version else ""
            print(f"  {status} {comp.name.upper():12} {comp.description}{version_str}")
        print()

    def _cmd_status(self, args: str) -> None:
        """Show system status."""
        print("\n═══ uCODE STATUS ═══\n")
        self._show_component_status()

        if self.detector.is_available("wizard"):
            print("🧙 Wizard Server control available: Use WIZARD [start|stop|status]")
        if self.detector.is_available("extensions"):
            print("🔌 Extension management available: Use PLUGIN [list|install|remove]")
        print()

    def _cmd_help(self, args: str) -> None:
        """Show help."""
        help_text = """
═══ uCODE HELP ═══

Core Commands:
  STATUS              - Show system status
  HELP                - This help message
  EXIT, QUIT          - Exit uCODE

System Management:
  SETUP               - View your setup profile from Wizard Server
  CONFIG              - Manage configuration variables
  DESTROY             - System cleanup (wipe user, compost, reset)
  SHAKEDOWN           - Validate system health
  REPAIR              - Fix issues and self-heal
  RESTART             - Restart/reload system
  USER                - User profile and permission management
  LOGS                - View unified system logs

Data & Stories:
  BINDER              - Multi-chapter project management
  STORY [name]        - Run story files (.md with questions/flow)
  RUN [file]          - Execute uPy scripts or USCRIPT files
  DATASET             - Manage data imports and datasets

Navigation & Info:
  MAP                 - Show spatial map
  GOTO [location]     - Travel to location
  FIND [query]        - Search for locations
  TELL [query]        - Get information
  BAG                 - Inventory management

"""
        if self.detector.is_available("wizard"):
            help_text += """Wizard Server:
  WIZARD start        - Start Wizard server
  WIZARD stop         - Stop Wizard server
  WIZARD status       - Check Wizard status
  WIZARD console      - Enter Wizard interactive console
  WIZARD [page]       - Show Wizard page (status, ai, devices, quota, logs)

"""
        if self.detector.is_available("extensions"):
            help_text += """Extensions:
  PLUGIN list         - List installed plugins
  PLUGIN install      - Install new plugin
  PLUGIN remove       - Remove plugin
  PLUGIN pack         - Package plugin for distribution
  EXT [cmd]           - Alias for PLUGIN

"""
        help_text += """
Examples:
  SETUP                      - View your setup profile
  STORY wizard-setup         - Run setup story
  DESTROY --wipe-user        - Wipe user data
  WIZARD start               - Start Wizard Server
  BINDER open my-project     - Open a project
  MAP                        - Show spatial map

For detailed help on any command, type the command name followed by --help
(e.g., CONFIG --help, DESTROY --help)

"""
        print(help_text)

    def _cmd_wizard(self, args: str) -> None:
        """Wizard server control."""
        if not self.detector.is_available("wizard"):
            print("❌ Wizard component not available.")
            return

        parts = args.split(None, 1)
        action = parts[0].lower() if parts else "status"
        subargs = parts[1] if len(parts) > 1 else ""

        if action == "start":
            print("\n🧙 Starting Wizard Server...")
            self._wizard_start()
        elif action == "stop":
            print("\n🧙 Stopping Wizard Server...")
            self._wizard_stop()
        elif action == "status":
            print("\n🧙 Wizard Server Status:")
            self._wizard_status()
        elif action == "console":
            print("\n🧙 Entering Wizard interactive console...")
            self._wizard_console()
        elif action in ("pages", "help"):
            print("\nWizard pages: status, ai, services, quota, devices, logs, config")
        else:
            print(f"\n🧙 Wizard [{action}]:")
            self._wizard_page(action)

    def _wizard_start(self) -> None:
        """Start Wizard server."""
        try:
            # Check if already running
            try:
                resp = requests.get("http://127.0.0.1:8765/health", timeout=1)
                if resp.status_code == 200:
                    print("  ✅ Wizard already running")
                    return
            except requests.exceptions.ConnectionError:
                pass  # Not running, proceed

            print("  Starting Wizard Server...")
            venv_activate = self.repo_root / ".venv" / "bin" / "activate"
            
            # Build command
            if venv_activate.exists():
                cmd = f"source {venv_activate} && python wizard/server.py"
            else:
                cmd = "python wizard/server.py"

            # Start in background with proper I/O isolation
            try:
                with open(os.devnull, 'w') as devnull:
                    with open(os.devnull, 'r') as devnull_in:
                        proc = subprocess.Popen(
                            cmd,
                            shell=True,
                            cwd=str(self.repo_root),
                            stdin=devnull_in,
                            stdout=devnull,
                            stderr=devnull,
                            preexec_fn=os.setsid if sys.platform != 'win32' else None
                        )
            except Exception as start_err:
                raise Exception(f"Failed to spawn wizard process: {start_err}")
            
            # Wait for server to be ready
            max_wait = 10
            start = time.time()
            while time.time() - start < max_wait:
                try:
                    resp = requests.get("http://127.0.0.1:8765/health", timeout=1)
                    if resp.status_code == 200:
                        print(f"  ✅ Wizard Server started (PID: {proc.pid})")
                        sys.stdout.flush()  # Ensure output is flushed
                        return
                except requests.exceptions.ConnectionError:
                    time.sleep(0.5)

            print("  ⚠️  Wizard Server started but not responding (timeout)")
            sys.stdout.flush()

        except Exception as e:
            self.logger.error(f"Failed to start Wizard: {e}")
            print(f"  ❌ Error: {e}")
            sys.stdout.flush()

    def _wizard_stop(self) -> None:
        """Stop Wizard server."""
        try:
            # Kill all python processes running wizard/server.py
            if sys.platform == 'win32':
                cmd = "taskkill /F /IM python.exe"
            else:
                cmd = "pkill -f 'wizard/server.py' || pkill -f 'wizard.server' || true"
            
            subprocess.run(cmd, shell=True, timeout=5)
            print("  ✅ Wizard Server stopped")
            sys.stdout.flush()  # Ensure output is flushed
            time.sleep(0.5)

        except Exception as e:
            self.logger.error(f"Failed to stop Wizard: {e}")
            print(f"  ❌ Error: {e}")
            sys.stdout.flush()

    def _wizard_status(self) -> None:
        """Check Wizard status."""
        try:
            resp = requests.get("http://127.0.0.1:8765/health", timeout=2)
            if resp.status_code == 200:
                print("  ✅ Wizard running on http://127.0.0.1:8765")
                data = resp.json()
                if "status" in data:
                    print(f"     Status: {data['status']}")
            else:
                print("  ❌ Wizard not responding")
        except requests.exceptions.ConnectionError:
            print("  ❌ Wizard not running")
        except Exception as e:
            print(f"  ⚠️  Error checking status: {e}")

    def _wizard_console(self) -> None:
        """Enter Wizard interactive console."""
        try:
            print("  Launching Wizard interactive console...")
            venv_activate = self.repo_root / ".venv" / "bin" / "activate"
            
            if venv_activate.exists():
                cmd = f"source {venv_activate} && python wizard/wizard_tui.py"
            else:
                cmd = "python wizard/wizard_tui.py"

            subprocess.run(cmd, shell=True, cwd=str(self.repo_root))

        except Exception as e:
            self.logger.error(f"Failed to launch Wizard console: {e}")
            print(f"  ❌ Error: {e}")

    def _wizard_page(self, page: str) -> None:
        """Show Wizard page via API."""
        try:
            # Map page names to API endpoints
            page_map = {
                "status": "/health",
                "ai": "/api/v1/ai/status",
                "services": "/api/v1/status",
                "devices": "/api/v1/devices",
                "quota": "/api/v1/ai/quota",
                "logs": "/api/v1/logs",
            }

            endpoint = page_map.get(page.lower())
            if not endpoint:
                print(f"  ❌ Unknown page: {page}")
                print(f"     Available: {', '.join(page_map.keys())}")
                return

            resp = requests.get(f"http://127.0.0.1:8765{endpoint}", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                print(json.dumps(data, indent=2))
            else:
                print(f"  ❌ Request failed: {resp.status_code}")

        except requests.exceptions.ConnectionError:
            print("  ❌ Wizard not running. Start with: WIZARD start")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    def _cmd_plugin(self, args: str) -> None:
        """Plugin/extension management."""
        if not self.detector.is_available("extensions"):
            print("❌ Extensions component not available.")
            return

        parts = args.split(None, 1)
        action = parts[0].lower() if parts else "list"
        subargs = parts[1] if len(parts) > 1 else ""

        if action == "list":
            print("\n🔌 Installed Plugins:\n")
            self._plugin_list()
        elif action == "install":
            print(f"\n🔌 Installing plugin: {subargs}")
            self._plugin_install(subargs)
        elif action == "remove":
            print(f"\n🔌 Removing plugin: {subargs}")
            self._plugin_remove(subargs)
        elif action == "pack":
            print(f"\n🔌 Packaging plugin: {subargs}")
            self._plugin_pack(subargs)
        elif action in ("help", "info"):
            print("\nPlugin commands: list, install <name>, remove <name>, pack <name>")
        else:
            print(f"\n🔌 Unknown plugin action: {action}")

    def _plugin_list(self) -> None:
        """List installed plugins."""
        try:
            ext_path = self.repo_root / "extensions"
            if not ext_path.exists():
                print("  ❌ Extensions folder not found")
                return

            # Scan for extensions
            extensions = []
            for item in ext_path.iterdir():
                if item.is_dir() and (item / "version.json").exists():
                    try:
                        with open(item / "version.json") as f:
                            data = json.load(f)
                            version = data.get("display") or data.get("version", "unknown")
                            extensions.append((item.name, version))
                    except Exception:
                        extensions.append((item.name, "error reading version"))

            if extensions:
                print("  Installed Extensions:")
                for name, version in sorted(extensions):
                    print(f"    ✅ {name:15} {version}")
            else:
                print("  No extensions installed")

        except Exception as e:
            print(f"  ❌ Error listing extensions: {e}")

    def _plugin_install(self, name: str) -> None:
        """Install a plugin."""
        try:
            print(f"  🔌 Installing plugin: {name}")
            print("  [TODO] Implement plugin install from registry")
            print("         Use PLUGIN list to see available plugins")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    def _plugin_remove(self, name: str) -> None:
        """Remove a plugin."""
        try:
            ext_path = self.repo_root / "extensions" / name
            if not ext_path.exists():
                print(f"  ❌ Plugin not found: {name}")
                return

            # Safety confirmation
            print(f"  ⚠️  Remove plugin: {name}?")
            response = input("  Type 'yes' to confirm: ").strip().lower()
            if response == 'yes':
                import shutil
                shutil.rmtree(ext_path)
                print(f"  ✅ Plugin removed: {name}")
            else:
                print("  Cancelled")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    def _plugin_pack(self, name: str) -> None:
        """Package a plugin for distribution."""
        try:
            ext_path = self.repo_root / "extensions" / name
            if not ext_path.exists():
                print(f"  ❌ Extension not found: {name}")
                return

            # Create distribution package
            dist_path = self.repo_root / "distribution" / "plugins" / name
            print(f"  📦 Packaging {name}...")
            
            # TODO: Real packaging logic (copy to distribution, create manifest, etc)
            print(f"  [TODO] Package {name} for distribution")
            print(f"         Output: {dist_path}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    def _cmd_exit(self, args: str) -> None:
        """Exit uCODE."""
        self.running = False
        print("\n👋 Goodbye!")

    def _cleanup(self) -> None:
        """Cleanup on exit."""
        self.logger.info("uCODE TUI shutting down")


def main():
    """Main entry point for uCODE."""
    tui = uCODETUI()
    tui.run()


if __name__ == "__main__":
    main()
