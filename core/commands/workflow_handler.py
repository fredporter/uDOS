"""
uDOS Workflow Command Handler

Provides workflow automation commands for mission execution:
- LOG: Console + file logging with levels
- LOAD_JSON/SAVE_JSON: JSON data persistence
- CHECK_ENV/ENSURE_DIR: Environment management
- RUN_PYTHON: Execute Python scripts (foreground/background)
- PROCESS_RUNNING: Check background process status
- SLEEP/TIMESTAMP: Timing and scheduling
- CHECKPOINT: Mission state persistence
- EXTRACT_METRIC/COUNT_PATTERN: Text analysis
- FIND_FILES/COUNT_LINES: File utilities
- DISPLAY/CREATE_REPORT: Formatted output

Version: 1.1.2 (Mission Control & Workflow Automation)
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import glob
import psutil
from core.output.syntax_highlighter import highlight_syntax

from core.config import Config
from core.commands.base_handler import BaseCommandHandler


class WorkflowHandler(BaseCommandHandler):
    """Handler for workflow automation commands."""

    def __init__(self, config: Config):
        """Initialize workflow handler.

        Args:
            config: uDOS configuration instance
        """
        super().__init__(config)
        self.log_dir = Path("memory/logs")
        self.log_file = self.log_dir / "workflow.log"
        self.checkpoint_dir = Path("memory/workflows/checkpoints")
        self.reports_dir = Path("memory/workflows/reports")
        self.background_processes: Dict[str, subprocess.Popen] = {}

        # Ensure directories exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def handle_command(self, command: str, args: List[str]) -> str:
        """Route workflow commands to appropriate handlers.

        Args:
            command: Command name (LOG, LOAD_JSON, etc.)
            args: Command arguments

        Returns:
            Command result as formatted string
        """
        handlers = {
            "LOG": self._handle_log,
            "LOAD_JSON": self._handle_load_json,
            "SAVE_JSON": self._handle_save_json,
            "CHECK_ENV": self._handle_check_env,
            "ENSURE_DIR": self._handle_ensure_dir,
            "RUN_PYTHON": self._handle_run_python,
            "PROCESS_RUNNING": self._handle_process_running,
            "SLEEP": self._handle_sleep,
            "TIMESTAMP": self._handle_timestamp,
            "SAVE_CHECKPOINT": self._handle_save_checkpoint,
            "LOAD_CHECKPOINT": self._handle_load_checkpoint,
            "EXTRACT_METRIC": self._handle_extract_metric,
            "COUNT_PATTERN": self._handle_count_pattern,
            "FIND_FILES": self._handle_find_files,
            "COUNT_LINES": self._handle_count_lines,
            "DISPLAY": self._handle_display,
            "CREATE_REPORT": self._handle_create_report,
            "HELP": self._handle_help,
        }

        handler = handlers.get(command.upper())
        if not handler:
            return f"❌ Unknown WORKFLOW command: {command}\n💡 Use WORKFLOW HELP for available commands"

        try:
            return handler(args)
        except Exception as e:
            error_msg = f"❌ Error in WORKFLOW {command}: {str(e)}"
            self._log_to_file("error", error_msg)
            return error_msg

    def _handle_log(self, args: List[str]) -> str:
        """Handle LOG command.

        Syntax:
            WORKFLOW LOG <message> [--level=info|warn|error|debug]

        Examples:
            WORKFLOW LOG "Starting mission"
            WORKFLOW LOG "Warning: quota low" --level=warn
        """
        if not args:
            return "❌ Usage: WORKFLOW LOG <message> [--level=info|warn|error|debug]"

        # Parse level flag
        level = "info"
        message_parts = []

        for arg in args:
            if arg.startswith("--level="):
                level = arg.split("=", 1)[1].lower()
            else:
                message_parts.append(arg)

        message = " ".join(message_parts)

        # Log to file
        self._log_to_file(level, message)

        # Format console output with emoji
        level_emoji = {
            "info": "ℹ️",
            "warn": "⚠️",
            "error": "❌",
            "debug": "🔍"
        }

        emoji = level_emoji.get(level, "📝")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"{emoji} [{level.upper()}] {message}\n📄 Logged to: {self.log_file}"

    def _log_to_file(self, level: str, message: str):
        """Write log entry to file.

        Args:
            level: Log level (info, warn, error, debug)
            message: Log message
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"

        with open(self.log_file, "a") as f:
            f.write(log_entry)

    def _handle_load_json(self, args: List[str]) -> str:
        """Handle LOAD_JSON command.

        Syntax:
            WORKFLOW LOAD_JSON <filepath> [--var=name]

        Examples:
            WORKFLOW LOAD_JSON memory/bank/data/config.json
            WORKFLOW LOAD_JSON data.json --var=mydata
        """
        if not args:
            return "❌ Usage: WORKFLOW LOAD_JSON <filepath> [--var=name]"

        filepath = args[0]
        var_name = None

        for arg in args[1:]:
            if arg.startswith("--var="):
                var_name = arg.split("=", 1)[1]

        # Use base handler method for safe JSON loading
        success, data, error = self.load_json_file(filepath)
        if not success:
            return self.format_error(error)

        # Pretty print preview
        preview = json.dumps(data, indent=2)
        if len(preview) > 500:
            preview = preview[:500] + "\n... (truncated)"

        result = f"✅ Loaded JSON from: {filepath}\n\n{preview}"

        if var_name:
            # In a real implementation, store in variable context
            result += f"\n\n💾 Stored as variable: {var_name}"

        return result

    def _handle_save_json(self, args: List[str]) -> str:
        """Handle SAVE_JSON command.

        Syntax:
            WORKFLOW SAVE_JSON <filepath> <data> [--pretty]

        Examples:
            WORKFLOW SAVE_JSON output.json {"key": "value"}
            WORKFLOW SAVE_JSON data.json $mydata --pretty
        """
        if len(args) < 2:
            return "❌ Usage: WORKFLOW SAVE_JSON <filepath> <data> [--pretty]"

        filepath = args[0]
        data_str = args[1]
        pretty = "--pretty" in args

        try:
            # Parse data (could be JSON string or variable reference)
            if data_str.startswith("$"):
                # Variable reference - in real implementation, lookup from context
                data = {"note": "Variable references not yet implemented"}
            else:
                data = json.loads(data_str)

            # Use base handler method for atomic JSON save
            indent = 2 if pretty else None
            success, error = self.save_json_file(filepath, data, indent=indent if indent else 0)
            if not success:
                return self.format_error(error)

            # Get file size
            from pathlib import Path
            size = Path(filepath).stat().st_size

            return f"✅ Saved JSON to: {filepath}\n📊 Size: {size} bytes"

        except json.JSONDecodeError as e:
            return self.format_error(f"Invalid JSON data: {str(e)}")
        except Exception as e:
            return self.format_error(f"Error saving file: {str(e)}")

    def _handle_check_env(self, args: List[str]) -> str:
        """Handle CHECK_ENV command.

        Syntax:
            WORKFLOW CHECK_ENV <var_name>

        Examples:
            WORKFLOW CHECK_ENV GEMINI_API_KEY
            WORKFLOW CHECK_ENV PATH
        """
        if not args:
            return "❌ Usage: WORKFLOW CHECK_ENV <var_name>"

        var_name = args[0]
        value = os.environ.get(var_name)

        if value:
            # Mask sensitive values
            if any(x in var_name.upper() for x in ["KEY", "SECRET", "TOKEN", "PASSWORD"]):
                masked = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
                return f"✅ {var_name} = {masked} (masked)"
            else:
                return f"✅ {var_name} = {value}"
        else:
            return f"❌ Environment variable not set: {var_name}"

    def _handle_ensure_dir(self, args: List[str]) -> str:
        """Handle ENSURE_DIR command.

        Syntax:
            WORKFLOW ENSURE_DIR <path>

        Examples:
            WORKFLOW ENSURE_DIR memory/workflows/missions/my-mission
        """
        if not args:
            return "❌ Usage: WORKFLOW ENSURE_DIR <path>"

        dir_path = Path(args[0])

        if dir_path.exists():
            if dir_path.is_dir():
                return f"✅ Directory exists: {dir_path}"
            else:
                return f"❌ Path exists but is not a directory: {dir_path}"

        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return f"✅ Created directory: {dir_path}"
        except Exception as e:
            return f"❌ Error creating directory: {str(e)}"

    def _handle_run_python(self, args: List[str]) -> str:
        """Handle RUN_PYTHON command.

        Syntax:
            WORKFLOW RUN_PYTHON <script> [args...] [--background] [--id=name]

        Examples:
            WORKFLOW RUN_PYTHON scripts/process.py
            WORKFLOW RUN_PYTHON scripts/server.py --background --id=server
        """
        if not args:
            return "❌ Usage: WORKFLOW RUN_PYTHON <script> [args...] [--background] [--id=name]"

        background = "--background" in args
        process_id = None
        script_args = []
        script = None

        for arg in args:
            if arg.startswith("--id="):
                process_id = arg.split("=", 1)[1]
            elif arg == "--background":
                continue
            elif script is None:
                script = arg
            else:
                script_args.append(arg)

        if not script:
            return "❌ No script specified"

        # Validate script path using base handler method
        is_valid, script_path, error = self.validate_file_path(script, must_exist=True)
        if not is_valid:
            return self.format_error(f"Script not found: {script}")

        try:
            # Build command (use string path for subprocess)
            cmd = [sys.executable, str(script_path)] + script_args

            if background:
                # Start background process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if process_id is None:
                    process_id = f"python_{process.pid}"

                self.background_processes[process_id] = process

                return f"✅ Started background process: {process_id}\n🆔 PID: {process.pid}\n💡 Use: WORKFLOW PROCESS_RUNNING {process_id}"
            else:
                # Run foreground (blocking)
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                output = f"✅ Script completed: {script}\n"
                output += f"📤 Exit code: {result.returncode}\n"

                if result.stdout:
                    output += f"\n📄 STDOUT:\n{result.stdout}"
                if result.stderr:
                    output += f"\n⚠️ STDERR:\n{result.stderr}"

                return output

        except subprocess.TimeoutExpired:
            return f"❌ Script timeout (300s): {script}"
        except Exception as e:
            return f"❌ Error running script: {str(e)}"

    def _handle_process_running(self, args: List[str]) -> str:
        """Handle PROCESS_RUNNING command.

        Syntax:
            WORKFLOW PROCESS_RUNNING <process_id>

        Examples:
            WORKFLOW PROCESS_RUNNING server
        """
        if not args:
            return "❌ Usage: WORKFLOW PROCESS_RUNNING <process_id>"

        process_id = args[0]

        if process_id not in self.background_processes:
            return f"❌ Unknown process: {process_id}\n💡 No background process with this ID"

        process = self.background_processes[process_id]

        if process.poll() is None:
            # Still running
            try:
                proc = psutil.Process(process.pid)
                cpu = proc.cpu_percent(interval=0.1)
                mem = proc.memory_info().rss / 1024 / 1024  # MB

                return f"✅ Process running: {process_id}\n🆔 PID: {process.pid}\n💻 CPU: {cpu:.1f}%\n🧠 Memory: {mem:.1f} MB"
            except:
                return f"✅ Process running: {process_id}\n🆔 PID: {process.pid}"
        else:
            # Process finished
            exit_code = process.returncode
            stdout, stderr = process.communicate()

            result = f"✅ Process completed: {process_id}\n📤 Exit code: {exit_code}\n"

            if stdout:
                result += f"\n📄 STDOUT:\n{stdout}"
            if stderr:
                result += f"\n⚠️ STDERR:\n{stderr}"

            # Clean up
            del self.background_processes[process_id]

            return result

    def _handle_sleep(self, args: List[str]) -> str:
        """Handle SLEEP command.

        Syntax:
            WORKFLOW SLEEP <seconds>

        Examples:
            WORKFLOW SLEEP 5
            WORKFLOW SLEEP 0.5
        """
        if not args:
            return "❌ Usage: WORKFLOW SLEEP <seconds>"

        try:
            seconds = float(args[0])
            if seconds < 0:
                return "❌ Sleep duration must be positive"

            time.sleep(seconds)
            return f"✅ Slept for {seconds} seconds"

        except ValueError:
            return f"❌ Invalid duration: {args[0]}"

    def _handle_timestamp(self, args: List[str]) -> str:
        """Handle TIMESTAMP command.

        Syntax:
            WORKFLOW TIMESTAMP [--format=iso|unix|human]

        Examples:
            WORKFLOW TIMESTAMP
            WORKFLOW TIMESTAMP --format=unix
        """
        format_type = "iso"

        for arg in args:
            if arg.startswith("--format="):
                format_type = arg.split("=", 1)[1].lower()

        now = datetime.now()

        if format_type == "unix":
            return str(int(now.timestamp()))
        elif format_type == "human":
            return now.strftime("%A, %B %d, %Y at %I:%M:%S %p")
        else:  # iso
            return now.isoformat()

    def _handle_save_checkpoint(self, args: List[str]) -> str:
        """Handle SAVE_CHECKPOINT command.

        Syntax:
            WORKFLOW SAVE_CHECKPOINT <name> <data>

        Examples:
            WORKFLOW SAVE_CHECKPOINT mission-progress {"step": 5}
        """
        if len(args) < 2:
            return "❌ Usage: WORKFLOW SAVE_CHECKPOINT <name> <data>"

        name = args[0]
        data_str = " ".join(args[1:])

        try:
            data = json.loads(data_str) if data_str.startswith("{") else {"value": data_str}

            checkpoint_file = self.checkpoint_dir / f"{name}.json"

            checkpoint = {
                "name": name,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }

            success, error = self.save_json_file(checkpoint_file, checkpoint)
            if not success:
                return f"❌ Error saving checkpoint: {error}"

            return f"✅ Checkpoint saved: {name}\n📁 File: {checkpoint_file}"

        except json.JSONDecodeError as e:
            return f"❌ Invalid JSON data: {str(e)}"

    def _handle_load_checkpoint(self, args: List[str]) -> str:
        """Handle LOAD_CHECKPOINT command.

        Syntax:
            WORKFLOW LOAD_CHECKPOINT <name>

        Examples:
            WORKFLOW LOAD_CHECKPOINT mission-progress
        """
        if not args:
            return "❌ Usage: WORKFLOW LOAD_CHECKPOINT <name>"

        name = args[0]
        checkpoint_file = self.checkpoint_dir / f"{name}.json"

        success, checkpoint, error = self.load_json_file(checkpoint_file)
        if not success:
            return f"❌ Error loading checkpoint: {error}"

        timestamp = checkpoint.get("timestamp", "unknown")
        data = checkpoint.get("data", {})

        preview = json.dumps(data, indent=2)
        if len(preview) > 500:
            preview = preview[:500] + "\n... (truncated)"

        return f"✅ Loaded checkpoint: {name}\n🕐 Saved: {timestamp}\n\n{preview}"

    def _handle_extract_metric(self, args: List[str]) -> str:
        """Handle EXTRACT_METRIC command.

        Syntax:
            WORKFLOW EXTRACT_METRIC <pattern> <text> [--group=N]

        Examples:
            WORKFLOW EXTRACT_METRIC r"completed: (\\d+)" "Status: completed: 25 of 100"
        """
        if len(args) < 2:
            return "❌ Usage: WORKFLOW EXTRACT_METRIC <pattern> <text> [--group=N]"

        pattern = args[0]
        text = " ".join(args[1:])
        group = 1

        # Extract group parameter
        text_parts = []
        for arg in args[1:]:
            if arg.startswith("--group="):
                group = int(arg.split("=", 1)[1])
            else:
                text_parts.append(arg)
        text = " ".join(text_parts)

        try:
            match = re.search(pattern, text)
            if match:
                value = match.group(group)
                return f"✅ Extracted: {value}"
            else:
                return f"❌ No match found for pattern: {pattern}"
        except Exception as e:
            return f"❌ Regex error: {str(e)}"

    def _handle_count_pattern(self, args: List[str]) -> str:
        """Handle COUNT_PATTERN command.

        Syntax:
            WORKFLOW COUNT_PATTERN <pattern> <text|filepath>

        Examples:
            WORKFLOW COUNT_PATTERN "TODO" myfile.py
        """
        if len(args) < 2:
            return "❌ Usage: WORKFLOW COUNT_PATTERN <pattern> <text|filepath>"

        pattern = args[0]
        target = " ".join(args[1:])

        # Check if target is a file
        if os.path.exists(target):
            try:
                with open(target, "r") as f:
                    text = f.read()
            except Exception as e:
                return f"❌ Error reading file: {str(e)}"
        else:
            text = target

        try:
            matches = re.findall(pattern, text)
            count = len(matches)
            return f"✅ Found {count} matches for: {pattern}"
        except Exception as e:
            return f"❌ Regex error: {str(e)}"

    def _handle_find_files(self, args: List[str]) -> str:
        """Handle FIND_FILES command.

        Syntax:
            WORKFLOW FIND_FILES <pattern> [--path=dir]

        Examples:
            WORKFLOW FIND_FILES "*.py"
            WORKFLOW FIND_FILES "test_*.py" --path=memory/ucode/tests
        """
        if not args:
            return "❌ Usage: WORKFLOW FIND_FILES <pattern> [--path=dir]"

        pattern = args[0]
        search_path = "."

        for arg in args[1:]:
            if arg.startswith("--path="):
                search_path = arg.split("=", 1)[1]

        try:
            full_pattern = os.path.join(search_path, "**", pattern)
            files = glob.glob(full_pattern, recursive=True)

            if not files:
                return f"❌ No files found matching: {pattern}"

            result = f"✅ Found {len(files)} files:\n\n"
            for f in sorted(files)[:50]:  # Limit to 50
                result += f"  📄 {f}\n"

            if len(files) > 50:
                result += f"\n... and {len(files) - 50} more"

            return result

        except Exception as e:
            return f"❌ Error finding files: {str(e)}"

    def _handle_count_lines(self, args: List[str]) -> str:
        """Handle COUNT_LINES command.

        Syntax:
            WORKFLOW COUNT_LINES <filepath> [--non-empty]

        Examples:
            WORKFLOW COUNT_LINES myfile.py
            WORKFLOW COUNT_LINES myfile.py --non-empty
        """
        if not args:
            return "❌ Usage: WORKFLOW COUNT_LINES <filepath> [--non-empty]"

        filepath = args[0]
        non_empty_only = "--non-empty" in args

        if not os.path.exists(filepath):
            return f"❌ File not found: {filepath}"

        try:
            with open(filepath, "r") as f:
                lines = f.readlines()

            total = len(lines)

            if non_empty_only:
                non_empty = sum(1 for line in lines if line.strip())
                return f"✅ Lines in {filepath}:\n  📊 Total: {total}\n  📝 Non-empty: {non_empty}"
            else:
                return f"✅ Lines in {filepath}: {total}"

        except Exception as e:
            return f"❌ Error reading file: {str(e)}"

    def _handle_display(self, args: List[str]) -> str:
        """Handle DISPLAY command.

        Syntax:
            WORKFLOW DISPLAY <text> [--style=box|banner|plain]

        Examples:
            WORKFLOW DISPLAY "Mission Complete!" --style=banner
        """
        if not args:
            return "❌ Usage: WORKFLOW DISPLAY <text> [--style=box|banner|plain]"

        style = "plain"
        text_parts = []

        for arg in args:
            if arg.startswith("--style="):
                style = arg.split("=", 1)[1].lower()
            else:
                text_parts.append(arg)

        text = " ".join(text_parts)

        if style == "box":
            border = "═" * (len(text) + 4)
            return f"╔{border}╗\n║  {text}  ║\n╚{border}╝"
        elif style == "banner":
            return f"\n{'=' * 60}\n{text.center(60)}\n{'=' * 60}\n"
        else:
            return text

    def _handle_create_report(self, args: List[str]) -> str:
        """Handle CREATE_REPORT command.

        Syntax:
            WORKFLOW CREATE_REPORT <template> <output> [--vars=json]

        Examples:
            WORKFLOW CREATE_REPORT mission-summary.txt report.txt
        """
        if len(args) < 2:
            return "❌ Usage: WORKFLOW CREATE_REPORT <template> <output> [--vars=json]"

        template_file = args[0]
        output_file = args[1]
        variables = {}

        for arg in args[2:]:
            if arg.startswith("--vars="):
                try:
                    variables = json.loads(arg.split("=", 1)[1])
                except:
                    pass

        if not os.path.exists(template_file):
            return f"❌ Template not found: {template_file}"

        try:
            with open(template_file, "r") as f:
                template = f.read()

            # Simple template substitution
            report = self._apply_template(template, variables)

            # Save report
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                f.write(report)

            return f"✅ Report created: {output_file}\n📄 From template: {template_file}"

        except Exception as e:
            return f"❌ Error creating report: {str(e)}"

    def _apply_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Apply variable substitution to template.

        Supports: {{var}}, ${var}

        Args:
            template: Template string
            variables: Variable dictionary

        Returns:
            Processed template
        """
        result = template

        # Replace {{var}} and ${var} patterns
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
            result = result.replace(f"${{{key}}}", str(value))

        # Add timestamp
        result = result.replace("{{timestamp}}", datetime.now().isoformat())
        result = result.replace("${timestamp}", datetime.now().isoformat())

        return result

    def _handle_help(self, args: List[str]) -> str:
        """Show WORKFLOW command help."""
        help_text = """
