"""
Error Interceptor Middleware

Wraps command execution with intelligent error handling, context capture,
and theme-aware prompts. Integrates with OK Assistant for AI-powered fixes.

Part of v1.2.22 - Self-Healing & Auto-Error-Awareness System
"""

import json
import os
import re
import subprocess
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from core.config import Config


class ErrorContext:
    """Represents captured error context with sanitization."""
    
    def __init__(self, error: Exception, command: str, params: List[str]):
        self.error = error
        self.command = command
        self.params = params
        self.timestamp = datetime.now()
        self.context = {}
        
    def capture_context(self, config: Config, session_analytics=None):
        """Capture full error context with sanitization."""
        # Basic error info
        self.context['error_type'] = type(self.error).__name__
        self.context['error_message'] = str(self.error)
        self.context['command'] = self.command
        self.context['params'] = self.params
        self.context['timestamp'] = self.timestamp.isoformat()
        
        # Stack trace (sanitized)
        tb = traceback.format_exception(type(self.error), self.error, self.error.__traceback__)
        self.context['stack_trace'] = self._sanitize_stack_trace(tb)
        
        # Git status (if available)
        try:
            git_result = subprocess.run(
                ['git', 'status', '--short'],
                capture_output=True,
                text=True,
                timeout=2,
                cwd=config.project_root
            )
            if git_result.returncode == 0:
                self.context['git_status'] = git_result.stdout.strip()
        except Exception:
            self.context['git_status'] = None
        
        # Recent commands (sanitized)
        if session_analytics:
            try:
                recent = session_analytics.get_recent_commands(10)
                self.context['recent_commands'] = self._sanitize_commands(recent)
            except Exception:
                self.context['recent_commands'] = []
        
        # Workspace state
        self.context['workspace'] = {
            'theme': config.get('theme', 'foundation'),
            'location': config.get('last_location', 'unknown'),
            'timezone': config.get_env('TIMEZONE', 'UTC')
        }
        
        # Severity classification
        self.context['severity'] = self._classify_severity()
        
        # Signature hash for pattern matching
        self.context['signature'] = self._generate_signature()
        
    def _sanitize_stack_trace(self, tb_lines: List[str]) -> str:
        """Compress and sanitize stack trace to single line."""
        # Extract relevant frames only
        relevant = []
        for line in tb_lines:
            if 'File "' in line:
                # Convert absolute paths to relative
                sanitized = re.sub(r'File ".*?/(core|extensions|memory)/', r'File "\1/', line)
                # Remove username from paths
                sanitized = re.sub(r'/Users/[^/]+/', '/Users/<user>/', sanitized)
                # Compress to single line format
                match = re.search(r'File "(.*?)", line (\d+)', sanitized)
                if match:
                    file_path, line_num = match.groups()
                    # Get error type from next line
                    error_match = re.search(r'^\s*(.+?):\s*(.+)$', line, re.MULTILINE)
                    if error_match:
                        relevant.append(f"File {file_path}:{line_num}")
        
        # Join to single line
        return " → ".join(relevant) if relevant else "unknown"
    
    def _sanitize_commands(self, commands: List[str]) -> str:
        """Compress command history to single line."""
        if not commands:
            return ""
        
        # Strip sensitive data from commands
        sanitized = []
        for cmd in commands:
            # Remove API keys
            cmd = re.sub(r'(api[_-]?key[=\s]+)[^\s]+', r'\1***', cmd, flags=re.I)
            # Remove passwords
            cmd = re.sub(r'(pass(word)?[=\s]+)[^\s]+', r'\1***', cmd, flags=re.I)
            # Remove absolute paths
            cmd = re.sub(r'/Users/[^/\s]+/', '<user>/', cmd)
            sanitized.append(cmd)
        
        return "; ".join(sanitized[-5:])  # Last 5 commands only
    
    def _classify_severity(self) -> str:
        """Classify error severity."""
        error_type = type(self.error).__name__
        
        critical_errors = [
            'SystemExit', 'KeyboardInterrupt', 'MemoryError',
            'RecursionError', 'SyntaxError'
        ]
        
        high_errors = [
            'PermissionError', 'FileNotFoundError', 'ImportError',
            'AttributeError', 'ModuleNotFoundError'
        ]
        
        if error_type in critical_errors:
            return 'critical'
        elif error_type in high_errors:
            return 'high'
        elif 'Error' in error_type:
            return 'medium'
        else:
            return 'low'
    
    def _generate_signature(self) -> str:
        """Generate unique signature for pattern matching."""
        import hashlib
        
        # Combine error type + message pattern + file location
        error_type = type(self.error).__name__
        message_pattern = re.sub(r'\d+', 'N', str(self.error))  # Replace numbers with N
        message_pattern = re.sub(r'["\'].*?["\']', '""', message_pattern)  # Replace strings
        
        # Extract file from stack trace
        file_pattern = ""
        if 'stack_trace' in self.context:
            match = re.search(r'File ([^:]+)', self.context['stack_trace'])
            if match:
                file_pattern = match.group(1)
        
        signature_str = f"{error_type}:{message_pattern}:{file_pattern}"
        return hashlib.sha256(signature_str.encode()).hexdigest()[:16]
    
    def to_json(self) -> str:
        """Serialize to single-line JSON."""
        return json.dumps(self.context, separators=(',', ':'))


