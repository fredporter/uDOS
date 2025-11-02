"""
uDOS v1.0.2 - Enhanced File Operations

Enhancements to FileCommandHandler:
- Smart file picker integration
- Batch operations
- File preview
- Recently used files
- Workspace bookmarks

Version: 1.0.2
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from .base_handler import BaseCommandHandler


class EnhancedFileCommandHandler(BaseCommandHandler):
    """Enhanced file handler with smart picker and batch operations."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._workspace_manager = None
        self._editor_manager = None
        self._smart_picker = None

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
            try:
                from core.services.editor_manager import EditorManager
                self._editor_manager = EditorManager()
            except ImportError:
                # Fallback mock for testing
                class MockEditorManager:
                    def edit_file(self, file_path, mode=None, editor=None):
                        return f"✅ Mock edit: {file_path} (mode: {mode}, editor: {editor})"
                self._editor_manager = MockEditorManager()
        return self._editor_manager

    @property
    def smart_picker(self):
        """Lazy load smart file picker."""
        if self._smart_picker is None:
            from core.utils.smart_picker import SmartFilePicker
            self._smart_picker = SmartFilePicker()
        return self._smart_picker

    def handle(self, command, params, grid, parser=None):
        """Route enhanced file commands."""
        # Existing commands
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

        # New enhanced commands
        elif command == "SEARCH":
            return self._handle_search(params)
        elif command == "RECENT":
            return self._handle_recent(params)
        elif command == "BOOKMARK":
            return self._handle_bookmark(params)
        elif command == "BATCH":
            return self._handle_batch(params)
        elif command == "PREVIEW":
            return self._handle_preview(params)

        else:
            return self.get_message("ERROR_UNKNOWN_FILE_COMMAND", command=command)

    def _handle_search(self, params):
        """Smart file search with fuzzy matching and progress indicators."""
        if not params:
            return "❌ Usage: SEARCH <query> [workspace]"

        query = params[0]
        workspace = params[1] if len(params) > 1 else 'sandbox'

        if workspace not in self.smart_picker.ALLOWED_DIRS:
            return f"❌ Invalid workspace: {workspace}. Use: {', '.join(self.smart_picker.ALLOWED_DIRS)}"

        # Import progress manager
        try:
            from core.services.progress_manager import progress_manager, ProgressConfig
        except ImportError:
            # Fallback to simple search without progress
            return self._simple_search(query, workspace)

        # Create progress indicator for multi-stage search
        stages = ["Scanning directories", "Loading files", "Fuzzy matching", "Generating previews"]
        search_progress = progress_manager.create_multi_stage_progress(
            f"file_search_{query}",
            stages,
            ProgressConfig(show_time_estimate=True, show_percentage=True)
        )

        try:
            # Stage 1: Scanning directories
            search_progress.start_stage(0, f"Scanning {workspace}/ directory structure")
            files = self.smart_picker.get_files_in_workspace(workspace)
            search_progress.complete_stage(f"Found {len(files)} files")

            # Stage 2: Loading file metadata
            search_progress.start_stage(1, "Loading file metadata", len(files))
            for i, file_path in enumerate(files):
                # Simulate some work for file metadata loading
                if i % 10 == 0:  # Update every 10 files
                    search_progress.update_stage(i, f"Processing {os.path.basename(file_path)}")
            search_progress.complete_stage("File metadata loaded")

            # Stage 3: Fuzzy matching
            search_progress.start_stage(2, f"Fuzzy matching against '{query}'", len(files))

            # Use the existing fuzzy_search method which returns (path, score) tuples
            matches = self.smart_picker.fuzzy_search(query, files)

            # Update progress as we process results
            for i in range(0, len(files), 50):  # Update every 50 files processed
                search_progress.update_stage(
                    min(i + 50, len(files)),
                    f"Matched {len(matches)} files so far"
                )

            search_progress.complete_stage(f"Found {len(matches)} matches")

            if not matches:
                search_progress.complete("Search completed - no matches found")
                return f"❌ No files found matching '{query}' in {workspace}/"

            # Stage 4: Generating previews
            preview_count = min(3, len(matches))
            search_progress.start_stage(3, f"Generating previews for top {preview_count} results", preview_count)

            # Format results with progress updates
            result = [f"🔍 Search Results for '{query}' in {workspace}/"]
            result.append("=" * 60)

            for i, (file_path, score) in enumerate(matches[:10], 1):
                file_info = self.smart_picker.format_file_info(file_path)
                result.append(f"{i:2d}. {file_info} (score: {score:.2f})")

                # Add preview for top 3 results with progress updates
                if i <= 3 and self.smart_picker.settings.get('preview_enabled', True):
                    search_progress.update_stage(i - 1, f"Generating preview for {os.path.basename(file_path)}")
                    preview = self.smart_picker.get_file_preview(file_path, 1)
                    if preview and "No preview" not in preview:
                        result.append(f"     Preview: {preview[:80]}...")

            search_progress.complete_stage("Previews generated")

            if len(matches) > 10:
                result.append(f"\n... and {len(matches) - 10} more matches")

            result.append(f"\n💡 Use: SHOW <filename> or EDIT <filename>")

            # Complete the search
            search_progress.complete(f"Search completed - {len(matches)} matches found")

            # Clean up progress after a short delay
            import threading
            def cleanup():
                import time
                time.sleep(2)  # Show completion for 2 seconds
                progress_manager.remove_progress(f"file_search_{query}")

            threading.Thread(target=cleanup, daemon=True).start()

            return "\n".join(result)

        except KeyboardInterrupt:
            search_progress.current_indicator.cancel("Search cancelled by user")
            return "🚫 Search operation cancelled"
        except Exception as e:
            search_progress.current_indicator.error(f"Search failed: {str(e)}")
            return f"❌ Search error: {str(e)}"

    def _simple_search(self, query, workspace):
        """Fallback search without progress indicators."""
        files = self.smart_picker.get_files_in_workspace(workspace)
        matches = self.smart_picker.fuzzy_search(query, files)

        if not matches:
            return f"❌ No files found matching '{query}' in {workspace}/"

        # Format results
        result = [f"🔍 Search Results for '{query}' in {workspace}/"]
        result.append("=" * 60)

        for i, (file_path, score) in enumerate(matches[:10], 1):
            file_info = self.smart_picker.format_file_info(file_path)
            result.append(f"{i:2d}. {file_info} (score: {score:.2f})")

            # Add preview for top 3 results
            if i <= 3 and self.smart_picker.settings.get('preview_enabled', True):
                preview = self.smart_picker.get_file_preview(file_path, 1)
                if preview and "No preview" not in preview:
                    result.append(f"     Preview: {preview[:80]}...")

        if len(matches) > 10:
            result.append(f"\n... and {len(matches) - 10} more matches")

        result.append(f"\n💡 Use: SHOW <filename> or EDIT <filename>")

        return "\n".join(result)

    def _handle_recent(self, params):
        """Show and manage recently used files."""
        if not params:
            # Show recent files
            recent_files = self.smart_picker.recent_files

            if not recent_files:
                return "📂 No recent files found"

            result = ["🕒 Recently Used Files"]
            result.append("=" * 40)

            for i, recent in enumerate(recent_files[:15], 1):
                rel_path = recent['relative_path']
                action = recent.get('action', 'accessed')
                frequency = recent.get('frequency', 1)

                # Check if file still exists
                if Path(rel_path).exists():
                    file_info = self.smart_picker.format_file_info(Path(rel_path))
                    result.append(f"{i:2d}. {file_info}")
                    result.append(f"     Last {action}, used {frequency} times")
                else:
                    result.append(f"{i:2d}. ❌ {rel_path} (missing)")

            result.append(f"\n💡 Use: RECENT clear - to clear history")
            result.append(f"💡 Use: SHOW/EDIT <number> - to open recent file")

            return "\n".join(result)

        elif params[0].lower() == 'clear':
            # Clear recent files
            self.smart_picker.recent_files = []
            self.smart_picker._save_recent_files()
            return "✅ Recent files history cleared"

        else:
            return "❌ Usage: RECENT [clear]"

    def _handle_bookmark(self, params):
        """Manage workspace bookmarks."""
        if not params:
            # Show bookmarks
            bookmarks = self.smart_picker.bookmarks

            if not bookmarks:
                return "🔖 No bookmarks found"

            result = ["🔖 Workspace Bookmarks"]
            result.append("=" * 30)

            for name, path in bookmarks.items():
                if Path(path).exists():
                    result.append(f"  {name} → {path}")
                else:
                    result.append(f"  {name} → {path} ❌ (missing)")

            result.append(f"\n💡 Use: BOOKMARK add <name> <path>")
            result.append(f"💡 Use: BOOKMARK remove <name>")
            result.append(f"💡 Use: SHOW @<name> - to open bookmark")

            return "\n".join(result)

        elif params[0].lower() == 'add' and len(params) >= 3:
            # Add bookmark
            name = params[1]
            path = params[2]

            if not Path(path).exists():
                return f"❌ File not found: {path}"

            self.smart_picker.add_bookmark(name, path)
            return f"✅ Bookmark added: {name} → {path}"

        elif params[0].lower() == 'remove' and len(params) >= 2:
            # Remove bookmark
            name = params[1]

            if name not in self.smart_picker.bookmarks:
                return f"❌ Bookmark not found: {name}"

            self.smart_picker.remove_bookmark(name)
            return f"✅ Bookmark removed: {name}"

        else:
            return "❌ Usage: BOOKMARK [add <name> <path>|remove <name>]"

    def _handle_batch(self, params):
        """Batch file operations."""
        if not params:
            return "❌ Usage: BATCH <operation> [pattern] [workspace]"

        operation = params[0].lower()
        pattern = params[1] if len(params) > 1 else '*'
        workspace = params[2] if len(params) > 2 else 'sandbox'

        if workspace not in self.smart_picker.ALLOWED_DIRS:
            return f"❌ Invalid workspace: {workspace}"

        # Get matching files
        files = self.smart_picker.get_files_in_workspace(workspace)
        matching_files = [f for f in files if f.match(pattern)]

        if not matching_files:
            return f"❌ No files found matching '{pattern}' in {workspace}/"

        if operation == 'list':
            # List matching files
            result = [f"📋 Batch List: {len(matching_files)} files matching '{pattern}' in {workspace}/"]
            result.append("=" * 60)

            for i, file_path in enumerate(matching_files[:20], 1):
                file_info = self.smart_picker.format_file_info(file_path)
                result.append(f"{i:2d}. {file_info}")

            if len(matching_files) > 20:
                result.append(f"... and {len(matching_files) - 20} more files")

            result.append(f"\n💡 Use: BATCH delete {pattern} - to delete all")
            result.append(f"💡 Use: BATCH copy {pattern} memory - to copy all to memory")

            return "\n".join(result)

        elif operation == 'delete':
            # Batch delete (with confirmation)
            print(f"⚠️  About to delete {len(matching_files)} files matching '{pattern}':")
            for file_path in matching_files[:10]:
                print(f"  - {file_path.name}")
            if len(matching_files) > 10:
                print(f"  ... and {len(matching_files) - 10} more")

            confirm = input("\nConfirm batch delete? (type 'DELETE' to confirm): ")
            if confirm != 'DELETE':
                return "❌ Batch delete cancelled"

            # Delete files
            deleted_count = 0
            errors = []

            for file_path in matching_files:
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        deleted_count += 1
                except Exception as e:
                    errors.append(f"{file_path.name}: {e}")

            result = [f"✅ Batch delete completed: {deleted_count} files deleted"]
            if errors:
                result.append(f"❌ Errors: {len(errors)}")
                for error in errors[:5]:
                    result.append(f"  - {error}")

            return "\n".join(result)

        elif operation == 'copy':
            # Batch copy to another workspace
            dest_workspace = params[3] if len(params) > 3 else 'memory'

            if dest_workspace not in self.smart_picker.ALLOWED_DIRS:
                return f"❌ Invalid destination workspace: {dest_workspace}"

            if dest_workspace == workspace:
                return "❌ Source and destination workspaces cannot be the same"

            # Copy files
            dest_path = Path(dest_workspace)
            dest_path.mkdir(exist_ok=True)

            copied_count = 0
            errors = []

            for file_path in matching_files:
                try:
                    if file_path.is_file():
                        dest_file = dest_path / file_path.name
                        if dest_file.exists():
                            dest_file = dest_path / f"copy_of_{file_path.name}"

                        shutil.copy2(file_path, dest_file)
                        copied_count += 1
                except Exception as e:
                    errors.append(f"{file_path.name}: {e}")

            result = [f"✅ Batch copy completed: {copied_count} files copied to {dest_workspace}/"]
            if errors:
                result.append(f"❌ Errors: {len(errors)}")
                for error in errors[:5]:
                    result.append(f"  - {error}")

            return "\n".join(result)

        else:
            return f"❌ Unknown batch operation: {operation}. Use: list, delete, copy"

    def _handle_preview(self, params):
        """Show file preview."""
        if not params:
            return "❌ Usage: PREVIEW <filename>"

        file_path = Path(params[0])

        if not file_path.exists():
            return f"❌ File not found: {params[0]}"

        # Security check
        abs_path = file_path.resolve()
        allowed_dirs = [Path(d).resolve() for d in self.smart_picker.ALLOWED_DIRS]

        if not any(str(abs_path).startswith(str(allowed_dir)) for allowed_dir in allowed_dirs):
            return f"❌ Access denied: {params[0]}\n\nOnly {', '.join(self.smart_picker.ALLOWED_DIRS)} directories are accessible"

        # Get file info and preview
        file_info = self.smart_picker.format_file_info(file_path)
        preview = self.smart_picker.get_file_preview(file_path, 20)

        result = [f"👁️  File Preview: {file_path.name}"]
        result.append("=" * 50)
        result.append(f"Info: {file_info}")
        result.append("")
        result.append("Content:")
        result.append("-" * 30)
        result.append(preview)
        result.append("-" * 30)
        result.append(f"\n💡 Use: EDIT {params[0]} - to edit")
        result.append(f"💡 Use: SHOW {params[0]} - to view full content")

        return "\n".join(result)

    # Enhanced versions of existing methods
    def _handle_show(self, params):
        """Enhanced SHOW with bookmark support."""
        if not params:
            # Use smart picker for interactive selection
            files = self.smart_picker.pick_file_interactive(
                workspace='sandbox',
                title="Select file to show",
                show_recent=True,
                show_bookmarks=True
            )
            if not files:
                return "❌ No file selected"
            file_path = files[0]
        else:
            file_path = params[0]

            # Check for bookmark reference
            if file_path.startswith('@'):
                bookmark_name = file_path[1:]
                if bookmark_name in self.smart_picker.bookmarks:
                    file_path = self.smart_picker.bookmarks[bookmark_name]
                else:
                    return f"❌ Bookmark not found: {bookmark_name}"

        # Add to recent files
        self.smart_picker.add_to_recent(file_path, 'viewed')

        # Continue with original SHOW logic
        mode = '--cli'
        if len(params) > 1 and params[1] in ['--web', '--browser']:
            mode = '--web'

        # Security check
        abs_path = os.path.abspath(file_path)
        allowed_dirs = [os.path.abspath(d) for d in self.smart_picker.ALLOWED_DIRS]
        if not any(abs_path.startswith(allowed_dir) for allowed_dir in allowed_dirs):
            return f"❌ Access denied: {file_path}\n\nOnly {', '.join(self.smart_picker.ALLOWED_DIRS)} are accessible"

        if not os.path.exists(file_path):
            return f"❌ File not found: {file_path}"

        if mode == '--web':
            import webbrowser
            webbrowser.open(f"file://{abs_path}")
            return f"✅ Opened in browser: {file_path}"
        else:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return f"📄 {file_path}\n{'═'*60}\n\n{content}\n\n{'═'*60}"
            except Exception as e:
                return f"❌ Error reading file: {str(e)}"

    def _handle_edit(self, params):
        """Enhanced EDIT with smart picker and recent files."""
        if not params:
            # Use smart picker for interactive selection
            files = self.smart_picker.pick_file_interactive(
                workspace='sandbox',
                title="Select file to edit",
                show_recent=True,
                show_bookmarks=True
            )
            if not files:
                return "❌ No file selected"
            file_path = files[0]
        else:
            file_path = params[0]

            # Check for bookmark reference
            if file_path.startswith('@'):
                bookmark_name = file_path[1:]
                if bookmark_name in self.smart_picker.bookmarks:
                    file_path = self.smart_picker.bookmarks[bookmark_name]
                else:
                    return f"❌ Bookmark not found: {bookmark_name}"

        # Add to recent files
        self.smart_picker.add_to_recent(file_path, 'edited')

        # Parse options
        mode = None
        specific_editor = None
        for param in params[1:]:
            if param in ['--cli', '--terminal']:
                mode = 'cli'
            elif param in ['--web', '--browser']:
                mode = 'web'
            elif param.startswith('--'):
                specific_editor = param[2:]

        try:
            result = self.editor_manager.edit_file(
                file_path,
                mode=mode,
                editor=specific_editor
            )
            return result
        except Exception as e:
            return f"❌ Error opening editor: {str(e)}"

    # Include all other existing methods from original FileCommandHandler
    def _handle_new(self, params):
        """Create new file with template selection (from original)."""
        from core.uDOS_interactive import InteractivePrompt
        prompt = InteractivePrompt()

        filename = params[0] if params else ''

        if not filename:
            filename = prompt.ask_text(
                "📄 File name",
                default="new_file.txt"
            )
            if not filename:
                return "❌ File creation cancelled"

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

        workspace = ws_choice.split()[0]

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

        template = template_choice.split()[0]

        try:
            file_path = self.workspace_manager.new_file(filename, template, workspace)

            # Add to recent files
            self.smart_picker.add_to_recent(str(file_path), 'created')

            return (f"✅ Created: {file_path}\n\n"
                   f"💡 Use: EDIT {filename} to start editing")
        except FileExistsError as e:
            return f"❌ {str(e)}"
        except Exception as e:
            return f"❌ Error creating file: {str(e)}"

    def _handle_delete(self, params):
        """Delete file with confirmation (from original)."""
        from core.uDOS_interactive import InteractivePrompt
        prompt = InteractivePrompt()

        filename = params[0] if params else ''

        files = self.workspace_manager.list_files()
        if not files:
            return "❌ No files in current workspace"

        if not filename:
            filename = prompt.ask_choice(
                "🗑️  Delete file",
                choices=[f.name for f in files],
                default=files[0].name if files else None
            )
            if not filename:
                return "❌ Delete cancelled"

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
        """Copy file within or between workspaces (from original)."""
        from core.uDOS_interactive import InteractivePrompt
        prompt = InteractivePrompt()

        source = params[0] if params else ''
        destination = params[1] if len(params) > 1 else ''

        files = self.workspace_manager.list_files()
        if not source:
            source = prompt.ask_choice(
                "📄 Source file",
                choices=[f.name for f in files],
                default=files[0].name if files else None
            )
            if not source:
                return "❌ Copy cancelled"

        if not destination:
            destination = prompt.ask_text(
                "📄 Destination name",
                default=f"copy_of_{source}"
            )
            if not destination:
                return "❌ Copy cancelled"

        workspaces = self.workspace_manager.list_workspaces()
        ws_choices = ['Same workspace'] + [name for name in workspaces.keys()]

        ws_choice = prompt.ask_choice(
            "📁 Destination workspace",
            choices=ws_choices,
            default='Same workspace'
        )

        dest_ws = None if ws_choice == 'Same workspace' else ws_choice

        try:
            new_path = self.workspace_manager.copy_file(source, destination, None, dest_ws)

            # Add to recent files
            self.smart_picker.add_to_recent(str(new_path), 'copied')

            return f"✅ Copied to: {new_path}"
        except (FileNotFoundError, FileExistsError) as e:
            return f"❌ {str(e)}"
        except Exception as e:
            return f"❌ Error copying file: {str(e)}"

    def _handle_move(self, params):
        """Move file between workspaces (from original)."""
        from core.uDOS_interactive import InteractivePrompt
        prompt = InteractivePrompt()

        source = params[0] if params else ''
        destination = params[1] if len(params) > 1 else ''

        files = self.workspace_manager.list_files()
        if not source:
            source = prompt.ask_choice(
                "📄 File to move",
                choices=[f.name for f in files],
                default=files[0].name if files else None
            )
            if not source:
                return "❌ Move cancelled"

        workspaces = self.workspace_manager.list_workspaces()
        ws_choices = list(workspaces.keys())

        dest_ws = prompt.ask_choice(
            "📁 Move to workspace",
            choices=ws_choices,
            default=ws_choices[0]
        )

        if not dest_ws:
            return "❌ Move cancelled"

        if not destination:
            destination = prompt.ask_text(
                "📄 New name (optional)",
                default=source
            )
            if not destination:
                destination = source

        try:
            new_path = self.workspace_manager.move_file(source, destination, None, dest_ws)

            # Add to recent files
            self.smart_picker.add_to_recent(str(new_path), 'moved')

            return f"✅ Moved to: {new_path}"
        except (FileNotFoundError, FileExistsError) as e:
            return f"❌ {str(e)}"
        except Exception as e:
            return f"❌ Error moving file: {str(e)}"

    def _handle_rename(self, params):
        """Rename file in current workspace (from original)."""
        from core.uDOS_interactive import InteractivePrompt
        prompt = InteractivePrompt()

        old_name = params[0] if params else ''
        new_name = params[1] if len(params) > 1 else ''

        files = self.workspace_manager.list_files()
        if not old_name:
            old_name = prompt.ask_choice(
                "📄 File to rename",
                choices=[f.name for f in files],
                default=files[0].name if files else None
            )
            if not old_name:
                return "❌ Rename cancelled"

        if not new_name:
            new_name = prompt.ask_text(
                "📄 New name",
                default=old_name
            )
            if not new_name or new_name == old_name:
                return "❌ Rename cancelled"

        try:
            new_path = self.workspace_manager.rename_file(old_name, new_name)

            # Add to recent files
            self.smart_picker.add_to_recent(str(new_path), 'renamed')

            return f"✅ Renamed to: {new_name}"
        except (FileNotFoundError, FileExistsError) as e:
            return f"❌ {str(e)}"
        except Exception as e:
            return f"❌ Error renaming file: {str(e)}"

    def _handle_run(self, params, parser):
        """Execute script file (from original)."""
        if not params:
            # Use smart picker for script selection
            files = self.smart_picker.pick_file_interactive(
                workspace='sandbox',
                title="Select script to run",
                file_patterns=['*.uscript', '*.py', '*.sh'],
                show_recent=True
            )
            if not files:
                return "❌ No script selected"
            script_file = files[0]
        else:
            script_file = params[0]

        if not os.path.exists(script_file):
            return f"❌ Script not found: {script_file}"

        # Add to recent files
        self.smart_picker.add_to_recent(script_file, 'executed')

        if script_file.endswith('.uscript'):
            try:
                from core.utils.ucode import UCodeInterpreter
                interpreter = UCodeInterpreter(command_handler=self)
                result = interpreter.execute_script(script_file)
                return f"📜 Executed: {script_file}\n\n{result}"
            except Exception as e:
                return f"❌ Script error: {str(e)}"
        else:
            import subprocess
            try:
                result = subprocess.run(['bash', script_file],
                                      capture_output=True, text=True)
                return f"📜 Executed: {script_file}\n\n{result.stdout}\n{result.stderr}"
            except Exception as e:
                return f"❌ Execution error: {str(e)}"
