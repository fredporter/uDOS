"""
GitHub Actions Monitor
======================

Service to monitor GitHub Actions workflows and provide self-healing capabilities.
Receives webhooks from GitHub, analyzes failures, and can trigger auto-fixes.

Features:
  - Webhook receiver for workflow_run events
  - Failure analysis and pattern detection
  - Auto-retry for transient failures
  - Notification to Wizard console
  - Integration with GitHub CLI for status checks
"""

import asyncio
import json
import subprocess
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass


@dataclass
class WorkflowRun:
    """GitHub Actions workflow run information."""
    id: int
    name: str
    status: str  # queued, in_progress, completed
    conclusion: Optional[str]  # success, failure, cancelled, skipped
    html_url: str
    created_at: str
    updated_at: str
    head_branch: str
    head_sha: str
    

class GitHubActionsMonitor:
    """Monitor GitHub Actions workflows and provide self-healing."""
    
    def __init__(self, repo_path: Path = None):
        """Initialize monitor."""
        self.repo_path = repo_path or Path.cwd()
        self.workflow_history: List[WorkflowRun] = []
        self.failure_patterns: Dict[str, int] = {}
        
    async def handle_webhook(self, event: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming GitHub webhook.
        
        Args:
            event: Event type (e.g., 'workflow_run')
            payload: Webhook payload
            
        Returns:
            Response dict with action taken
        """
        if event == "workflow_run":
            return await self._handle_workflow_run(payload)
        elif event == "ping":
            return {"status": "ok", "message": "Webhook receiver active"}
        else:
            return {"status": "ignored", "message": f"Unknown event type: {event}"}
    
    async def _handle_workflow_run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow_run event."""
        action = payload.get("action")
        workflow_run = payload.get("workflow_run", {})
        
        # Extract workflow info
        run_info = WorkflowRun(
            id=workflow_run.get("id"),
            name=workflow_run.get("name"),
            status=workflow_run.get("status"),
            conclusion=workflow_run.get("conclusion"),
            html_url=workflow_run.get("html_url"),
            created_at=workflow_run.get("created_at"),
            updated_at=workflow_run.get("updated_at"),
            head_branch=workflow_run.get("head_branch"),
            head_sha=workflow_run.get("head_sha"),
        )
        
        self.workflow_history.append(run_info)
        
        # Log to console
        print(f"\n🔔 GitHub Actions: {run_info.name}")
        print(f"   Status: {run_info.status} - {run_info.conclusion or 'in progress'}")
        print(f"   Branch: {run_info.head_branch}")
        print(f"   URL: {run_info.html_url}")
        
        # Handle completed workflows
        if action == "completed":
            if run_info.conclusion == "failure":
                return await self._handle_failure(run_info)
            elif run_info.conclusion == "success":
                print("   ✅ Workflow completed successfully\n")
                return {"status": "success", "action": "none"}
        
        return {"status": "acknowledged"}
    
    async def _handle_failure(self, run_info: WorkflowRun) -> Dict[str, Any]:
        """Handle workflow failure with self-healing logic."""
        print(f"   ❌ Workflow failed - analyzing...\n")
        
        # Get failure details using GitHub CLI
        failure_reason = await self._get_failure_reason(run_info)
        
        # Track failure pattern
        pattern_key = f"{run_info.name}:{failure_reason}"
        self.failure_patterns[pattern_key] = self.failure_patterns.get(pattern_key, 0) + 1
        
        # Check if this is a transient failure (retry candidate)
        if self._is_transient_failure(failure_reason):
            print("   🔄 Detected transient failure - attempting auto-retry...")
            retry_result = await self._retry_workflow(run_info)
            return {"status": "failure", "action": "auto_retry", "result": retry_result}
        
        # Check for known fixable patterns
        fix_result = await self._attempt_auto_fix(run_info, failure_reason)
        if fix_result["fixed"]:
            return {"status": "failure", "action": "auto_fix", "result": fix_result}
        
        # No auto-fix available - notify for manual intervention
        print("   ⚠️  Manual intervention required")
        print(f"   Failure reason: {failure_reason}\n")
        return {
            "status": "failure",
            "action": "notify",
            "reason": failure_reason,
            "url": run_info.html_url
        }
    
    async def _get_failure_reason(self, run_info: WorkflowRun) -> str:
        """Get failure reason from workflow logs using GitHub CLI."""
        try:
            # Use GitHub CLI to get run details
            result = subprocess.run(
                ["gh", "run", "view", str(run_info.id), "--repo", self._get_repo_name()],
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                # Parse output for failure reason
                output = result.stdout
                if "test" in output.lower() and "failed" in output.lower():
                    return "test_failure"
                elif "build" in output.lower() and "failed" in output.lower():
                    return "build_failure"
                elif "timeout" in output.lower():
                    return "timeout"
                elif "network" in output.lower() or "connection" in output.lower():
                    return "network_error"
                else:
                    return "unknown"
            else:
                return "cli_error"
                
        except subprocess.TimeoutExpired:
            return "timeout"
        except FileNotFoundError:
            print("   ⚠️  GitHub CLI not installed - install with 'brew install gh'")
            return "no_cli"
        except Exception as e:
            print(f"   ⚠️  Error getting failure reason: {e}")
            return "unknown"
    
    def _is_transient_failure(self, failure_reason: str) -> bool:
        """Check if failure is transient (network, timeout, etc.)."""
        transient_reasons = {"timeout", "network_error", "connection_error"}
        return failure_reason in transient_reasons
    
    async def _retry_workflow(self, run_info: WorkflowRun) -> Dict[str, Any]:
        """Retry failed workflow using GitHub CLI."""
        try:
            result = subprocess.run(
                ["gh", "run", "rerun", str(run_info.id), "--repo", self._get_repo_name()],
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode == 0:
                print("   ✅ Workflow re-triggered successfully\n")
                return {"success": True, "message": "Workflow re-triggered"}
            else:
                error = result.stderr or "Unknown error"
                print(f"   ❌ Failed to retry workflow: {error}\n")
                return {"success": False, "error": error}
                
        except Exception as e:
            print(f"   ❌ Error retrying workflow: {e}\n")
            return {"success": False, "error": str(e)}
    
    async def _attempt_auto_fix(self, run_info: WorkflowRun, failure_reason: str) -> Dict[str, Any]:
        """Attempt automatic fixes for known failure patterns."""
        
        # Auto-fix pattern: dependency installation failures
        if failure_reason == "build_failure":
            print("   🔧 Attempting dependency cache clear...")
            # TODO: Trigger workflow with cache clear
            return {"fixed": False, "reason": "Manual cache clear required"}
        
        # Auto-fix pattern: test flakiness
        if failure_reason == "test_failure":
            # Check failure count for this pattern
            pattern_key = f"{run_info.name}:{failure_reason}"
            count = self.failure_patterns.get(pattern_key, 0)
            
            if count <= 2:
                print("   🔧 Test failure detected - auto-retrying (flaky test suspected)")
                return await self._retry_workflow(run_info)
        
        # No auto-fix available
        return {"fixed": False, "reason": "No auto-fix available"}
    
    def _get_repo_name(self) -> str:
        """Get GitHub repository name from git config."""
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            
            if result.returncode == 0:
                url = result.stdout.strip()
                # Parse github.com/owner/repo from URL
                if "github.com" in url:
                    parts = url.split("github.com")[1].strip("/:").split("/")
                    if len(parts) >= 2:
                        owner = parts[0]
                        repo = parts[1].replace(".git", "")
                        return f"{owner}/{repo}"
            
            return "unknown/unknown"
            
        except Exception:
            return "unknown/unknown"
    
    async def get_recent_runs(self, limit: int = 10) -> List[WorkflowRun]:
        """Get recent workflow runs using GitHub CLI."""
        try:
            result = subprocess.run(
                ["gh", "run", "list", "--repo", self._get_repo_name(), "--limit", str(limit), "--json", "databaseId,name,status,conclusion,url,createdAt,updatedAt,headBranch,headSha"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                runs_data = json.loads(result.stdout)
                runs = []
                for run in runs_data:
                    runs.append(WorkflowRun(
                        id=run["databaseId"],
                        name=run["name"],
                        status=run["status"],
                        conclusion=run.get("conclusion"),
                        html_url=run["url"],
                        created_at=run["createdAt"],
                        updated_at=run["updatedAt"],
                        head_branch=run["headBranch"],
                        head_sha=run["headSha"],
                    ))
                return runs
            else:
                return []
                
        except Exception as e:
            print(f"Error getting recent runs: {e}")
            return []


# Singleton instance
_monitor_instance: Optional[GitHubActionsMonitor] = None


def get_github_monitor() -> GitHubActionsMonitor:
    """Get GitHub Actions monitor singleton."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = GitHubActionsMonitor()
    return _monitor_instance
