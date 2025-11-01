"""
uDOS v1.0.0 - File Command Handler

Handles all file-related commands:
- NEW: Create new file with template
- DELETE/DEL: Delete file with confirmation
- COPY/DUPLICATE: Copy file within or between workspaces
- MOVE: Move file between workspaces
- RENAME: Rename file in current workspace
- SHOW: Display file in browser or terminal
- EDIT: Edit file with nano/micro/typo
- RUN: Execute script file

Version: 1.0.0
"""

import os
from pathlib import Path
from .base_handler import BaseCommandHandler


class FileCommandHandler(BaseCommandHandler):
    """Handles file management and editing commands."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._workspace_manager = None
        self._editor_manager = None

    @property
    def workspace_manager(self):
        """Lazy load workspace manager."""
        if self._workspace_manager is None:
            from core.uDOS_files import WorkspaceManager
            self._workspace_manager = WorkspaceManager()
        return self._workspace_manager

    @property
    def editor_manager(self):
        """Lazy load editor manager."""
        if self._editor_manager is None:
            from core.uDOS_editor import EditorManager
            self._editor_manager = EditorManager()
        return self._editor_manager

    def handle(self, command, params, grid, parser=None):
        """
        Route file commands to appropriate handlers.

        Args:
            command: Command name
            params: Command parameters
            grid: Grid instance
            parser: Parser instance (optional)

        Returns:
            Command result message
        """
        if command == "NEW":
            return self._handle_new(params)
        elif command in ["DELETE", "DEL"]:
            return self._handle_delete(params)
        elif command in ["COPY", "DUPLICATE"]:
            return self._handle_copy(params)
        elif command == "MOVE":
            return self._handle_move(params)
        elif command == "RENAME":
            return self._handle_rename(params)
        elif command == "SHOW":
            return self._handle_show(params)
        elif command == "EDIT":
            return self._handle_edit(params)
        elif command == "RUN":
            return self._handle_run(params, parser)
        else:
            return self.get_message("ERROR_UNKNOWN_FILE_COMMAND", command=command)

    def _handle_new(self, params):
        """Create new file with template selection."""
        from core.uDOS_interactive import InteractivePrompt
        prompt = InteractivePrompt()

        filename = params[0] if params else ''

        # Ask for filename if not provided
        if not filename:
            filename = prompt.ask_text(
                "📄 File name",
                default="new_file.txt"
            )
            if not filename:
                return "❌ File creation cancelled"

        # Show workspaces
        workspaces = self.workspace_manager.list_workspaces()
        ws_choices = [f"{name} - {ws['description']}"
                     for name, ws in workspaces.items()]

        ws_choice = prompt.ask_choice(
            "📁 Workspace",
            choices=ws_choices,
            default=ws_choices[0]
        )

        if not ws_choice:
            return "❌ File creation cancelled"

        workspace = ws_choice.split()[0]  # Extract name

        # Template selection
        templates = self.workspace_manager.TEMPLATES
        template_choices = [f"{key} - {tpl['name']}"
                           for key, tpl in templates.items()]

        template_choice = prompt.ask_choice(
            "📝 Template",
            choices=template_choices,
            default=template_choices[0]
        )

        if not template_choice:
            return "❌ File creation cancelled"

        template = template_choice.split()[0]  # Extract key

        try:
            file_path = self.workspace_manager.create_file(
                workspace, filename, template
            )
            return (f"✅ Created: {file_path}\n\n"
                   f"💡 Use: EDIT {filename} to start editing")
        except FileExistsError as e:
            return f"❌ {str(e)}"
        except Exception as e:
            return f"❌ Error creating file: {str(e)}"

    def _handle_delete(self, params):
        """Delete file with confirmation."""
        from core.uDOS_interactive import InteractivePrompt
        prompt = InteractivePrompt()

        filename = params[0] if params else ''

        # Show files in current workspace
        files = self.workspace_manager.list_files()

        if not files:
            return "❌ No files in current workspace"

        if not filename:
            # Interactive file selection
            filename = prompt.ask_choice(
                "🗑️  Delete file",
                choices=files,
                default=files[0]
            )
            if not filename:
                return "❌ Delete cancelled"

        # Confirm deletion
        confirm = prompt.ask_yes_no(
            f"⚠️  Delete {filename}? This cannot be undone!",
            default=False
        )

        if not confirm:
            return "❌ Delete cancelled"

        try:
            self.workspace_manager.delete_file(filename)
            return f"✅ Deleted: {filename}"
        except FileNotFoundError as e:
            return f"❌ {str(e)}"
        except Exception as e:
            return f"❌ Error deleting file: {str(e)}"

    def _handle_copy(self, params):
        """Copy file within or between workspaces."""
        from core.uDOS_interactive import InteractivePrompt
        prompt = InteractivePrompt()

        source = params[0] if params else ''
        destination = params[1] if len(params) > 1 else ''

        # Select source file
        files = self.workspace_manager.list_files()
        if not source:
            source = prompt.ask_choice(
                "📄 Source file",
                choices=files,
                default=files[0] if files else None
            )
            if not source:
                return "❌ Copy cancelled"

        # Ask for destination
        if not destination:
            destination = prompt.ask_text(
                "📄 Destination name",
                default=f"copy_of_{source}"
            )
            if not destination:
                return "❌ Copy cancelled"

        # Ask if copying to different workspace
        workspaces = self.workspace_manager.list_workspaces()
        ws_choices = ['Same workspace'] + [name for name in workspaces.keys()]

        ws_choice = prompt.ask_choice(
            "📁 Destination workspace",
            choices=ws_choices,
            default='Same workspace'
        )

        dest_ws = None if ws_choice == 'Same workspace' else ws_choice

        try:
            new_path = self.workspace_manager.copy_file(source, destination, dest_ws)
            return f"✅ Copied to: {new_path}"
        except (FileNotFoundError, FileExistsError) as e:
            return f"❌ {str(e)}"
        except Exception as e:
            return f"❌ Error copying file: {str(e)}"

    def _handle_move(self, params):
        """Move file between workspaces."""
        from core.uDOS_interactive import InteractivePrompt
        prompt = InteractivePrompt()

        source = params[0] if params else ''
        destination = params[1] if len(params) > 1 else ''

        # Select source file
        files = self.workspace_manager.list_files()
        if not source:
            source = prompt.ask_choice(
                "📄 File to move",
                choices=files,
                default=files[0] if files else None
            )
            if not source:
                return "❌ Move cancelled"

        # Select destination workspace
        workspaces = self.workspace_manager.list_workspaces()
        ws_choices = list(workspaces.keys())

        dest_ws = prompt.ask_choice(
            "📁 Move to workspace",
            choices=ws_choices,
            default=ws_choices[0]
        )

        if not dest_ws:
            return "❌ Move cancelled"

        # Ask for new name (optional)
        if not destination:
            destination = prompt.ask_text(
                "📄 New name (optional)",
                default=source
            )
            if not destination:
                destination = source

        try:
            new_path = self.workspace_manager.move_file(source, dest_ws, destination)
            return f"✅ Moved to: {new_path}"
        except (FileNotFoundError, FileExistsError) as e:
            return f"❌ {str(e)}"
        except Exception as e:
            return f"❌ Error moving file: {str(e)}"

    def _handle_rename(self, params):
        """Rename file in current workspace."""
        from core.uDOS_interactive import InteractivePrompt
        prompt = InteractivePrompt()

        old_name = params[0] if params else ''
        new_name = params[1] if len(params) > 1 else ''

        # Select file to rename
        files = self.workspace_manager.list_files()
        if not old_name:
            old_name = prompt.ask_choice(
                "📄 File to rename",
                choices=files,
                default=files[0] if files else None
            )
            if not old_name:
                return "❌ Rename cancelled"

        # Ask for new name
        if not new_name:
            new_name = prompt.ask_text(
                "📄 New name",
                default=old_name
            )
            if not new_name or new_name == old_name:
                return "❌ Rename cancelled"

        try:
            new_path = self.workspace_manager.rename_file(old_name, new_name)
            return f"✅ Renamed to: {new_name}"
        except (FileNotFoundError, FileExistsError) as e:
            return f"❌ {str(e)}"
        except Exception as e:
            return f"❌ Error renaming file: {str(e)}"

    def _handle_show(self, params):
        """Display file in browser or terminal."""
        if not params:
            # Interactive file picker
            from core.uDOS_interactive import InteractivePrompt
            prompt = InteractivePrompt()

            files = self.workspace_manager.list_files()
            if not files:
                return "❌ No files to show"

            file_path = prompt.ask_choice(
                "📄 Show file",
                choices=files,
                default=files[0]
            )
            if not file_path:
                return "❌ Show cancelled"
        else:
            file_path = params[0]

        # Parse flags
        mode = '--cli'  # Default to terminal display
        if len(params) > 1 and params[1] in ['--web', '--browser']:
            mode = '--web'

        # Security check
        abs_path = os.path.abspath(file_path)
        allowed_dirs = [os.path.abspath('sandbox'), os.path.abspath('memory')]
        if not any(abs_path.startswith(allowed_dir) for allowed_dir in allowed_dirs):
            return f"❌ Access denied: {file_path}\n\nOnly sandbox/ and memory/ are accessible"

        if not os.path.exists(file_path):
            return f"❌ File not found: {file_path}"

        if mode == '--web':
            # Open in browser
            import webbrowser
            webbrowser.open(f"file://{abs_path}")
            return f"✅ Opened in browser: {file_path}"
        else:
            # Display in terminal
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return f"📄 {file_path}\n{'═'*60}\n\n{content}\n\n{'═'*60}"
            except Exception as e:
                return f"❌ Error reading file: {str(e)}"

    def _handle_edit(self, params):
        """Edit file with nano/micro/typo."""
        if not params:
            # Interactive file picker
            from core.uDOS_interactive import InteractivePrompt
            prompt = InteractivePrompt()

            files = self.workspace_manager.list_files()
            if not files:
                return "❌ No files to edit"

            file_path = prompt.ask_choice(
                "📝 Edit file",
                choices=files,
                default=files[0]
            )
            if not file_path:
                return "❌ Edit cancelled"
        else:
            file_path = params[0]

        mode = None
        specific_editor = None

        # Parse options
        for i, param in enumerate(params[1:], 1):
            if param in ['--cli', '--terminal']:
                mode = 'cli'
            elif param in ['--web', '--browser']:
                mode = 'web'
            elif param in ['--nano', '--micro', '--typo']:
                specific_editor = param[2:]  # Remove --

        try:
            result = self.editor_manager.edit_file(
                file_path,
                mode=mode,
                editor=specific_editor
            )
            return result
        except Exception as e:
            return f"❌ Error opening editor: {str(e)}"

    def _handle_run(self, params, parser):
        """Execute script file."""
        if not params:
            # Interactive file picker
            from core.uDOS_interactive import InteractivePrompt
            prompt = InteractivePrompt()

            # Show .uscript files
            script_files = [f for f in self.workspace_manager.list_files()
                          if f.endswith('.uscript')]

            if not script_files:
                return "❌ No .uscript files found"

            script_file = prompt.ask_choice(
                "▶️  Run script",
                choices=script_files,
                default=script_files[0]
            )
            if not script_file:
                return "❌ Run cancelled"
        else:
            script_file = params[0]

        if not os.path.exists(script_file):
            return f"❌ Script not found: {script_file}"

        # Check if it's a .uscript file (uCODE with IF/THEN logic)
        if script_file.endswith('.uscript'):
            try:
                from core.uDOS_ucode import UCodeInterpreter
                interpreter = UCodeInterpreter(command_handler=self)
                result = interpreter.execute_script(script_file)
                return f"📜 Executed: {script_file}\n\n{result}"
            except Exception as e:
                return f"❌ Script error: {str(e)}"
        else:
            # Regular shell script
            import subprocess
            try:
                result = subprocess.run(['bash', script_file],
                                      capture_output=True, text=True)
                return f"📜 Executed: {script_file}\n\n{result.stdout}\n{result.stderr}"
            except Exception as e:
                return f"❌ Execution error: {str(e)}"