class ErrorContextManager:
    """Manages error context storage with unified smart retention."""
    
    def __init__(self, config: Config):
        self.config = config
        self.contexts_dir = Path(config.project_root) / "memory" / "logs" / "error_contexts"
        self.archive_dir = self.contexts_dir / ".archive"
        self.contexts_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Create symlink for latest error
        self.latest_link = self.contexts_dir / "latest.json"
    
    def add_context(self, error_context: ErrorContext):
        """Add error context with smart retention."""
        # Save context file
        filename = f"{error_context.timestamp.strftime('%Y%m%d_%H%M%S')}_{error_context.context['signature']}.json"
        filepath = self.contexts_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(error_context.to_json())
        
        # Update latest symlink
        if self.latest_link.exists() or self.latest_link.is_symlink():
            self.latest_link.unlink()
        self.latest_link.symlink_to(filename)
        
        # Apply retention policy
        self._apply_retention()
    
    def _apply_retention(self):
        """Unified smart retention policy."""
        all_contexts = list(self.contexts_dir.glob("*.json"))
        all_contexts = [f for f in all_contexts if f.name != "latest.json"]
        
        now = datetime.now()
        keep = set()
        
        # Parse and categorize contexts
        contexts_data = []
        for filepath in all_contexts:
            try:
                with open(filepath, 'r') as f:
                    data = json.loads(f.read())
                    data['filepath'] = filepath
                    data['timestamp_dt'] = datetime.fromisoformat(data['timestamp'])
                    contexts_data.append(data)
            except Exception:
                continue
        
        # Rule 1: Keep all from last 7 days
        seven_days_ago = now - timedelta(days=7)
        for ctx in contexts_data:
            if ctx['timestamp_dt'] > seven_days_ago:
                keep.add(ctx['filepath'])
        
        # Rule 2: Keep last 20 critical/high severity
        high_severity = [c for c in contexts_data if c.get('severity') in ['critical', 'high']]
        high_severity.sort(key=lambda x: x['timestamp_dt'], reverse=True)
        for ctx in high_severity[:20]:
            keep.add(ctx['filepath'])
        
        # Rule 3: Keep last 5 per unique signature
        by_signature = {}
        for ctx in contexts_data:
            sig = ctx.get('signature', 'unknown')
            if sig not in by_signature:
                by_signature[sig] = []
            by_signature[sig].append(ctx)
        
        for signature_contexts in by_signature.values():
            signature_contexts.sort(key=lambda x: x['timestamp_dt'], reverse=True)
            for ctx in signature_contexts[:5]:
                keep.add(ctx['filepath'])
        
        # Archive old contexts (monthly archives)
        for ctx in contexts_data:
            if ctx['filepath'] not in keep:
                month = ctx['timestamp_dt'].strftime('%Y-%m')
                archive_file = self.archive_dir / f"{month}.json.gz"
                
                # Append to monthly archive (compressed)
                import gzip
                mode = 'ab' if archive_file.exists() else 'wb'
                with gzip.open(archive_file, mode) as f:
                    f.write((json.dumps(ctx) + '\n').encode())
                
                # Delete original
                ctx['filepath'].unlink()
    
    def get_recent(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get all errors from last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        results = []
        
        for filepath in self.contexts_dir.glob("*.json"):
            if filepath.name == "latest.json":
                continue
            
            try:
                with open(filepath, 'r') as f:
                    data = json.loads(f.read())
                    if datetime.fromisoformat(data['timestamp']) > cutoff:
                        results.append(data)
            except Exception:
                continue
        
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)
    
    def get_by_severity(self, level: str) -> List[Dict[str, Any]]:
        """Get errors by severity level."""
        results = []
        
        for filepath in self.contexts_dir.glob("*.json"):
            if filepath.name == "latest.json":
                continue
            
            try:
                with open(filepath, 'r') as f:
                    data = json.loads(f.read())
                    if data.get('severity') == level:
                        results.append(data)
            except Exception:
                continue
        
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)
    
    def get_by_signature(self, signature: str) -> List[Dict[str, Any]]:
        """Get errors matching signature pattern."""
        results = []
        
        for filepath in self.contexts_dir.glob("*.json"):
            if filepath.name == "latest.json":
                continue
            
            try:
                with open(filepath, 'r') as f:
                    data = json.loads(f.read())
                    if data.get('signature') == signature:
                        results.append(data)
            except Exception:
                continue
        
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)