╔═══════════════════════════════════════════════════════════════╗
║               WORKFLOW AUTOMATION COMMANDS                    ║
╚═══════════════════════════════════════════════════════════════╝

📝 LOGGING & OUTPUT
  WORKFLOW LOG <message> [--level=info|warn|error|debug]
    Log to console and file with severity levels

  WORKFLOW DISPLAY <text> [--style=box|banner|plain]
    Formatted text display

💾 DATA PERSISTENCE
  WORKFLOW LOAD_JSON <filepath> [--var=name]
    Load JSON file into memory

  WORKFLOW SAVE_JSON <filepath> <data> [--pretty]
    Save data to JSON file

  WORKFLOW SAVE_CHECKPOINT <name> <data>
    Save mission checkpoint

  WORKFLOW LOAD_CHECKPOINT <name>
    Load mission checkpoint

🔧 ENVIRONMENT
  WORKFLOW CHECK_ENV <var_name>
    Check environment variable (masks secrets)

  WORKFLOW ENSURE_DIR <path>
    Create directory if not exists

🐍 PYTHON EXECUTION
  WORKFLOW RUN_PYTHON <script> [args...] [--background] [--id=name]
    Execute Python script (foreground or background)

  WORKFLOW PROCESS_RUNNING <process_id>
    Check background process status

