"""
Mission & Task Templates for uDOS Workflow System

Templates for quickly creating new projects with pre-configured mission definitions,
task structures, and seed data suitable for AI ingestion and import handling.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path


class MissionTemplates:
    """Pre-defined mission templates for common project types."""

    @staticmethod
    def software_project() -> Dict[str, Any]:
        """Template for software development projects."""
        return {
            "id": "software-project",
            "name": "Software Development Project",
            "description": "Standard software development with requirements, implementation, testing, and deployment",
            "guidelines": (
                "1. Follow SOLID principles\n"
                "2. Write tests for all features\n"
                "3. Conduct code reviews\n"
                "4. Document APIs and modules\n"
                "5. Use semantic versioning"
            ),
            "process": (
                "1. Create feature branch\n"
                "2. Implement functionality\n"
                "3. Write unit tests\n"
                "4. Submit PR for review\n"
                "5. Address feedback\n"
                "6. Merge to main\n"
                "7. Deploy to staging\n"
                "8. QA testing\n"
                "9. Deploy to production"
            )
        }

    @staticmethod
    def research_project() -> Dict[str, Any]:
        """Template for research and exploration projects."""
        return {
            "id": "research-project",
            "name": "Research & Exploration",
            "description": "Research projects focused on learning, prototyping, and knowledge discovery",
            "guidelines": (
                "1. Document assumptions\n"
                "2. Validate hypotheses\n"
                "3. Share findings\n"
                "4. Link to references\n"
                "5. Keep notes organized"
            ),
            "process": (
                "1. Define research question\n"
                "2. Literature review\n"
                "3. Design experiment/prototype\n"
                "4. Execute\n"
                "5. Analyze results\n"
                "6. Document conclusions\n"
                "7. Share findings"
            )
        }

    @staticmethod
    def marketing_campaign() -> Dict[str, Any]:
        """Template for marketing campaigns."""
        return {
            "id": "marketing-campaign",
            "name": "Marketing Campaign",
            "description": "Coordinated marketing campaign with multiple channels and stakeholders",
            "guidelines": (
                "1. Maintain brand consistency\n"
                "2. Target audience alignment\n"
                "3. Measure analytics\n"
                "4. Coordinate across channels\n"
                "5. Document results"
            ),
            "process": (
                "1. Define objectives and KPIs\n"
                "2. Plan channels and timeline\n"
                "3. Create content\n"
                "4. Schedule posts\n"
                "5. Monitor performance\n"
                "6. Engage with audience\n"
                "7. Analyze and optimize\n"
                "8. Report results"
            )
        }

    @staticmethod
    def event_planning() -> Dict[str, Any]:
        """Template for event planning."""
        return {
            "id": "event-planning",
            "name": "Event Planning",
            "description": "Comprehensive event planning from concept to execution and follow-up",
            "guidelines": (
                "1. Coordinate with stakeholders\n"
                "2. Track budget carefully\n"
                "3. Plan contingencies\n"
                "4. Maintain timeline\n"
                "5. Communicate clearly"
            ),
            "process": (
                "1. Define event scope\n"
                "2. Set budget and timeline\n"
                "3. Book venue/vendors\n"
                "4. Plan logistics\n"
                "5. Send invitations\n"
                "6. Confirm RSVPs\n"
                "7. Execute event\n"
                "8. Collect feedback\n"
                "9. Post-event wrap-up"
            )
        }

    @staticmethod
    def hiring_pipeline() -> Dict[str, Any]:
        """Template for recruitment and hiring process."""
        return {
            "id": "hiring-pipeline",
            "name": "Hiring & Recruitment",
            "description": "End-to-end recruiting from job posting to onboarding",
            "guidelines": (
                "1. Maintain recruiting standards\n"
                "2. Fair evaluation process\n"
                "3. Timely communication\n"
                "4. Document decisions\n"
                "5. Follow compliance requirements"
            ),
            "process": (
                "1. Define role requirements\n"
                "2. Post job opening\n"
                "3. Screen applications\n"
                "4. Schedule interviews\n"
                "5. Conduct technical assessment\n"
                "6. Team interviews\n"
                "7. Make offer\n"
                "8. Negotiation\n"
                "9. Onboarding preparation"
            )
        }


class TaskTemplates:
    """Pre-defined task templates for different item types."""

    @staticmethod
    def create_standard_tasks(project_id: str) -> List[Dict[str, Any]]:
        """Create standard starter tasks for a project."""
        return [
            {
                "id": f"task-setup-{project_id}-001",
                "mission_id": project_id,
                "title": "Project kickoff meeting",
                "description": "Initial project meeting with team to align on goals and timeline",
                "item_type": "task",
                "status": "todo",
                "priority": "high",
                "tags": ["kickoff", "planning"],
                "source": "manual",
                "metadata": {},
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat()
            },
            {
                "id": f"task-setup-{project_id}-002",
                "mission_id": project_id,
                "title": "Set up project infrastructure",
                "description": "Create repositories, set up CI/CD, configure environments",
                "item_type": "task",
                "status": "todo",
                "priority": "high",
                "tags": ["setup", "infrastructure"],
                "source": "manual",
                "metadata": {},
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat()
            },
            {
                "id": f"task-setup-{project_id}-003",
                "mission_id": project_id,
                "title": "Document project scope and requirements",
                "description": "Create detailed project documentation",
                "item_type": "task",
                "status": "todo",
                "priority": "medium",
                "tags": ["documentation", "planning"],
                "source": "manual",
                "metadata": {},
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat()
            }
        ]

    @staticmethod
    def create_calendar_event(
        mission_id: str,
        title: str,
        description: str,
        event_datetime: str,
        duration_minutes: int = 60,
        organizer: str = "organizer@company.com"
    ) -> Dict[str, Any]:
        """Create a calendar event task."""
        start = datetime.fromisoformat(event_datetime)
        end = start + timedelta(minutes=duration_minutes)

        return {
            "id": f"evt-{mission_id}-{datetime.now().timestamp()}",
            "mission_id": mission_id,
            "title": title,
            "description": description,
            "item_type": "calendar_event",
            "status": "todo",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "organizer": organizer,
            "attendees": [
                {
                    "name": "Organizer",
                    "email": organizer,
                    "status": "accepted"
                }
            ],
            "tags": ["calendar", "meeting"],
            "source": "manual",
            "metadata": {
                "recurring": False
            },
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }

    @staticmethod
    def create_reminder(
        mission_id: str,
        title: str,
        description: str,
        due_datetime: str,
        alert_type: str = "notification",
        alert_interval: str = "1hour"
    ) -> Dict[str, Any]:
        """Create a reminder task."""
        return {
            "id": f"rem-{mission_id}-{datetime.now().timestamp()}",
            "mission_id": mission_id,
            "title": title,
            "description": description,
            "item_type": "reminder",
            "status": "todo",
            "priority": "high",
            "due_date": due_datetime,
            "tags": ["reminder"],
            "source": "manual",
            "metadata": {
                "alert_type": alert_type,
                "alert_interval": alert_interval
            },
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }

    @staticmethod
    def create_imported_item(
        mission_id: str,
        title: str,
        description: str,
        source: str,
        source_id: str,
        item_category: str = "imported",
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """Create an imported item task."""
        return {
            "id": f"imp-{mission_id}-{datetime.now().timestamp()}",
            "mission_id": mission_id,
            "title": title,
            "description": description,
            "item_type": "imported",
            "status": "todo",
            "priority": priority,
            "tags": ["imported", source],
            "source": source,
            "source_id": source_id,
            "metadata": {
                "item_category": item_category,
                "import_timestamp": datetime.now().isoformat()
            },
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }


class ProjectInitializer:
    """Initialize new projects with templates and seed data."""

    @staticmethod
    def initialize_project(
        project_id: str,
        vault_root: str,
        template_type: str = "software_project",
        with_seed_tasks: bool = True
    ) -> Dict[str, Any]:
        """
        Initialize a new project with mission and optional seed tasks.

        Args:
            project_id: Unique project identifier
            vault_root: Path to vault root directory
            template_type: Type of mission template (software_project, research_project, etc.)
            with_seed_tasks: Whether to create starter tasks

        Returns:
            Status and paths created
        """
        # Get mission template
        if template_type == "software_project":
            mission = MissionTemplates.software_project()
        elif template_type == "research_project":
            mission = MissionTemplates.research_project()
        elif template_type == "marketing_campaign":
            mission = MissionTemplates.marketing_campaign()
        elif template_type == "event_planning":
            mission = MissionTemplates.event_planning()
        elif template_type == "hiring_pipeline":
            mission = MissionTemplates.hiring_pipeline()
        else:
            return {"status": "error", "message": f"Unknown template: {template_type}"}

        # Create project directory
        project_dir = Path(vault_root) / "@binders" / project_id
        project_dir.mkdir(parents=True, exist_ok=True)

        # Update mission ID to match project
        mission["id"] = project_id

        # Write mission.json
        mission_path = project_dir / "mission.json"
        with open(mission_path, 'w') as f:
            json.dump(mission, f, indent=4)

        # Create moves.json with optional seed tasks
        moves_data = {"moves": []}
        if with_seed_tasks:
            moves_data["moves"] = TaskTemplates.create_standard_tasks(project_id)

        moves_path = project_dir / "moves.json"
        with open(moves_path, 'w') as f:
            json.dump(moves_data, f, indent=4)

        # Create empty milestones.json
        milestones_path = project_dir / "milestones.json"
        with open(milestones_path, 'w') as f:
            json.dump({"milestones": []}, f, indent=4)

        return {
            "status": "success",
            "project_id": project_id,
            "template": template_type,
            "paths": {
                "mission": str(mission_path),
                "moves": str(moves_path),
                "milestones": str(milestones_path)
            },
            "seed_tasks": len(moves_data["moves"]) if with_seed_tasks else 0
        }


if __name__ == "__main__":
    # Example: Initialize new project
    result = ProjectInitializer.initialize_project(
        project_id="my-startup",
        vault_root="./vault",
        template_type="software_project",
        with_seed_tasks=True
    )
    print(json.dumps(result, indent=2))