class ErrorInterceptor:
    """Main error interceptor for command execution."""
    
    def __init__(self, config: Config, theme_messenger=None, session_analytics=None):
        self.config = config
        self.theme_messenger = theme_messenger
        self.session_analytics = session_analytics
        self.context_manager = ErrorContextManager(config)
    
    def intercept(self, func: Callable, *args, **kwargs) -> Tuple[Any, Optional[Exception]]:
        """Intercept function execution with error handling."""
        try:
            result = func(*args, **kwargs)
            return result, None
        except Exception as e:
            # Don't intercept system exits or keyboard interrupts
            if isinstance(e, (SystemExit, KeyboardInterrupt)):
                raise
            
            # Capture error context
            error_context = ErrorContext(
                e,
                kwargs.get('command', 'unknown'),
                kwargs.get('params', [])
            )
            error_context.capture_context(self.config, self.session_analytics)
            
            # Save context
            self.context_manager.add_context(error_context)
            
            # Prompt user with theme-aware options
            action = self._prompt_user(error_context)
            
            if action == 'retry':
                # Retry the command
                return self.intercept(func, *args, **kwargs)
            elif action == 'ok_help':
                # Trigger OK FIX command
                return None, e
            elif action == 'dev_mode':
                # Enable DEV MODE at error line
                return None, e
            else:
                # Continue (return error)
                return None, e
    
    def _prompt_user(self, error_context: ErrorContext) -> str:
        """Display theme-aware error prompt."""
        if self.theme_messenger:
            # Use theme messenger for formatted output
            prompt = self.theme_messenger.format_message(
                'prompt',
                'prompt_error_options',
                error=error_context.context['error_type'],
                message=error_context.context['error_message']
            )
        else:
            # Fallback to plain text
            prompt = f"\n💀 Error: {error_context.context['error_type']}\n"
            prompt += f"   {error_context.context['error_message']}\n\n"
            prompt += "Options:\n"
            prompt += "  1. Retry\n"
            prompt += "  2. Get OK Help (AI-powered fix)\n"
            prompt += "  3. Enter DEV MODE\n"
            prompt += "  4. Continue\n\n"
            prompt += "Choose [1|2|3|4]: "
        
        print(prompt, end='')
        
        try:
            choice = input().strip()
            if choice == '1':
                return 'retry'
            elif choice == '2':
                return 'ok_help'
            elif choice == '3':
                return 'dev_mode'
            else:
                return 'continue'
        except (EOFError, KeyboardInterrupt):
            return 'continue'


# Global singleton instance
_error_context_manager = None


def get_error_context_manager() -> 'ErrorContextManager':
    """Get global ErrorContextManager singleton."""
    global _error_context_manager
    if _error_context_manager is None:
        from core.config import Config
        config = Config()
        _error_context_manager = ErrorContextManager(config)
    return _error_context_manager
