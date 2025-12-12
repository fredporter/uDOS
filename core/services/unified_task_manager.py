"""
Unified Task Manager for uDOS v1.2.23

Single source of truth for all task-like entities:
- Simple tasks (calendar items)
- Checklist items (guided processes)
- Workflow steps (automated execution)
- Mission objectives (project deliverables)

Features:
- Relationship tracking (tasks → projects → missions)
- Location-aware (TILE codes from uDOS ID standard)
- Auto-archiving of completed items
- UNDO/REDO/BACKUP/RESTORE integration
- FilenameGenerator for consistent naming

Author: uDOS Team
Version: 1.2.23
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from core.config import Config
from core.utils.filename_generator import FilenameGenerator
from core.utils.archive_manager import ArchiveManager


class UnifiedTaskManager:
    """Manage all task-like entities in unified system."""
    
    # Task types
    TASK = "task"
    CHECKLIST_ITEM = "checklist_item"
    WORKFLOW_STEP = "workflow_step"
    MISSION = "mission"
    
    # Task statuses
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    DONE = "done"
    ARCHIVED = "archived"
    
    # Priorities
    NORMAL = "normal"
    URGENT = "urgent"
    CRITICAL = "critical"
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize unified task manager.
        
        Args:
            config: uDOS configuration instance
        """
        self.config = config or Config()
        self.filename_gen = FilenameGenerator(config=self.config)
        self.archive_mgr = ArchiveManager()
        
        # Paths
        self.tasks_dir = Path("memory/workflows/tasks")
        self.tasks_file = self.tasks_dir / "unified_tasks.json"
        self.archive_dir = self.tasks_dir / ".archive"
        self.backups_dir = self.tasks_dir / "backups"
        
        # Ensure directories exist
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize data
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load unified tasks data from JSON file."""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Warning: Could not load tasks file: {e}")
                return self._create_empty_data()
        else:
            return self._create_empty_data()
    
    def _create_empty_data(self) -> Dict[str, Any]:
        """Create empty data structure."""
        return {
            "tasks": [],
            "projects": [],
            "next_task_num": 1,
            "next_project_num": 1,
            "version": "1.2.23",
            "last_modified": datetime.now().isoformat()
        }
    
    def _save_data(self, create_backup: bool = True):
        """
        Save unified tasks data to JSON file.
        
        Args:
            create_backup: Whether to create backup before saving
        """
        # Create backup if requested and file exists
        if create_backup and self.tasks_file.exists():
            try:
                self.archive_mgr.add_backup(self.tasks_file, self.backups_dir.parent)
            except Exception as e:
                print(f"⚠️  Warning: Could not create backup: {e}")
        
        # Update last modified timestamp
        self.data["last_modified"] = datetime.now().isoformat()
        
        # Save to file
        with open(self.tasks_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID using FilenameGenerator."""
        task_num = self.data["next_task_num"]
        self.data["next_task_num"] += 1
        
        task_id = self.filename_gen.generate(
            base_name=f"task-{task_num:03d}",
            extension="",
            include_date=True,
            include_time=True
        )
        return task_id
    
    def _generate_project_id(self, name: str) -> str:
        """Generate unique project ID using FilenameGenerator."""
        project_num = self.data["next_project_num"]
        self.data["next_project_num"] += 1
        
        # Create slug from name
        slug = name.lower().replace(' ', '-').replace('_', '-')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')[:30]
        
        project_id = self.filename_gen.generate(
            base_name=f"mission-{slug}",
            extension="",
            include_date=True,
            include_time=True
        )
        return project_id
    
    def create_task(
        self,
        description: str,
        task_type: str = TASK,
        parent_id: Optional[str] = None,
        project: Optional[str] = None,
        priority: str = NORMAL,
        due_date: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new task.
        
        Args:
            description: Task description
            task_type: Type of task (task, checklist_item, workflow_step, mission)
            parent_id: Parent task/project ID
            project: Project name
            priority: Priority level (normal, urgent, critical)
            due_date: Due date (YYYY-MM-DD format)
            **kwargs: Additional metadata (tags, location, workflow_file, etc.)
        
        Returns:
            Created task dictionary
        """
        task_id = self._generate_task_id()
        
        # Get location from config if not provided
        location = kwargs.get('location', self.config.get('current_tile', None))
        timezone = kwargs.get('timezone', self.config.get('timezone', 'UTC'))
        
        task = {
            "id": task_id,
            "type": task_type,
            "description": description,
            "status": self.PENDING,
            "priority": priority,
            "due_date": due_date,
            "created": datetime.now().isoformat(),
            "completed": None,
            "progress": 0,
            
            # Relationships
            "parent_id": parent_id,
            "project": project,
            "workflow_file": kwargs.get('workflow_file'),
            "checklist_ref": kwargs.get('checklist_ref'),
            
            # Location awareness
            "location": location,
            "timezone": timezone,
            
            # Metadata
            "tags": kwargs.get('tags', []),
            "estimated_hours": kwargs.get('estimated_hours'),
            "actual_hours": kwargs.get('actual_hours', 0),
            
            # Archive tracking
            "archived_at": None,
            "archived_path": None
        }
        
        self.data["tasks"].append(task)
        self._save_data()
        
        return task
    
    def create_project(
        self,
        name: str,
        description: str,
        location: Optional[str] = None,
        workflow_file: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new project/mission.
        
        Args:
            name: Project name
            description: Project description
            location: TILE code (defaults to config)
            workflow_file: Associated workflow .upy file
            **kwargs: Additional metadata
        
        Returns:
            Created project dictionary
        """
        project_id = self._generate_project_id(name)
        
        # Get location from config if not provided
        if location is None:
            location = self.config.get('current_tile', None)
        
        project = {
            "id": project_id,
            "name": name,
            "description": description,
            "status": "active",
            "created": datetime.now().isoformat(),
            "completed": None,
            "location": location,
            "workflow_file": workflow_file,
            "task_ids": [],
            "completion_percentage": 0,
            "tags": kwargs.get('tags', [])
        }
        
        self.data["projects"].append(project)
        self._save_data()
        
        return project
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID."""
        for task in self.data["tasks"]:
            if task["id"] == task_id:
                return task
        return None
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID."""
        for project in self.data["projects"]:
            if project["id"] == project_id:
                return project
        return None
    
    def list_tasks(
        self,
        status: Optional[str] = None,
        project: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List tasks with optional filters.
        
        Args:
            status: Filter by status
            project: Filter by project name
            task_type: Filter by task type
        
        Returns:
            List of matching tasks
        """
        tasks = self.data["tasks"]
        
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        if project:
            tasks = [t for t in tasks if t.get("project") == project]
        if task_type:
            tasks = [t for t in tasks if t["type"] == task_type]
        
        return tasks
    
    def list_projects(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List projects with optional status filter."""
        projects = self.data["projects"]
        
        if status:
            projects = [p for p in projects if p["status"] == status]
        
        return projects
    
    def update_task(self, task_id: str, **updates) -> bool:
        """
        Update task fields.
        
        Args:
            task_id: Task ID
            **updates: Fields to update
        
        Returns:
            True if updated successfully
        """
        task = self.get_task(task_id)
        if not task:
            return False
        
        for key, value in updates.items():
            if key in task:
                task[key] = value
        
        self._save_data()
        return True
    
    def complete_task(self, task_id: str) -> bool:
        """Mark task as done."""
        return self.update_task(
            task_id,
            status=self.DONE,
            completed=datetime.now().isoformat(),
            progress=100
        )
    
    def archive_task(self, task_id: str) -> Optional[Path]:
        """
        Archive completed task to .archive/.
        
        Args:
            task_id: Task ID to archive
        
        Returns:
            Path to archived task file, or None if failed
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        # Create monthly archive folder
        now = datetime.now()
        month_folder = self.archive_dir / f"{now.year}-{now.month:02d}"
        month_folder.mkdir(parents=True, exist_ok=True)
        
        # Generate archive filename
        archive_filename = self.filename_gen.generate(
            base_name=f"archived-task-{task_id}",
            extension=".json",
            include_date=True
        )
        archive_path = month_folder / archive_filename
        
        # Save task to archive
        with open(archive_path, 'w') as f:
            json.dump(task, f, indent=2)
        
        # Update task status and remove from active list
        task["status"] = self.ARCHIVED
        task["archived_at"] = datetime.now().isoformat()
        task["archived_path"] = str(archive_path)
        
        self.data["tasks"] = [t for t in self.data["tasks"] if t["id"] != task_id]
        self._save_data()
        
        return archive_path
    
    def archive_project(self, project_id: str) -> Optional[Path]:
        """
        Archive completed project and all related tasks.
        
        Args:
            project_id: Project ID to archive
        
        Returns:
            Path to archived project file, or None if failed
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        # Archive all related tasks first
        project_tasks = [t for t in self.data["tasks"] if t.get("parent_id") == project_id]
        for task in project_tasks:
            self.archive_task(task["id"])
        
        # Create projects archive folder
        projects_folder = self.archive_dir / "projects"
        projects_folder.mkdir(parents=True, exist_ok=True)
        
        # Generate archive filename
        archive_filename = f"{project_id}.json"
        archive_path = projects_folder / archive_filename
        
        # Save project to archive
        with open(archive_path, 'w') as f:
            json.dump(project, f, indent=2)
        
        # Remove from active list
        self.data["projects"] = [p for p in self.data["projects"] if p["id"] != project_id]
        self._save_data()
        
        return archive_path
    
    def link_task_to_project(self, task_id: str, project_id: str) -> bool:
        """Link a task to a project."""
        task = self.get_task(task_id)
        project = self.get_project(project_id)
        
        if not task or not project:
            return False
        
        # Update task
        task["parent_id"] = project_id
        task["project"] = project["name"]
        
        # Update project
        if task_id not in project["task_ids"]:
            project["task_ids"].append(task_id)
        
        # Recalculate project completion
        self._update_project_completion(project_id)
        
        self._save_data()
        return True
    
    def _update_project_completion(self, project_id: str):
        """Update project completion percentage based on tasks."""
        project = self.get_project(project_id)
        if not project:
            return
        
        task_ids = project["task_ids"]
        if not task_ids:
            project["completion_percentage"] = 0
            return
        
        total_tasks = len(task_ids)
        completed_tasks = sum(
            1 for task_id in task_ids
            if self.get_task(task_id) and self.get_task(task_id)["status"] == self.DONE
        )
        
        project["completion_percentage"] = int((completed_tasks / total_tasks) * 100)


def create_task_manager(config: Optional[Config] = None) -> UnifiedTaskManager:
    """Factory function to create task manager instance."""
    return UnifiedTaskManager(config)
