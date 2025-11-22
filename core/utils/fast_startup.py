"""
uDOS v1.0.31 - Fast Startup Module
Optimized system initialization with lazy loading and optional health checks

Improvements:
- Skip health checks by default (opt-in with --check flag)
- Lazy-load heavy modules (only when needed)
- Cache system detection results
- Parallel initialization where possible
- Progress indicators with visual feedback

Author: uDOS Development Team
Version: 1.0.31
Date: November 22, 2025
"""

import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path


class FastStartup:
    """Optimized startup with minimal overhead."""

    def __init__(self, verbose: bool = False, run_health_check: bool = False):
        """
        Initialize fast startup.

        Args:
            verbose: Show detailed startup messages
            run_health_check: Run full system health check (slower)
        """
        self.verbose = verbose
        self.run_health_check = run_health_check
        self.components = {}
        self._cache_file = Path.home() / '.udos' / 'startup_cache.json'

    def initialize(self, is_script_mode: bool = False) -> Dict[str, Any]:
        """
        Fast initialization with minimal checks.

        Args:
            is_script_mode: True if running a script (skip interactive setup)

        Returns:
            Dictionary of initialized components
        """
        if self.verbose and not is_script_mode:
            from core.services.standardized_input import StandardizedInput
            si = StandardizedInput()
            si.show_status("Starting uDOS", "info")

        # Step 1: Viewport (cached if available)
        viewport = self._init_viewport(is_script_mode)
        self.components['viewport'] = viewport

        # Step 2: User profile (required by main)
        from core.services.user_manager import UserManager
        user_manager = UserManager()
        viewport_data = viewport.get_status_summary()

        if user_manager.needs_user_setup():
            user_manager.run_user_setup(interactive=not is_script_mode, viewport_data=viewport_data)
        else:
            user_manager.load_user_profile()
            import time
            session_id = f"session_{int(time.time())}"
            user_manager.update_session_data(session_id, viewport_data)

        self.components['user_manager'] = user_manager

        # Step 3: Story/User data (quick load)
        story_data = self._init_story(is_script_mode)
        self.components['story_data'] = story_data

        # Step 4: Connection (initialize, but don't check unless needed)
        from core.services.connection_manager import ConnectionMonitor
        connection = ConnectionMonitor()
        # Don't check internet unless explicitly requested (saves time)
        if self.run_health_check:
            connection.check_internet_connection()
        self.components['connection'] = connection

        # Step 5: Optional health check
        if self.run_health_check and not is_script_mode:
            health = self._run_health_check()
            self.components['health'] = health

        # Step 6: History (lazy load)
        # Initialize on first use, not at startup
        self.components['history_manager'] = None
        self.components['command_history'] = None

        return self.components

    def _init_viewport(self, is_script_mode: bool):
        """Initialize viewport with caching."""
        if is_script_mode:
            # Skip detection in script mode
            from core.utils.viewport import ViewportDetector
            viewport = ViewportDetector()
            viewport.width = 80
            viewport.height = 24
            return viewport

        # Try loading from cache
        cached_viewport = self._load_viewport_cache()
        if cached_viewport:
            if self.verbose:
                print(f"{TeletextChars.SUCCESS} Viewport (cached)")
            return cached_viewport

        # Detect and cache
        if self.verbose:
            print(f"{TeletextChars.PENDING} Detecting viewport...", end=" ", flush=True)

        from core.utils.viewport import ViewportDetector
        viewport = ViewportDetector()
        viewport.detect_terminal_size()
        viewport.classify_device()

        self._save_viewport_cache(viewport)

        if self.verbose:
            print(f"\r{TeletextChars.SUCCESS} Viewport ({viewport.width}x{viewport.height})")

        return viewport

    def _init_story(self, is_script_mode: bool) -> Dict[str, Any]:
        """Initialize story/user data quickly."""
        from core.utils.setup import SystemSetup

        setup = SystemSetup()

        if setup.needs_setup():
            if is_script_mode:
                story_data = setup.create_default_story()
            else:
                if self.verbose:
                    print(f"{TeletextChars.INFO} First-time setup required")
                story_data = setup.run_setup()
        else:
            story_data = setup.load_story()

        setup.increment_session()
        self.components['setup'] = setup

        return story_data

    def _run_health_check(self) -> Any:
        """Run full health check (only if requested)."""
        if self.verbose:
            print(f"\n{TeletextChars.PENDING} Running system health check...")

        from core.uDOS_startup import check_system_health

        health = check_system_health(verbose=self.verbose, return_dict=False)

        if health.is_healthy():
            if self.verbose:
                print(f"{TeletextChars.SUCCESS} System healthy")
        else:
            if self.verbose:
                print(f"{TeletextChars.WARNING} Issues detected - run REPAIR command")

        return health

    def _load_viewport_cache(self) -> Optional[Any]:
        """Load cached viewport data."""
        if not self._cache_file.exists():
            return None

        try:
            import json
            from core.utils.viewport import ViewportDetector

            with open(self._cache_file) as f:
                data = json.load(f)

            # Check if cache is recent (less than 1 day old)
            import time
            cache_age = time.time() - data.get('timestamp', 0)
            if cache_age > 86400:  # 1 day
                return None

            viewport = ViewportDetector()
            viewport.width = data.get('width', 80)
            viewport.height = data.get('height', 24)
            viewport.device_class = data.get('device_class', 'desktop')

            return viewport

        except Exception:
            return None

    def _save_viewport_cache(self, viewport: Any):
        """Save viewport data to cache."""
        try:
            import json
            import time

            self._cache_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                'timestamp': time.time(),
                'width': viewport.width,
                'height': viewport.height,
                'device_class': getattr(viewport, 'device_class', 'desktop')
            }

            with open(self._cache_file, 'w') as f:
                json.dump(data, f)

        except Exception:
            pass  # Cache failure is non-critical


# Import teletext chars for status messages
from core.ui.visual_selector import TeletextChars


def fast_initialize(
    verbose: bool = False,
    run_health_check: bool = False,
    is_script_mode: bool = False
) -> Dict[str, Any]:
    """
    Fast initialization wrapper.

    Args:
        verbose: Show startup messages
        run_health_check: Run full health check (adds ~2 seconds)
        is_script_mode: Running in script mode

    Returns:
        Initialized components dictionary
    """
    startup = FastStartup(verbose=verbose, run_health_check=run_health_check)
    return startup.initialize(is_script_mode=is_script_mode)
