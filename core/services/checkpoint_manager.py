"""
Checkpoint Manager for uDOS Workflows (v1.2.20)

Manages workflow state checkpoints with save, resume, and rollback capabilities.
Supports auto-save at critical workflow milestones and manual checkpoint creation.

Features:
- Save workflow state at milestones
- Resume from specific checkpoint
- Checkpoint history and timeline
- Rollback to previous state
- Auto-save on critical workflow steps
- Progress visualization

Storage: memory/workflows/checkpoints/

Usage:
    from core.services.checkpoint_manager import CheckpointManager
    
    mgr = CheckpointManager()
    
    # Create checkpoint
    checkpoint_id = mgr.create_checkpoint(workflow_id, state_data)
    
    # List checkpoints
    checkpoints = mgr.list_checkpoints(workflow_id)
    
    # Resume from checkpoint
    state = mgr.load_checkpoint(checkpoint_id)
    
    # Rollback
    previous_state = mgr.rollback(workflow_id)
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from core.utils.path_manager import PATHS


@dataclass
class Checkpoint:
    """Workflow checkpoint data."""
    id: str
    workflow_id: str
    timestamp: str
    label: str
    state: Dict[str, Any]
    auto_created: bool
    previous_checkpoint: Optional[str]
    next_checkpoint: Optional[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Checkpoint':
        """Create from dictionary."""
        return cls(**data)


class CheckpointManager:
    """Manages workflow checkpoints and state persistence."""
    
    def __init__(self):
        """Initialize checkpoint manager."""
        self.checkpoints_dir = PATHS.MEMORY / "workflows" / "checkpoints"
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        
        # Archive old checkpoints
        self.archive_dir = self.checkpoints_dir / ".archive"
        self.archive_dir.mkdir(exist_ok=True)
        
        # Retention policy (days)
        self.retention_days = 30
    
    def create_checkpoint(
        self,
        workflow_id: str,
        state: Dict[str, Any],
        label: Optional[str] = None,
        auto_created: bool = False
    ) -> str:
        """Create a new checkpoint.
        
        Args:
            workflow_id: Workflow identifier
            state: Current workflow state to save
            label: Optional checkpoint label
            auto_created: Whether checkpoint was auto-created
            
        Returns:
            Checkpoint ID
        """
        # Generate checkpoint ID
        timestamp = datetime.now()
        timestamp_str = timestamp.isoformat()
        
        checkpoint_id = self._generate_checkpoint_id(workflow_id, timestamp)
        
        # Get previous checkpoint (for linked list)
        previous_checkpoint = self._get_latest_checkpoint_id(workflow_id)
        
        # Create checkpoint
        checkpoint = Checkpoint(
            id=checkpoint_id,
            workflow_id=workflow_id,
            timestamp=timestamp_str,
            label=label or f"Checkpoint {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            state=state,
            auto_created=auto_created,
            previous_checkpoint=previous_checkpoint,
            next_checkpoint=None,
            metadata={
                "progress": state.get("progress", "0/0"),
                "current_step": state.get("current_step", 0),
                "total_steps": state.get("total_steps", 0)
            }
        )
        
        # Update previous checkpoint's next pointer
        if previous_checkpoint:
            try:
                prev_cp = self.load_checkpoint(previous_checkpoint)
                if prev_cp:
                    prev_cp.next_checkpoint = checkpoint_id
                    self._save_checkpoint(prev_cp)
            except Exception:
                pass  # Ignore if previous checkpoint is missing
        
        # Save checkpoint
        self._save_checkpoint(checkpoint)
        
        return checkpoint_id
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Load checkpoint by ID.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            Checkpoint object or None if not found
        """
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            with open(checkpoint_file, "r") as f:
                data = json.load(f)
            return Checkpoint.from_dict(data)
        except Exception as e:
            print(f"Error loading checkpoint {checkpoint_id}: {e}")
            return None
    
    def list_checkpoints(
        self,
        workflow_id: str,
        limit: Optional[int] = None
    ) -> List[Checkpoint]:
        """List checkpoints for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            limit: Optional limit on number of checkpoints
            
        Returns:
            List of checkpoints (newest first)
        """
        checkpoints = []
        
        # Load all checkpoint files for this workflow
        for checkpoint_file in self.checkpoints_dir.glob(f"{workflow_id}_*.json"):
            try:
                with open(checkpoint_file, "r") as f:
                    data = json.load(f)
                checkpoints.append(Checkpoint.from_dict(data))
            except Exception:
                pass
        
        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda cp: cp.timestamp, reverse=True)
        
        if limit:
            checkpoints = checkpoints[:limit]
        
        return checkpoints
    
    def get_checkpoint_timeline(self, workflow_id: str) -> List[Checkpoint]:
        """Get ordered timeline of checkpoints.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            List of checkpoints in chronological order
        """
        checkpoints = self.list_checkpoints(workflow_id)
        # Reverse to get chronological order (oldest first)
        return list(reversed(checkpoints))
    
    def rollback(self, workflow_id: str, steps: int = 1) -> Optional[Checkpoint]:
        """Rollback to previous checkpoint.
        
        Args:
            workflow_id: Workflow identifier
            steps: Number of checkpoints to roll back
            
        Returns:
            Checkpoint to restore, or None if not available
        """
        checkpoints = self.list_checkpoints(workflow_id)
        
        if not checkpoints:
            return None
        
        # Get checkpoint at specified position
        if steps >= len(checkpoints):
            # Rollback to first checkpoint
            return checkpoints[-1]
        else:
            return checkpoints[steps]
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            True if deleted, False otherwise
        """
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        
        if checkpoint_file.exists():
            try:
                # Move to archive instead of deleting
                archive_file = self.archive_dir / checkpoint_file.name
                checkpoint_file.rename(archive_file)
                return True
            except Exception as e:
                print(f"Error deleting checkpoint {checkpoint_id}: {e}")
                return False
        
        return False
    
    def cleanup_old_checkpoints(self, workflow_id: str, keep_count: int = 10):
        """Clean up old checkpoints for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            keep_count: Number of recent checkpoints to keep
        """
        checkpoints = self.list_checkpoints(workflow_id)
        
        # Keep the most recent N checkpoints
        if len(checkpoints) > keep_count:
            old_checkpoints = checkpoints[keep_count:]
            
            for checkpoint in old_checkpoints:
                self.delete_checkpoint(checkpoint.id)
    
    def auto_checkpoint(
        self,
        workflow_id: str,
        state: Dict[str, Any],
        milestone: str
    ) -> str:
        """Create auto-checkpoint at workflow milestone.
        
        Args:
            workflow_id: Workflow identifier
            state: Current workflow state
            milestone: Milestone description
            
        Returns:
            Checkpoint ID
        """
        label = f"Auto: {milestone}"
        return self.create_checkpoint(
            workflow_id=workflow_id,
            state=state,
            label=label,
            auto_created=True
        )
    
    def get_workflow_progress(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow progress from checkpoints.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Progress summary with timeline
        """
        checkpoints = self.get_checkpoint_timeline(workflow_id)
        
        if not checkpoints:
            return {
                "total_checkpoints": 0,
                "latest_checkpoint": None,
                "progress": "0%",
                "timeline": []
            }
        
        latest = checkpoints[-1]
        
        # Calculate progress from latest checkpoint
        progress = "0%"
        if "progress" in latest.metadata:
            progress = latest.metadata["progress"]
        
        # Build timeline
        timeline = []
        for cp in checkpoints:
            timeline.append({
                "id": cp.id,
                "timestamp": cp.timestamp,
                "label": cp.label,
                "progress": cp.metadata.get("progress", "0%"),
                "auto": cp.auto_created
            })
        
        return {
            "total_checkpoints": len(checkpoints),
            "latest_checkpoint": latest.id,
            "progress": progress,
            "timeline": timeline
        }
    
    # Private helper methods
    
    def _generate_checkpoint_id(self, workflow_id: str, timestamp: datetime) -> str:
        """Generate unique checkpoint ID.
        
        Args:
            workflow_id: Workflow identifier
            timestamp: Checkpoint timestamp
            
        Returns:
            Checkpoint ID
        """
        # Format: workflow_id_YYYYMMDD_HHMMSS_hash
        ts_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Short hash for uniqueness
        hash_input = f"{workflow_id}{timestamp.isoformat()}"
        short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:6]
        
        return f"{workflow_id}_{ts_str}_{short_hash}"
    
    def _get_latest_checkpoint_id(self, workflow_id: str) -> Optional[str]:
        """Get ID of most recent checkpoint for workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Checkpoint ID or None
        """
        checkpoints = self.list_checkpoints(workflow_id, limit=1)
        return checkpoints[0].id if checkpoints else None
    
    def _save_checkpoint(self, checkpoint: Checkpoint):
        """Save checkpoint to disk.
        
        Args:
            checkpoint: Checkpoint object
        """
        checkpoint_file = self.checkpoints_dir / f"{checkpoint.id}.json"
        
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint.to_dict(), f, indent=2)


# Global checkpoint manager instance
_checkpoint_manager: Optional[CheckpointManager] = None


def get_checkpoint_manager() -> CheckpointManager:
    """Get global checkpoint manager instance."""
    global _checkpoint_manager
    if _checkpoint_manager is None:
        _checkpoint_manager = CheckpointManager()
    return _checkpoint_manager
