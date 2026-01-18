"""
Missions API routes for workflow management.
"""

import sys
from pathlib import Path
from flask import Blueprint, jsonify, request

# Add core to path
core_path = Path(__file__).parent.parent.parent.parent / "core"
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))

missions_bp = Blueprint("missions", __name__)


def get_workflow_service():
    """Lazy import workflow service."""
    try:
        from core_beta.services.request_workflow_service import RequestWorkflowService

        return RequestWorkflowService()
    except ImportError:
        return None


@missions_bp.route("/api/missions/active", methods=["GET"])
def get_active_missions():
    """Get active missions and pending tasks."""
    service = get_workflow_service()

    if not service:
        return jsonify(
            {
                "missions": [],
                "pending_tasks": [],
                "error": "Workflow service not available",
            }
        )

    try:
        # Get active missions
        active_missions = []
        for mission in service.missions.values():
            if mission.status not in ["completed", "cancelled"]:
                completed_tasks = sum(
                    1 for t in mission.tasks if t.status == "completed"
                )
                progress = (
                    int((completed_tasks / len(mission.tasks)) * 100)
                    if mission.tasks
                    else 0
                )

                active_missions.append(
                    {
                        "id": mission.id,
                        "title": mission.title,
                        "description": mission.description,
                        "status": mission.status,
                        "progress": progress,
                        "tasks": [
                            {
                                "id": t.id,
                                "title": t.title,
                                "priority": (
                                    t.priority.value
                                    if hasattr(t.priority, "value")
                                    else t.priority
                                ),
                                "status": t.status,
                                "provider": (
                                    t.provider.value
                                    if hasattr(t.provider, "value")
                                    else str(t.provider)
                                ),
                                "estimated_cost": t.estimated_cost,
                                "attempts": t.attempts,
                            }
                            for t in mission.tasks[:10]  # Limit tasks
                        ],
                        "checklist": mission.checklist[:5] if mission.checklist else [],
                        "budget": mission.budget,
                        "actual_cost": mission.actual_cost,
                        "created_at": (
                            mission.created_at.isoformat()
                            if mission.created_at
                            else None
                        ),
                    }
                )

        # Get pending tasks not in missions
        pending_tasks = []
        for task in service.tasks.values():
            if task.status == "pending" and task.mission_id is None:
                pending_tasks.append(
                    {
                        "id": task.id,
                        "title": task.title,
                        "priority": (
                            task.priority.value
                            if hasattr(task.priority, "value")
                            else task.priority
                        ),
                        "status": task.status,
                        "provider": (
                            task.provider.value
                            if hasattr(task.provider, "value")
                            else str(task.provider)
                        ),
                        "estimated_cost": task.estimated_cost,
                    }
                )

        return jsonify(
            {
                "missions": active_missions,
                "pending_tasks": pending_tasks[:20],  # Limit pending tasks
            }
        )

    except Exception as e:
        return jsonify({"missions": [], "pending_tasks": [], "error": str(e)}), 500


@missions_bp.route("/api/missions", methods=["POST"])
def create_mission():
    """Create a new mission."""
    service = get_workflow_service()

    if not service:
        return jsonify({"error": "Workflow service not available"}), 503

    data = request.json or {}
    title = data.get("title", "New Mission")
    description = data.get("description", "")
    budget = data.get("budget")
    checklist = data.get("checklist", [])

    try:
        mission = service.create_mission(
            title=title,
            description=description,
            budget=float(budget) if budget else None,
            checklist=checklist,
        )

        return jsonify(
            {
                "success": True,
                "mission_id": mission.id,
                "message": f"Mission '{title}' created",
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@missions_bp.route("/api/missions/<mission_id>", methods=["GET"])
def get_mission(mission_id: str):
    """Get mission details."""
    service = get_workflow_service()

    if not service:
        return jsonify({"error": "Workflow service not available"}), 503

    mission = service.missions.get(mission_id)
    if not mission:
        return jsonify({"error": "Mission not found"}), 404

    completed_tasks = sum(1 for t in mission.tasks if t.status == "completed")
    progress = int((completed_tasks / len(mission.tasks)) * 100) if mission.tasks else 0

    return jsonify(
        {
            "id": mission.id,
            "title": mission.title,
            "description": mission.description,
            "status": mission.status,
            "progress": progress,
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "priority": (
                        t.priority.value if hasattr(t.priority, "value") else t.priority
                    ),
                    "status": t.status,
                    "provider": (
                        t.provider.value
                        if hasattr(t.provider, "value")
                        else str(t.provider)
                    ),
                    "estimated_cost": t.estimated_cost,
                    "actual_cost": t.actual_cost,
                    "attempts": t.attempts,
                    "result_summary": t.result_summary,
                }
                for t in mission.tasks
            ],
            "checklist": mission.checklist,
            "budget": mission.budget,
            "actual_cost": mission.actual_cost,
            "created_at": (
                mission.created_at.isoformat() if mission.created_at else None
            ),
            "completed_at": (
                mission.completed_at.isoformat() if mission.completed_at else None
            ),
        }
    )


