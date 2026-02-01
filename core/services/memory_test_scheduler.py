"""Memory test scheduler and starter utility.

Automatically detects new or modified files under memory/tests/ and runs the
Python automation runner as part of the self-heal/startup pipeline.
"""

import json
import logging
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from core.services.logging_service import get_logger


class MemoryTestScheduler:
    METADATA_NAME = '.memory-test-run.json'
    AUTOMATION_SCRIPT = 'automation.py'

    def __init__(self, repo_root: Path, logger: Optional[logging.Logger] = None):
        self.repo_root = repo_root
        self.logger = logger or get_logger('memory-tests')
        self.tests_dir = (self.repo_root / 'memory' / 'tests')
        self.metadata_path = self.tests_dir / self.METADATA_NAME
        self.log_path = self.repo_root / 'memory' / 'logs' / 'memory-tests.log'
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._thread: Optional[threading.Thread] = None
        self.summary: Dict[str, Any] = {
            'status': 'idle',
            'pending': 0,
            'last_run': None,
            'result': None,
            'log_path': str(self.log_path),
        }

    def schedule(self) -> Dict[str, Any]:
        if not self.tests_dir.exists():
            self.summary.update({
                'status': 'missing',
                'pending': 0,
                'result': None,
                'error': 'memory/tests directory not found',
                'log_path': str(self.log_path),
            })
            return self.summary

        pending, snapshot, metadata = self._evaluate_pending(metadata=self._read_metadata())
        self.summary.update({
            'pending': pending,
            'last_run': metadata.get('timestamp'),
            'result': metadata.get('result'),
            'log_path': str(self.log_path),
        })

        if pending == 0:
            self.summary['status'] = 'up-to-date'
            return self.summary

        if self._thread and self._thread.is_alive():
            self.summary['status'] = 'running'
            return self.summary

        self.summary['status'] = 'scheduled'
        self._thread = threading.Thread(target=self._run_tests, args=(snapshot,), daemon=True)
        self._thread.start()
        return self.summary

    def _evaluate_pending(
        self,
        metadata: Dict[str, Any],
    ) -> Tuple[int, Dict[str, float], Dict[str, Any]]:
        test_files = [p for p in sorted(self.tests_dir.glob('test_*.py')) if p.is_file()]
        snapshot: Dict[str, float] = {}
        pending = 0
        recorded = metadata.get('files', {})

        for test_file in test_files:
            mtime = test_file.stat().st_mtime
            snapshot[test_file.name] = mtime
            if mtime > recorded.get(test_file.name, 0):
                pending += 1

        return pending, snapshot, metadata

    def _run_tests(self, snapshot: Dict[str, float]) -> None:
        script_path = self.tests_dir / self.AUTOMATION_SCRIPT
        if not script_path.exists():
            self.logger.warning('[MemoryTests] Automation script missing: %s', script_path)
            self.summary.update({'status': 'error', 'error': 'automation.py missing'})
            return

        self.logger.info('[MemoryTests] Detected changes, running automation suite...')
        start = time.time()
        cmd = [sys.executable, str(script_path)]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.tests_dir,
        )
        duration = time.time() - start
        success = result.returncode == 0
        metadata = {
            'timestamp': time.time(),
            'files': snapshot,
            'result': 'pass' if success else 'fail',
        }
        self._write_metadata(metadata)

        status = 'success' if success else 'failed'
        self.summary.update({
            'status': status,
            'pending': 0,
            'last_run': metadata['timestamp'],
            'result': metadata['result'],
            'duration': duration,
            'output': result.stdout,
            'errors': result.stderr,
            'log_path': str(self.log_path),
        })

        self.logger.info(
            '[MemoryTests] %s (duration: %.2fs)',
            'passed' if success else 'failed',
            duration,
        )
        self._append_log(result.stdout, result.stderr, success, duration)

    def _write_metadata(self, metadata: Dict[str, Any]) -> None:
        try:
            self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.metadata_path, 'w') as fh:
                json.dump(metadata, fh)
        except Exception as exc:
            self.logger.warning('[MemoryTests] Failed to write metadata: %s', exc)

    def _read_metadata(self) -> Dict[str, Any]:
        if not self.metadata_path.exists():
            return {'timestamp': 0, 'files': {}, 'result': None}
        try:
            with open(self.metadata_path, 'r') as fh:
                return json.load(fh)
        except Exception as exc:
            self.logger.warning('[MemoryTests] Failed to read metadata: %s', exc)
            return {'timestamp': 0, 'files': {}, 'result': None}

    def _append_log(self, stdout: str, stderr: str, success: bool, duration: float) -> None:
        entry = {
            'timestamp': time.time(),
            'status': 'pass' if success else 'fail',
            'duration': duration,
            'stdout': stdout[:1024],
            'stderr': stderr[:1024],
        }
        try:
            with open(self.log_path, 'a') as fh:
                fh.write(json.dumps(entry) + '\n')
        except Exception as exc:
            self.logger.warning('[MemoryTests] Failed to write log: %s', exc)
