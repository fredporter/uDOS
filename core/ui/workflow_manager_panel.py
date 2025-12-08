"""
Workflow Manager Panel for uDOS TUI

W-key opens workflow manager with mission templates and workflow lifecycle management.
Supports user workflows (survival missions) and dev workflows (build/test/deploy).

Features:
- List workflows (active, paused, completed)
- Mission templates (water, shelter, navigation, medical, communication)
- Create workflow from template
- Start/pause/resume/complete actions
- Integration with memory/workflows/ and memory/ucode/adventures/

Usage:
    Press W-key to open workflow manager
    Navigate with arrow keys (or numpad 8/2)
    Press ENTER to select workflow
    Press ESC to close panel
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from prompt_toolkit.formatted_text import HTML, FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Window
from prompt_toolkit.layout.controls import FormattedTextControl

from core.utils.paths import PATHS


class WorkflowState:
    """Represents state of a workflow."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowEntry:
    """Single workflow entry."""
    
    def __init__(self, data: Dict):
        self.id = data.get("id", "")
        self.name = data.get("name", "Unnamed Workflow")
        self.type = data.get("type", "mission")  # mission or dev
        self.state = data.get("state", WorkflowState.DRAFT)
        self.template = data.get("template", None)
        self.progress = data.get("progress", "0/0")
        self.start_time = data.get("start_time", None)
        self.last_checkpoint = data.get("last_checkpoint", None)
        self.tile_code = data.get("tile_code", None)  # Optional TILE location
        self.description = data.get("description", "")
    
    def get_state_emoji(self) -> str:
        """Get emoji indicator for workflow state."""
        return {
            WorkflowState.DRAFT: "📝",
            WorkflowState.ACTIVE: "🔄",
            WorkflowState.PAUSED: "⏸️",
            WorkflowState.COMPLETED: "✅",
            WorkflowState.FAILED: "❌"
        }.get(self.state, "❓")
    
    def get_type_emoji(self) -> str:
        """Get emoji indicator for workflow type."""
        return "🎯" if self.type == "mission" else "🛠️"
    
    def format_progress(self) -> str:
        """Format progress display."""
        if "/" in self.progress:
            try:
                current, total = map(int, self.progress.split("/"))
                if total > 0:
                    percent = int((current / total) * 100)
                    return f"{percent}%"
            except ValueError:
                pass
        return self.progress


class MissionTemplate:
    """Predefined mission template."""
    
    def __init__(self, name: str, category: str, description: str, script_path: Optional[str] = None):
        self.name = name
        self.category = category  # water, shelter, navigation, medical, communication, dev
        self.description = description
        self.script_path = script_path
    
    def get_category_emoji(self) -> str:
        """Get emoji for template category."""
        return {
            "water": "💧",
            "shelter": "🏠",
            "navigation": "🧭",
            "medical": "🏥",
            "communication": "📡",
            "dev": "💻",
            "food": "🍖",
            "fire": "🔥"
        }.get(self.category, "📋")