⏱️ TIMING
  WORKFLOW SLEEP <seconds>
    Pause execution

  WORKFLOW TIMESTAMP [--format=iso|unix|human]
    Get current timestamp

📊 TEXT ANALYSIS
  WORKFLOW EXTRACT_METRIC <pattern> <text> [--group=N]
    Extract value using regex

  WORKFLOW COUNT_PATTERN <pattern> <text|filepath>
    Count pattern matches

📁 FILE UTILITIES
  WORKFLOW FIND_FILES <pattern> [--path=dir]
    Find files by glob pattern

  WORKFLOW COUNT_LINES <filepath> [--non-empty]
    Count lines in file

📄 REPORTING
  WORKFLOW CREATE_REPORT <template> <output> [--vars=json]
    Generate report from template

═══════════════════════════════════════════════════════════════

Examples:
"""
        # Add highlighted examples
        help_text += f"  {highlight_syntax('WORKFLOW(LOG|\"Mission started\"|--level=info)')}\n"
        help_text += f"  {highlight_syntax('WORKFLOW(LOAD_JSON|data.json|--var=config)')}\n"
        help_text += f"  {highlight_syntax('WORKFLOW(RUN_PYTHON|scripts/process.py|--background|--id=worker)')}\n"
        help_text += f"  {highlight_syntax('WORKFLOW(TIMESTAMP|--format=human)')}\n"
        help_text += f"  {highlight_syntax('WORKFLOW(EXTRACT_METRIC|r\"(\\\\d+) complete\"|\"Tasks: 25 complete\")')}\n"
        help_text += "\n💡 All WORKFLOW commands log to: memory/logs/workflow.log"

        return help_text.strip()


def handle_workflow_command(command: str, args: List[str], config: Config) -> str:
    """Main entry point for WORKFLOW commands.

    Args:
        command: Command name
        args: Command arguments
        config: uDOS configuration

    Returns:
        Command result
    """
    handler = WorkflowHandler(config)
    return handler.handle_command(command, args)