@missions_bp.route("/api/missions/<mission_id>/tasks", methods=["POST"])
def add_task_to_mission(mission_id: str):
    """Add a task to a mission."""
    service = get_workflow_service()

    if not service:
        return jsonify({"error": "Workflow service not available"}), 503

    data = request.json or {}

    try:
        # Import enums
        from core_beta.services.request_workflow_service import RequestCategory, TaskPriority

        # Parse category
        category_str = data.get("category", "ai_generate")
        category = (
            RequestCategory(category_str)
            if category_str in [e.value for e in RequestCategory]
            else RequestCategory.AI_GENERATE
        )

        # Parse priority
        priority_str = data.get("priority", "normal")
        priority = (
            TaskPriority(priority_str)
            if priority_str in [e.value for e in TaskPriority]
            else TaskPriority.NORMAL
        )

        task = service.create_task(
            title=data.get("title", "New Task"),
            category=category,
            priority=priority,
            prompt=data.get("prompt", ""),
            estimated_cost=float(data.get("estimated_cost", 0)),
            mission_id=mission_id,
        )

        return jsonify(
            {"success": True, "task_id": task.id, "message": f"Task added to mission"}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@missions_bp.route("/api/missions/<mission_id>/cancel", methods=["POST"])
def cancel_mission(mission_id: str):
    """Cancel a mission."""
    service = get_workflow_service()

    if not service:
        return jsonify({"error": "Workflow service not available"}), 503

    try:
        success = service.cancel_mission(mission_id)

        if success:
            return jsonify({"success": True, "message": "Mission cancelled"})
        else:
            return jsonify({"error": "Failed to cancel mission"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@missions_bp.route("/api/tasks", methods=["POST"])
def create_task():
    """Create a standalone task."""
    service = get_workflow_service()

    if not service:
        return jsonify({"error": "Workflow service not available"}), 503

    data = request.json or {}

    try:
        from core_beta.services.request_workflow_service import RequestCategory, TaskPriority

        category_str = data.get("category", "ai_generate")
        category = (
            RequestCategory(category_str)
            if category_str in [e.value for e in RequestCategory]
            else RequestCategory.AI_GENERATE
        )

        priority_str = data.get("priority", "normal")
        priority = (
            TaskPriority(priority_str)
            if priority_str in [e.value for e in TaskPriority]
            else TaskPriority.NORMAL
        )

        task = service.create_task(
            title=data.get("title", "New Task"),
            category=category,
            priority=priority,
            prompt=data.get("prompt", ""),
            estimated_cost=float(data.get("estimated_cost", 0)),
        )

        return jsonify(
            {
                "success": True,
                "task_id": task.id,
                "message": f"Task '{task.title}' created",
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@missions_bp.route("/api/tasks/<task_id>/complete", methods=["POST"])
def complete_task(task_id: str):
    """Mark a task as completed."""
    service = get_workflow_service()

    if not service:
        return jsonify({"error": "Workflow service not available"}), 503

    data = request.json or {}

    try:
        success = service.complete_task(
            task_id=task_id,
            result=data.get("result"),
            actual_cost=float(data.get("actual_cost", 0)),
        )

        if success:
            return jsonify({"success": True, "message": "Task completed"})
        else:
            return jsonify({"error": "Failed to complete task"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === Milestone Endpoints ===


@missions_bp.route("/api/missions/<mission_id>/milestones", methods=["GET"])
def get_mission_milestones(mission_id: str):
    """Get all milestones for a mission."""
    service = get_workflow_service()

    if not service:
        return jsonify({"error": "Workflow service not available"}), 503

    try:
        milestones = service.get_mission_milestones(mission_id)
        if not milestones and mission_id not in service._missions:
            return jsonify({"error": "Mission not found"}), 404

        return jsonify(
            {
                "mission_id": mission_id,
                "milestones": milestones,
                "total": len(milestones),
                "reached": sum(1 for m in milestones if m.get("status") == "reached"),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@missions_bp.route("/api/missions/<mission_id>/milestones", methods=["POST"])
def add_milestone(mission_id: str):
    """Add a milestone to a mission."""
    service = get_workflow_service()

    if not service:
        return jsonify({"error": "Workflow service not available"}), 503

    data = request.json or {}

    try:
        milestone = service.add_milestone(
            mission_id=mission_id,
            title=data.get("title", "New Milestone"),
            description=data.get("description", ""),
            required_tasks=data.get("required_tasks", []),
            required_checklist_items=data.get("required_checklist_items", []),
            progress_threshold=float(data.get("progress_threshold", 0)),
            is_checkpoint=data.get("is_checkpoint", False),
            celebration_message=data.get("celebration_message", ""),
            order=data.get("order"),
        )

        if milestone:
            return jsonify(
                {
                    "success": True,
                    "milestone": milestone.to_dict(),
                    "message": f"Milestone '{milestone.title}' added",
                }
            )
        else:
            return (
                jsonify({"error": "Failed to add milestone - mission not found"}),
                404,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@missions_bp.route("/api/missions/<mission_id>/milestones/check", methods=["POST"])
def check_milestones(mission_id: str):
    """Check and update milestone progress."""
    service = get_workflow_service()

    if not service:
        return jsonify({"error": "Workflow service not available"}), 503

    try:
        result = service.check_milestone_progress(mission_id)

        if "error" in result:
            return jsonify(result), 404

        return jsonify(
            {
                "success": True,
                **result,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@missions_bp.route(
    "/api/missions/<mission_id>/milestones/<milestone_id>/skip", methods=["POST"]
)
def skip_milestone(mission_id: str, milestone_id: str):
    """Skip a milestone."""
    service = get_workflow_service()

    if not service:
        return jsonify({"error": "Workflow service not available"}), 503

    data = request.json or {}
    reason = data.get("reason", "")

    try:
        success = service.skip_milestone(mission_id, milestone_id, reason)

        if success:
            return jsonify(
                {
                    "success": True,
                    "message": "Milestone skipped",
                }
            )
        else:
            return jsonify({"error": "Milestone not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@missions_bp.route("/api/missions/<mission_id>/milestones/standard", methods=["POST"])
def create_standard_milestones(mission_id: str):
    """Create standard milestone waypoints."""
    service = get_workflow_service()

    if not service:
        return jsonify({"error": "Workflow service not available"}), 503

    data = request.json or {}
    milestone_type = data.get("type", "quartile")

    try:
        milestones = service.create_standard_milestones(mission_id, milestone_type)

        if milestones:
            return jsonify(
                {
                    "success": True,
                    "milestones": [m.to_dict() for m in milestones],
                    "message": f"Created {len(milestones)} {milestone_type} milestones",
                }
            )
        else:
            return (
                jsonify({"error": "Failed to create milestones - mission not found"}),
                404,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@missions_bp.route("/api/workflow/stats", methods=["GET"])
def get_workflow_stats():
    """Get workflow statistics."""
    service = get_workflow_service()

    if not service:
        return jsonify(
            {
                "total_missions": 0,
                "active_missions": 0,
                "total_tasks": 0,
                "pending_tasks": 0,
                "completed_tasks": 0,
                "total_cost": 0.0,
            }
        )

    try:
        active_missions = sum(
            1
            for m in service.missions.values()
            if m.status not in ["completed", "cancelled"]
        )
        completed_tasks = sum(
            1 for t in service.tasks.values() if t.status == "completed"
        )
        pending_tasks = sum(1 for t in service.tasks.values() if t.status == "pending")
        total_cost = sum(m.actual_cost or 0 for m in service.missions.values())

        return jsonify(
            {
                "total_missions": len(service.missions),
                "active_missions": active_missions,
                "total_tasks": len(service.tasks),
                "pending_tasks": pending_tasks,
                "completed_tasks": completed_tasks,
                "total_cost": total_cost,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
