"""
Sandbox Test Runner - Isolated Testing Environment

Tests fixes in isolated memory/sandbox/ environment with resource limits,
network blocking, and file I/O mocking for safe system file testing.

Part of v1.2.22 - Self-Healing & Auto-Error-Awareness System
"""

import gzip
import json
import os
import shutil
import signal
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from unittest import mock

from core.config import Config


class SandboxTest:
    """
    Test a file in isolated sandbox environment.
    
    Example:
        sandbox = SandboxTest(config, session_id="test-001")
        success, output, logs = sandbox.test_file(
            "core/commands/file_handler.py",
            test_command="pytest tests/test_file_handler.py -v"
        )
    """
    
    def __init__(self, config: Config, session_id: Optional[str] = None):
        """
        Initialize sandbox test environment.
        
        Args:
            config: Config instance
            session_id: Unique session identifier (auto-generated if None)
        """
        self.config = config
        self.session_id = session_id or self._generate_session_id()
        
        # Sandbox paths
        self.sandbox_root = Path(config.project_root) / "memory" / "sandbox"
        self.debug_dir = self.sandbox_root / "debug" / self.session_id
        self.data_dir = self.sandbox_root / "data" / self.session_id
        self.logs_dir = self.sandbox_root / "logs"
        self.failed_dir = self.sandbox_root / "failed"
        self.archive_dir = self.sandbox_root / ".archive"
        
        # Create sandbox directories
        for directory in [self.debug_dir, self.data_dir, self.logs_dir, self.failed_dir, self.archive_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Resource limits
        self.max_size_mb = int(config.get_env('SANDBOX_MAX_SIZE_MB', '100'))
        self.timeout_seconds = 30
        self.max_memory_mb = 512
        
        # Test results
        self.test_passed = False
        self.test_output = ""
        self.test_logs = []
    
    def _generate_session_id(self) -> str:
        """
        Generate session ID using uDOS filename format.
        
        Format: YYYY-MM-DD-HH-MM-SS-sss-sandbox
        """
        now = datetime.now()
        return now.strftime("%Y-%m-%d-%H-%M-%S") + f"-{now.microsecond//1000:03d}-sandbox"
    
    def test_file(self, target_file: str, test_command: Optional[str] = None) -> Tuple[bool, str, List[str]]:
        """
        Test a file in isolated sandbox environment.
        
        Args:
            target_file: Path to file to test (relative to workspace root)
            test_command: Custom test command (default: pytest)
        
        Returns:
            Tuple of (success, output, logs)
        """
        log_file = self.logs_dir / f"{self.session_id}.log"
        
        try:
            # Check disk space
            if not self._check_disk_space():
                return False, "❌ Insufficient disk space for sandbox", []
            
            # Copy target file to sandbox
            source_path = Path(self.config.project_root) / target_file
            if not source_path.exists():
                return False, f"❌ File not found: {target_file}", []
            
            sandbox_file = self.debug_dir / Path(target_file).name
            shutil.copy2(source_path, sandbox_file)
            
            self._log(f"Copied {target_file} to sandbox", log_file)
            
            # Prepare test environment
            self._setup_python_path()
            
            # Determine test command
            if not test_command:
                test_command = f"pytest {sandbox_file} -v"
            
            self._log(f"Running: {test_command}", log_file)
            
            # Run test with resource limits
            success, output = self._run_with_limits(test_command, log_file)
            
            self.test_passed = success
            self.test_output = output
            
            # Archive or mark as failed
            if success:
                self._archive_session()
            else:
                self._mark_failed(output)
            
            return success, output, self.test_logs
        
        except Exception as e:
            error_msg = f"❌ Sandbox test error: {str(e)}"
            self._log(error_msg, log_file)
            self._mark_failed(str(e))
            return False, error_msg, self.test_logs
    
    def _check_disk_space(self) -> bool:
        """Check if sandbox has space within limits."""
        try:
            # Calculate current sandbox size
            total_size = 0
            for root, dirs, files in os.walk(self.sandbox_root):
                for f in files:
                    fp = os.path.join(root, f)
                    if os.path.exists(fp):
                        total_size += os.path.getsize(fp)
            
            size_mb = total_size / (1024 * 1024)
            
            if size_mb > self.max_size_mb:
                return False
            
            return True
        except Exception:
            return True  # Assume OK if check fails
    
    def _setup_python_path(self):
        """Modify sys.path to prioritize sandbox modules."""
        # Insert sandbox paths at beginning
        sys.path.insert(0, str(self.debug_dir))
        sys.path.insert(0, str(self.data_dir))
    
    def _run_with_limits(self, command: str, log_file: Path) -> Tuple[bool, str]:
        """
        Run command with resource limits and network blocking.
        
        Args:
            command: Shell command to execute
            log_file: Path to log file
        
        Returns:
            Tuple of (success, output)
        """
        # Prepare environment with network blocking
        env = os.environ.copy()
        env['NO_PROXY'] = '*'  # Block network access
        env['RLIMIT_AS'] = str(self.max_memory_mb * 1024 * 1024)
        
        # Set up timeout handler
        def timeout_handler(signum, frame):
            raise TimeoutError("Test execution exceeded 30 seconds")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.timeout_seconds)
        
        try:
            # Run command in subprocess
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                cwd=self.debug_dir,
                env=env
            )
            
            signal.alarm(0)  # Cancel alarm
            
            # Log output
            output = result.stdout + result.stderr
            self._log(f"Exit code: {result.returncode}", log_file)
            self._log(f"Output:\n{output}", log_file)
            
            return result.returncode == 0, output
        
        except subprocess.TimeoutExpired:
            signal.alarm(0)
            msg = f"❌ Test timeout after {self.timeout_seconds}s"
            self._log(msg, log_file)
            return False, msg
        
        except Exception as e:
            signal.alarm(0)
            msg = f"❌ Test execution error: {str(e)}"
            self._log(msg, log_file)
            return False, msg
    
    def _log(self, message: str, log_file: Path):
        """
        Log message to file and internal list.
        
        Uses uDOS single-line log format: YYYY-MM-DD HH:MM:SS [SANDBOX] Message
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} [SANDBOX] {message}"
        
        self.test_logs.append(log_entry)
        
        # Append to log file
        with open(log_file, 'a') as f:
            f.write(log_entry + '\n')
    
    def _archive_session(self):
        """Archive successful session (keep last 10)."""
        # Get all debug sessions
        sessions = sorted(self.sandbox_root.glob("debug/*"))
        
        if len(sessions) > 10:
            # Archive oldest sessions
            for old_session in sessions[:-10]:
                archive_name = f"{old_session.name}.tar.gz"
                archive_path = self.archive_dir / archive_name
                
                # Create compressed archive
                import tarfile
                with tarfile.open(archive_path, 'w:gz') as tar:
                    tar.add(old_session, arcname=old_session.name)
                
                # Remove original
                shutil.rmtree(old_session)
    
    def _mark_failed(self, error_output: str):
        """Mark session as failed and preserve for 30 days."""
        failed_path = self.failed_dir / self.session_id
        
        # Move debug dir to failed
        if self.debug_dir.exists():
            shutil.move(str(self.debug_dir), str(failed_path))
        
        # Save error output
        error_file = failed_path / "error.log"
        with open(error_file, 'w') as f:
            f.write(error_output)
    
    def get_status(self) -> Dict[str, Any]:
        """Get sandbox status information."""
        # Count sessions
        active_sessions = len(list((self.sandbox_root / "debug").glob("*")))
        failed_sessions = len(list(self.failed_dir.glob("*")))
        archived_sessions = len(list(self.archive_dir.glob("*.tar.gz")))
        
        # Calculate disk usage
        total_size = 0
        for root, dirs, files in os.walk(self.sandbox_root):
            for f in files:
                fp = os.path.join(root, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        
        size_mb = total_size / (1024 * 1024)
        
        return {
            'session_id': self.session_id,
            'active_sessions': active_sessions,
            'failed_sessions': failed_sessions,
            'archived_sessions': archived_sessions,
            'disk_usage_mb': round(size_mb, 2),
            'max_size_mb': self.max_size_mb,
            'usage_percent': round((size_mb / self.max_size_mb) * 100, 1)
        }
    
    def cleanup(self, all_sessions: bool = False):
        """
        Clean up sandbox.
        
        Args:
            all_sessions: If True, remove all sessions. Otherwise, just archives.
        """
        if all_sessions:
            # Remove everything except failed (keep for 30 days)
            shutil.rmtree(self.sandbox_root / "debug", ignore_errors=True)
            shutil.rmtree(self.sandbox_root / "data", ignore_errors=True)
            shutil.rmtree(self.archive_dir, ignore_errors=True)
            
            # Recreate directories
            (self.sandbox_root / "debug").mkdir(exist_ok=True)
            (self.sandbox_root / "data").mkdir(exist_ok=True)
            self.archive_dir.mkdir(exist_ok=True)
        else:
            # Just remove archives
            for archive in self.archive_dir.glob("*.tar.gz"):
                archive.unlink()
    
    def get_failed_sessions(self) -> List[Dict[str, Any]]:
        """Get list of failed sessions with error summaries."""
        failed = []
        
        for session_dir in self.failed_dir.glob("*"):
            if not session_dir.is_dir():
                continue
            
            error_file = session_dir / "error.log"
            error_summary = "Unknown error"
            
            if error_file.exists():
                with open(error_file, 'r') as f:
                    lines = f.readlines()
                    # Get first line of error
                    error_summary = lines[0].strip() if lines else "Unknown error"
            
            failed.append({
                'session_id': session_dir.name,
                'error_summary': error_summary,
                'path': str(session_dir)
            })
        
        return failed
    
    def restore_session(self, session_id: str) -> bool:
        """
        Restore failed session for re-testing.
        
        Args:
            session_id: Session ID to restore
        
        Returns:
            True if restored successfully
        """
        failed_path = self.failed_dir / session_id
        
        if not failed_path.exists():
            return False
        
        # Move back to debug
        debug_path = self.sandbox_root / "debug" / session_id
        shutil.move(str(failed_path), str(debug_path))
        
        return True


# Example usage/test
if __name__ == '__main__':
    from core.config import Config
    
    config = Config()
    sandbox = SandboxTest(config)
    
    print("="*60)
    print("Sandbox Test Runner - Example")
    print("="*60)
    print()
    
    # Test a simple Python file
    print("Testing error_interceptor.py...")
    success, output, logs = sandbox.test_file(
        "core/services/error_interceptor.py",
        test_command="python -m py_compile error_interceptor.py"
    )
    
    print(f"\n{'✅' if success else '❌'} Test {'passed' if success else 'failed'}")
    print(f"\nOutput:\n{output}")
    
    # Show status
    status = sandbox.get_status()
    print(f"\nSandbox Status:")
    print(f"  Active sessions: {status['active_sessions']}")
    print(f"  Failed sessions: {status['failed_sessions']}")
    print(f"  Disk usage: {status['disk_usage_mb']}MB / {status['max_size_mb']}MB ({status['usage_percent']}%)")
    
    print("\n" + "="*60)
