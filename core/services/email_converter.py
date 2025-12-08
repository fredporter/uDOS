"""
Email to Markdown Converter for uDOS v1.2.9

Converts parsed Gmail emails into uDOS-compatible formats:
- Markdown notes (memory/docs/)
- Task checklists (memory/checklists/)
- Mission workflows (memory/missions/)

Features:
- Intelligent format detection
- Template-based conversion
- Metadata preservation
- File naming conventions
- Duplicate detection

Author: @fredporter
Version: 1.2.9
Date: December 2025
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.services.email_parser import get_email_parser


class EmailConverter:
    """
    Convert parsed emails to uDOS formats.

    Handles:
    - Email to markdown notes
    - Email to task checklists
    - Email to mission workflows
    - File naming and organization
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize email converter.

        Args:
            project_root: Project root path
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.parser = get_email_parser()

        # Output directories
        self.docs_dir = self.project_root / "memory" / "docs"
        self.checklists_dir = self.project_root / "memory" / "checklists"
        self.missions_dir = self.project_root / "memory" / "missions"

        # Ensure directories exist
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.checklists_dir.mkdir(parents=True, exist_ok=True)
        self.missions_dir.mkdir(parents=True, exist_ok=True)

    def convert_to_note(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert email to markdown note.

        Args:
            email_data: Parsed email data

        Returns:
            Conversion result with file path
        """
        # Parse email if not already parsed
        if 'metadata' not in email_data:
            parsed = self.parser.parse_email(email_data)
        else:
            parsed = email_data

        metadata = parsed['metadata']
        content = parsed['content']
        urls = parsed.get('urls', [])

        # Generate filename
        subject = metadata['subject']
        filename = self._sanitize_filename(subject) + '.md'
        filepath = self.docs_dir / filename

        # Check for duplicates
        if filepath.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self._sanitize_filename(subject)}_{timestamp}.md"
            filepath = self.docs_dir / filename

        # Build markdown content
        md_lines = [
            f"# {subject}",
            "",
            "## Email Metadata",
            f"**From:** {metadata['from']['name']} <{metadata['from']['email']}>",
            f"**Date:** {metadata['date']}",
            f"**Message ID:** {metadata['message_id']}",
            ""
        ]

        # Add labels if any
        if metadata.get('labels'):
            md_lines.append(f"**Labels:** {', '.join(metadata['labels'])}")
            md_lines.append("")

        # Add content
        md_lines.extend([
            "## Content",
            "",
            content,
            ""
        ])

        # Add URLs if any
        if urls:
            md_lines.extend([
                "## Links",
                ""
            ])
            for url in urls:
                md_lines.append(f"- {url}")
            md_lines.append("")

        # Write file
        filepath.write_text('\n'.join(md_lines), encoding='utf-8')

        return {
            'success': True,
            'type': 'note',
            'path': str(filepath),
            'filename': filename
        }

    def convert_to_checklist(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert email to task checklist.

        Args:
            email_data: Parsed email data

        Returns:
            Conversion result with file path
        """
        # Parse email if not already parsed
        if 'metadata' not in email_data:
            parsed = self.parser.parse_email(email_data)
        else:
            parsed = email_data

        metadata = parsed['metadata']
        tasks = parsed.get('tasks', [])
        priority = parsed.get('priority', 'medium')
        deadline = parsed.get('deadline')

        if not tasks:
            return {
                'success': False,
                'error': 'No tasks found in email'
            }

        # Generate filename
        subject = metadata['subject']
        filename = self._sanitize_filename(subject) + '_tasks.md'
        filepath = self.checklists_dir / filename

        # Check for duplicates
        if filepath.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self._sanitize_filename(subject)}_tasks_{timestamp}.md"
            filepath = self.checklists_dir / filename

        # Build checklist
        md_lines = [
            f"# {subject}",
            "",
            "## Details",
            f"**From:** {metadata['from']['name']} <{metadata['from']['email']}>",
            f"**Date:** {metadata['date']}",
            f"**Priority:** {priority.upper()}",
        ]

        if deadline:
            md_lines.append(f"**Deadline:** {deadline}")

        md_lines.extend([
            "",
            "## Tasks",
            ""
        ])

        # Add tasks
        for task in tasks:
            checkbox = "☐"
            task_line = f"{checkbox} {task['text']}"

            if task.get('deadline'):
                task_line += f" (by {task['deadline']})"

            md_lines.append(task_line)

        md_lines.append("")

        # Add source
        md_lines.extend([
            "---",
            f"Source: Email from {metadata['from']['email']}",
            f"Message ID: {metadata['message_id']}"
        ])

        # Write file
        filepath.write_text('\n'.join(md_lines), encoding='utf-8')

        return {
            'success': True,
            'type': 'checklist',
            'path': str(filepath),
            'filename': filename,
            'task_count': len(tasks)
        }

    def convert_to_mission(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert email to mission workflow.

        Args:
            email_data: Parsed email data

        Returns:
            Conversion result with file path
        """
        # Parse email if not already parsed
        if 'metadata' not in email_data:
            parsed = self.parser.parse_email(email_data)
        else:
            parsed = email_data

        metadata = parsed['metadata']
        tasks = parsed.get('tasks', [])
        priority = parsed.get('priority', 'medium')
        deadline = parsed.get('deadline')

        if not tasks:
            return {
                'success': False,
                'error': 'No tasks found in email'
            }

        # Generate filename
        subject = metadata['subject']
        filename = self._sanitize_filename(subject) + '_mission.upy'
        filepath = self.missions_dir / filename

        # Check for duplicates
        if filepath.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self._sanitize_filename(subject)}_mission_{timestamp}.upy"
            filepath = self.missions_dir / filename

        # Build mission script (uPY format)
        mission_lines = [
            f"# Mission: {subject}",
            f"# Generated from email: {metadata['date']}",
            f"# From: {metadata['from']['email']}",
            f"# Priority: {priority.upper()}",
        ]

        if deadline:
            mission_lines.append(f"# Deadline: {deadline}")

        mission_lines.extend([
            "",
            "# Mission setup",
            f'$MISSION.NAME = "{subject}"',
            f'$MISSION.PRIORITY = "{priority}"',
            f'$MISSION.SOURCE = "email:{metadata["message_id"]}"',
            ""
        ])

        if deadline:
            mission_lines.append(f'$MISSION.DEADLINE = "{deadline}"')
            mission_lines.append("")

        # Add tasks as checkpoints
        mission_lines.extend([
            "# Task checkpoints",
            ""
        ])

        for i, task in enumerate(tasks, 1):
            task_text = task['text'].replace('"', '\\"')  # Escape quotes
            mission_lines.append(f'CHECKPOINT "Task {i}: {task_text}"')

            if task.get('deadline'):
                mission_lines.append(f'  # Due: {task["deadline"]}')

            mission_lines.append("")

        # Add completion
        mission_lines.extend([
            "# Mission complete",
            'PRINT "✅ Mission completed: ' + subject.replace('"', '\\"') + '"',
            ""
        ])

        # Write file
        filepath.write_text('\n'.join(mission_lines), encoding='utf-8')

        return {
            'success': True,
            'type': 'mission',
            'path': str(filepath),
            'filename': filename,
            'task_count': len(tasks)
        }

    def convert_thread_to_mission(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert email thread to comprehensive mission.

        Args:
            thread_data: Parsed thread context

        Returns:
            Conversion result with file path
        """
        subject = thread_data.get('subject', 'Untitled Thread')
        all_tasks = thread_data.get('all_tasks', [])
        participants = thread_data.get('participants', [])

        if not all_tasks:
            return {
                'success': False,
                'error': 'No tasks found in thread'
            }

        # Generate filename
        filename = self._sanitize_filename(subject) + '_thread_mission.upy'
        filepath = self.missions_dir / filename

        # Check for duplicates
        if filepath.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self._sanitize_filename(subject)}_thread_mission_{timestamp}.upy"
            filepath = self.missions_dir / filename

        # Build mission script
        mission_lines = [
            f"# Thread Mission: {subject}",
            f"# Messages: {thread_data['message_count']}",
            f"# Participants: {', '.join(participants)}",
            f"# Generated: {datetime.now().isoformat()}",
            "",
            "# Mission setup",
            f'$MISSION.NAME = "{subject}"',
            f'$MISSION.TYPE = "thread"',
            f'$MISSION.THREAD_ID = "{thread_data["thread_id"]}"',
            "",
            "# Aggregated tasks from thread",
            ""
        ]

        # Add all tasks
        for i, task in enumerate(all_tasks, 1):
            task_text = task['text'].replace('"', '\\"')
            mission_lines.append(f'CHECKPOINT "Task {i}: {task_text}"')

            if task.get('deadline'):
                mission_lines.append(f'  # Due: {task["deadline"]}')

            mission_lines.append("")

        mission_lines.extend([
            "# Thread mission complete",
            'PRINT "✅ Thread mission completed"',
            ""
        ])

        # Write file
        filepath.write_text('\n'.join(mission_lines), encoding='utf-8')

        return {
            'success': True,
            'type': 'thread_mission',
            'path': str(filepath),
            'filename': filename,
            'task_count': len(all_tasks)
        }

    def auto_convert(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically determine best conversion format.

        Args:
            email_data: Parsed email data

        Returns:
            Conversion result
        """
        # Parse email if not already parsed
        if 'metadata' not in email_data:
            parsed = self.parser.parse_email(email_data)
        else:
            parsed = email_data

        tasks = parsed.get('tasks', [])

        # Decision logic
        if len(tasks) >= 3:
            # Many tasks -> mission
            return self.convert_to_mission(parsed)
        elif len(tasks) > 0:
            # Few tasks -> checklist
            return self.convert_to_checklist(parsed)
        else:
            # No tasks -> note
            return self.convert_to_note(parsed)

    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize string for use as filename.

        Args:
            name: Original name

        Returns:
            Sanitized filename (no extension)
        """
        # Remove/replace invalid characters
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        name = re.sub(r'\s+', '_', name)
        name = name.strip('._')

        # Limit length
        if len(name) > 100:
            name = name[:100]

        return name.lower()


# Singleton instance
_email_converter_instance = None

def get_email_converter() -> EmailConverter:
    """Get singleton email converter instance."""
    global _email_converter_instance
    if _email_converter_instance is None:
        _email_converter_instance = EmailConverter()
    return _email_converter_instance
