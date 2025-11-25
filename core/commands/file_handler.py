"""
uDOS v1.0.29 - File Command Handler (Smart Mode)

Handles all file-related commands with smart input:
- FILE: Interactive operation menu (v1.0.29)
- NEW: Create new file with template
- DELETE/DEL: Delete file with confirmation
- COPY/DUPLICATE: Copy file within or between workspaces
- MOVE: Move file between workspaces
- RENAME: Rename file in current workspace
- SHOW: Display file in browser or terminal
- EDIT: Edit file with nano/micro/typo
- RUN: Execute script file

Smart Mode (v1.0.29):
- Zero arguments triggers interactive operation picker
- File picker integration with InputManager
- Smart context detection

Version: 1.0.29
"""

import os
from pathlib import Path
from datetime import datetime
from .base_handler import BaseCommandHandler


class FileCommandHandler(BaseCommandHandler):
    """Handles file management and editing commands."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._workspace_manager = None
        self._editor_manager = None
        self._file_picker = None

    @property
    def workspace_manager(self):
        """Lazy load workspace manager."""
        if self._workspace_manager is None:
            from core.utils.files import WorkspaceManager
            self._workspace_manager = WorkspaceManager()
        return self._workspace_manager

    @property
    def editor_manager(self):
        """Lazy load editor manager."""
        if self._editor_manager is None:
            from core.services.editor_manager import EditorManager
            self._editor_manager = EditorManager()
        return self._editor_manager

    @property
    def file_picker(self):
        """Lazy load file picker service."""
        if self._file_picker is None:
            from core.ui.file_picker import FilePicker
            self._file_picker = FilePicker(self.workspace_manager)
        return self._file_picker

    def handle(self, command, params, grid, parser=None):
        """
        Route file commands to appropriate handlers (v1.0.29 Smart Mode).

        Args:
            command: Command name (FILE, NEW, DELETE, etc.)
            params: Command parameters
            grid: Grid instance
            parser: Parser instance (optional)

        Returns:
            Command result message
        """
        # SMART MODE: FILE with no params → Interactive menu
        if command == "FILE" and not params:
            return self._file_interactive_menu()

        # Handle MENU command (from [FILE|MENU] uCODE)
        if command == "MENU":
            return self._file_interactive_menu()

        # EXPLICIT MODE: Traditional command routing
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
        elif command == "PICK":
            return self._handle_pick(params)
        elif command == "RECENT":
            return self._handle_recent(params)
        elif command == "BATCH":
            return self._handle_batch(params)
        elif command == "BOOKMARKS":
            return self._handle_bookmarks(params)
        elif command == "PREVIEW":
            return self._handle_preview(params)
        elif command == "INFO":
            return self._handle_info(params)
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
        """Display file in browser or terminal (v1.0.30 with micro editor)."""
        if not params:
            # v1.0.30: Use knowledge file picker for .md and .uscript files
            from core.ui.knowledge_file_picker import KnowledgeFilePicker
            picker = KnowledgeFilePicker()

            file_path = picker.pick_file(
                workspace='both',
                prompt="📄 Select file to view",
                file_types=['.md', '.uscript', '.txt', '.json']
            )

            if not file_path:
                return "❌ View cancelled"
        else:
            file_path = params[0]

        # Parse flags
        mode = '--cli'  # Default to terminal display
        if len(params) > 1 and params[1] in ['--web', '--browser']:
            mode = '--web'

        # Security check
        abs_path = os.path.abspath(file_path)
        allowed_dirs = [
            os.path.abspath('sandbox'),
            os.path.abspath('memory'),
            os.path.abspath('knowledge')  # v1.0.30: Allow knowledge access
        ]
        if not any(abs_path.startswith(allowed_dir) for allowed_dir in allowed_dirs):
            return f"❌ Access denied: {file_path}\n\nOnly sandbox/, memory/, and knowledge/ are accessible"

        if not os.path.exists(file_path):
            return f"❌ File not found: {file_path}"

        if mode == '--web':
            # Open in browser
            import webbrowser
            webbrowser.open(f"file://{abs_path}")
            return f"✅ Opened in browser: {file_path}"
        else:
            # Use nano/less for viewing (better than custom editor)
            try:
                # Try less first (better for viewing)
                result = subprocess.run(['less', file_path], check=False)
                return f"✅ Viewed: {file_path}"
            except Exception as e:
                # Fallback to simple display
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    return f"📄 {file_path}\n{'═'*60}\n\n{content}\n\n{'═'*60}"
                except Exception as e2:
                    return f"❌ Error reading file: {str(e2)}"

    def _handle_edit(self, params):
        """Edit file with nano/micro/vim editor."""
        if not params:
            # Use knowledge file picker for .md and .uscript files
            from core.ui.knowledge_file_picker import KnowledgeFilePicker
            picker = KnowledgeFilePicker()

            file_path = picker.pick_file(
                workspace='both',
                prompt="📝 Select file to edit",
                file_types=['.md', '.uscript', '.txt', '.json']
            )

            if not file_path:
                return "❌ Edit cancelled"
        else:
            file_path = params[0]

        # Use nano/micro/vim via EditorManager
        mode = 'CLI'  # Force CLI mode
        specific_editor = None

        # Parse options
        for i, param in enumerate(params[1:], 1):
            if param in ['--web', '--browser']:
                mode = 'WEB'
            elif param in ['--nano', '--vim', '--micro']:
                specific_editor = param[2:]  # Remove --

        try:
            result = self.editor_manager.open_file(
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
                # Pass the main CommandHandler for executing nested commands
                interpreter = UCodeInterpreter(
                    command_handler=self.main_handler if hasattr(self, 'main_handler') else None,
                    parser=parser,
                    grid=None  # Grid will be passed when UCodeInterpreter calls handle_command
                )
                result = interpreter.execute_script(script_file)
                return result  # UCodeInterpreter already formats output
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                return f"❌ Script error: {str(e)}\n\n{error_detail}"
        else:
            # Regular shell script
            import subprocess
            try:
                result = subprocess.run(['bash', script_file],
                                      capture_output=True, text=True)
                return f"📜 Executed: {script_file}\n\n{result.stdout}\n{result.stderr}"
            except Exception as e:
                return f"❌ Execution error: {str(e)}"

    def _handle_pick(self, params):
        """Interactive file picker with fuzzy search."""
        from core.uDOS_interactive import InteractivePrompt
        prompt = InteractivePrompt()

        # Get search pattern
        pattern = params[0] if params else ''
        if not pattern:
            pattern = prompt.ask_text(
                "🔍 Search pattern",
                default=""
            )
            if not pattern:
                pattern = ""

        # Get workspace filter
        workspaces = list(self.workspace_manager.WORKSPACES.keys())
        workspace_choices = ["all"] + workspaces

        workspace_choice = prompt.ask_choice(
            "📁 Workspace",
            choices=workspace_choices,
            default="all"
        )

        workspace = None if workspace_choice == "all" else workspace_choice

        # Perform search
        results = self.file_picker.fuzzy_search_files(
            pattern, workspace=workspace, max_results=20
        )

        if not results:
            return f"❌ No files found matching '{pattern}'"

        # Display results with selection
        file_choices = []
        for i, file_info in enumerate(results):
            score_bar = "█" * int(file_info['score'] * 10)
            git_status = f" [{file_info['git_status']}]" if file_info.get('git_status') else ""
            size_kb = file_info['size'] // 1024 if file_info['size'] > 1024 else file_info['size']
            size_unit = "KB" if file_info['size'] > 1024 else "B"

            file_choices.append(
                f"{file_info['workspace']}/{file_info['file_path']} "
                f"({score_bar} {file_info['score']:.2f}) "
                f"[{file_info['file_type']}] {size_kb}{size_unit}{git_status}"
            )

        selected = prompt.ask_choice(
            "📄 Select file",
            choices=file_choices,
            default=file_choices[0]
        )

        if not selected:
            return "❌ File selection cancelled"

        # Extract file info from selection
        selected_index = file_choices.index(selected)
        selected_file = results[selected_index]

        # Record file access
        self.file_picker.record_file_access(
            selected_file['file_path'],
            selected_file['workspace'],
            'pick'
        )

        return (f"✅ Selected: {selected_file['workspace']}/{selected_file['file_path']}\n"
               f"📊 Score: {selected_file['score']:.2f}\n"
               f"🏷️ Type: {selected_file['file_type']}\n"
               f"📦 Size: {selected_file['size']} bytes\n"
               f"💡 Use: EDIT {selected_file['file_path']} to open")

    def _handle_recent(self, params):
        """Show recently accessed files."""
        count = 20
        workspace = None

        # Parse parameters
        if params:
            try:
                count = int(params[0])
            except ValueError:
                workspace = params[0]
                if len(params) > 1:
                    try:
                        count = int(params[1])
                    except ValueError:
                        pass

        recent_files = self.file_picker.get_recent_files(
            count=count, workspace=workspace
        )

        if not recent_files:
            ws_msg = f" in {workspace}" if workspace else ""
            return f"❌ No recent files found{ws_msg}"

        # Format output
        output = f"📁 Recent Files (last {count})\n\n"

        for i, file_info in enumerate(recent_files, 1):
            exists_icon = "✅" if file_info['exists'] else "❌"
            access_time = file_info['last_access'][:19]  # Remove microseconds

            output += (f"{i:2d}. {exists_icon} {file_info['workspace']}/{file_info['file_path']}\n"
                      f"     🕒 {access_time} ({file_info['access_count']} times)\n"
                      f"     🏷️ {file_info.get('file_type', 'unknown')}\n\n")

        output += "💡 Use: FILE PICK <filename> to select a file"
        return output

    def _handle_batch(self, params):
        """Handle batch file operations."""
        from core.uDOS_interactive import InteractivePrompt
        prompt = InteractivePrompt()

        if not params:
            return ("❌ Batch operation required\n"
                   "Usage: FILE BATCH [DELETE|COPY|MOVE] <pattern> [destination]")

        operation = params[0].upper()

        if operation not in ['DELETE', 'COPY', 'MOVE']:
            return f"❌ Unknown batch operation: {operation}"

        if len(params) < 2:
            return f"❌ Pattern required for batch {operation}"

        pattern = params[1]
        destination = params[2] if len(params) > 2 else None

        # Find matching files
        matches = self.file_picker.fuzzy_search_files(
            pattern, max_results=100
        )

        if not matches:
            return f"❌ No files found matching pattern '{pattern}'"

        # Show matches and confirm
        match_list = "\n".join([
            f"  {m['workspace']}/{m['file_path']}" for m in matches[:10]
        ])

        if len(matches) > 10:
            match_list += f"\n  ... and {len(matches) - 10} more files"

        confirm_msg = (f"⚠️ {operation} {len(matches)} files:\n{match_list}\n\n"
                      f"Continue? (y/N)")

        if not prompt.ask_yes_no(confirm_msg, default=False):
            return "❌ Batch operation cancelled"

        # Perform operation
        success_count = 0
        error_count = 0
        errors = []

        for file_info in matches:
            try:
                source_path = (self.workspace_manager.get_workspace_path(file_info['workspace']) /
                              file_info['file_path'])

                if operation == "DELETE":
                    source_path.unlink()
                    success_count += 1

                elif operation == "COPY":
                    if not destination:
                        errors.append(f"No destination for {file_info['file_path']}")
                        error_count += 1
                        continue

                    dest_path = Path(destination) / source_path.name
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.copy2(source_path, dest_path)
                    success_count += 1

                elif operation == "MOVE":
                    if not destination:
                        errors.append(f"No destination for {file_info['file_path']}")
                        error_count += 1
                        continue

                    dest_path = Path(destination) / source_path.name
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    source_path.rename(dest_path)
                    success_count += 1

            except Exception as e:
                errors.append(f"{file_info['file_path']}: {str(e)}")
                error_count += 1

        # Record batch operation
        for file_info in matches[:success_count]:
            self.file_picker.record_file_access(
                file_info['file_path'],
                file_info['workspace'],
                f'batch_{operation.lower()}'
            )

        result = f"✅ Batch {operation}: {success_count} successful"
        if error_count > 0:
            result += f", {error_count} errors"
            if errors[:3]:  # Show first 3 errors
                result += f"\n❌ Errors:\n" + "\n".join(f"  • {e}" for e in errors[:3])

        return result

    def _handle_bookmarks(self, params):
        """Manage file bookmarks."""
        from core.uDOS_interactive import InteractivePrompt
        prompt = InteractivePrompt()

        if not params:
            # List bookmarks
            bookmarks = self.file_picker.get_bookmarks()

            if not bookmarks:
                return "📚 No bookmarks found\n💡 Use: FILE BOOKMARKS ADD <filename> to add"

            output = "📚 File Bookmarks\n\n"
            for i, bookmark in enumerate(bookmarks, 1):
                exists_icon = "✅" if bookmark['exists'] else "❌"
                name = bookmark['bookmark_name'] or bookmark['file_path']
                tags = f" 🏷️ {', '.join(bookmark['tags'])}" if bookmark['tags'] else ""

                output += (f"{i:2d}. {exists_icon} {name}\n"
                          f"     📁 {bookmark['workspace']}/{bookmark['file_path']}{tags}\n\n")

            output += "💡 Use: FILE BOOKMARKS ADD/REMOVE <filename>"
            return output

        action = params[0].upper()

        if action == "ADD":
            if len(params) < 2:
                # Show file picker
                files = self.workspace_manager.list_files()
                if not files:
                    return "❌ No files to bookmark"

                file_choice = prompt.ask_choice(
                    "📄 File to bookmark",
                    choices=files,
                    default=files[0]
                )

                if not file_choice:
                    return "❌ Bookmark cancelled"

                filename = file_choice
            else:
                filename = params[1]

            # Ask for bookmark name and tags
            bookmark_name = prompt.ask_text(
                "📝 Bookmark name (optional)",
                default=filename
            )

            tags_input = prompt.ask_text(
                "🏷️ Tags (comma-separated, optional)",
                default=""
            )

            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]

            success = self.file_picker.add_bookmark(
                filename,
                self.workspace_manager.current_workspace,
                bookmark_name,
                tags
            )

            if success:
                return f"✅ Bookmarked: {filename}"
            else:
                return f"❌ Failed to bookmark: {filename}"

        elif action == "REMOVE":
            if len(params) < 2:
                # Show bookmarks to remove
                bookmarks = self.file_picker.get_bookmarks()
                if not bookmarks:
                    return "❌ No bookmarks to remove"

                bookmark_choices = [
                    f"{b['bookmark_name'] or b['file_path']} ({b['workspace']})"
                    for b in bookmarks
                ]

                choice = prompt.ask_choice(
                    "📚 Bookmark to remove",
                    choices=bookmark_choices,
                    default=bookmark_choices[0]
                )

                if not choice:
                    return "❌ Remove cancelled"

                # Extract bookmark info
                selected_index = bookmark_choices.index(choice)
                selected_bookmark = bookmarks[selected_index]
                filename = selected_bookmark['file_path']
                workspace = selected_bookmark['workspace']
            else:
                filename = params[1]
                workspace = self.workspace_manager.current_workspace

            success = self.file_picker.remove_bookmark(filename, workspace)

            if success:
                return f"✅ Removed bookmark: {filename}"
            else:
                return f"❌ Bookmark not found: {filename}"

        else:
            return f"❌ Unknown bookmark action: {action}\nUse: ADD or REMOVE"

    def _handle_preview(self, params):
        """Show file preview with metadata."""
        if not params:
            return "❌ Filename required for preview"

        filename = params[0]
        file_path = self.workspace_manager.get_workspace_path() / filename

        if not file_path.exists():
            return f"❌ File not found: {filename}"

        try:
            # Get file stats
            stat = file_path.stat()
            size = stat.st_size
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

            # Determine file type
            extension = file_path.suffix.lower()
            file_type = self.file_picker._classify_file_type(extension)

            # Get git status
            git_status = self.file_picker._get_git_status(file_path)
            git_info = f" (git: {git_status})" if git_status else ""

            output = f"📄 File Preview: {filename}\n\n"
            output += f"📦 Size: {size:,} bytes ({size/1024:.1f} KB)\n"
            output += f"🕒 Modified: {mtime}\n"
            output += f"🏷️ Type: {file_type} ({extension}){git_info}\n\n"

            # Show content preview for text files
            if file_type in ['text', 'code', 'config', 'script'] and size < 10000:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    lines = content.split('\n')

                    output += "📝 Content Preview (first 20 lines):\n"
                    output += "─" * 50 + "\n"

                    for i, line in enumerate(lines[:20], 1):
                        output += f"{i:3d}: {line}\n"

                    if len(lines) > 20:
                        output += f"... ({len(lines) - 20} more lines)\n"

                    output += "─" * 50 + "\n"

                except UnicodeDecodeError:
                    output += "📝 Binary file - content preview unavailable\n"
            else:
                output += f"📝 File too large for preview ({size:,} bytes)\n"

            # Record access
            self.file_picker.record_file_access(filename, access_type='preview')

            return output

        except Exception as e:
            return f"❌ Preview error: {str(e)}"

    def _handle_info(self, params):
        """Show detailed file information."""
        if not params:
            return "❌ Filename required for info"

        filename = params[0]
        file_path = self.workspace_manager.get_workspace_path() / filename

        if not file_path.exists():
            return f"❌ File not found: {filename}"

        try:
            # Get comprehensive file info
            stat = file_path.stat()

            # File size with multiple units
            size_bytes = stat.st_size
            size_kb = size_bytes / 1024
            size_mb = size_kb / 1024

            # Timestamps
            mtime = datetime.fromtimestamp(stat.st_mtime)
            ctime = datetime.fromtimestamp(stat.st_ctime)
            atime = datetime.fromtimestamp(stat.st_atime)

            # File type classification
            extension = file_path.suffix.lower()
            file_type = self.file_picker._classify_file_type(extension)

            # Git information
            git_status = self.file_picker._get_git_status(file_path)

            # Check if file is in bookmarks
            bookmarks = self.file_picker.get_bookmarks()
            is_bookmarked = any(
                b['file_path'] == filename and
                b['workspace'] == self.workspace_manager.current_workspace
                for b in bookmarks
            )

            # Get recent access info
            recent_files = self.file_picker.get_recent_files(count=1000)
            access_info = next(
                (f for f in recent_files if f['file_path'] == filename),
                None
            )

            output = f"ℹ️ File Information: {filename}\n\n"

            # Basic info
            output += "📊 Basic Information:\n"
            output += f"  📦 Size: {size_bytes:,} bytes ({size_kb:.1f} KB, {size_mb:.2f} MB)\n"
            output += f"  🏷️ Type: {file_type} ({extension or 'no extension'})\n"
            output += f"  📁 Workspace: {self.workspace_manager.current_workspace}\n"
            output += f"  📚 Bookmarked: {'Yes' if is_bookmarked else 'No'}\n\n"

            # Timestamps
            output += "🕒 Timestamps:\n"
            output += f"  📝 Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"  📅 Created: {ctime.strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"  👁️ Accessed: {atime.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            # Git info
            if git_status:
                output += f"🔧 Git Status: {git_status}\n\n"

            # Access history
            if access_info:
                output += "📈 Access History:\n"
                output += f"  🔢 Times accessed: {access_info['access_count']}\n"
                output += f"  🕒 Last access: {access_info['last_access'][:19]}\n\n"

            # Line count for text files
            if file_type in ['text', 'code', 'config', 'script'] and size_bytes < 100000:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    lines = len(content.split('\n'))
                    chars = len(content)
                    words = len(content.split())

                    output += "📝 Text Statistics:\n"
                    output += f"  📄 Lines: {lines:,}\n"
                    output += f"  🔤 Characters: {chars:,}\n"
                    output += f"  📝 Words: {words:,}\n\n"
                except UnicodeDecodeError:
                    output += "📝 Binary file - text statistics unavailable\n\n"

            output += "💡 Commands:\n"
            output += f"  EDIT {filename} - Edit file\n"
            output += f"  FILE PREVIEW {filename} - Show content preview\n"
            if not is_bookmarked:
                output += f"  FILE BOOKMARKS ADD {filename} - Add to bookmarks\n"

            # Record access
            self.file_picker.record_file_access(filename, access_type='info')

            return output

        except Exception as e:
            return f"❌ Info error: {str(e)}"

    # ======================================================================
    # SMART MODE (v1.0.29) - Interactive File Operations
    # ======================================================================

    def _file_interactive_menu(self):
        """
        Smart mode: Interactive file operations menu.
        Prompts user for operation and file selection.
        """
        try:
            # Present operation choices
            operations = [
                "Create New File",
                "Edit Existing File",
                "View/Show File",
                "Copy File",
                "Move File",
                "Rename File",
                "Delete File",
                "File Info",
                "Recent Files",
                "Bookmarks",
                "Cancel"
            ]

            operation = self.input_manager.prompt_choice(
                message="What would you like to do?",
                choices=operations,
                default="Edit Existing File"
            )

            if operation == "Cancel":
                return "File operation cancelled."

            # Route to appropriate handler based on choice
            if operation == "Create New File":
                return self._smart_create_file()

            elif operation == "Edit Existing File":
                return self._smart_edit_file()

            elif operation == "View/Show File":
                return self._smart_show_file()

            elif operation == "Copy File":
                return self._smart_copy_file()

            elif operation == "Move File":
                return self._smart_move_file()

            elif operation == "Rename File":
                return self._smart_rename_file()

            elif operation == "Delete File":
                return self._smart_delete_file()

            elif operation == "File Info":
                return self._smart_file_info()

            elif operation == "Recent Files":
                return self._handle_recent([])

            elif operation == "Bookmarks":
                return self._handle_bookmarks([])

            else:
                return "Unknown operation."

        except KeyboardInterrupt:
            return "\n⚠️ File operation cancelled."
        except Exception as e:
            return self.output_formatter.format_error(
                "File operation failed",
                error_details=str(e)
            )

    def _smart_create_file(self):
        """Smart mode: Create new file with prompts."""
        try:
            # Ask for filename
            filename = self.input_manager.prompt_user(
                message="Enter filename:",
                required=True
            )

            # Get workspace choices
            workspaces = self.workspace_manager.list_workspaces()
            ws_choices = [f"{name} - {ws['description']}"
                         for name, ws in workspaces.items()]

            ws_choice = self.input_manager.prompt_choice(
                message="Select workspace:",
                choices=ws_choices,
                default=ws_choices[0] if ws_choices else None
            )

            if not ws_choice:
                return "❌ File creation cancelled"

            workspace = ws_choice.split()[0]  # Extract name

            # Template selection
            templates = self.workspace_manager.TEMPLATES
            template_choices = [f"{key} - {tpl['name']}"
                               for key, tpl in templates.items()]

            template_choice = self.input_manager.prompt_choice(
                message="Select template:",
                choices=template_choices,
                default=template_choices[0] if template_choices else None
            )

            if not template_choice:
                return "❌ File creation cancelled"

            template = template_choice.split()[0]  # Extract key

            # Create file
            file_path = self.workspace_manager.create_file(
                workspace, filename, template
            )

            return self.output_formatter.format_success(
                f"File created: {filename}",
                details=f"Workspace: {workspace}\nTemplate: {template}\nPath: {file_path}"
            )

        except Exception as e:
            return self.output_formatter.format_error(
                "File creation failed",
                error_details=str(e)
            )

    def _smart_edit_file(self):
        """Smart mode: Edit file with file picker."""
        try:
            # Use knowledge file picker (same as EDIT command)
            from core.ui.knowledge_file_picker import KnowledgeFilePicker
            picker = KnowledgeFilePicker()

            file_path = picker.pick_file(
                workspace='both',
                prompt="📝 Select file to edit",
                file_types=['.md', '.uscript', '.txt', '.json']
            )

            if not file_path:
                return "❌ No file selected"

            # Edit the file
            return self._handle_edit([file_path])

        except Exception as e:
            return self.output_formatter.format_error(
                "File edit failed",
                error_details=str(e)
            )

    def _smart_show_file(self):
        """Smart mode: Show/view file with file picker."""
        try:
            # Use knowledge file picker (same as EDIT command)
            from core.ui.knowledge_file_picker import KnowledgeFilePicker
            picker = KnowledgeFilePicker()

            file_path = picker.pick_file(
                workspace='both',
                prompt="📄 Select file to view",
                file_types=['.md', '.uscript', '.txt', '.json']
            )

            if not file_path:
                return "❌ No file selected"

            # Show the file
            return self._handle_show([file_path])

        except Exception as e:
            return self.output_formatter.format_error(
                "File show failed",
                error_details=str(e)
            )

    def _smart_copy_file(self):
        """Smart mode: Copy file with prompts."""
        try:
            # Use knowledge file picker (same as EDIT command)
            from core.ui.knowledge_file_picker import KnowledgeFilePicker
            picker = KnowledgeFilePicker()

            source = picker.pick_file(
                workspace='both',
                prompt="📎 Select file to copy",
                file_types=['.md', '.uscript', '.txt', '.json']
            )

            if not source:
                return "❌ No source file selected"

            # Ask for destination filename
            dest = self.input_manager.prompt_user(
                message=f"Copy '{source}' to:",
                default=f"{source}.copy",
                required=True
            )

            # Confirm operation
            confirm = self.input_manager.prompt_confirm(
                message=f"Copy '{source}' to '{dest}'?",
                default=True
            )

            if not confirm:
                return "❌ Copy cancelled"

            # Perform copy
            return self._handle_copy([source, dest])

        except Exception as e:
            return self.output_formatter.format_error(
                "File copy failed",
                error_details=str(e)
            )

    def _smart_move_file(self):
        """Smart mode: Move file with prompts."""
        try:
            # Use knowledge file picker (same as EDIT command)
            from core.ui.knowledge_file_picker import KnowledgeFilePicker
            picker = KnowledgeFilePicker()

            source = picker.pick_file(
                workspace='both',
                prompt="📦 Select file to move",
                file_types=['.md', '.uscript', '.txt', '.json']
            )

            if not source:
                return "❌ No source file selected"

            # Ask for destination
            dest = self.input_manager.prompt_user(
                message=f"Move '{source}' to:",
                required=True
            )

            # Confirm operation
            confirm = self.input_manager.prompt_confirm(
                message=f"Move '{source}' to '{dest}'?",
                default=True
            )

            if not confirm:
                return "❌ Move cancelled"

            # Perform move
            return self._handle_move([source, dest])

        except Exception as e:
            return self.output_formatter.format_error(
                "File move failed",
                error_details=str(e)
            )

    def _smart_rename_file(self):
        """Smart mode: Rename file with prompts."""
        try:
            # Use knowledge file picker (same as EDIT command)
            from core.ui.knowledge_file_picker import KnowledgeFilePicker
            picker = KnowledgeFilePicker()

            old_name = picker.pick_file(
                workspace='both',
                prompt="✏️  Select file to rename",
                file_types=['.md', '.uscript', '.txt', '.json']
            )

            if not old_name:
                return "❌ No file selected"

            # Ask for new name
            new_name = self.input_manager.prompt_user(
                message=f"Rename '{old_name}' to:",
                default=old_name,
                required=True
            )

            # Confirm operation
            confirm = self.input_manager.prompt_confirm(
                message=f"Rename '{old_name}' to '{new_name}'?",
                default=True
            )

            if not confirm:
                return "❌ Rename cancelled"

            # Perform rename
            return self._handle_rename([old_name, new_name])

        except Exception as e:
            return self.output_formatter.format_error(
                "File rename failed",
                error_details=str(e)
            )

    def _smart_delete_file(self):
        """Smart mode: Delete file with prompts."""
        try:
            # Use knowledge file picker (same as EDIT command)
            from core.ui.knowledge_file_picker import KnowledgeFilePicker
            picker = KnowledgeFilePicker()

            filename = picker.pick_file(
                workspace='both',
                prompt="🗑️  Select file to delete",
                file_types=['.md', '.uscript', '.txt', '.json']
            )

            if not filename:
                return "❌ No file selected"

            # Confirm deletion
            confirm = self.input_manager.prompt_confirm(
                message=f"⚠️ Delete '{filename}'? This cannot be undone!",
                default=False
            )

            if not confirm:
                return "❌ Delete cancelled"

            # Perform deletion
            return self._handle_delete([filename])

        except Exception as e:
            return self.output_formatter.format_error(
                "File delete failed",
                error_details=str(e)
            )

    def _smart_file_info(self):
        """Smart mode: Show file info with file picker."""
        try:
            # Use knowledge file picker (same as EDIT command)
            from core.ui.knowledge_file_picker import KnowledgeFilePicker
            picker = KnowledgeFilePicker()

            filename = picker.pick_file(
                workspace='both',
                prompt="ℹ️  Select file for info",
                file_types=['.md', '.uscript', '.txt', '.json']
            )

            if not filename:
                return "❌ No file selected"

            # Show info
            return self._handle_info([filename])

        except Exception as e:
            return self.output_formatter.format_error(
                "File info failed",
                error_details=str(e)
            )

    # ======================================================================
