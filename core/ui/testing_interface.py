"""
Testing Interface (v1.2.19)

Run SHAKEDOWN and other tests from TUI with visualization.
T-key access for testing.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import subprocess
import json
from datetime import datetime


class TestResult:
    """Represents a test result"""
    
    def __init__(self, name: str, status: str, duration: float = 0.0, error: str = ''):
        self.name = name
        self.status = status  # PASS, FAIL, SKIP, ERROR
        self.duration = duration
        self.error = error
    
    def format(self) -> str:
        """Format test result for display"""
        icons = {
            'PASS': '✅',
            'FAIL': '❌',
            'SKIP': '⊝',
            'ERROR': '💥'
        }
        icon = icons.get(self.status, '?')
        
        duration_str = f"{self.duration:.2f}s" if self.duration > 0 else ''
        
        result = f"{icon} {self.name}"
        if duration_str:
            result += f" ({duration_str})"
        
        return result


class TestingInterface:
    """
    TUI interface for running tests.
    
    Features:
    - Run SHAKEDOWN from TUI
    - Test result visualization
    - Quick retry failed tests
    - Coverage reports
    """
    
    def __init__(self):
        """Initialize testing interface"""
        from core.utils.paths import PATHS
        self.project_root = PATHS.PROJECT_ROOT
        self.tests_dir = PATHS.MEMORY / 'ucode' / 'tests'
        
        # State
        self.test_results: List[TestResult] = []
        self.current_test_suite = 'shakedown'
        self.running = False
        self.selected_index = 0
        self.show_only_failed = False
        
        # Available test suites
        self.test_suites = {
            'shakedown': 'memory/tests/shakedown.uscript',
            'pytest': 'memory/ucode/tests/',
            'integration': 'memory/tests/integration/'
        }
    
    def render(self) -> str:
        """Render testing interface"""
        output = []
        
        # Header
        status = "RUNNING..." if self.running else "READY"
        output.append(f"╔══ TESTING INTERFACE - {status} ══╗")
        output.append("")
        
        # Test suite tabs
        output.append(self._render_suite_tabs())
        output.append("=" * 70)
        output.append("")
        
        # Summary stats
        if self.test_results:
            output.append(self._render_summary())
            output.append("")
        
        # Test results
        output.extend(self._render_test_results())
        
        # Footer
        output.append("")
        output.append(self._render_footer())
        
        return "\n".join(output)
    
    def _render_suite_tabs(self) -> str:
        """Render test suite tabs"""
        tabs = []
        for suite in self.test_suites.keys():
            if suite == self.current_test_suite:
                tabs.append(f"[{suite.upper()}]")
            else:
                tabs.append(f" {suite} ")
        
        return "  |  ".join(tabs)
    
    def _render_summary(self) -> str:
        """Render test summary"""
        total = len(self.test_results)
        passed = len([r for r in self.test_results if r.status == 'PASS'])
        failed = len([r for r in self.test_results if r.status == 'FAIL'])
        errors = len([r for r in self.test_results if r.status == 'ERROR'])
        skipped = len([r for r in self.test_results if r.status == 'SKIP'])
        
        total_duration = sum(r.duration for r in self.test_results)
        
        return (
            f"📊 Results: {passed} passed, {failed} failed, "
            f"{errors} errors, {skipped} skipped | "
            f"Total: {total} tests in {total_duration:.2f}s"
        )
    
    def _render_test_results(self) -> List[str]:
        """Render test results"""
        output = []
        
        if not self.test_results:
            output.append("  No tests run yet. Press [R] to run tests.")
            return output
        
        # Filter if showing only failed
        results = self.test_results
        if self.show_only_failed:
            results = [r for r in results if r.status in ['FAIL', 'ERROR']]
        
        if not results:
            output.append("  No failed tests!")
            return output
        
        # Render each result
        for i, result in enumerate(results):
            prefix = "→ " if i == self.selected_index else "  "
            output.append(prefix + result.format())
            
            # Show error details for selected failed test
            if i == self.selected_index and result.error:
                error_lines = result.error.split('\n')[:3]  # First 3 lines
                for line in error_lines:
                    output.append(f"     {line}")
        
        return output
    
    def _render_footer(self) -> str:
        """Render footer with controls"""
        if self.running:
            return "⏳ Test suite running... Please wait."
        
        controls = [
            "[R]un Tests",
            "[F]ailed Only" if not self.show_only_failed else "[A]ll Tests",
            "[E]xport Results",
            "↑↓ Navigate",
            "[ESC] Close"
        ]
        
        return "  ".join(controls)
    
    def switch_suite(self, suite: str):
        """Switch to a different test suite"""
        if suite in self.test_suites:
            self.current_test_suite = suite
            self.test_results = []
            self.selected_index = 0
    
    def run_tests(self) -> Dict[str, Any]:
        """Run the current test suite"""
        if self.running:
            return {'success': False, 'error': 'Tests already running'}
        
        self.running = True
        self.test_results = []
        
        try:
            if self.current_test_suite == 'shakedown':
                result = self._run_shakedown()
            elif self.current_test_suite == 'pytest':
                result = self._run_pytest()
            else:
                result = {'success': False, 'error': 'Suite not implemented'}
        finally:
            self.running = False
        
        return result
    
    def _run_shakedown(self) -> Dict[str, Any]:
        """Run SHAKEDOWN test suite"""
        shakedown_path = self.project_root / self.test_suites['shakedown']
        
        if not shakedown_path.exists():
            return {'success': False, 'error': f'SHAKEDOWN not found: {shakedown_path}'}
        
        try:
            # Run SHAKEDOWN via start_udos.sh
            result = subprocess.run(
                ['./start_udos.sh', str(shakedown_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse output for test results
            output_lines = result.stdout.splitlines()
            
            # Look for test results (simple pattern matching)
            for line in output_lines:
                if '✓' in line or 'PASS' in line.upper():
                    # Extract test name
                    test_name = line.strip('✓ ').strip()
                    self.test_results.append(TestResult(test_name, 'PASS'))
                elif '✗' in line or 'FAIL' in line.upper():
                    test_name = line.strip('✗ ').strip()
                    self.test_results.append(TestResult(test_name, 'FAIL'))
            
            # If no results parsed, add summary
            if not self.test_results:
                self.test_results.append(
                    TestResult(
                        'SHAKEDOWN Complete',
                        'PASS' if result.returncode == 0 else 'FAIL',
                        error=result.stderr if result.returncode != 0 else ''
                    )
                )
            
            return {
                'success': result.returncode == 0,
                'tests_run': len(self.test_results),
                'exit_code': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Test suite timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _run_pytest(self) -> Dict[str, Any]:
        """Run pytest test suite"""
        try:
            # Run pytest with JSON output
            result = subprocess.run(
                ['pytest', str(self.tests_dir), '--tb=short', '-v'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Parse pytest output
            output_lines = result.stdout.splitlines()
            
            for line in output_lines:
                if '::' in line:  # Test case line
                    if 'PASSED' in line:
                        test_name = line.split('::')[1].split(' ')[0]
                        self.test_results.append(TestResult(test_name, 'PASS'))
                    elif 'FAILED' in line:
                        test_name = line.split('::')[1].split(' ')[0]
                        self.test_results.append(TestResult(test_name, 'FAIL'))
                    elif 'SKIPPED' in line:
                        test_name = line.split('::')[1].split(' ')[0]
                        self.test_results.append(TestResult(test_name, 'SKIP'))
                    elif 'ERROR' in line:
                        test_name = line.split('::')[1].split(' ')[0]
                        self.test_results.append(TestResult(test_name, 'ERROR'))
            
            return {
                'success': result.returncode == 0,
                'tests_run': len(self.test_results),
                'exit_code': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Test suite timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def toggle_failed_only(self):
        """Toggle showing only failed tests"""
        self.show_only_failed = not self.show_only_failed
        self.selected_index = 0
    
    def move_selection(self, delta: int):
        """Move selection up/down"""
        results = self.test_results
        if self.show_only_failed:
            results = [r for r in results if r.status in ['FAIL', 'ERROR']]
        
        if not results:
            return
        
        self.selected_index = (self.selected_index + delta) % len(results)
    
    def export_results(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """Export test results to file"""
        if not self.test_results:
            return {'success': False, 'error': 'No test results to export'}
        
        if output_path is None:
            from core.utils.paths import PATHS
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = PATHS.MEMORY_DOCS / f"test_results_{timestamp}.txt"
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(f"# Test Results Export\n")
                f.write(f"# Suite: {self.current_test_suite}\n")
                f.write(f"# Exported: {datetime.now().isoformat()}\n\n")
                
                # Summary
                passed = len([r for r in self.test_results if r.status == 'PASS'])
                failed = len([r for r in self.test_results if r.status == 'FAIL'])
                errors = len([r for r in self.test_results if r.status == 'ERROR'])
                
                f.write(f"Summary: {passed} passed, {failed} failed, {errors} errors\n\n")
                
                # Results
                for result in self.test_results:
                    f.write(f"{result.status}: {result.name}\n")
                    if result.error:
                        f.write(f"  Error: {result.error}\n")
            
            return {
                'success': True,
                'path': str(output_path),
                'tests': len(self.test_results)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get testing interface summary"""
        return {
            'suite': self.current_test_suite,
            'total_tests': len(self.test_results),
            'running': self.running,
            'show_only_failed': self.show_only_failed
        }


# Global instance
_testing_interface: Optional[TestingInterface] = None


def get_testing_interface() -> TestingInterface:
    """Get global TestingInterface instance"""
    global _testing_interface
    if _testing_interface is None:
        _testing_interface = TestingInterface()
    return _testing_interface