class WorkflowManagerPanel:
    """Workflow Manager Panel for TUI."""
    
    # Predefined mission templates
    TEMPLATES = [
        MissionTemplate("Water Collection", "water", "Locate and collect clean water sources", "water_collection.upy"),
        MissionTemplate("Water Purification", "water", "Purify water using available methods", "water_purification.upy"),
        MissionTemplate("Shelter Building", "shelter", "Build emergency shelter from local materials", "shelter_building.upy"),
        MissionTemplate("Navigation Route", "navigation", "Plan and execute navigation to destination", "navigation_route.upy"),
        MissionTemplate("First Aid Response", "medical", "Provide emergency first aid", "first_aid_response.upy"),
        MissionTemplate("Radio Setup", "communication", "Set up emergency radio communication", "radio_setup.upy"),
        MissionTemplate("Fire Starting", "fire", "Start fire using available methods", "fire_starting.upy"),
        MissionTemplate("Food Foraging", "food", "Identify and forage for edible plants", "food_foraging.upy"),
        MissionTemplate("Dev Build", "dev", "Build and test development branch", "dev_build.upy"),
        MissionTemplate("Dev Release", "dev", "Create and deploy release", "dev_release.upy"),
    ]
    
    def __init__(self):
        self.selected_index = 0
        self.view_mode = "workflows"  # workflows, templates, details
        self.workflows: List[WorkflowEntry] = []
        self.selected_workflow: Optional[WorkflowEntry] = None
        
        # Paths
        self.workflows_dir = PATHS.MEMORY / "workflows" / "missions"
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        self.templates_dir = PATHS.MEMORY / "ucode" / "adventures"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.checkpoints_dir = PATHS.MEMORY / "workflows" / "checkpoints"
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_dir = PATHS.MEMORY / "workflows" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Load workflows
        self._load_workflows()
    
    def _load_workflows(self):
        """Load workflows from memory/workflows/missions/."""
        self.workflows = []
        
        # Load from state directory
        for state_file in self.state_dir.glob("*.json"):
            try:
                with open(state_file, "r") as f:
                    data = json.load(f)
                    self.workflows.append(WorkflowEntry(data))
            except Exception as e:
                print(f"Error loading workflow {state_file}: {e}")
        
        # Sort by state priority (active > paused > draft > completed/failed)
        state_priority = {
            WorkflowState.ACTIVE: 0,
            WorkflowState.PAUSED: 1,
            WorkflowState.DRAFT: 2,
            WorkflowState.COMPLETED: 3,
            WorkflowState.FAILED: 4
        }
        self.workflows.sort(key=lambda w: state_priority.get(w.state, 99))
    
    def _save_workflow(self, workflow: WorkflowEntry):
        """Save workflow state."""
        state_file = self.state_dir / f"{workflow.id}.json"
        
        data = {
            "id": workflow.id,
            "name": workflow.name,
            "type": workflow.type,
            "state": workflow.state,
            "template": workflow.template,
            "progress": workflow.progress,
            "start_time": workflow.start_time,
            "last_checkpoint": workflow.last_checkpoint,
            "tile_code": workflow.tile_code,
            "description": workflow.description
        }
        
        with open(state_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def create_workflow_from_template(self, template: MissionTemplate, tile_code: Optional[str] = None):
        """Create new workflow from template."""
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        workflow = WorkflowEntry({
            "id": workflow_id,
            "name": template.name,
            "type": "dev" if template.category == "dev" else "mission",
            "state": WorkflowState.DRAFT,
            "template": template.script_path,
            "progress": "0/1",
            "start_time": None,
            "last_checkpoint": None,
            "tile_code": tile_code,
            "description": template.description
        })
        
        self._save_workflow(workflow)
        self._load_workflows()
        
        return workflow
    
    def start_workflow(self, workflow: WorkflowEntry):
        """Start a workflow."""
        workflow.state = WorkflowState.ACTIVE
        workflow.start_time = datetime.now().isoformat()
        self._save_workflow(workflow)
        self._load_workflows()
    
    def pause_workflow(self, workflow: WorkflowEntry):
        """Pause a workflow."""
        if workflow.state == WorkflowState.ACTIVE:
            workflow.state = WorkflowState.PAUSED
            self._save_workflow(workflow)
            self._load_workflows()
    
    def resume_workflow(self, workflow: WorkflowEntry):
        """Resume a paused workflow."""
        if workflow.state == WorkflowState.PAUSED:
            workflow.state = WorkflowState.ACTIVE
            self._save_workflow(workflow)
            self._load_workflows()
    
    def complete_workflow(self, workflow: WorkflowEntry):
        """Mark workflow as completed."""
        workflow.state = WorkflowState.COMPLETED
        self._save_workflow(workflow)
        self._load_workflows()
    
    def render(self) -> FormattedText:
        """Render workflow manager panel."""
        if self.view_mode == "workflows":
            return self._render_workflows_view()
        elif self.view_mode == "templates":
            return self._render_templates_view()
        elif self.view_mode == "details":
            return self._render_details_view()
        return FormattedText([])
    
    def _render_workflows_view(self) -> FormattedText:
        """Render main workflows list."""
        lines = []
        
        # Header
        lines.append(("", "\n"))
        lines.append(("class:title", "╔═══════════════════════════════════════════════════════════════════════════════╗\n"))
        lines.append(("class:title", "║ 🎯 WORKFLOW MANAGER                                                           ║\n"))
        lines.append(("class:title", "╠═══════════════════════════════════════════════════════════════════════════════╣\n"))
        lines.append(("", "║ W-key: Workflows | T-key: Templates | ENTER: Select | ESC: Close              ║\n"))
        lines.append(("class:title", "╚═══════════════════════════════════════════════════════════════════════════════╝\n"))
        lines.append(("", "\n"))
        
        # Workflows list
        if not self.workflows:
            lines.append(("class:hint", "  No workflows found. Press T to create from template.\n"))
        else:
            for idx, workflow in enumerate(self.workflows):
                prefix = "▶ " if idx == self.selected_index else "  "
                style = "class:selected" if idx == self.selected_index else ""
                
                state_emoji = workflow.get_state_emoji()
                type_emoji = workflow.get_type_emoji()
                progress = workflow.format_progress()
                
                tile_info = f" @ {workflow.tile_code}" if workflow.tile_code else ""
                
                line = f"{prefix}{state_emoji} {type_emoji} {workflow.name} [{workflow.state}] {progress}{tile_info}\n"
                lines.append((style, line))
        
        # Footer actions
        lines.append(("", "\n"))
        if self.workflows and self.selected_index < len(self.workflows):
            workflow = self.workflows[self.selected_index]
            lines.append(("class:hint", "  Actions: "))
            
            if workflow.state == WorkflowState.DRAFT:
                lines.append(("class:action", "[S]tart "))
            elif workflow.state == WorkflowState.ACTIVE:
                lines.append(("class:action", "[P]ause "))
                lines.append(("class:action", "[C]omplete "))
            elif workflow.state == WorkflowState.PAUSED:
                lines.append(("class:action", "[R]esume "))
                lines.append(("class:action", "[C]omplete "))
            
            lines.append(("class:action", "[D]etails "))
            lines.append(("class:action", "[X]Delete\n"))
        
        return FormattedText(lines)
    
    def _render_templates_view(self) -> FormattedText:
        """Render mission templates list."""
        lines = []
        
        # Header
        lines.append(("", "\n"))
        lines.append(("class:title", "╔═══════════════════════════════════════════════════════════════════════════════╗\n"))
        lines.append(("class:title", "║ 📋 MISSION TEMPLATES                                                          ║\n"))
        lines.append(("class:title", "╠═══════════════════════════════════════════════════════════════════════════════╣\n"))
        lines.append(("", "║ ENTER: Create Workflow | ESC: Back                                            ║\n"))
        lines.append(("class:title", "╚═══════════════════════════════════════════════════════════════════════════════╝\n"))
        lines.append(("", "\n"))
        
        # Templates by category
        current_category = None
        for idx, template in enumerate(self.TEMPLATES):
            if template.category != current_category:
                current_category = template.category
                lines.append(("class:category", f"\n  {template.get_category_emoji()} {current_category.upper()}\n"))
            
            prefix = "▶ " if idx == self.selected_index else "  "
            style = "class:selected" if idx == self.selected_index else ""
            
            line = f"{prefix}  {template.name} - {template.description}\n"
            lines.append((style, line))
        
        return FormattedText(lines)
    
    def _render_details_view(self) -> FormattedText:
        """Render workflow details."""
        lines = []
        
        if not self.selected_workflow:
            return FormattedText([("", "No workflow selected.\n")])
        
        w = self.selected_workflow
        
        # Header
        lines.append(("", "\n"))
        lines.append(("class:title", "╔═══════════════════════════════════════════════════════════════════════════════╗\n"))
        lines.append(("class:title", f"║ {w.get_state_emoji()} {w.name:<74} ║\n"))
        lines.append(("class:title", "╠═══════════════════════════════════════════════════════════════════════════════╣\n"))
        lines.append(("", "\n"))
        
        # Details
        lines.append(("class:label", f"  ID: "))
        lines.append(("", f"{w.id}\n"))
        
        lines.append(("class:label", f"  Type: "))
        lines.append(("", f"{w.get_type_emoji()} {w.type}\n"))
        
        lines.append(("class:label", f"  State: "))
        lines.append(("", f"{w.get_state_emoji()} {w.state}\n"))
        
        lines.append(("class:label", f"  Progress: "))
        lines.append(("", f"{w.format_progress()} ({w.progress})\n"))
        
        if w.start_time:
            lines.append(("class:label", f"  Started: "))
            lines.append(("", f"{w.start_time}\n"))
        
        if w.last_checkpoint:
            lines.append(("class:label", f"  Checkpoint: "))
            lines.append(("", f"{w.last_checkpoint}\n"))
        
        if w.tile_code:
            lines.append(("class:label", f"  Location: "))
            lines.append(("", f"{w.tile_code}\n"))
        
        if w.template:
            lines.append(("class:label", f"  Template: "))
            lines.append(("", f"{w.template}\n"))
        
        lines.append(("class:label", f"\n  Description:\n"))
        lines.append(("", f"  {w.description}\n"))
        
        # Footer
        lines.append(("", "\n"))
        lines.append(("class:title", "╚═══════════════════════════════════════════════════════════════════════════════╝\n"))
        lines.append(("class:hint", "  ESC: Back\n"))
        
        return FormattedText(lines)
    
    def move_up(self):
        """Move selection up."""
        if self.view_mode == "workflows":
            max_idx = len(self.workflows) - 1
        elif self.view_mode == "templates":
            max_idx = len(self.TEMPLATES) - 1
        else:
            return
        
        if self.selected_index > 0:
            self.selected_index -= 1
    
    def move_down(self):
        """Move selection down."""
        if self.view_mode == "workflows":
            max_idx = len(self.workflows) - 1
        elif self.view_mode == "templates":
            max_idx = len(self.TEMPLATES) - 1
        else:
            return
        
        if self.selected_index < max_idx:
            self.selected_index += 1
    
    def select_current(self):
        """Select current item."""
        if self.view_mode == "workflows":
            if self.workflows and self.selected_index < len(self.workflows):
                self.selected_workflow = self.workflows[self.selected_index]
                self.view_mode = "details"
        
        elif self.view_mode == "templates":
            if self.selected_index < len(self.TEMPLATES):
                template = self.TEMPLATES[self.selected_index]
                workflow = self.create_workflow_from_template(template)
                self.view_mode = "workflows"
                self.selected_index = 0
    
    def go_back(self):
        """Navigate back."""
        if self.view_mode == "details":
            self.view_mode = "workflows"
            self.selected_workflow = None
        elif self.view_mode == "templates":
            self.view_mode = "workflows"
            self.selected_index = 0
    
    def show_templates(self):
        """Switch to templates view."""
        self.view_mode = "templates"
        self.selected_index = 0
    
    def handle_action(self, action: str):
        """Handle workflow action."""
        if not self.workflows or self.selected_index >= len(self.workflows):
            return
        
        workflow = self.workflows[self.selected_index]
        
        if action == "s":  # Start
            if workflow.state == WorkflowState.DRAFT:
                self.start_workflow(workflow)
        
        elif action == "p":  # Pause
            if workflow.state == WorkflowState.ACTIVE:
                self.pause_workflow(workflow)
        
        elif action == "r":  # Resume
            if workflow.state == WorkflowState.PAUSED:
                self.resume_workflow(workflow)
        
        elif action == "c":  # Complete
            if workflow.state in [WorkflowState.ACTIVE, WorkflowState.PAUSED]:
                self.complete_workflow(workflow)
        
        elif action == "d":  # Details
            self.selected_workflow = workflow
            self.view_mode = "details"
        
        elif action == "x":  # Delete
            state_file = self.state_dir / f"{workflow.id}.json"
            if state_file.exists():
                state_file.unlink()
            self._load_workflows()
    
    def handle_input(self, user_input: str) -> str:
        """Handle user input while panel is open.
        
        Args:
            user_input: Raw user input string
            
        Returns:
            Action result or empty string to stay in panel
        """
        inp = user_input.lower().strip()
        
        # Navigation
        if inp in ['up', '8', 'k']:
            self.move_up()
            return ""
        elif inp in ['down', '2', 'j']:
            self.move_down()
            return ""
        elif inp in ['enter', '5', '']:
            self.select_current()
            return ""
        elif inp in ['esc', 'q', '0']:
            return "close"
        
        # View switching
        elif inp in ['t', 'templates']:
            self.show_templates()
            return ""
        elif inp in ['w', 'workflows']:
            self.view_mode = "workflows"
            self.selected_index = 0
            return ""
        elif inp in ['back', 'b']:
            self.go_back()
            return ""
        
        # Workflow actions
        elif inp in ['s', 'start']:
            self.handle_action('s')
            return ""
        elif inp in ['p', 'pause']:
            self.handle_action('p')
            return ""
        elif inp in ['r', 'resume']:
            self.handle_action('r')
            return ""
        elif inp in ['c', 'complete']:
            self.handle_action('c')
            return ""
        elif inp in ['d', 'details']:
            self.handle_action('d')
            return ""
        elif inp in ['x', 'delete']:
            self.handle_action('x')
            return ""
        
        # Unknown command
        return ""
